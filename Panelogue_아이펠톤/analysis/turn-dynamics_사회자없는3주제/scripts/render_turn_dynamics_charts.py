#!/usr/bin/env python3
"""턴별 입장 변화 분석 결과를 PNG 차트 세트로 렌더링한다.

사용: python scripts/render_turn_dynamics_charts.py analysis/turn-dynamics analysis/charts
"""
from __future__ import annotations
import argparse, csv, math
from collections import Counter
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for _f in [r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\malgunbd.ttf"]:
    try:
        font_manager.fontManager.addfont(_f)
    except Exception:
        pass
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, INK, GREY = "#2563eb", "#f97316", "#1e293b", "#64748b"
PALETTE = ["#2563eb", "#f97316", "#10b981", "#8b5cf6", "#e11d48"]
TOPIC_KO = {"world-peace-summit": "세계 평화 정상 대토론",
            "kkondae-avengers": "대한민국 꼰대 어벤져스",
            "playground-deception": "운동장 대토론"}


def head(ax, title, sub=""):
    """제목은 축 위 두 단으로 배치한다(부제가 제목을 가리지 않도록 y 좌표를 분리)."""
    if sub:
        ax.set_title("", pad=30)
        ax.text(0, 1.155, title, transform=ax.transAxes, fontsize=13,
                fontweight="bold", color=INK, va="bottom")
        ax.text(0, 1.045, sub, transform=ax.transAxes, fontsize=9, color=GREY, va="bottom")
    else:
        ax.set_title(title, fontsize=13, fontweight="bold", color=INK, loc="left", pad=8)


def bare(ax, keep_y=True):
    for s in ["top", "right"] + ([] if keep_y else ["left"]):
        ax.spines[s].set_visible(False)


def save(fig, out: Path, name):
    fig.tight_layout()
    fig.savefig(out / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  ", name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    out = a.output
    out.mkdir(parents=True, exist_ok=True)

    ev = list(csv.DictReader(open(a.analysis / "stance-events.csv", encoding="utf-8-sig")))
    ser = list(csv.DictReader(open(a.analysis / "turn-stance-series.csv", encoding="utf-8-sig")))
    trig = list(csv.DictReader(open(a.analysis / "trigger-summary.csv", encoding="utf-8-sig")))
    corr = list(csv.DictReader(open(a.analysis / "personality-correlations.csv", encoding="utf-8-sig")))
    for r in ev:
        r["delta"] = float(r["delta"])
        r["absolute_delta"] = float(r["absolute_delta"])
        r["target_turn"] = int(r["target_turn"])
        r["new_stance"] = float(r["new_stance"])

    idx = 0
    datasets = [d for d in TOPIC_KO if any(r["dataset"] == d for r in ev)]
    if not datasets:
        datasets = sorted({r["dataset"] for r in ev})

    # ── 01~03 주제별 계단 그래프 ──────────────────────────────
    for ds in datasets:
        idx += 1
        rows = [r for r in ser if r["dataset"] == ds]
        agents = sorted({r["agent_name"] for r in rows})
        fig, ax = plt.subplots(figsize=(9.2, 4.6))
        for i, ag in enumerate(agents):
            pts = sorted((int(r["turn"]), float(r["stance"])) for r in rows if r["agent_name"] == ag)
            ax.step([p[0] for p in pts], [p[1] for p in pts], where="post",
                    color=PALETTE[i % len(PALETTE)], lw=2, label=ag)
        evs = [r for r in ev if r["dataset"] == ds]
        for r in evs:
            i = agents.index(r["agent_name"]) if r["agent_name"] in agents else 0
            ax.plot(r["target_turn"], r["new_stance"], "o", ms=5, mfc="white",
                    mec=PALETTE[i % len(PALETTE)], mew=1.6, zorder=5)
        ax.axhline(0, color="#94a3b8", lw=.8, ls="--")
        ax.set_ylim(-105, 105)
        ax.set_xlabel("전역 대화 턴", fontsize=10)
        ax.set_ylabel("입장지수", fontsize=10)
        head(ax, f"{TOPIC_KO.get(ds, ds)} · 턴별 입장 변화",
             f"입장지수 -100(반대) ~ +100(찬성) · 원형 표시는 입장 변화 사건 {len(evs)}건 · 사회자 없음")
        ax.legend(fontsize=9, ncol=len(agents), loc="lower center",
                  bbox_to_anchor=(.5, -.30), frameon=False)
        bare(ax)
        ax.text(0, -.44, "자료: Panelogue JSON의 messages·stanceHistory·influencedByMessageIds",
                transform=ax.transAxes, fontsize=7.5, color=GREY)
        save(fig, out, f"{idx:02d}_{ds}_stance_steps.png")

    # ── 04 트리거 효과 ────────────────────────────────────────
    idx += 1
    tr = sorted(((r["category_ko"], int(r["event_source_links"]), float(r["mean_absolute_delta"]))
                 for r in trig), key=lambda x: x[2])
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.barh([t[0] for t in tr], [t[2] for t in tr], color=ORANGE, height=.62)
    for i, t in enumerate(tr):
        ax.text(t[2] + .12, i, f"{t[2]:.1f} · n={t[1]}", va="center", fontsize=9.5, color=INK)
    ax.set_xlim(0, max(t[2] for t in tr) * 1.35)
    head(ax, "반응 구절 유형별 입장 변화폭",
         f"{len(ev)}건 입장 변화 사건의 자동 1차 코딩 · 막대는 평균 절대 변화폭(점)")
    ax.xaxis.set_visible(False)
    bare(ax, keep_y=False)
    save(fig, out, f"{idx:02d}_trigger_effects.png")

    # ── 05 변화 유형 분포 ─────────────────────────────────────
    idx += 1
    ct = Counter(r["change_type"] for r in ev)
    fig, ax = plt.subplots(figsize=(9.2, 3.4))
    ks = [k for k, _ in ct.most_common()]
    vs = [ct[k] for k in ks]
    cols = ["#10b981" if "완화" in k else "#e11d48" if "강화" in k else "#8b5cf6" for k in ks]
    ax.barh(ks, vs, color=cols, height=.55)
    for i, v in enumerate(vs):
        ax.text(v + max(vs) * .015, i, f"{v} · {v / len(ev) * 100:.1f}%",
                va="center", fontsize=10, color=INK)
    ax.set_xlim(0, max(vs) * 1.3)
    ax.invert_yaxis()
    head(ax, "입장 변화는 어느 방향으로 일어났나",
         "극성 전환·강화·완화의 구성 · 초기값이 척도 경계가 아니어서 강화도 구조적으로 가능")
    ax.xaxis.set_visible(False)
    bare(ax, keep_y=False)
    save(fig, out, f"{idx:02d}_change_type_distribution.png")

    # ── 06 페르소나 입력관계 × 반응 히트맵 ────────────────────
    idx += 1
    rel = ["사회자 탐색 질문", "페르소나 반대 입력", "페르소나 지지 입력"]
    res = ["반대 입력 수용·페르소나 완화", "반발·페르소나 재강화", "지지 입력으로 페르소나 복귀",
           "지지 입력에도 페르소나 이탈", "탐색 질문 후 강화", "탐색 질문 후 완화"]
    M = np.zeros((len(rel), len(res)))
    for r in ev:
        if r["trigger_persona_relation"] in rel and r["persona_response"] in res:
            M[rel.index(r["trigger_persona_relation"]), res.index(r["persona_response"])] += 1
    fig, ax = plt.subplots(figsize=(9.6, 3.3))
    ax.imshow(M, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(res)))
    short = {"반대 입력 수용·페르소나 완화": "반대 입력 수용\n페르소나 완화",
             "반발·페르소나 재강화": "반발\n페르소나 재강화",
             "지지 입력으로 페르소나 복귀": "지지 입력으로\n페르소나 복귀",
             "지지 입력에도 페르소나 이탈": "지지 입력에도\n페르소나 이탈",
             "탐색 질문 후 강화": "탐색 질문 후\n강화",
             "탐색 질문 후 완화": "탐색 질문 후\n완화"}
    ax.set_xticklabels([short.get(r, r) for r in res], fontsize=7.6)
    ax.set_yticks(range(len(rel)))
    ax.set_yticklabels(rel, fontsize=9)
    for i in range(len(rel)):
        for j in range(len(res)):
            v = int(M[i, j])
            ax.text(j, i, v, ha="center", va="center", fontsize=11, fontweight="bold",
                    color="white" if v > M.max() * .55 else INK)
    head(ax, "페르소나 입력 관계 × 실제 반응",
         "상대 발언의 입장 부호가 반응자의 초기 입장을 지지/반대하는지로 교차 집계 · 사회자 없어 1행은 0")
    ax.set_xlabel("셀 값 = 입장 변화 사건 수", fontsize=9)
    save(fig, out, f"{idx:02d}_persona_input_response_heatmap.png")

    # ── 07 성격 상관 ──────────────────────────────────────────
    idx += 1
    cs = [(r["configured_feature_ko"], float(r["pearson_r"]))
          for r in corr if r["observed_outcome"] == "total_volatility" and r["pearson_r"]]
    cs.sort(key=lambda x: x[1])
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.barh([c[0] for c in cs], [c[1] for c in cs],
            color=["#e11d48" if c[1] < 0 else "#10b981" for c in cs], height=.6)
    for i, c in enumerate(cs):
        ax.text(c[1] + (.03 if c[1] >= 0 else -.03), i, f"{c[1]:+.2f}", va="center",
                ha="left" if c[1] >= 0 else "right", fontsize=9.5, color=INK)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlim(-1, 1)
    head(ax, "성격·행동 설정값 × 실제 총 변동성",
         "Pearson r · 행 단위는 주제×에이전트 12행이며 독립 표본 추론이 아님")
    ax.set_xlabel("Pearson r (-1 ~ +1)", fontsize=9)
    bare(ax, keep_y=False)
    save(fig, out, f"{idx:02d}_personality_volatility_correlations.png")

    # ── 08 주제별 사건 수 ─────────────────────────────────────
    idx += 1
    cnt = Counter(r["dataset"] for r in ev)
    fig, ax = plt.subplots(figsize=(9.2, 3.4))
    ks = [TOPIC_KO.get(k, k) for k in datasets]
    vs = [cnt[k] for k in datasets]
    ax.bar(ks, vs, color=BLUE, width=.5)
    for i, v in enumerate(vs):
        ax.text(i, v + max(vs) * .03, str(v), ha="center", fontsize=11,
                fontweight="bold", color=INK)
    ax.set_ylim(0, max(vs) * 1.2)
    head(ax, "주제별 입장 변화 사건 수",
         "각 주제 1회 실행 · 반복 실행이 없어 회차 간 안정성은 평가 불가")
    ax.set_ylabel("사건 수", fontsize=9)
    bare(ax)
    save(fig, out, f"{idx:02d}_topic_event_counts.png")

    # ── 09 누가 누구를 움직였나 ───────────────────────────────
    idx += 1
    srcs = sorted({r["source_speaker"] for r in ev if r["source_speaker"]})
    tgts = sorted({r["agent_name"] for r in ev})
    M2 = np.zeros((len(srcs), len(tgts)))
    for r in ev:
        if r["source_speaker"] in srcs:
            M2[srcs.index(r["source_speaker"]), tgts.index(r["agent_name"])] += 1
    fig, ax = plt.subplots(figsize=(9.2, max(3.2, .40 * len(srcs) + 1.8)))
    ax.imshow(M2, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(tgts)))
    ax.set_xticklabels(tgts, fontsize=8.5, rotation=20, ha="right")
    ax.set_yticks(range(len(srcs)))
    ax.set_yticklabels(srcs, fontsize=8.5)
    for i in range(len(srcs)):
        for j in range(len(tgts)):
            v = int(M2[i, j])
            if v:
                ax.text(j, i, v, ha="center", va="center", fontsize=9.5, fontweight="bold",
                        color="white" if v > M2.max() * .55 else INK)
    head(ax, "누가 누구의 입장을 움직였나",
         "행=반응을 유발한 발화자, 열=입장이 변한 에이전트 · 사회자 없이 전원 패널")
    save(fig, out, f"{idx:02d}_source_target_heatmap.png")

    # ── 10 초기 vs 최종 ───────────────────────────────────────
    idx += 1
    fig, axes = plt.subplots(1, len(datasets), figsize=(9.6, 3.4))
    axes = np.atleast_1d(axes)
    for ax, ds in zip(axes, datasets):
        rows = [r for r in ser if r["dataset"] == ds]
        ags = sorted({r["agent_name"] for r in rows})
        for i, ag in enumerate(ags):
            pts = sorted((int(r["turn"]), float(r["stance"])) for r in rows if r["agent_name"] == ag)
            ini, fin = pts[0][1], pts[-1][1]
            ax.plot([ini, fin], [i, i], color="#cbd5e1", lw=2, zorder=1)
            ax.plot(ini, i, "o", ms=6, color="white", mec=PALETTE[i % 5], mew=1.8, zorder=3)
            ax.plot(fin, i, "o", ms=7, color=PALETTE[i % 5], zorder=3)
            ax.text(fin + (7 if fin >= 0 else -7), i, f"{fin:+.0f}", va="center",
                    ha="left" if fin >= 0 else "right", fontsize=8, color=INK)
        ax.set_yticks(range(len(ags)))
        ax.set_yticklabels(ags, fontsize=8)
        ax.set_xlim(-135, 135)
        ax.axvline(0, color="#94a3b8", lw=.8, ls="--")
        ax.set_title(TOPIC_KO.get(ds, ds), fontsize=10, fontweight="bold", color=INK)
        bare(ax, keep_y=False)
        ax.invert_yaxis()
    fig.suptitle("초기 입장과 최종 입장", fontsize=13, fontweight="bold", color=INK,
                 x=.01, ha="left", y=1.16)
    fig.text(.01, 1.05, "빈 원=초기값, 채운 원=최종값 · 초기값이 ±100 경계가 아니어서 강화·완화가 모두 가능",
             fontsize=9, color=GREY)
    fig.text(.5, -.07, "입장지수 (-100 반대 ~ +100 찬성)", ha="center", fontsize=9)
    save(fig, out, f"{idx:02d}_initial_final_stance.png")

    # ── 11 변화폭 분포 ────────────────────────────────────────
    idx += 1
    bins = [("1-5", 0, 5), ("6-10", 5, 10), ("11-20", 10, 20), ("21점 이상", 20, 10**9)]
    fig, ax = plt.subplots(figsize=(9.2, 3.6))
    W = .8 / len(datasets)
    for k, ds in enumerate(datasets):
        vals = [abs(r["delta"]) for r in ev if r["dataset"] == ds]
        cnts = [sum(1 for v in vals if lo < v <= hi) for _, lo, hi in bins]
        ax.bar([i + k * W - .4 + W / 2 for i in range(len(bins))], cnts, width=W,
               color=PALETTE[k], label=TOPIC_KO.get(ds, ds))
    ax.set_xticks(range(len(bins)))
    ax.set_xticklabels([b[0] for b in bins], fontsize=9.5)
    head(ax, "입장 변화폭 분포", "절대 변화폭을 네 구간으로 나눠 주제별 반응 강도를 비교")
    ax.set_ylabel("사건 수", fontsize=9)
    ax.legend(fontsize=9, frameon=False)
    bare(ax)
    save(fig, out, f"{idx:02d}_delta_distribution.png")

    # ── 00 컨택트 시트 ────────────────────────────────────────
    files = sorted(p for p in out.glob("*.png") if not p.name.startswith("00_"))
    cols = 3
    rows_n = math.ceil(len(files) / cols)
    fig, axes = plt.subplots(rows_n, cols, figsize=(cols * 5.0, rows_n * 3.3))
    flat = np.array(axes).ravel()
    for ax, p in zip(flat, files):
        ax.imshow(plt.imread(p))
        ax.set_title(p.stem, fontsize=8, color=INK, pad=4)
    for ax in flat:
        ax.axis("off")
    fig.suptitle("Panelogue 턴별 입장 변화 — 그래프 목록 (사회자 없는 3주제)",
                 fontsize=15, fontweight="bold", color=INK, y=.995)
    save(fig, out, "00_graph_contact_sheet.png")


if __name__ == "__main__":
    main()
