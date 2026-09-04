#!/usr/bin/env python3
"""
멀티 페르소나 회의 — OpenRouter 키 하나로 4개 회사 모델을 섞어 돌립니다.

준비:
    pip install openai pyyaml python-dotenv
    .env 파일에  OPENROUTER_API_KEY=sk-or-v1-...  한 줄

실행:
    python meeting.py                    # personas.yaml 그대로
    python meeting.py --length 1min      # 길이만 바꿔서
    python meeting.py --dry-run          # API 안 쓰고 흐름만 확인 (비용 0)
"""

import argparse
import json
import os
import pathlib
import sys
import time
from datetime import datetime

import yaml
from dotenv import load_dotenv
from openai import OpenAI

# 윈도우 cmd 기본 인코딩(cp949)에서 한글이 깨지는 것을 막습니다.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 길이 → 턴 수. 시간으로는 제어가 안 되므로 턴으로 환산합니다.
LENGTH_TO_TURNS = {"1min": 8, "3min": 20, "5min": 35}

BASE_URL = "https://openrouter.ai/api/v1"


# ----------------------------------------------------------------- 클라이언트
class Router:
    """OpenRouter 호출 + 토큰/비용 누적."""

    def __init__(self, api_key, dry_run=False):
        self.dry_run = dry_run
        self.client = None if dry_run else OpenAI(base_url=BASE_URL, api_key=api_key)
        self.spent_usd = 0.0
        self.calls = []

    def ask(self, model, system, messages, max_tokens=400):
        if self.dry_run:
            time.sleep(0.05)
            return f"[dry-run] {model} 응답 자리", 0.0

        resp = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=max_tokens,
            temperature=0.9,
            extra_headers={"X-OpenRouter-Title": "Persona Meeting"},
            # 응답에 실제 과금액을 함께 받습니다 (OpenRouter 전용 옵션)
            extra_body={"usage": {"include": True}},
        )

        text = (resp.choices[0].message.content or "").strip()

        cost = 0.0
        usage = getattr(resp, "usage", None)
        if usage is not None:
            cost = float(getattr(usage, "cost", 0.0) or 0.0)
            self.calls.append({
                "model": model,
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "cost_usd": cost,
            })
        self.spent_usd += cost
        return text, cost


# ----------------------------------------------------------------- 컨텍스트
def build_context(transcript, recent_turns, summary):
    """
    최근 N턴만 원문으로, 그 이전은 요약 한 덩어리로 넘깁니다.
    이걸 안 하면 입력 토큰이 턴 수의 제곱으로 늘어납니다.
    """
    parts = []
    if summary:
        parts.append(f"[여기까지의 논의 요약]\n{summary}")
    for t in transcript[-recent_turns:]:
        parts.append(f"{t['speaker']}: {t['text']}")
    return "\n\n".join(parts) if parts else "(아직 발언 없음)"


def summarize(router, model, transcript):
    body = "\n".join(f"{t['speaker']}: {t['text']}" for t in transcript)
    text, _ = router.ask(
        model,
        "다음 토론 기록을 6줄 이내로 압축하라. 누가 무엇을 주장했고 어디서 의견이 갈렸는지만 남긴다.",
        [{"role": "user", "content": body}],
        max_tokens=300,
    )
    return text


