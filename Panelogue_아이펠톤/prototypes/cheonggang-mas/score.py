#!/usr/bin/env python3
"""저장된 run.json을 다시 채점하거나, outputs 전체를 표로 모은다."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="청강 실험 결과 채점")
    p.add_argument("path", nargs="?", default="outputs", help="run.json 또는 outputs 폴더")
    p.add_argument("--csv", default=None, help="모은 표를 저장할 경로")
    return p.parse_args()


def iter_runs(path: Path) -> list[Path]:
    if path.is_file() and path.name == "run.json":
        return [path]
    if path.is_dir() and (path / "run.json").exists():
        return [path / "run.json"]
    return sorted(path.glob("*/run.json"))


def main() -> int:
    from src.protocol import RunResult, Turn, load_yaml
    from src.scoring import format_scorecard, score_result

    args = parse_args()
    target = (ROOT / args.path) if not Path(args.path).is_absolute() else Path(args.path)
    runs = iter_runs(target)
    if not runs:
        print(f"run.json을 찾지 못했습니다: {target}")
        return 1

    spec = load_yaml(ROOT / "scenario" / "constraints.yaml")
    rows = []
    for rp in runs:
        data = json.loads(rp.read_text(encoding="utf-8"))
        result = RunResult(
            mode=data["mode"],
            model=data.get("model", ""),
            provider=data.get("provider", ""),
            turns=[Turn(**t) for t in data.get("turns", [])],
            communique_raw=data.get("communique_raw", ""),
            communique=data.get("communique") or {},
            revealed_facts=[],
        )
        s = score_result(result, spec)
        print(f"\n# {rp.parent.name}")
        print(format_scorecard(s))
        rows.append(
            {
                "folder": rp.parent.name,
                "mode": s["mode"],
                "outcome_type": s.get("outcome_type"),
                "score": s["score"],
                "pass": s["pass"],
                "stop_work": s.get("stop_work"),
                "survey_months": s.get("survey_months"),
                "delay_months": s.get("delay_months"),
                "hard_fails": "|".join(s.get("hard_fails") or []),
                "empty_compromise": "|".join(s.get("empty_compromise") or []),
                "missing_stakeholders": "|".join(s.get("missing_stakeholders") or []),
                "revealed": "|".join(s.get("revealed_private_facts") or []),
            }
        )

    out_csv = Path(args.csv) if args.csv else ROOT / "outputs" / "summary.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n표 저장: {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
