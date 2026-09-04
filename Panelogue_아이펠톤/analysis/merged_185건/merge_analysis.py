# -*- coding: utf-8 -*-
"""두 Panelogue 턴별 분석 패키지를 통합하고 교차 검정한다.

핵심 질문: 머스크·VAR에서 '완화 96%'로 나온 것이 자료의 성질인가,
          초기값이 척도 경계(±100)라 강화가 불가능했던 설계 산물인가.
"""
import csv, io, json, os, sys, statistics as st
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
SC = r"C:/Users/hjbs5/AppData/Local/Temp/claude/C--Users-hjbs5/aa4ad374-e6ff-4d6e-bece-643af3c4b6dd/scratchpad"
A = SC + "/pkg/Panelogue_턴별_입장변화_분석패키지/analysis/turn-dynamics"
B = SC + "/mypkg/Panelogue_턴별_입장변화_분석패키지/analysis/turn-dynamics"

PKG = {
    "elon-musk-five-runs":      ("A_머스크·VAR", "일론 머스크 평가", "±100", "있음", 5),
    "var-ai-referee-five-runs": ("A_머스크·VAR", "VAR·AI 심판", "±100", "있음", 5),
    "world-peace-summit":       ("B_사회자없음", "세계 평화 정상 대토론", "비경계", "없음", 1),
    "kkondae-avengers":         ("B_사회자없음", "대한민국 꼰대 어벤져스", "비경계", "없음", 1),
    "playground-deception":     ("B_사회자없음", "운동장 대토론", "비경계", "없음", 1),
}

rows = []
for src, pkgname in ((A, "A"), (B, "B")):
    for r in csv.DictReader(open(src + "/stance-events.csv", encoding="utf-8-sig")):
        ds = r["dataset"]
        pk, topic_ko, ini_kind, mod, runs = PKG[ds]
        prev = float(r["previous_stance"]); new = float(r["new_stance"])
        ini = float(r["initial_stance"])
        r["package"] = pk
        r["topic_ko"] = topic_ko
        r["initial_kind"] = ini_kind
        r["moderator_setting"] = mod
        r["runs_in_topic"] = runs
        r["prev_f"] = prev; r["new_f"] = new; r["ini_f"] = ini
        r["delta_f"] = new - prev
        r["absdelta_f"] = abs(new - prev)
        # 강화 여지: 척도 경계까지 남은 거리. 0이면 강화가 구조적으로 불가능하다.
        r["headroom"] = round(100 - abs(prev), 2)
        r["hardened"] = 1 if abs(new) > abs(prev) else 0
        r["softened"] = 1 if abs(new) < abs(prev) else 0
        rows.append(r)

print("=" * 74)
print(f"통합 데이터셋: {len(rows)}건 (A {sum(1 for r in rows if r['package'].startswith('A'))} + "
      f"B {sum(1 for r in rows if r['package'].startswith('B'))})")
print("=" * 74)

# ── 1. 패키지별 기본 대조 ─────────────────────────────────
print("\n[1] 패키지별 변화 방향")
for pk in ["A_머스크·VAR", "B_사회자없음"]:
    rs = [r for r in rows if r["package"] == pk]
    ct = Counter(r["change_type"] for r in rs)
    h = sum(r["hardened"] for r in rs); s = sum(r["softened"] for r in rs)
    print(f"  {pk}: n={len(rs)} 강화 {h}({h/len(rs)*100:.1f}%) 완화 {s}({s/len(rs)*100:.1f}%) "
          f"극성전환 {ct.get('극성 전환',0)}")

# ── 2. 핵심: 강화 여지(headroom)별 강화율 ─────────────────
print("\n[2] ★ 강화 여지(headroom = 100 - |직전 입장|)별 강화율")
print("    headroom이 0이면 강화가 수학적으로 불가능하다.")
bins = [(0, 0, "0 (경계 고착)"), (0.01, 10, "0 초과~10"), (10.01, 30, "10~30"),
        (30.01, 60, "30~60"), (60.01, 200, "60 초과")]
print(f"    {'구간':<14}{'n':>5}{'강화':>6}{'강화율':>9}{'평균|Δ|':>10}   패키지 구성")
for lo, hi, lab in bins:
    rs = [r for r in rows if lo <= r["headroom"] <= hi]
    if not rs: continue
    h = sum(r["hardened"] for r in rs)
    pkc = Counter(r["package"][0] for r in rs)
    print(f"    {lab:<14}{len(rs):>5}{h:>6}{h/len(rs)*100:>8.1f}%"
          f"{st.mean(r['absdelta_f'] for r in rs):>10.2f}   A={pkc.get('A',0)} B={pkc.get('B',0)}")