# ----------------------------------------------------------------- 회의 진행
def run(cfg, router, turns):
    topic = cfg["topic"]
    mod = cfg["moderator"]
    panel = {p["name"]: p for p in cfg["panel"]}
    names = list(panel.keys())
    recent = int(cfg.get("recent_turns", 8))

    transcript = []
    summary = ""
    last_speaker = None

    print(f"\n주제: {topic}")
    print(f"참가자: {', '.join(names)}  |  목표 {turns}턴\n" + "─" * 60)

    for i in range(turns):
        ctx = build_context(transcript, recent, summary)

        # 1) 사회자가 다음 발언자를 지목
        mod_prompt = (
            f"토론 주제: {topic}\n"
            f"참가자: {', '.join(names)}\n"
            f"직전 발언자: {last_speaker or '없음'} (이 사람은 다시 지목하지 말 것)\n\n"
            f"{ctx}\n\n"
            "다음에 말할 사람 한 명을 고르고 그에게 질문하라.\n"
            "반드시 첫 줄에 `NEXT: 이름` 형식으로 이름만 쓰고, 다음 줄부터 질문을 쓴다."
        )
        mod_text, _ = router.ask(mod["model"], mod["persona"],
                                 [{"role": "user", "content": mod_prompt}], max_tokens=250)

        # NEXT: 파싱. 실패하면 직전 발언자를 제외하고 순번으로 넘김.
        speaker, question = None, mod_text
        for line in mod_text.splitlines():
            if line.strip().upper().startswith("NEXT:"):
                cand = line.split(":", 1)[1].strip()
                speaker = next((n for n in names if n in cand), None)
                question = mod_text.replace(line, "", 1).strip()
                break
        if speaker is None or speaker == last_speaker:
            pool = [n for n in names if n != last_speaker]
            speaker = pool[i % len(pool)]

        print(f"\n[{mod['name']}] {question}")
        transcript.append({"speaker": mod["name"], "text": question,
                           "model": mod["model"], "turn": i})

        # 2) 지목된 패널이 답변
        p = panel[speaker]
        panel_prompt = (
            f"토론 주제: {topic}\n\n{build_context(transcript, recent, summary)}\n\n"
            f"사회자가 당신({speaker})에게 물었다. 당신의 관점에서 답하라.\n"
            "다른 참가자의 말에 동의만 하지 말고, 틀렸다고 보면 짚어라. 이름표는 붙이지 않는다."
        )
        text, cost = router.ask(p["model"], p["persona"],
                                [{"role": "user", "content": panel_prompt}], max_tokens=400)

        print(f"[{speaker} · {p['model'].split('/')[0]}] {text}")
        transcript.append({"speaker": speaker, "text": text,
                           "model": p["model"], "turn": i})
        last_speaker = speaker

        # 3) 오래된 기록 압축
        if len(transcript) > recent * 2 and i % 6 == 5:
            summary = summarize(router, mod["model"], transcript[:-recent])
            print(f"\n  … 이전 논의를 요약해 압축했습니다 (누적 ${router.spent_usd:.4f})\n")

    return transcript


# ----------------------------------------------------------------- 저장
def save(transcript, cfg, router, outdir):
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    payload = {
        "topic": cfg["topic"],
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "participants": [{"name": p["name"], "model": p["model"]} for p in cfg["panel"]],
        "moderator": {"name": cfg["moderator"]["name"], "model": cfg["moderator"]["model"]},
        "total_cost_usd": round(router.spent_usd, 6),
        "calls": router.calls,
        "transcript": transcript,
    }
    j = outdir / f"meeting_{stamp}.json"
    j.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [f"# {cfg['topic']}", "",
             f"*{payload['created_at']} · {len(transcript)}개 발언 · ${router.spent_usd:.4f}*", ""]
    for t in transcript:
        lines.append(f"**{t['speaker']}**  \n{t['text']}\n")
    m = outdir / f"meeting_{stamp}.md"
    m.write_text("\n".join(lines), encoding="utf-8")

    return j, m


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="personas.yaml")
    ap.add_argument("--length", choices=list(LENGTH_TO_TURNS), default=None)
    ap.add_argument("--turns", type=int, default=None, help="턴 수 직접 지정")
    ap.add_argument("--out", default="logs")
    ap.add_argument("--dry-run", action="store_true", help="API 호출 없이 흐름만 확인")
    args = ap.parse_args()

    load_dotenv()
    key = os.getenv("OPENROUTER_API_KEY")
    if not key and not args.dry_run:
        sys.exit("OPENROUTER_API_KEY 가 없습니다. .env 파일을 확인하세요.")

    cfg = yaml.safe_load(pathlib.Path(args.config).read_text(encoding="utf-8"))
    turns = args.turns or LENGTH_TO_TURNS[args.length or cfg.get("length", "3min")]

    router = Router(key, dry_run=args.dry_run)
    try:
        transcript = run(cfg, router, turns)
    except KeyboardInterrupt:
        print("\n중단됨. 여기까지 기록을 저장합니다.")
        transcript = []

    j, m = save(transcript, cfg, router, args.out)
    print("\n" + "─" * 60)
    print(f"총 비용: ${router.spent_usd:.4f}")
    print(f"로그:  {j}\n       {m}")


if __name__ == "__main__":
    main()
