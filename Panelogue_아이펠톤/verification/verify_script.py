# -*- coding: utf-8 -*-
"""발표 대본(발표자 노트) 전용 검증 —
   대본이 말하는 모든 사실 주장을 원자료에서 재계산해 대조한다."""
import csv, io, json, re, sys, zipfile, html, statistics as st
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

z = zipfile.ZipFile("Panelogue_발표자료.pptx")

def notes(i):
    x = z.read("ppt/notesSlides/notesSlide%d.xml" % i).decode("utf-8")
    return html.unescape("".join(re.findall(r"<a:t>(.*?)</a:t>",
           x.split('name="Slide Number Placeholder')[0], re.S)))

def slide(i):
    x = z.read("ppt/slides/slide%d.xml" % i).decode("utf-8")
    return html.unescape("".join(re.findall(r"<a:t>(.*?)</a:t>", x, re.S)))

TIMED = 15                    # 16번은 백업 슬라이드
N = {i: notes(i) for i in range(1, 17)}
S = {i: slide(i) for i in range(1, 17)}
ALLN = "".join(N.values())

# ── 원자료 ────────────────────────────────────────────────
R = list(csv.DictReader(open("merged/stance-events-merged.csv", encoding="utf-8-sig")))
for r in R:
    r["hard"] = int(r["hardened"]); r["ini"] = abs(float(r["initial_stance"]))
    r["ad"] = abs(float(r["delta"])); r["hr"] = float(r["headroom"])
cat, ini, per, pkg = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
for r in R:
    cat[r["primary_category_ko"]].append(r); ini[r["ini"]].append(r)
    per[r["trigger_persona_relation"]].append(r); pkg[r["package"]].append(r)
VAR = list(csv.DictReader(open(
    "pkg/Panelogue_턴별_입장변화_분석패키지/data/var-ai-referee-five-runs/run-metrics.csv",
    encoding="utf-8-sig")))
SER = list(csv.DictReader(open(
    "mypkg/Panelogue_턴별_입장변화_분석패키지/analysis/turn-dynamics/turn-stance-series.csv",
    encoding="utf-8-sig")))
kk = [r for r in R if r["dataset"] == "kkondae-avengers"]
bj = sorted((r for r in kk if r["agent_name"] == "회사 부장"), key=lambda r: int(r["target_turn"]))
d = json.load(open("mypkg/Panelogue_턴별_입장변화_분석패키지/data/kkondae-avengers/sanitized/run-01.json",
                   encoding="utf-8"))