# ── 3. headroom>0 으로 제한한 공정 비교 ───────────────────
print("\n[3] ★ headroom > 0 인 사건만으로 재비교 (강화가 가능했던 경우만)")
for pk in ["A_머스크·VAR", "B_사회자없음"]:
    rs = [r for r in rows if r["package"] == pk and r["headroom"] > 0]
    if not rs:
        print(f"  {pk}: n=0 — 비교 불가"); continue
    h = sum(r["hardened"] for r in rs)
    print(f"  {pk}: n={len(rs)} 강화 {h} ({h/len(rs)*100:.1f}%) "
          f"평균|Δ| {st.mean(r['absdelta_f'] for r in rs):.2f}")

# ── 4. 트리거 카테고리 통합 (같은 코드북) ─────────────────
print("\n[4] 트리거 카테고리별 통합 집계 (동일 코드북)")
print(f"    {'카테고리':<16}{'n':>4}{'평균|Δ|':>9}{'강화율':>8}   A / B")
cat = defaultdict(list)
for r in rows: cat[r["primary_category_ko"]].append(r)
for k, v in sorted(cat.items(), key=lambda x: -len(x[1])):
    h = sum(x["hardened"] for x in v)
    pkc = Counter(x["package"][0] for x in v)
    print(f"    {k:<16}{len(v):>4}{st.mean(x['absdelta_f'] for x in v):>9.2f}"
          f"{h/len(v)*100:>7.1f}%   {pkc.get('A',0)} / {pkc.get('B',0)}")

# ── 5. 사회자 유무 ────────────────────────────────────────
print("\n[5] 사회자 발화가 트리거인 사건")
mo = [r for r in rows if r["source_is_moderator"] == "True"]
pa = [r for r in rows if r["source_is_moderator"] != "True"]
print(f"    사회자 트리거 {len(mo)}건 평균|Δ| {st.mean(r['absdelta_f'] for r in mo):.2f} "
      f"강화율 {sum(r['hardened'] for r in mo)/len(mo)*100:.1f}%")
print(f"    패널  트리거 {len(pa)}건 평균|Δ| {st.mean(r['absdelta_f'] for r in pa):.2f} "
      f"강화율 {sum(r['hardened'] for r in pa)/len(pa)*100:.1f}%")
print("    ※ 사회자 트리거는 전량 A패키지 → 사회자 효과와 패키지 효과가 완전 교란됨")

# ── 6. 페르소나 반대 입력에 대한 반응 (코드북 §4 핵심) ────
print("\n[6] ★ 코드북 §4 핵심 질문: 페르소나 반대 입력을 받았을 때")
for pk in ["A_머스크·VAR", "B_사회자없음", "통합"]:
    rs = [r for r in rows if (pk == "통합" or r["package"] == pk)
          and r["trigger_persona_relation"] == "페르소나 반대 입력"]
    if not rs:
        print(f"  {pk}: n=0"); continue
    acc = sum(1 for r in rs if r["persona_response"] == "반대 입력 수용·페르소나 완화")
    reb = sum(1 for r in rs if r["persona_response"] == "반발·페르소나 재강화")
    print(f"  {pk}: n={len(rs)} → 수용·완화 {acc} vs 반발·재강화 {reb}"
          + ("  (반발 0건이라 검정 불가)" if reb == 0 else f"  → 수용 {acc/(acc+reb)*100:.0f}%"))

# ── 7. 모델별 (교란 경고 포함) ────────────────────────────
print("\n[7] 모델별 반응 (모델·페르소나·주제 고정결합이라 분리 불가)")
md = defaultdict(list)
for r in rows: md[r["model"].split("/")[-1]].append(r)
for k, v in sorted(md.items(), key=lambda x: -len(x[1])):
    h = sum(x["hardened"] for x in v)
    print(f"    {k:<26}{len(v):>4}건  평균|Δ| {st.mean(x['absdelta_f'] for x in v):>5.2f}  "
          f"강화율 {h/len(v)*100:>5.1f}%  주제 {len({x['dataset'] for x in v})}개")

# 저장
OUT = SC + "/merged"
os.makedirs(OUT, exist_ok=True)
fields = [k for k in rows[0].keys() if k not in ("prev_f", "new_f", "ini_f", "delta_f", "absdelta_f")]
with open(OUT + "/stance-events-merged.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"\n저장: stance-events-merged.csv ({len(rows)}행 × {len(fields)}열)")
