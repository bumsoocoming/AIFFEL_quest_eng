# -*- coding: utf-8 -*-
"""발표용 차트 5종 — 크림슨·틸·그래파이트 팔레트"""
import csv, io, os, sys, statistics as st
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for _f in [r"C:\Windows\Fonts\HanSantteutDotum-Regular.ttf",
           r"C:\Windows\Fonts\HanSantteutDotum-Bold.ttf"]:
    try: font_manager.fontManager.addfont(_f)
    except Exception: pass
plt.rcParams["font.family"] = "Han Santteut Dotum"
plt.rcParams["axes.unicode_minus"] = False

OUT = "deck"; os.makedirs(OUT, exist_ok=True)
INK   = "#26242E"
MUT   = "#8B8797"
CRIM  = "#C8102E"
TEAL  = "#0F8B8D"
PURP  = "#6B4E9B"
SLATE = "#5B6B7F"
CRIM_S = "#FCEFF1"
TEAL_L = "#BFE3E3"
TEAL_M = "#79C7C8"
SLATE_L = "#B4BECB"

def save(fig, n):
    fig.savefig(f"{OUT}/{n}", dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig); print("  ", n)

rows = list(csv.DictReader(open("merged/stance-events-merged.csv", encoding="utf-8-sig")))
for r in rows:
    r["hard"] = int(r["hardened"]); r["turn"] = int(r["target_turn"])
    r["new"] = float(r["new_stance"]); r["ad"] = abs(float(r["delta"]))
    r["ini"] = abs(float(r["initial_stance"]))

# ══ PC1. 계단 그래프 ══════════════════════════════════════
ser = list(csv.DictReader(open(
    "mypkg/Panelogue_턴별_입장변화_분석패키지/analysis/turn-dynamics/turn-stance-series.csv",
    encoding="utf-8-sig")))
ds = "kkondae-avengers"
rows_s = [r for r in ser if r["dataset"] == ds]
agents = ["회사 부장", "잔소리많은 아버지", "동네 통장", "아파트 관리 소장"]
PAL = [CRIM, SLATE, TEAL, PURP]
fig, ax = plt.subplots(figsize=(12.4, 6.0))
for i, ag in enumerate(agents):
    pts = sorted((int(r["turn"]), float(r["stance"])) for r in rows_s if r["agent_name"] == ag)
    lw, al, z = (4.4, 1.0, 5) if i == 0 else (2.2, .5, 3)
    ax.step([p[0] for p in pts], [p[1] for p in pts], where="post",
            color=PAL[i], lw=lw, alpha=al, label=ag, zorder=z)
for r in [x for x in rows if x["dataset"] == ds and x["agent_name"] == "회사 부장"]:
    ax.plot(r["turn"], r["new"], "o", ms=11, mfc="white", mec=CRIM, mew=3, zorder=8)
ax.axhline(0, color=MUT, lw=1.4, ls="--", zorder=1)

ax.annotate("", xy=(5.2, 33), xytext=(30, 6),
            arrowprops=dict(arrowstyle="->", color=CRIM, lw=3.2,
                            connectionstyle="arc3,rad=-.22"), zorder=9)
ax.add_patch(FancyBboxPatch((30, -20), 68, 50, boxstyle="round,pad=1.6",
                            fc=CRIM_S, ec=CRIM, lw=2.4, zorder=10,
                            transform=ax.transData))
ax.text(64, 19, "\u201c분리배출 시간을 게시판에 규정 조항까지\n붙여놓으면 20대 세대가 오히려 제일 잘 지킵니다\u201d",
        ha="center", va="center", fontsize=14.5, color=INK, zorder=11, linespacing=1.5)
ax.text(64, -4, "- 아파트 관리 소장, 2턴", ha="center", va="center",
        fontsize=12.5, color=MUT, zorder=11)
ax.text(64, -15, "회사 부장은 이 규칙 우선론을 거부하며 -25 에서 +35 로 극성 전환",
        ha="center", va="center", fontsize=13, color=CRIM, fontweight="bold", zorder=11)

ax.set_xlim(0, 104); ax.set_ylim(-108, 108)
ax.set_xlabel("토론 턴", fontsize=17, color=INK)
ax.set_ylabel("입장 지수", fontsize=17, color=INK)
ax.tick_params(labelsize=15, colors=INK)
ax.legend(fontsize=14.5, ncol=4, loc="upper center", bbox_to_anchor=(.5, 1.10), frameon=False)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
ax.grid(axis="y", alpha=.2)
save(fig, "pc1_steps.png")

# ══ PC2. 트리거 범주별 건수 ═══════════════════════════════
cat = defaultdict(list)
for r in rows: cat[r["primary_category_ko"]].append(r)
items = sorted(((k, len(v), st.mean(x["ad"] for x in v)) for k, v in cat.items()
                if len(v) >= 5), key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(12.4, 5.4))
ys = [i[0] for i in items]; ns = [i[1] for i in items]
ax.barh(ys, ns, color=[CRIM if n >= 40 else TEAL_M for n in ns], height=.66)
for i, (k, n, m) in enumerate(items):
    ax.text(n + 2, i, f"{n}건   평균 {m:.1f}점 이동", va="center", fontsize=15, color=INK)
