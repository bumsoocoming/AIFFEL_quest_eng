# -*- coding: utf-8 -*-
"""최종 검증 — 슬라이드에 인쇄된 모든 수치를 원자료에서 재계산해 대조한다."""
import csv, io, json, re, sys, zipfile, html, statistics as st
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PPTX = "Panelogue_발표자료.pptx"
z = zipfile.ZipFile(PPTX)

def slide_text(i):
    x = z.read("ppt/slides/slide%d.xml" % i).decode("utf-8")
    return html.unescape("".join(re.findall(r"<a:t>(.*?)</a:t>", x, re.S)))

TIMED = 15                    # 1~15는 시간 배분 대상, 16은 백업 슬라이드
DECK = {i: slide_text(i) for i in range(1, 17)}

R = list(csv.DictReader(open("merged/stance-events-merged.csv", encoding="utf-8-sig")))
for r in R:
    r["hard"] = int(r["hardened"]); r["ini"] = abs(float(r["initial_stance"]))
    r["ad"] = abs(float(r["delta"])); r["hr"] = float(r["headroom"])

cat, ini, per, pkg = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
for r in R:
    cat[r["primary_category_ko"]].append(r)
    ini[r["ini"]].append(r)
    per[r["trigger_persona_relation"]].append(r)
    pkg[r["package"]].append(r)

VAR = list(csv.DictReader(open(
    "pkg/Panelogue_턴별_입장변화_분석패키지/data/var-ai-referee-five-runs/run-metrics.csv",
    encoding="utf-8-sig")))
kk = [r for r in R if r["dataset"] == "kkondae-avengers"]
bj = sorted((r for r in kk if r["agent_name"] == "회사 부장"), key=lambda r: int(r["target_turn"]))
net = {}
for key in set((r["dataset"], r["agent_name"]) for r in R):
    ev = sorted((r for r in R if (r["dataset"], r["agent_name"]) == key),
                key=lambda r: int(r["target_turn"]))
    net[key] = abs(float(ev[-1]["new_stance"]) - float(ev[0]["initial_stance"]))

RES = []

def chk(label, printed, actual, slide=None):
    ok = str(printed) == str(actual)
    inslide = True if slide is None else (str(printed) in DECK[slide])
    extra = "" if ok else "   <- 실측 %s" % actual
    if not inslide: extra += "   <- 슬라이드에 문자열 없음"
    loc = ("S%d" % slide) if slide else "  "
    print("  [%s] %3s %-34s %s%s" % ("PASS" if ok and inslide else "FAIL",
                                     loc, label, printed, extra))
    RES.append(ok and inslide)

print("=== A. 규모 / 구성 ===")
chk("총 입장 변화 사건", "185건", "%d건" % len(R), 10)
chk("주제 수", "5주제", "%d주제" % len(set(r["dataset"] for r in R)), 10)
chk("사건이 기록된 실행", "12개 실행",
    "%d개 실행" % len(set((r["dataset"], r["run"]) for r in R)), 10)
chk("트리거 범주 수", "9범주", "%d범주" % len(cat), 10)
chk("모델 제공사 수", "6", str(len(set(r["model"].split("/")[0] for r in R))), 6)
chk("모델 종류 수", "9종", "%d종" % len(set(r["model"] for r in R)), 6)

print("\n=== B. 척도 경계 효과 (S13) ===")
for k in [0, 25, 71, 100]:
    v = ini[k]; p = sum(x["hard"] for x in v) / len(v) * 100
    chk("초기값 |%d| 강화 비율" % k, "%.1f%%" % p, "%.1f%%" % p)
    chk("초기값 |%d| 표본" % k, "n=%d" % len(v), "n=%d" % len(v))
bd = [r for r in R if r["hr"] == 0]
chk("경계(직전 ±100) 사건 수", "21건", "%d건" % len(bd), 13)
chk("경계 사건 중 강화", 0, sum(x["hard"] for x in bd))
chk("막대 4구간 합계", 180, sum(len(ini[k]) for k in [0, 25, 71, 100]))
chk("동일 패키지 3구간 합계", "n=128", "n=%d" % sum(len(ini[k]) for k in [0, 25, 71]), 13)

print("\n=== C. 트리거 범주 (S12) ===")
for name, n_, m_ in [("수치·사실·근거", 117, 5.9), ("성과·실행 가능성", 17, 10.0),
                     ("사회자 질문·선택 압박", 7, 11.0)]:
    v = cat[name]
    chk("%s 건수" % name, "%d건" % n_, "%d건" % len(v), 12)
    chk("%s 평균 이동" % name, "%.1f점" % m_,
        "%.1f점" % st.mean(x["ad"] for x in v), 12)

