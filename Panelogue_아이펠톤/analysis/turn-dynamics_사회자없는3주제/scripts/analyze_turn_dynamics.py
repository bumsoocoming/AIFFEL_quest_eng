#!/usr/bin/env python3
"""Panelogue turn-by-turn stance and trigger analysis.

Reads Panelogue JSON exports, reconstructs each agent's stance at every global
turn, links explicit stance changes to the messages named in stanceHistory,
and produces reviewable CSV/JSON/Markdown artifacts.

The trigger and persona labels are rule-based research annotations. They are
kept separate from the source fields so that a human coder can audit or replace
them without changing the original transcript evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


CATEGORY_LABELS = {
    "empirical_evidence": "수치·사실·근거",
    "counterexample_risk": "반례·실패·위험",
    "harm_fairness": "피해·공정성·책임",
    "performance_execution": "성과·실행 가능성",
    "power_structure": "권력·자본·제도 구조",
    "tradeoff_condition": "조건·비용·절충",
    "concession_reciprocity": "양보·부분 인정",
    "emotional_moral": "감정·도덕적 압박",
    "moderator_pressure": "사회자 질문·선택 압박",
    "general_argument": "일반 주장",
}

CATEGORY_KEYWORDS = {
    "empirical_evidence": [
        "수치", "통계", "데이터", "근거", "증거", "사실", "검증", "기록", "보고서",
        "계약", "시장점유", "사고율", "연구", "%", "년", "회", "건", "숫자",
        "data", "evidence", "verified", "study", "statistic", "contract",
    ],
    "counterexample_risk": [
        "실패", "오류", "지연", "과장", "약속", "위험", "부작용", "예외", "오심",
        "문제", "사고", "불확실", "미이행", "반례", "취소", "한계", "왜곡",
        "failure", "risk", "delay", "counterexample", "uncertain", "error",
    ],
    "harm_fairness": [
        "피해", "노동", "안전", "환경", "책임", "권리", "공정", "인권", "희생",
        "탄압", "차별", "부당", "복지", "보호", "존중", "신뢰", "선수", "심판",
        "harm", "fair", "rights", "labor", "safety", "responsibility",
    ],
    "performance_execution": [
        "성과", "성공", "실행", "혁신", "효율", "정확", "개선", "재사용", "발전",
        "기술", "가능", "도입", "해결", "착륙", "재비행", "판정 정확도",
        "success", "performance", "execution", "innovation", "accuracy",
    ],
    "power_structure": [
        "권력", "자본", "정부", "공공", "독점", "집중", "기업", "국방부", "NASA",
        "지원", "정책", "규제", "사유화", "계약", "구조", "플랫폼",
        "power", "capital", "government", "monopoly", "regulation",
    ],
    "tradeoff_condition": [
        "하지만", "그러나", "다만", "조건", "대신", "균형", "절충", "비용", "한편",
        "동시에", "경우", "범위", "기준", "최소", "제한", "원칙", "보완",
        "but", "however", "conditional", "trade-off", "cost", "balance",
    ],
    "concession_reciprocity": [
        "인정", "동의", "수용", "양보", "맞다", "일리", "받아들", "부분적으로",
        "acknowledg", "agree", "concede", "accept", "admit",
    ],
    "emotional_moral": [
        "분노", "화가", "잔인", "무책임", "끔찍", "미친", "사기", "박살", "괴물",
        "헛소리", "개소리", "씨발", "병신", "도덕", "부끄", "터무니",
        "angry", "immoral", "reckless", "shame", "damn",
    ],
}

STOPWORDS = {
    "그", "이", "저", "것", "수", "등", "및", "또", "더", "한", "를", "을", "에",
    "가", "이", "은", "는", "와", "과", "로", "으로", "하다", "한다", "있다", "없다",
    "그리고", "하지만", "그러나", "대한", "통해", "때문", "정도", "입장", "주장",
    "the", "a", "an", "and", "or", "to", "of", "in", "is", "are", "that",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("reports/turn-dynamics"))
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[가-힣A-Za-z0-9%]+", text.lower())
    return {t for t in tokens if len(t) > 1 and t not in STOPWORDS}


def sentence_split(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", clean_text(text))
    return [p.strip() for p in parts if p.strip()]


def keyword_score(text: str, words: Iterable[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(word.lower()) for word in words)


def select_trigger_clause(text: str, reason: str, limit: int = 220) -> str:
    """Select the source sentence most lexically connected to the logged reason."""
    sentences = sentence_split(text)
    if not sentences:
        return ""
    reason_tokens = tokenize(reason)
    scored: list[tuple[float, int, str]] = []
    all_keywords = [word for words in CATEGORY_KEYWORDS.values() for word in words]
    for idx, sentence in enumerate(sentences):
        st = tokenize(sentence)
        overlap = len(st & reason_tokens)
        density = overlap / max(1, len(st | reason_tokens))
        evidence_bonus = min(4, keyword_score(sentence, all_keywords)) * 0.08
        scored.append((density + evidence_bonus, -idx, sentence))
    selected = max(scored)[2]
    return selected if len(selected) <= limit else selected[: limit - 1].rstrip() + "…"


def classify_trigger(text: str, reason: str, is_moderator: bool) -> tuple[str, list[str], dict[str, int]]:
    combined = f"{text} {reason}".lower()
    scores = {category: keyword_score(combined, words) for category, words in CATEGORY_KEYWORDS.items()}
    if is_moderator:
        scores["moderator_pressure"] = 2 + combined.count("?")
    if not any(scores.values()):
        scores["general_argument"] = 1
    ordered = sorted(scores, key=lambda key: (-scores[key], key))
    primary = ordered[0]
    secondary = [key for key in ordered if scores[key] > 0 and key != primary][:2]
    return primary, [primary, *secondary], scores


def sign(value: float | int | None) -> int:
    if value is None:
        return 0
    return 1 if value > 0 else -1 if value < 0 else 0


def change_type(previous: float, current: float) -> str:
    if sign(previous) and sign(current) and sign(previous) != sign(current):
        return "극성 전환"
    if abs(current) < abs(previous):
        return "중앙으로 완화"
    if abs(current) > abs(previous):
        return "기존 방향 강화"
    return "동일 강도 이동"


def source_persona_relation(source_stance: Any, initial_stance: float, is_moderator: bool) -> str:
    if is_moderator or source_stance is None:
        return "사회자 탐색 질문"
    if sign(float(source_stance)) == 0 or sign(initial_stance) == 0:
        return "중립·판단 유보"
    return "페르소나 지지 입력" if sign(float(source_stance)) == sign(initial_stance) else "페르소나 반대 입력"


def persona_response(previous: float, current: float, initial: float, source_relation: str) -> str:
    before = abs(previous - initial)
    after = abs(current - initial)
    if sign(previous) and sign(current) and sign(previous) != sign(current):
        return "입장 극성 전환"
    if source_relation == "페르소나 반대 입력":
        if after > before:
            return "반대 입력 수용·페르소나 완화"
        if after < before:
            return "반발·페르소나 재강화"
        return "반대 입력 후 강도 조정"
    if source_relation == "페르소나 지지 입력":
        if after < before:
            return "지지 입력으로 페르소나 복귀"
        if after > before:
            return "지지 입력에도 페르소나 이탈"
        return "지지 입력 후 강도 조정"
    return "탐색 질문 후 완화" if abs(current) < abs(previous) else "탐색 질문 후 강화"


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else None


def analyze_run(path: Path, data_root: Path) -> dict[str, Any]:
    raw = read_json(path)
    dataset = path.parent.parent.name
    run = path.stem
    topic = clean_text(raw.get("topic") or raw.get("settings", {}).get("topic"))
    settings = raw.get("settings") or {}
    agents = settings.get("agents") or []
    agent_map = {agent.get("id"): agent for agent in agents}
    messages = sorted(raw.get("messages") or [], key=lambda msg: int(msg.get("turn") or 0))
    message_map = {msg.get("id"): msg for msg in messages if msg.get("id")}
    max_turn = max((int(msg.get("turn") or 0) for msg in messages), default=0)

    changes_by_turn_agent: dict[tuple[int, str], dict[str, Any]] = {}
    events: list[dict[str, Any]] = []
    for history in raw.get("stanceHistory") or []:
        agent_id = history.get("agentId")
        agent = agent_map.get(agent_id, {})
        turn = int(history.get("turn") or 0)
        previous = float(history.get("previousStance") or 0)
        current = float(history.get("newStance") or 0)
        if current == previous:
            continue
        target_message = next(
            (msg for msg in messages if int(msg.get("turn") or 0) == turn and msg.get("speakerId") == agent_id),
            {},
        )
        trigger_ids = list(history.get("influencedByMessageIds") or [])
        reply_id = (target_message.get("metadata") or {}).get("replyToId")
        if not trigger_ids and reply_id:
            trigger_ids = [reply_id]
        sources = [message_map[msg_id] for msg_id in trigger_ids if msg_id in message_map]
        if not sources:
            prior = [msg for msg in messages if int(msg.get("turn") or 0) < turn]
            sources = prior[-1:] if prior else []

        reason = clean_text(history.get("reason") or (target_message.get("metadata") or {}).get("stanceReason"))
        initial = float(agent.get("initialStance") or previous)
        for source_index, source in enumerate(sources or [{}], start=1):
            source_text = clean_text(source.get("text"))
            is_moderator = bool(source.get("isModerator"))
            primary, categories, category_scores = classify_trigger(source_text, reason, is_moderator)
            source_stance = (source.get("metadata") or {}).get("stance")
            relation = source_persona_relation(source_stance, initial, is_moderator)
            event = {
                "dataset": dataset,
                "run": run,
                "topic": topic,
                "target_turn": turn,
                "agent_id": agent_id,
                "agent_name": history.get("agentName") or agent.get("name") or agent_id,
                "agent_job": agent.get("job", ""),
                "model": agent.get("customModel", ""),
                "initial_stance": initial,
                "previous_stance": previous,
                "new_stance": current,
                "delta": current - previous,
                "absolute_delta": abs(current - previous),
                "change_type": change_type(previous, current),
                "stance_reason": reason,
                "source_index": source_index,
                "source_message_id": source.get("id", ""),
                "source_turn": int(source.get("turn") or 0),
                "source_speaker_id": source.get("speakerId", ""),
                "source_speaker": source.get("speakerName", ""),
                "source_is_moderator": is_moderator,
                "source_stance": source_stance,
                "source_text": source_text,
                "trigger_clause": select_trigger_clause(source_text, reason),
                "primary_category": primary,
                "primary_category_ko": CATEGORY_LABELS[primary],
                "all_categories": " | ".join(categories),
                "category_scores": category_scores,
                "trigger_persona_relation": relation,
                "persona_response": persona_response(previous, current, initial, relation),
                "persona_text": clean_text(agent.get("simplePersona")),
                "speaking_style": clean_text(agent.get("speakingStyle")),
                "confidence": (target_message.get("metadata") or {}).get("confidence"),
                "speech_act": (target_message.get("metadata") or {}).get("speechAct", ""),
                "coding_status": "자동 1차 코딩—사람 검토 필요",
            }
            events.append(event)
        changes_by_turn_agent[(turn, agent_id)] = history

    message_by_turn = {int(msg.get("turn") or 0): msg for msg in messages}
    series: list[dict[str, Any]] = []
    agent_summaries: list[dict[str, Any]] = []
    for agent in agents:
        agent_id = agent.get("id")
        stance = float(agent.get("initialStance") or 0)
        confidence: Any = None
        speeches = 0
        unique_changes: list[float] = []
        series.append({
            "dataset": dataset, "run": run, "topic": topic, "turn": 0,
            "agent_id": agent_id, "agent_name": agent.get("name"), "stance": stance,
            "confidence": confidence, "speaker_this_turn": False, "stance_changed": False,
        })
        for turn in range(1, max_turn + 1):
            msg = message_by_turn.get(turn, {})
            speaker_this_turn = msg.get("speakerId") == agent_id
            if speaker_this_turn:
                speeches += 1
                metadata = msg.get("metadata") or {}
                if metadata.get("stance") is not None:
                    stance = float(metadata["stance"])
                if metadata.get("confidence") is not None:
                    confidence = metadata["confidence"]
            history = changes_by_turn_agent.get((turn, agent_id))
            changed = bool(history and float(history.get("newStance") or 0) != float(history.get("previousStance") or 0))
            if history:
                stance = float(history.get("newStance") or stance)
                if changed:
                    unique_changes.append(abs(float(history.get("newStance") or 0) - float(history.get("previousStance") or 0)))
            series.append({
                "dataset": dataset, "run": run, "topic": topic, "turn": turn,
                "agent_id": agent_id, "agent_name": agent.get("name"), "stance": stance,
                "confidence": confidence, "speaker_this_turn": speaker_this_turn, "stance_changed": changed,
            })
        behavior = agent.get("behavior") or {}
        personality = agent.get("personality") or {}
        agent_events = [e for e in events if e["agent_id"] == agent_id]
        unique_event_turns = sorted({e["target_turn"] for e in agent_events})
        persona_softening = sum(e["persona_response"] == "반대 입력 수용·페르소나 완화" for e in agent_events)
        agent_summaries.append({
            "dataset": dataset,
            "run": run,
            "agent_id": agent_id,
            "agent_name": agent.get("name"),
            "agent_job": agent.get("job", ""),
            "model": agent.get("customModel", ""),
            "initial_stance": agent.get("initialStance"),
            "final_stance": stance,
            "net_change": stance - float(agent.get("initialStance") or 0),
            "speeches": speeches,
            "stance_change_events": len(unique_event_turns),
            "event_rate_per_speech": len(unique_event_turns) / speeches if speeches else 0,
            "mean_absolute_delta": statistics.mean(unique_changes) if unique_changes else 0,
            "total_volatility": sum(unique_changes),
            "persona_softening_events": persona_softening,
            "configured_stance_shift_probability": behavior.get("stanceShiftProbability"),
            "configured_concession_probability": behavior.get("concessionProbability"),
            "configured_aggressiveness": behavior.get("aggressiveness"),
            "configured_evidence_demand": behavior.get("evidenceDemand"),
            "configured_independent_judgment": behavior.get("independentJudgment"),
            "personality_assertiveness": personality.get("assertiveness"),
            "personality_agreeableness": personality.get("agreeableness"),
            "personality_skepticism": personality.get("skepticism"),
            "personality_emotionality": personality.get("emotionality"),
            "stance_flexibility": agent.get("stanceFlexibility"),
        })

    transcript = {
        "dataset": dataset,
        "run": run,
        "topic": topic,
        "agents": agents,
        "messages": messages,
        "events": events,
    }
    return {"events": events, "series": series, "agent_summaries": agent_summaries, "transcript": transcript}


def write_annotated_transcript(path: Path, run_data: dict[str, Any]) -> None:
    transcript = run_data["transcript"]
    events_by_turn: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in run_data["events"]:
        events_by_turn[int(event["target_turn"])].append(event)
    lines = [
        f"# {transcript['dataset']} / {transcript['run']} 턴별 주석 대화록",
        "",
        f"**주제:** {transcript['topic']}",
        "",
        "> 입장·반응 구절·변화 이유는 원본 JSON의 메시지와 stanceHistory를 연결했다. 트리거 카테고리는 자동 1차 코딩이므로 발표 전 사람 검토가 필요하다.",
        "",
    ]
    for msg in transcript["messages"]:
        turn = int(msg.get("turn") or 0)
        meta = msg.get("metadata") or {}
        stance = meta.get("stance")
        stance_label = f" · 입장 {float(stance):+g}" if stance is not None else ""
        confidence = meta.get("confidence")
        confidence_label = f" · 확신 {confidence}" if confidence is not None else ""
        lines += [
            f"## T{turn}. {msg.get('speakerName', msg.get('speakerId', ''))}{stance_label}{confidence_label}",
            "",
            clean_text(msg.get("text")),
            "",
        ]
        for event in events_by_turn.get(turn, []):
            lines += [
                f"- **입장 변화:** {event['previous_stance']:+g} → {event['new_stance']:+g} ({event['delta']:+g}) · {event['change_type']}",
                f"- **반응한 구절:** “{event['trigger_clause']}” — {event['source_speaker']} T{event['source_turn']}",
                f"- **기록된 이유:** {event['stance_reason']}",
                f"- **자동 코딩:** {event['primary_category_ko']} / {event['trigger_persona_relation']} / {event['persona_response']}",
                "",
            ]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    data_root = args.data_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    transcript_dir = output / "annotated-transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted(data_root.glob("*/sanitized/run-*.json"))
    if not paths:
        raise SystemExit(f"No run JSON files found under {data_root}")

    all_events: list[dict[str, Any]] = []
    all_series: list[dict[str, Any]] = []
    all_agents: list[dict[str, Any]] = []
    datasets: dict[str, dict[str, Any]] = defaultdict(lambda: {"runs": [], "topics": set()})
    for path in paths:
        result = analyze_run(path, data_root)
        all_events.extend(result["events"])
        all_series.extend(result["series"])
        all_agents.extend(result["agent_summaries"])
        transcript = result["transcript"]
        datasets[transcript["dataset"]]["runs"].append(transcript["run"])
        datasets[transcript["dataset"]]["topics"].add(transcript["topic"])
        write_annotated_transcript(
            transcript_dir / f"{transcript['dataset']}__{transcript['run']}.md",
            result,
        )

    category_counts = Counter(event["primary_category"] for event in all_events)
    category_deltas: dict[str, list[float]] = defaultdict(list)
    cross_counts: Counter[tuple[str, str]] = Counter()
    for event in all_events:
        category_deltas[event["primary_category"]].append(float(event["absolute_delta"]))
        cross_counts[(event["primary_category"], event["persona_response"])] += 1

    trigger_summary = [
        {
            "category": key,
            "category_ko": CATEGORY_LABELS[key],
            "event_source_links": count,
            "mean_absolute_delta": round(statistics.mean(category_deltas[key]), 3),
            "median_absolute_delta": round(statistics.median(category_deltas[key]), 3),
        }
        for key, count in category_counts.most_common()
    ]
    cross_tab = [
        {
            "category": category,
            "category_ko": CATEGORY_LABELS[category],
            "persona_response": response,
            "count": count,
        }
        for (category, response), count in sorted(cross_counts.items())
    ]

    correlation_specs = {
        "설정 입장변화 확률": "configured_stance_shift_probability",
        "설정 양보 확률": "configured_concession_probability",
        "설정 공격성": "configured_aggressiveness",
        "설정 근거 요구": "configured_evidence_demand",
        "설정 독립 판단": "configured_independent_judgment",
        "성격 주장성": "personality_assertiveness",
        "성격 친화성": "personality_agreeableness",
        "성격 회의성": "personality_skepticism",
        "성격 감정성": "personality_emotionality",
        "입장 유연성": "stance_flexibility",
    }
    correlations = []
    for label, field in correlation_specs.items():
        usable = [row for row in all_agents if row.get(field) is not None]
        xs = [float(row[field]) for row in usable]
        for outcome_label, outcome_field in [
            ("실제 변화율", "event_rate_per_speech"),
            ("변화폭 평균", "mean_absolute_delta"),
            ("총 변동성", "total_volatility"),
        ]:
            ys = [float(row[outcome_field]) for row in usable]
            value = pearson(xs, ys)
            correlations.append({
                "configured_feature": field,
                "configured_feature_ko": label,
                "observed_outcome": outcome_field,
                "observed_outcome_ko": outcome_label,
                "pearson_r": round(value, 4) if value is not None else None,
                "n_run_agent_rows": len(usable),
                "warning": "반복 실행의 동일 페르소나가 중복된 기술통계이며 독립 표본 추론이 아님",
            })

    event_fields = [
        "dataset", "run", "topic", "target_turn", "agent_id", "agent_name", "agent_job", "model",
        "initial_stance", "previous_stance", "new_stance", "delta", "absolute_delta", "change_type",
        "stance_reason", "source_index", "source_message_id", "source_turn", "source_speaker_id",
        "source_speaker", "source_is_moderator", "source_stance", "source_text", "trigger_clause",
        "primary_category", "primary_category_ko", "all_categories", "trigger_persona_relation",
        "persona_response", "persona_text", "speaking_style", "confidence", "speech_act", "coding_status",
    ]
    series_fields = [
        "dataset", "run", "topic", "turn", "agent_id", "agent_name", "stance", "confidence",
        "speaker_this_turn", "stance_changed",
    ]
    agent_fields = list(all_agents[0].keys()) if all_agents else []
    write_csv(output / "stance-events.csv", all_events, event_fields)
    write_csv(output / "turn-stance-series.csv", all_series, series_fields)
    write_csv(output / "agent-personality-outcomes.csv", all_agents, agent_fields)
    write_csv(output / "trigger-summary.csv", trigger_summary, list(trigger_summary[0].keys()))
    write_csv(output / "trigger-persona-crosstab.csv", cross_tab, list(cross_tab[0].keys()))
    write_csv(output / "personality-correlations.csv", correlations, list(correlations[0].keys()))

    compact_events = [{k: v for k, v in event.items() if k != "category_scores"} for event in all_events]
    payload = {
        "meta": {
            "source_files": len(paths),
            "datasets": len(datasets),
            "total_messages": len({
                (row["dataset"], row["run"], row["turn"])
                for row in all_series if int(row["turn"]) > 0
            }),
            "agent_messages": sum(1 for row in all_series if row["speaker_this_turn"]),
            "stance_event_source_links": len(all_events),
            "unique_stance_events": len({(e["dataset"], e["run"], e["target_turn"], e["agent_id"]) for e in all_events}),
            "coding": "원본 stanceHistory 연결 + 규칙 기반 1차 카테고리화",
        },
        "datasets": {
            key: {"runs": sorted(value["runs"]), "topics": sorted(value["topics"])}
            for key, value in datasets.items()
        },
        "events": compact_events,
        "series": all_series,
        "agent_summaries": all_agents,
        "trigger_summary": trigger_summary,
        "trigger_persona_crosstab": cross_tab,
        "personality_correlations": correlations,
    }
    write_json(output / "turn-dynamics-analysis.json", payload)

    report_lines = [
        "# 턴별 입장 변화·반응 구절·페르소나 교차분석",
        "",
        f"- 원본 JSON: {len(paths)}개",
        f"- 전체 대화 메시지: {payload['meta']['total_messages']}턴",
        f"- 패널 발언: {payload['meta']['agent_messages']}턴",
        f"- 고유 입장 변화 사건: {payload['meta']['unique_stance_events']}건",
        f"- 사건–반응 구절 연결: {payload['meta']['stance_event_source_links']}건",
        "",
        "## 분석 단위",
        "",
        "1. `turn-stance-series.csv`: 모든 전역 턴에서 각 에이전트의 직전 입장을 유지해 계단 그래프용 시계열을 구성한다.",
        "2. `stance-events.csv`: stanceHistory의 변화 사건과 influencedByMessageIds의 원문 메시지를 연결한다.",
        "3. `trigger-persona-crosstab.csv`: 반응 구절 유형과 페르소나 반응 패턴을 교차 집계한다.",
        "4. `agent-personality-outcomes.csv`: 설정된 성격·행동값과 실제 변화율·변화폭을 비교한다.",
        "",
        "## 자동 1차 코딩 결과",
        "",
        "|트리거 카테고리|구절 연결 수|평균 절대 변화폭|중앙값|",
        "|---|---:|---:|---:|",
    ]
    for row in trigger_summary:
        report_lines.append(
            f"|{row['category_ko']}|{row['event_source_links']}|{row['mean_absolute_delta']:.2f}|{row['median_absolute_delta']:.2f}|"
        )
    report_lines += [
        "",
        "## 해석 시 주의",
        "",
        "- 입장 변화 수치와 영향 메시지 ID는 원본 로그에서 직접 가져왔다.",
        "- ‘반응한 구절’은 기록된 변화 이유와 어휘가 가장 겹치는 문장을 자동 선택한 것이다.",
        "- 트리거·페르소나 관계 카테고리는 규칙 기반 1차 코딩이며, 논문 통계에는 2인 이상의 사람 코딩과 일치도(Cohen’s κ)를 권장한다.",
        "- 상관계수의 단위는 실행×에이전트 행이다. 동일 페르소나 반복값이므로 독립 표본의 유의성 검정으로 사용하면 안 된다.",
        "- 모델과 페르소나가 고정 결합된 현재 설계에서는 ‘성격 효과’와 ‘모델 효과’를 분리할 수 없다. 후속 실험은 모델–페르소나 라틴 스퀘어 배치를 권장한다.",
        "",
    ]
    (output / "분석_요약.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(json.dumps(payload["meta"], ensure_ascii=False, indent=2))
    print(f"output={output}")


if __name__ == "__main__":
    main()
