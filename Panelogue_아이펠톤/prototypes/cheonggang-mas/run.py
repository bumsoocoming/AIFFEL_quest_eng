#!/usr/bin/env python3
"""청강 신도시 매장유산 시나리오 — 단일 vs 멀티 에이전트 실행."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if load_dotenv:
    load_dotenv(ROOT / ".env")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="청강 신도시 멀티에이전트 실험")
    p.add_argument(
        "--mode",
        choices=["multi", "single", "compare", "week"],
        default="week",
        help="week=1주 최소실험(단일3+멀티3, 1라운드). multi/single/compare는 수동",
    )
    p.add_argument("--runs", type=int, default=None, help="각 모드 반복 횟수. week는 기본 3")
    p.add_argument("--rounds", type=int, default=None, help="멀티 토론 라운드 수. week는 1")
    p.add_argument("--provider", default=None, help="auto | openai | gemini | dry")
    p.add_argument("--model", default=None, help="모델 이름")
    p.add_argument("--dry-run", action="store_true", help="API 없이 가짜 대사로 파이프라인만 확인")
    p.add_argument("--tag", default=None, help="출력 폴더 이름에 붙일 태그")
    return p.parse_args()


def load_cfg() -> dict:
    import yaml

    path = ROOT / "config.yaml"
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {}


def main() -> int:
    args = parse_args()
    cfg = load_cfg()
    exp = cfg.get("experiment") or {}

    from src.llm import ChatModel, LLMConfig, default_model, detect_provider
    from src.run_experiment import execute
    from src.scoring import format_scorecard

    if args.dry_run:
        provider = "dry"
    else:
        provider = detect_provider(args.provider or os.getenv("MAS_PROVIDER") or cfg.get("provider") or "auto")

    model_name = args.model or os.getenv("MAS_MODEL") or cfg.get("model") or default_model(provider)
    week = args.mode == "week"
    if week:
        n_rounds = args.rounds if args.rounds is not None else 1
        n_runs = args.runs if args.runs is not None else int(exp.get("week_runs") or 3)
        modes = ["single", "multi"]
    else:
        n_rounds = args.rounds if args.rounds is not None else int(exp.get("rounds") or 1)
        n_runs = args.runs if args.runs is not None else 1
        modes = ["single", "multi"] if args.mode == "compare" else [args.mode]
    max_chars = int(exp.get("speaker_max_chars") or 380)

    llm = ChatModel(
        LLMConfig(
            provider=provider,
            model=model_name,
            temperature=float(exp.get("temperature") or 0.7),
            max_tokens=int(exp.get("max_tokens") or 4096),
        )
    )

    print(
        f"provider={provider}  model={model_name}  modes={modes}  "
        f"runs={n_runs}  rounds={n_rounds}"
    )
    if week:
        print("1주 최소실험: 단일 3회 + 멀티 3회, 토론 1라운드. 할당량이 끊겨도 이미 끝난 회차는 저장된다.")

    if provider == "dry":
        print("드라이런입니다. 대사는 고정 예시이고 실험 결과가 아닙니다.")

    summaries = []
    for mode in modes:
        for i in range(n_runs):
            tag = args.tag or f"{'week' if week else 'r'}{i+1}"
            print(f"\n--- {mode} ({i+1}/{n_runs}) ---")
            try:
                result, score, folder = execute(
                    ROOT,
                    llm,
                    mode=mode,
                    n_rounds=n_rounds,
                    max_chars=max_chars,
                    tag=tag,
                )
            except Exception as exc:
                print(f"실패, 다음 회차로 넘어갑니다: {exc}")
                continue
            print(format_scorecard(score))
            print(f"저장: {folder}")
            summaries.append((folder, score))

    if summaries:
        print("\n=== 요약 ===")
        for folder, score in summaries:
            print(
                f"{score['mode']:7}  {score.get('outcome_type')}  "
                f"score={score['score']:3}  pass={score['pass']}  "
                f"{folder.name}"
            )
        if week or len(summaries) > 1:
            _write_week_table(summaries)
    else:
        print("저장된 실행이 없습니다.")
    return 0


def _write_week_table(summaries) -> None:
    import csv

    path = ROOT / "outputs" / "week_summary.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for folder, score in summaries:
        rows.append(
            {
                "folder": folder.name,
                "mode": score.get("mode"),
                "outcome_type": score.get("outcome_type"),
                "score": score.get("score"),
                "pass": score.get("pass"),
                "survey_months": score.get("survey_months"),
                "delay_months": score.get("delay_months"),
                "hard_fails": "|".join(score.get("hard_fails") or []),
                "empty_compromise": "|".join(score.get("empty_compromise") or []),
                "missing": "|".join(score.get("missing_stakeholders") or []),
                "revealed": "|".join(score.get("revealed_private_facts") or []),
            }
        )
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"주간 표: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