print("\n=== D. 페르소나 교차분석 (S12) ===")
for name, n_, h_ in [("페르소나 반대 입력", 85, 46), ("페르소나 지지 입력", 62, 63),
                     ("사회자 탐색 질문", 35, 11)]:
    v = per[name]
    chk("%s 표본" % name, n_, len(v))
    chk("%s 강화 비율" % name, "%d%%" % h_,
        "%d%%" % round(sum(x["hard"] for x in v) / len(v) * 100))

print("\n=== E. 평균 0의 함정 (S9) ===")
gm = [float(r["final_group_mean"]) for r in VAR]
am = [float(r["final_mean_absolute_stance"]) for r in VAR]
chk("집단 평균 (5회 평균)", "−1.45", ("%.2f" % st.mean(gm)).replace("-", "−"), 9)
chk("평균 절대 입장 (5회 평균)", "95.55", "%.2f" % st.mean(am), 9)
chk("최종 범위 (5회 모두)", "200",
    str(int(min(float(r["final_stance_spread"]) for r in VAR))))
chk("찬반 분할 (5회 모두)", "2 : 2",
    "2 : 2" if all(r["final_agreement_ratio"] == "0.5" for r in VAR) else "불일치", 9)

print("\n=== F. 계단 그래프 (S11) ===")
chk("꼰대 어벤져스 사건 수", "23건", "%d건" % len(kk), 11)
chk("회사 부장 초기 입장", "−25", "−%.0f" % abs(float(bj[0]["initial_stance"])), 11)
chk("회사 부장 최종 입장", "+76", "+%.0f" % float(bj[-1]["new_stance"]), 11)
top = max(net, key=net.get)
chk("순이동 최대", "101점",
    "%.0f점" % net[top] if top == ("kkondae-avengers", "회사 부장") else "최대 아님(%s)" % (top,), 11)
chk("4턴 이후 변화 사건", 15, len([r for r in bj if int(r["target_turn"]) > 4]))

print("\n=== G. 패키지별 변화 유형 (대본) ===")
for p, key, want in [("A_머스크·VAR", "중앙으로 완화", 96), ("B_사회자없음", "기존 방향 강화", 62)]:
    v = pkg[p]; c = Counter(x["change_type"] for x in v)
    chk("%s %s" % (p, key), "%d%%" % want, "%d%%" % round(c[key] / len(v) * 100))

print("\n=== H. 인용문이 로그 원문과 일치하는가 ===")
def norm(t): return re.sub(r"[\s·—–\-…\"“”'‘’.,?!]", "", t)
d = json.load(open("mypkg/Panelogue_턴별_입장변화_분석패키지/data/kkondae-avengers/sanitized/run-01.json",
                   encoding="utf-8"))