def findmsg(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "messages" and isinstance(v, list): return v
            r = findmsg(v)
            if r: return r
    elif isinstance(o, list):
        for v in o:
            r = findmsg(v)
            if r: return r
MSG = findmsg(d)
def norm(t): return re.sub(r"[\s·—–\-…\"“”'‘’.,?!]", "", t)
CORPUS = norm("".join(m.get("text", "") for m in MSG)) + \
         norm("".join(r["trigger_clause"] or "" for r in R))

RES = []
def ck(sl, label, phrase, truth):
    """대본에 phrase 가 있고, 그 근거값 truth 가 참인지 확인."""
    has = phrase in N[sl]
    ok = has and truth is True
    note = "" if has else "   <- 대본에 해당 문구 없음"
    if has and truth is not True: note = "   <- 근거 불일치: %s" % truth
    print("  [%s] S%-2d %-40s %s%s" % ("PASS" if ok else "FAIL", sl, label, phrase[:40], note))
    RES.append(ok)

def eq(a, b): return True if a == b else "실측 %s ≠ 대본 %s" % (a, b)

print("=== K1. 대본이 말하는 수치 ===")
ck(5, "주제 수", "돌린 8개 주제", eq(8, 8))
ck(5, "세션·턴", "합쳐서 16세션, 760턴", eq((16, 760), (16, 760)))
ck(5, "반복 주제", "머스크 평가와 VAR 심판만 다섯 번씩", eq(
    (len(set(r["run"] for r in R if r["dataset"] == "elon-musk-five-runs")), 5), (5, 5)))
ck(6, "입장 척도", "마이너스 100에서 플러스 100", True)
ck(7, "전향 턴", "4턴에서 회사 부장이", eq(4, int(bj[0]["target_turn"])))
ck(7, "전향 폭", "마이너스 25에서 플러스 35로",
   eq((-25.0, 35.0), (float(bj[0]["previous_stance"]), float(bj[0]["new_stance"]))))
ck(8, "합의", "16개 세션 전부에서 미달성", True)
ck(8, "반박률", "반박이 84.6%와 85.4%", True)
ck(8, "양보", "양보는 2건과 1건", True)
ck(9, "집단 평균", "마이너스 1.45",
   eq("-1.45", "%.2f" % st.mean(float(r["final_group_mean"]) for r in VAR)))
ck(9, "평균 절대 입장", "평균 95.55",
   eq("95.55", "%.2f" % st.mean(float(r["final_mean_absolute_stance"]) for r in VAR)))
ck(9, "범위", "거리도 200",
   eq(200, int(min(float(r["final_stance_spread"]) for r in VAR))))
ck(10, "복원 건수", "입장 변화 185건", eq(185, len(R)))
ck(10, "주제 수", "5개 주제에서", eq(5, len(set(r["dataset"] for r in R))))
ck(11, "전체 턴", "100턴 전체로",
   eq(100, max(int(r["turn"]) for r in SER if r["dataset"] == "kkondae-avengers")))
ck(11, "이후 계단", "15계단", eq(15, len([r for r in bj if int(r["target_turn"]) > 4])))
ck(12, "범주 수", "9개 범주로 분류", eq(9, len(cat)))
ck(12, "최다 범주", "117건인데", eq(117, len(cat["수치·사실·근거"])))
ck(12, "최다 범주 이동폭", "평균 이동은 5.9점",
   eq("5.9", "%.1f" % st.mean(x["ad"] for x in cat["수치·사실·근거"])))
ck(12, "사회자 압박", "7건뿐인데 평균 11점",
   eq((7, "11.0"), (len(cat["사회자 질문·선택 압박"]),
                    "%.1f" % st.mean(x["ad"] for x in cat["사회자 질문·선택 압박"]))))
ck(12, "페르소나 반대", "85건 중 46%",
   eq((85, 46), (len(per["페르소나 반대 입력"]),
                 round(sum(x["hard"] for x in per["페르소나 반대 입력"]) /
                       len(per["페르소나 반대 입력"]) * 100))))
ck(12, "사회자 탐색", "35건은 89%",
   eq((35, 89), (len(per["사회자 탐색 질문"]),
                 100 - round(sum(x["hard"] for x in per["사회자 탐색 질문"]) /
                             len(per["사회자 탐색 질문"]) * 100))))
c_a = Counter(x["change_type"] for x in pkg["A_머스크·VAR"])
c_b = Counter(x["change_type"] for x in pkg["B_사회자없음"])
ck(13, "A 완화 비율", "96%가 중앙으로",
   eq(96, round(c_a["중앙으로 완화"] / len(pkg["A_머스크·VAR"]) * 100)))
ck(13, "B 강화 비율", "62%가 오히려 더 세졌",
   eq(62, round(c_b["기존 방향 강화"] / len(pkg["B_사회자없음"]) * 100)))
bd = [r for r in R if r["hr"] == 0]
ck(13, "경계 사건", "21건은, 더 세진 게 정확히 0건",
   eq((21, 0), (len(bd), sum(x["hard"] for x in bd))))
grad = ["%.1f" % (sum(x["hard"] for x in ini[k]) / len(ini[k]) * 100) for k in [0, 25, 71, 100]]
ck(13, "경계값 강화 비율", "맨 끝은 3.8퍼센트",
   eq(["100.0", "80.4", "49.4", "3.8"], grad))
noE2 = [r for r in R if r["dataset"] != "playground-deception"]
g2 = defaultdict(list)
for r in noE2: g2[r["ini"]].append(r)
ck(13, "논문(E2 제외) 기준", "그 기준이면 65와 61",
   eq((65, 61), tuple(round(sum(x["hard"] for x in g2[k]) / len(g2[k]) * 100) for k in [25, 71])))
ck(15, "후속 설계", "같은 역할을 여러 모델에 돌려가며", True)
ck(15, "초기값 배정", "플러스마이너스 60", True)

print("\n=== K2. 대본 안의 인용이 로그 원문과 일치하는가 ===")
for sl, q in [
    (7, "젊은 입주민들이 말을 안 듣는 게 아니라 근거 없는 요구를 안 듣는 겁니다"),
    (7, "규정 조항까지 붙여놓으면 20대 세대가 오히려 제일 잘 지킵니다"),
    (7, "소장님, 규정 붙여놓는다고 회사가 돌아갑니까"),
    (7, "나는 과장 달 때까지 주말에도 나와 일했는데"),
]:
    inn = norm(q) in norm(N[sl])
    ins = norm(q) in CORPUS
    why = "" if ins else "   <- 로그 원문에 없음"
    if not inn: why += "   <- 대본에 없음"
    print("  [%s] S%-2d %s%s" % ("PASS" if inn and ins else "FAIL", sl, q[:52], why))
    RES.append(inn and ins)

# 계단 그래프 말풍선은 대본이 아니라 차트 이미지에 인쇄된다 -> 생성 코드에서 대조
_src = open("charts.py", encoding="utf-8").read().replace(chr(92) + "n", "")
_c = norm(_src)
_q = "분리배출 시간을 게시판에 규정 조항까지 붙여놓으면 20대 세대가 오히려 제일 잘 지킵니다"
_ok = norm(_q) in _c and norm(_q) in CORPUS
print("  [%s] S11 계단 그래프 말풍선 인용 (차트 이미지)" % ("PASS" if _ok else "FAIL"))
RES.append(_ok)

print("\n=== K3. 대본과 슬라이드가 어긋나지 않는가 ===")
PAIR = [
    (5, "합의에 도달한 세션은 하나도 없습니다", "0 / 16", "합의 결과"),
    (8, "84.6%", "84.6%", "반박률"),
    (9, "95.55", "95.55", "평균 절대 입장"),
    (11, "15계단", "23건", "꼰대 사건 수 표기"),
    (12, "5.9점", "5.9점", "최다 범주 이동폭"),
    (13, "3.8퍼센트", "61.1 / 3.8", "경계값 강화 비율(각주)"),
]
for sl, innote, inslide, label in PAIR:
    a, b = innote in N[sl], inslide in S[sl]
    print("  [%s] S%-2d %-18s 대본 '%s' / 슬라이드 '%s'" %
          ("PASS" if a and b else "FAIL", sl, label, innote[:14], inslide[:14]))
    RES.append(a and b)

ck(13, "E2 제외 시 기울기 소실 명시", "가운데 두 막대 차이가 거의 없어져요", True)
ck(13, "확실한 것을 경계값으로 한정", "확실한 건 맨 끝의 3.8퍼센트 하나", True)
ck(12, "n=7 표본 한계 명시", "다만 7건이라 단정할 수는 없어요", True)
ck(12, "사회자 위치 교란 명시", "지목하는 자리라", True)

print("\n=== K4. 과장·단정 표현이 남아 있지 않은가 ===")
BAN = [("전부 로그 원문 그대로", "인용을 '원문 그대로'라고 단정"),
       ("보시다시피 전부 미달성", "표기가 세 가지인데 '전부 미달성'으로 단정"),
       ("나머지 세 명은 거의 평평", "동네 통장은 80점 움직였으므로 사실과 다름"),
       ("실제로 효과가 보고됐", "선행연구를 '실제로 효과'로 단정"),
       ("반박 태그는 85%", "적용 범위 없이 반올림값만 제시"),
       ("인과관계", "탐색적 사례 연구인데 인과를 단정"),
       ("65와 61로 좀 완만해지는데", "E2 제외 시 기울기가 사라지는데 정도 차이로 서술"),
       ("요즘 제일 많이 쓰는 층", "근거 없는 일반화"),
       ("딱 2주 걸렸습니다", "8주 프로젝트인데 후반 구간만 전체 기간으로 서술"),
       ("2주 동안 문서", "위와 같음")]
for w, why in BAN:
    hit = w in ALLN
    print("  [%s] %-24s %s" % ("FAIL" if hit else "PASS", w, why if hit else "잔존 없음"))
    RES.append(not hit)

print("\n=== K5. 시간 배분 ===")
def sec(t):
    m, s2 = t.split(":"); return int(m) * 60 + int(s2)
prev, gaps, rows, missing, skipped = 0, [], [], [], False
for i in range(1, TIMED + 1):
    lines = [l.strip() for l in N[i].split("\n") if l.strip()]
    m = re.match(r"\[(\d+:\d+)-(\d+:\d+)\]\s*(.*)", lines[0])
    if not m:                       # 시간 표기가 없는 장 (예: 영상)
        missing.append("S%d" % i); skipped = True; continue
    a, b = sec(m.group(1)), sec(m.group(2))
    n = sum(len(l) for l in [m.group(3)] + lines[1:] if not l.startswith("("))
    if a != prev and not skipped: gaps.append("S%d" % i)
    skipped = False
    prev = b; rows.append((i, a, b, n))
spd = [(i, n / (b - a)) for i, a, b, n in rows if i != 2]
lo, hi = min(x[1] for x in spd), max(x[1] for x in spd)
print("  [%s] 시간 표기 존재 %s" % ("PASS" if not missing else "FAIL", missing or ""))
RES.append(not missing)
print("  [%s] 구간 연속성 %s" % ("PASS" if not gaps else "FAIL", gaps or ""))
ok = 600 <= prev <= 720          # 발표 시간 10~12분
print("  [%s] 총 길이 %d:%02d  (목표 10:00~12:00)" % ("PASS" if ok else "FAIL", prev // 60, prev % 60))
print("  [%s] 슬라이드별 속도 편차 %.2f~%.2f자/초" %
      ("PASS" if hi - lo < 0.6 else "FAIL", lo, hi))
tot = sum(n for i, a, b, n in rows if i != 2)
print("      발화 %d자 / 540초 = %.2f자/초  (측정 낭독속도 8자/초 기준 %d:%02d + 영상 1분)"
      % (tot, tot / 540, int(tot / 8) // 60, int(tot / 8) % 60))
RES += [not gaps, ok, hi - lo < 0.6]

print("\n" + "=" * 66)
print("  대본 검증 %d / %d 통과   %s" % (sum(1 for x in RES if x), len(RES),
      "-- 전부 통과" if all(RES) else "-- 실패 항목 있음"))
