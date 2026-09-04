from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.llm import ChatModel
from src.protocol import (
    Agent,
    RunResult,
    Turn,
    collect_private,
    load_agents,
    load_text,
    mediator_final_prompt,
    mediator_round_prompt,
    mediator_system,
    parse_communique,
    single_system,
    single_user_prompt,
    speaker_user_prompt,
    stakeholder_system,
)
from src.scoring import score_result


def run_multi(
    model: ChatModel,
    briefing: str,
    people: list[Agent],
    mediator: Agent,
    n_rounds: int,
    max_chars: int,
    recap: bool = True,
) -> RunResult:
    turns: list[Turn] = []
    for rnd in range(1, n_rounds + 1):
        for agent in people:
            sys = stakeholder_system(agent, briefing, max_chars)
            user = speaker_user_prompt(agent, turns, rnd, n_rounds, max_chars)
            print(f"  발언 중: 라운드 {rnd} · {agent.label}")
            text = model.complete(sys, user)
            turns.append(Turn(rnd, agent.id, agent.label, text))
        if recap and rnd < n_rounds:
            rec = model.complete(
                mediator_system(mediator, briefing),
                mediator_round_prompt(turns, rnd),
            )
            turns.append(Turn(rnd, "mediator", mediator.label, rec))

    print("  합의문 작성 중")
    raw = model.complete(
        mediator_system(mediator, briefing),
        mediator_final_prompt(turns),
    )
    return RunResult(
        mode="multi",
        model=model.cfg.model,
        provider=model.cfg.provider,
        turns=turns,
        communique_raw=raw,
        communique=parse_communique(raw),
        revealed_facts=[],
    )


def run_single(
    model: ChatModel,
    briefing: str,
    people: list[Agent],
) -> RunResult:
    sys = single_system(briefing, collect_private(people))
    raw = model.complete(sys, single_user_prompt())
    return RunResult(
        mode="single",
        model=model.cfg.model,
        provider=model.cfg.provider,
        turns=[],
        communique_raw=raw,
        communique=parse_communique(raw),
        revealed_facts=["single_has_all_private_memos"],
    )


def transcript_markdown(result: RunResult) -> str:
    lines = [
        f"# {result.mode} 실행 기록",
        "",
        f"- 모델: `{result.provider}/{result.model}`",
        f"- 결과 유형: `{result.communique.get('outcome_type')}`",
        "",
        "## 발언",
        "",
    ]
    if not result.turns:
        lines.append("_단일 조건이라 라운드 발언이 없습니다._")
        lines.append("")
    for t in result.turns:
        lines.append(f"### 라운드 {t.round} · {t.agent_label}")
        lines.append("")
        lines.append(t.text.strip())
        lines.append("")
    lines.append("## 합의문 원문")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(result.communique, ensure_ascii=False, indent=2))
    lines.append("```")
    if result.communique.get("parse_error"):
        lines.append("")
        lines.append("### 파싱 실패 원문")
        lines.append("")
        lines.append(result.communique_raw)
    return "\n".join(lines).rstrip() + "\n"


def save_run(
    result: RunResult,
    score: dict[str, Any],
    out_dir: Path,
    tag: str | None = None,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{stamp}_{result.mode}"
    if tag:
        name += f"_{tag}"
    folder = out_dir / name
    folder.mkdir(parents=True, exist_ok=True)

    payload = {
        "mode": result.mode,
        "provider": result.provider,
        "model": result.model,
        "communique": result.communique,
        "communique_raw": result.communique_raw,
        "turns": [
            {
                "round": t.round,
                "agent_id": t.agent_id,
                "agent_label": t.agent_label,
                "text": t.text,
            }
            for t in result.turns
        ],
        "score": score,
    }
    (folder / "run.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (folder / "transcript.md").write_text(transcript_markdown(result), encoding="utf-8")
    return folder


def load_scenario(root: Path) -> tuple[str, list[Agent], Agent, dict[str, Any]]:
    briefing = load_text(root / "scenario" / "briefing.md")
    people, mediator = load_agents(root / "scenario" / "agents.yaml")
    constraints = yaml_load(root / "scenario" / "constraints.yaml")
    return briefing, people, mediator, constraints


def yaml_load(path: Path) -> dict[str, Any]:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def execute(
    root: Path,
    model: ChatModel,
    mode: str,
    n_rounds: int,
    max_chars: int,
    tag: str | None = None,
) -> tuple[RunResult, dict[str, Any], Path]:
    briefing, people, mediator, constraints = load_scenario(root)
    if mode == "single":
        result = run_single(model, briefing, people)
    elif mode == "multi":
        result = run_multi(model, briefing, people, mediator, n_rounds, max_chars)
    else:
        raise ValueError(f"unknown mode: {mode}")
    score = score_result(result, constraints)
    score["revealed_private_facts"] = score.get("revealed_private_facts") or []
    folder = save_run(result, score, root / "outputs", tag=tag)
    (folder / "score.txt").write_text(
        _score_text(score),
        encoding="utf-8",
    )
    return result, score, folder


def _score_text(score: dict[str, Any]) -> str:
    from src.scoring import format_scorecard

    return format_scorecard(score) + "\n"
