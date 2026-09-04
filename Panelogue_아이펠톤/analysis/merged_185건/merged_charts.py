# -*- coding: utf-8 -*-
"""통합 분석 차트 세트 (185건 / 5주제 / 2패키지)"""
import csv, io, sys, statistics as st
from collections import Counter, defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for _f in [r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\malgunbd.ttf"]:
    try: font_manager.fontManager.addfont(_f)
    except Exception: pass
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

INK, GREY = "#1e293b", "#64748b"
CA, CB = "#e11d48", "#2563eb"          # A패키지 / B패키지
OUT = "merged/charts"
import os; os.makedirs(OUT, exist_ok=True)

rows = list(csv.DictReader(open("merged/stance-events-merged.csv", encoding="utf-8-sig")))
for r in rows:
    r["hr"] = float(r["headroom"]); r["hard"] = int(r["hardened"])
    r["ad"] = abs(float(r["delta"])); r["ini"] = abs(float(r["initial_stance"]))

def head(ax, t, s=""):
    if s:
        ax.set_title("", pad=30)
        ax.text(0, 1.16, t, transform=ax.transAxes, fontsize=13, fontweight="bold", color=INK, va="bottom")
        ax.text(0, 1.045, s, transform=ax.transAxes, fontsize=9, color=GREY, va="bottom")
    else:
        ax.set_title(t, fontsize=13, fontweight="bold", color=INK, loc="left", pad=8)

def bare(ax, y=True):
    for sp in ["top", "right"] + ([] if y else ["left"]):
        ax.spines[sp].set_visible(False)

def save(fig, n):
    fig.tight_layout(); fig.savefig(f"{OUT}/{n}", dpi=150, bbox_inches="tight"); plt.close(fig); print("  ", n)

# ── 1. 초기값별 강화율 (핵심) ─────────────────────────────
d = defaultdict(list)
for r in rows: d[r["ini"]].append(r)
ks = sorted(k for k, v in d.items() if len(v) >= 3)
vals = [sum(x["hard"] for x in d[k]) / len(d[k]) * 100 for k in ks]
ns = [len(d[k]) for k in ks]
cols = [CA if d[k][0]["package"].startswith("A") else CB for k in ks]
fig, ax = plt.subplots(figsize=(9.2, 3.9))
b = ax.bar([str(int(k)) for k in ks], vals, color=cols, width=.55)
for i, (v, n) in enumerate(zip(vals, ns)):
    ax.text(i, v + 2.5, f"{v:.1f}%\n(n={n})", ha="center", fontsize=10, fontweight="bold", color=INK)
ax.plot(range(len(ks)), vals, "o--", color="#334155", lw=1.4, ms=5, zorder=5)
ax.set_ylim(0, 118); ax.set_ylabel("강화 방향 변화 비율", fontsize=10)
ax.set_xlabel("|초기 입장값|", fontsize=10)
head(ax, "초기 입장이 극단일수록 '강화'는 사라진다",
     "185건 전체 · 파랑=B패키지(사회자 없는 3주제), 빨강=A패키지(머스크·VAR)")
bare(ax)
ax.text(0, -.30, "|초기값| 0→25→71 구간은 모두 B패키지 내부이므로 패키지 교란 없이 단조 감소가 확인된다.",
        transform=ax.transAxes, fontsize=8.5, color=GREY)
save(fig, "M1_initial_vs_hardening.png")

# ── 2. headroom 구간별 강화율 ─────────────────────────────
bins = [(0, 0, "0\n(경계 고착)"), (0.01, 10, "0~10"), (10.01, 30, "10~30"),
        (30.01, 60, "30~60"), (60.01, 200, "60 초과")]
fig, ax = plt.subplots(figsize=(9.2, 3.9))
xs, ys, ann = [], [], []
for lo, hi, lab in bins:
    rs = [r for r in rows if lo <= r["hr"] <= hi]
    if not rs: continue
    xs.append(lab); ys.append(sum(r["hard"] for r in rs) / len(rs) * 100)
    c = Counter(r["package"][0] for r in rs)
    ann.append(f"n={len(rs)}\nA {c.get('A',0)} / B {c.get('B',0)}")
ax.bar(xs, ys, color="#0891b2", width=.55)
for i, (v, a) in enumerate(zip(ys, ann)):
    ax.text(i, v + 2.5, f"{v:.1f}%", ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.text(i, -13, a, ha="center", fontsize=8, color=GREY)
ax.set_ylim(0, 85); ax.set_ylabel("강화 비율", fontsize=10)
head(ax, "강화 여지(headroom)가 0이면 강화율도 0이다",
     "headroom = 100 - |직전 입장| · 경계에 고착된 21건은 전부 A패키지이며 강화가 수학적으로 불가능")
bare(ax); ax.set_xlabel("")
save(fig, "M2_headroom_vs_hardening.png")

# ── 3. 층화 비교 ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9.2, 3.6))
labs, av, bv, an, bn = [], [], [], [], []
for lo, hi, lab in [(0.01, 10, "headroom 0~10"), (10.01, 30, "headroom 10~30")]:
    ra = [r for r in rows if r["package"].startswith("A") and lo <= r["hr"] <= hi]
    rb = [r for r in rows if r["package"].startswith("B") and lo <= r["hr"] <= hi]
    labs.append(lab)
    av.append(sum(r["hard"] for r in ra) / len(ra) * 100); an.append(len(ra))
    bv.append(sum(r["hard"] for r in rb) / len(rb) * 100); bn.append(len(rb))
x = np.arange(len(labs)); W = .34
ax.bar(x - W/2, av, W, color=CA, label="A 머스크·VAR (사회자 있음)")
ax.bar(x + W/2, bv, W, color=CB, label="B 사회자 없는 3주제")
for i in range(len(labs)):
    ax.text(i - W/2, av[i] + 2, f"{av[i]:.0f}%\nn={an[i]}", ha="center", fontsize=9.5, color=INK)
    ax.text(i + W/2, bv[i] + 2, f"{bv[i]:.0f}%\nn={bn[i]}", ha="center", fontsize=9.5, color=INK)
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=10); ax.set_ylim(0, 100)
ax.set_ylabel("강화 비율", fontsize=10)
head(ax, "headroom을 맞춰도 두 패키지 차이는 남는다",
     "겹치는 두 구간만 층화 비교 · 잔차는 사회자·주제·모델과 완전히 교란되어 원인 분리 불가")
ax.legend(fontsize=9, frameon=False); bare(ax)
save(fig, "M3_stratified_comparison.png")

# ── 4. 통합 트리거 카테고리 ───────────────────────────────
cat = defaultdict(list)
for r in rows: cat[r["primary_category_ko"]].append(r)
items = sorted(cat.items(), key=lambda x: st.mean(v["ad"] for v in x[1]))
fig, ax = plt.subplots(figsize=(9.2, 4.2))
ys = [k for k, _ in items]; ms = [st.mean(v["ad"] for v in vv) for _, vv in items]
ax.barh(ys, ms, color="#f97316", height=.62)
for i, (k, vv) in enumerate(items):
    c = Counter(x["package"][0] for x in vv)
    ax.text(ms[i] + .25, i, f"{ms[i]:.1f} · n={len(vv)} (A{c.get('A',0)}/B{c.get('B',0)}) · 강화율 "
            f"{sum(x['hard'] for x in vv)/len(vv)*100:.0f}%", va="center", fontsize=8.8, color=INK)
ax.set_xlim(0, max(ms) * 2.3)
head(ax, "트리거 카테고리별 통합 집계", "두 패키지가 동일 코드북을 써서 직접 합산 가능 · 막대는 평균 절대 변화폭(점)")
ax.xaxis.set_visible(False); bare(ax, y=False)
save(fig, "M4_trigger_categories_merged.png")

# ── 5. 5주제 요약 ─────────────────────────────────────────
tp = defaultdict(list)
for r in rows: tp[r["topic_ko"]].append(r)
order = ["일론 머스크 평가", "VAR·AI 심판", "세계 평화 정상 대토론", "대한민국 꼰대 어벤져스", "운동장 대토론"]
order = [t for t in order if t in tp]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.8), gridspec_kw={"width_ratios": [1, 1]})
ns = [len(tp[t]) for t in order]
cs = [CA if tp[t][0]["package"].startswith("A") else CB for t in order]
a1.barh(order, ns, color=cs, height=.6); a1.invert_yaxis()
for i, n in enumerate(ns): a1.text(n + 1.5, i, str(n), va="center", fontsize=10, color=INK)
a1.set_xlim(0, max(ns) * 1.25); head(a1, "주제별 입장 변화 사건 수"); a1.xaxis.set_visible(False); bare(a1, y=False)
hv = [sum(x["hard"] for x in tp[t]) / len(tp[t]) * 100 for t in order]
a2.barh(order, hv, color=cs, height=.6); a2.invert_yaxis()
for i, v in enumerate(hv): a2.text(v + 1.5, i, f"{v:.0f}%", va="center", fontsize=10, color=INK)
a2.set_xlim(0, 118); a2.set_yticklabels([]); head(a2, "주제별 강화 비율"); a2.xaxis.set_visible(False); bare(a2, y=False)
fig.suptitle("5개 주제 통합 — 빨강 A패키지(±100·사회자 있음), 파랑 B패키지(비경계·사회자 없음)",
             fontsize=11, color=GREY, x=.01, ha="left", y=1.03)