ax.set_xlim(0, max(ns) * 1.62)
ax.tick_params(axis="y", labelsize=16, colors=INK); ax.xaxis.set_visible(False)
for s in ["top", "right", "bottom", "left"]: ax.spines[s].set_visible(False)
save(fig, "pc2_categories.png")

# ══ PC3. 초기값별 강도 증가 ═══════════════════════════════
d = defaultdict(list)
for r in rows: d[r["ini"]].append(r)
ks = [0, 25, 71, 100]
vals = [sum(x["hard"] for x in d[k]) / len(d[k]) * 100 for k in ks]
ns = [len(d[k]) for k in ks]
fig, ax = plt.subplots(figsize=(12.4, 5.8))
cols = ["#D6EDED", TEAL_M, TEAL, CRIM]
ax.bar([str(k) for k in ks], vals, color=cols, width=.58, zorder=3)
ax.plot(range(4), vals, "o--", color=INK, lw=2.6, ms=9, zorder=4)
halo = dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=.92)
for i, (v, n) in enumerate(zip(vals, ns)):
    ax.text(i, v + (10 if i == 3 else 5), f"{v:.1f}%", ha="center", fontsize=25,
            fontweight="bold", color=CRIM if i == 3 else INK, zorder=6, bbox=halo)
    ax.text(i, v + (22 if i == 3 else -10), f"n={n}", ha="center", fontsize=13.5,
            color=INK if i in (0, 3) else "white", zorder=6)
ax.set_ylim(0, 122)
ax.set_xlabel("초기 입장의 절대값", fontsize=18, color=INK)
ax.set_ylabel("강도 증가 비율", fontsize=17, color=INK)
ax.tick_params(labelsize=16, colors=INK)
ax.text(3, 46, "척도 경계\n= 강화 불가", ha="center", fontsize=16, color=CRIM,
        fontweight="bold", linespacing=1.5, zorder=6)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
ax.grid(axis="y", alpha=.2, zorder=0)
save(fig, "pc3_initial.png")

# ══ PC4. 평균 0의 함정 ════════════════════════════════════
fig, ax = plt.subplots(figsize=(12.4, 5.2))
runs = ["1회", "2회", "3회", "4회", "5회"]
center = [3.75, -5.50, 0, 0, -5.50]
x = np.arange(5)
ax.bar(x - .19, center, .38, color=SLATE_L, label="집단 평균 (부호 있음)")
absv = [96.25, 94.50, 100.00, 92.50, 94.50]   # run-metrics.csv 실측값
ax.bar(x + .19, absv, .38, color=CRIM, label="평균 절대 입장")
for i, c in enumerate(center):
    ax.text(i - .19, c + (4 if c >= 0 else -9), f"{c:+.2f}", ha="center", fontsize=13.5, color=INK)
for i, v in enumerate(absv):
    ax.text(i + .19, v + 3, f"{v:g}", ha="center", fontsize=13.5, color=INK, fontweight="bold")
ax.axhline(0, color=INK, lw=1.4)
ax.set_xticks(x); ax.set_xticklabels(runs, fontsize=16)
ax.set_ylim(-20, 112); ax.tick_params(labelsize=15, colors=INK)
ax.set_ylabel("입장 지수", fontsize=16, color=INK)
ax.legend(fontsize=15, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(.5, 1.13))
for s in ["top", "right"]: ax.spines[s].set_visible(False)
ax.grid(axis="y", alpha=.2)
save(fig, "pc4_average_trap.png")

# ══ PC5. 교차분석 — 페르소나 관계 × 반응 방향 ══════════════
dp = defaultdict(list)
for r in rows: dp[r["trigger_persona_relation"]].append(r)
keys = ["페르소나 반대 입력", "페르소나 지지 입력", "사회자 탐색 질문"]
fig, ax = plt.subplots(figsize=(9.6, 4.6))
for i, k in enumerate(keys):
    v = dp[k]; n = len(v); h = sum(x["hard"] for x in v) / n * 100
    ax.barh(i, h, color=CRIM, height=.56)
    ax.barh(i, 100 - h, left=h, color=TEAL_L, height=.56)
    ax.text(h / 2, i, f"{h:.0f}%", ha="center", va="center", fontsize=17,
            fontweight="bold", color="white")
    ax.text(h + (100 - h) / 2, i, f"{100-h:.0f}%", ha="center", va="center",
            fontsize=17, fontweight="bold", color=INK)
    ax.text(103, i, f"n={n}", va="center", fontsize=13.5, color=MUT)
ax.set_yticks(list(range(len(keys))))
ax.set_yticklabels([k.replace(" ", "\n", 1) for k in keys], fontsize=14.5, color=INK)
ax.set_xlim(0, 112); ax.set_xticks([]); ax.invert_yaxis()
for s in ["top", "right", "bottom", "left"]: ax.spines[s].set_visible(False)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=CRIM),
                   plt.Rectangle((0, 0), 1, 1, fc=TEAL_L)],
          labels=["강도 증가", "완화·전환"], fontsize=14, ncol=2, frameon=False,
          loc="upper center", bbox_to_anchor=(.46, 1.16))
save(fig, "pc5_persona.png")
print("완료")
