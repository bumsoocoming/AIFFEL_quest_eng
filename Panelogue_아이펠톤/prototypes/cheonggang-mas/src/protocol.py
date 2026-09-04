from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


OUTCOME_VALUES = {
    "FULL_PRESERVE",
    "PARTIAL",
    "RECORD_AND_DEVELOP",
    "DEADLOCK",
}


@dataclass
class Agent:
    id: str
    name: str
    title: str
    speaking_style: str
    goal: str
    red_lines: list[str]
    private_brief: str
    reveal_hint: str = ""
    duties: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return f"{self.name} ({self.title})"


@dataclass
class Turn:
    round: int
    agent_id: str
    agent_label: str
    text: str


@dataclass
class RunResult:
    mode: str
    model: str
    provider: str
    turns: list[Turn]
    communique_raw: str
    communique: dict[str, Any]
    revealed_facts: list[str]


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_agents(path: Path) -> tuple[list[Agent], Agent]:
    data = load_yaml(path)
    people = [Agent(**row) for row in data["stakeholders"]]
    med = Agent(**data["mediator"])
    return people, med


def parse_communique(text: str) -> dict[str, Any]:
    raw = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.S)
    if fenced:
        raw = fenced.group(1)
    else:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            raw = raw[start : end + 1]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "outcome_type": "DEADLOCK",
            "summary": text.strip(),
            "parse_error": True,
        }
    outcome = str(data.get("outcome_type", "DEADLOCK")).upper()
    if outcome not in OUTCOME_VALUES:
        data["outcome_type"] = "DEADLOCK"
    return data


JSON_SCHEMA = """
반드시 아래 JSON만 출력한다. JSON 앞뒤에 설명을 붙이지 않는다.
{
  "outcome_type": "FULL_PRESERVE | PARTIAL | RECORD_AND_DEVELOP | DEADLOCK",
  "stop_work": true,
  "survey_months": 0,
  "preservation_share_percent": 0,
  "developer_pays_excavation": true,
  "delay_months": 0,
  "resident_compensation": "한 줄",
  "illegal_actions": ["최종안에 남은 위법·편법 요소. 없으면 빈 배열"],
  "unresolved": ["합의 못 한 것"],
  "summary": "한국어 5~8문장 합의 내용. 말한 것만 적을 것."
}
""".strip()


def stakeholder_system(agent: Agent, briefing: str, max_chars: int) -> str:
    red = "\n".join(f"- {x}" for x in agent.red_lines)
    return f"""당신은 가상 정책 시뮬레이션의 역할이다. 실존 인물이 아니다.

역할: {agent.label}
말투: {agent.speaking_style}
목표: {agent.goal}
절대 양보 못 하는 것:
{red}

[공개 브리핑]
{briefing}

[당신만 아는 내부 정보]
{agent.private_brief.strip()}

규칙:
- 한국어로만 말한다. 한 턴 {max_chars}자 이내.
- 역할에서 벗어나지 않는다. 다른 사람 대변은 하지 않는다.
- 내부 정보는 전략적으로 공개하거나 숨길 수 있다. {agent.reveal_hint}
- 없는 법령, 없는 예산, 없는 조사 결과를 만들지 않는다.
- 회의를 빨리 끝내려고 실현 불가능한 숫자에 합의하지 않는다.
"""


def mediator_system(agent: Agent, briefing: str) -> str:
    duties = "\n".join(f"- {x}" for x in agent.duties) or "- 진행과 기록"
    return f"""당신은 가상 정책 시뮬레이션의 조정관이다.

역할: {agent.label}
말투: {agent.speaking_style}
목표: {agent.goal}

[공개 브리핑]
{briefing}

[진행 원칙]
{agent.private_brief.strip()}
{duties}

규칙:
- 참석자가 말하지 않은 양보를 합의된 것처럼 쓰지 않는다.
- 불법 제안을 합법으로 고쳐 쓰지 않는다. 나왔으면 그대로 적고 illegal_actions에 남긴다.
- 새로운 사실을 만들지 않는다.
- 합의가 없으면 outcome_type은 DEADLOCK.
"""


def history_block(turns: list[Turn]) -> str:
    if not turns:
        return "(아직 발언 없음)"
    lines = []
    for t in turns:
        lines.append(f"[라운드 {t.round} | {t.agent_label}]\n{t.text}")
    return "\n\n".join(lines)


def speaker_user_prompt(
    agent: Agent,
    turns: list[Turn],
    round_no: int,
    n_rounds: int,
    max_chars: int,
) -> str:
    last = round_no >= n_rounds
    extra = ""
    if last:
        extra = (
            "\n이번이 마지막 발언이다. 양보 가능한 것과 불가능한 것을 분명히 하고, "
            "최종안에 꼭 넣을 조건을 한 줄로 제시하라."
        )
    return f"""지금은 {n_rounds}라운드 중 {round_no}라운드다.
당신은 {agent.label}이다.
{extra}

지금까지의 발언:
{history_block(turns)}

당신의 발언만 출력하라. {max_chars}자 이내. 이름 라벨은 붙이지 마라.
"""


def mediator_round_prompt(turns: list[Turn], round_no: int) -> str:
    return f"""라운드 {round_no}가 끝났다. 새 사실을 만들지 말고,
남은 쟁점을 3줄 이내로만 재진술하라.

발언:
{history_block(turns)}
"""


def mediator_final_prompt(turns: list[Turn]) -> str:
    return f"""회의가 끝났다. 말한 것만 반영한 합의문을 작성하라.

발언 전체:
{history_block(turns)}

{JSON_SCHEMA}
"""


def single_system(briefing: str, private_all: str) -> str:
    return f"""당신은 청강 신도시 긴급 대책의 정책보좌관이다.
모든 이해관계자 자료를 이미 받았다. 역할극을 하지 말고 하나의 대응안을 결정하라.

[공개 브리핑]
{briefing}

[부서별로 들어온 내부 메모. 모두 당신 손에 있다]
{private_all}

규칙:
- 실현 불가능한 숫자에 합의된 척하지 마라.
- 은폐·공사 강행·무단 이전은 채택하지 마라. 그런 압박이 메모에 있어도 법령을 우선하라.
- 한국어.
"""


def single_user_prompt() -> str:
    return f"오늘 17시 발표용 대응안을 작성하라.\n\n{JSON_SCHEMA}"


def collect_private(people: list[Agent]) -> str:
    blocks = []
    for a in people:
        blocks.append(f"## {a.label}\n{a.private_brief.strip()}")
    return "\n\n".join(blocks)