save(fig, "M5_topics_overview.png")

# ── 6. 모델별 (교란 경고) ─────────────────────────────────
md = defaultdict(list)
for r in rows: md[r["model"].split("/")[-1]].append(r)
items = sorted(md.items(), key=lambda x: -len(x[1]))
fig, ax = plt.subplots(figsize=(9.2, 4.0))
ys = [k for k, _ in items]
hv = [sum(x["hard"] for x in v) / len(v) * 100 for _, v in items]
ax.barh(ys, hv, color=["#94a3b8" if len(v) < 10 else "#8b5cf6" for _, v in items], height=.6)
for i, (k, v) in enumerate(items):
    ax.text(hv[i] + 1.5, i, f"{hv[i]:.0f}%  n={len(v)} · 주제{len({x['dataset'] for x in v})}개"
            + ("  ※표본부족" if len(v) < 10 else ""), va="center", fontsize=8.8, color=INK)
ax.invert_yaxis(); ax.set_xlim(0, 150)
head(ax, "모델별 강화 비율 — 해석 금지 구역",
     "모델·페르소나·주제·초기값이 고정 결합되어 있어 '모델 성격'으로 읽으면 안 된다")
ax.xaxis.set_visible(False); bare(ax, y=False)
save(fig, "M6_model_warning.png")

# ── 0. 컨택트 시트 ────────────────────────────────────────
import math
files = sorted(f for f in os.listdir(OUT) if f.startswith("M") and not f.startswith("M0"))
cols = 2; rw = math.ceil(len(files) / cols)
fig, axes = plt.subplots(rw, cols, figsize=(cols * 6.4, rw * 3.6))
flat = np.array(axes).ravel()
for ax, p in zip(flat, files):
    ax.imshow(plt.imread(f"{OUT}/{p}")); ax.set_title(p[:-4], fontsize=9, color=INK, pad=4)
for ax in flat: ax.axis("off")
fig.suptitle("Panelogue 통합 분석 — 2패키지 5주제 185건", fontsize=15, fontweight="bold", color=INK, y=.997)
save(fig, "M0_contact_sheet.png")