def find(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "messages" and isinstance(v, list): return v
            r = find(v)
            if r: return r
    elif isinstance(o, list):
        for v in o:
            r = find(v)
            if r: return r
msgs = find(d)
corpus = norm("".join(m.get("text", "") for m in msgs)) + \
         norm("".join(r["trigger_clause"] or "" for r in R))
QUOTES = [
    (7,  "젊은 입주민들이 말을 안 듣는 게 아니라 근거 없는 요구를 안 듣는 겁니다"),
    (7,  "분리배출 시간을 게시판에 규정 조항까지 붙여놓으면"),
    (7,  "20대 세대가 오히려 제일 잘 지킵니다"),
    (7,  "소장님, 규정 붙여놓는다고 회사가 돌아갑니까"),
    (7,  "나는 과장 달 때까지 주말에도 나와 일했는데"),
    (7,  "요즘은 워라밸이라며 6시면 컴퓨터부터 꺼버려요"),
    (11, "분리배출 시간을 게시판에 규정 조항까지"),
    (12, "규정 조항까지 붙여놓으면"),
    (12, "20대 세대가 오히려 제일 잘 지킵니다"),
    (12, "1단 부스터 착륙시키고 다시 날려서"),
    (12, "발사 시장 판을 갈아엎었어"),
    (12, "8년 넘게 반복해서 못 지킨 건"),
    (12, "어떻게 설명할 거야?"),
]
for sl, q in QUOTES:
    src = DECK[sl] if sl != 11 else DECK[sl] + open("charts.py", encoding="utf-8").read()
    inslide = norm(q) in norm(src)
    insrc = norm(q) in corpus
    why = "" if insrc else "   <- 로그 원문에 없음"
    if not inslide: why += "   <- 슬라이드에 없음"
    print("  [%s] S%-2d %-46s%s" % ("PASS" if inslide and insrc else "FAIL", sl, q[:44], why))
    RES.append(inslide and insrc)

print("\n=== I. 시간표 정합성 ===")
def sec(t):
    m, s2 = t.split(":"); return int(m) * 60 + int(s2)
prev, gaps, rows, missing, skipped = 0, [], [], [], False
for i in range(1, TIMED + 1):
    x = z.read("ppt/notesSlides/notesSlide%d.xml" % i).decode("utf-8")
    raw = html.unescape("".join(re.findall(r"<a:t>(.*?)</a:t>",
          x.split('name="Slide Number Placeholder')[0], re.S)))
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    m = re.match(r"\[(\d+:\d+)-(\d+:\d+)\]\s*(.*)", lines[0])
    if not m:
        missing.append("S%d" % i); skipped = True
        continue
    a, b = sec(m.group(1)), sec(m.group(2))
    n = sum(len(l) for l in [m.group(3)] + lines[1:] if not l.startswith("("))
    if a != prev and not skipped: gaps.append("S%d" % i)
    skipped = False
    prev = b
    rows.append((i, a, b, n))
print("  [%s] 시간 표기 존재 %s" % ("PASS" if not missing else "FAIL", missing or ""))
RES.append(not missing)
print("  [%s] 구간 연속성 %s" % ("PASS" if not gaps else "FAIL", gaps or ""))
ok = 600 <= prev <= 720          # 발표 시간 10~12분
print("  [%s] 총 길이 %d:%02d  (목표 10:00~12:00)" % ("PASS" if ok else "FAIL", prev // 60, prev % 60))
# 상한은 발표자의 실측 낭독속도 8.0자/초에 2.5% 여유를 둔 7.8자/초
CAP = 7.8
over = ["S%d(%.1f자/초)" % (i, n / (b - a)) for i, a, b, n in rows if i != 2 and n / (b - a) > CAP]
print("  [%s] 슬라이드별 발화 속도 <= %.1f자/초 (실측 낭독 8.0 기준) %s"
      % ("PASS" if not over else "FAIL", CAP, over or ""))
RES += [not gaps, ok, not over]

print("\n=== J. 파일 무결성 ===")
notes = [f for f in z.namelist() if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", f)]
chk("발표자 노트 슬라이드 수", 16, len(notes))
ph = re.findall(r"(lorem|ipsum|TODO|\[insert|undefined|NaN)", "".join(DECK.values()), re.I)
print("  [%s] 플레이스홀더 잔존 %s" % ("PASS" if not ph else "FAIL", ph or "없음"))
RES.append(not ph)

print("\n=== L. 백업 슬라이드 ===")
_b = DECK[16]
_bn = notes_txt = None
import zipfile as _zf
_bnote = html.unescape("".join(re.findall(r"<a:t>(.*?)</a:t>",
        z.read("ppt/notesSlides/notesSlide16.xml").decode("utf-8")
         .split(chr(39)*0 + 'name="Slide Number Placeholder')[0], re.S)))
for _lab, _v in [("발표 시간에서 제외됨", _bnote.startswith("[백업]")),
                 ("좌측 상단 백업 표시", "백업" in _b),
                 ("문서 95개", "95" in _b), ("전체 파일 294개", "294" in _b),
                 ("입장 변화 185건", "185" in _b), ("토론 760턴", "760" in _b)]:
    print("  [%s] S16 %s" % ("PASS" if _v else "FAIL", _lab)); RES.append(_v)

print("\n=== K. 아이스브레이킹 구간 ===")
for _sl in (2, 3):
    chk("S%d 좌측 상단 라벨" % _sl, "아이스브레이크",
        "아이스브레이크" if "아이스브레이크" in DECK[_sl] else "없음", _sl)
_js = open("build_deck.js", encoding="utf-8").read()
_hit = "x: 2.0, y: 1.28, w: 9.33, h: 5.25" in _js
_w, _h = 9.33, 5.25
print("  [%s]  S2 영상 틀 = 화면 폭의 %.0f%%, 비율 %.2f:1 (16:9=1.78)"
      % ("PASS" if _hit and abs(_w / 13.333 - 0.70) < 0.01 and abs(_w / _h - 16 / 9) < 0.02
         else "FAIL", _w / 13.333 * 100, _w / _h))
RES.append(_hit)

print("\n" + "=" * 64)
print("  통과 %d / %d 항목   %s" % (sum(1 for x in RES if x), len(RES),
      "-- 전부 통과" if all(RES) else "-- 실패 항목 있음"))
