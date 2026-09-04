# -*- coding: utf-8 -*-
"""Panelogue 통합 분석 보고서 PDF"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, Image)

pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBd", r"C:\Windows\Fonts\malgunbd.ttf"))
registerFontFamily("Malgun", normal="Malgun", bold="MalgunBd",
                   italic="Malgun", boldItalic="MalgunBd")

SLATE = colors.HexColor("#1e293b"); CYAN = colors.HexColor("#0891b2")
LIGHT = colors.HexColor("#f1f5f9"); GREY = colors.HexColor("#64748b")
INK = colors.HexColor("#1e293b"); RED = colors.HexColor("#e11d48")
BLUE = colors.HexColor("#2563eb"); GREEN = colors.HexColor("#16a34a")
GOLD = colors.HexColor("#d4a017")

PAGE_W, PAGE_H = A4
CW = PAGE_W - 40*mm
SC = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\hjbs5\OneDrive\Desktop\아이펠톤(인간시대)\새 폴더\Panelogue_통합분석_보고서.pdf"
img = lambda f: os.path.join(SC, "merged", "charts", f)


def st_(n, **kw):
    b = dict(fontName="Malgun", fontSize=10, leading=16.5, textColor=INK); b.update(kw)
    return ParagraphStyle(n, **b)

S = {
    "h2": st_("h2", fontName="MalgunBd", fontSize=12.5, leading=19, textColor=SLATE,
              spaceBefore=10, spaceAfter=6),
    "body": st_("body", spaceAfter=6),
    "small": st_("small", fontSize=8.5, leading=13, textColor=GREY),
    "cell": st_("cell", fontSize=9, leading=13.5),
    "cellsm": st_("cellsm", fontSize=8.3, leading=12.4),
    "cellc": st_("cellc", fontSize=9, leading=13.5, alignment=TA_CENTER),
    "hcell": st_("hcell", fontName="MalgunBd", fontSize=8.8, leading=13,
                 textColor=colors.white, alignment=TA_CENTER),
    "cap": st_("cap", fontSize=8.8, leading=13, textColor=GREY, alignment=TA_CENTER, spaceBefore=4),
    "kpin": st_("kpin", fontName="MalgunBd", fontSize=17, leading=22, textColor=SLATE, alignment=TA_CENTER),
    "kpit": st_("kpit", fontSize=8.3, leading=12, textColor=GREY, alignment=TA_CENTER),
}
P = lambda t, s="body": Paragraph(t, S[s])
hexs = lambda c: "#" + c.hexval()[2:]


def sect(no, title, sub=""):
    num = Paragraph(f'<font color="#1e293b"><b>{no}</b></font>',
                    st_("sn", fontName="MalgunBd", fontSize=15, leading=20, alignment=TA_CENTER))
    m = f'<font color="white"><b>{title}</b></font>'
    if sub: m += f'<br/><font color="#94a3b8" size="8.5">{sub}</font>'
    t = Table([[num, Paragraph(m, st_("stt", fontName="MalgunBd", fontSize=14, leading=19,
                                      textColor=colors.white))]], colWidths=[13*mm, CW-13*mm])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (0,0), CYAN), ("BACKGROUND", (1,0), (1,0), SLATE),
                           ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (1,0), (1,0), 10),
                           ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    return [t, Spacer(1, 9)]


def fimg(f, ratio, cap=None):
    o = [Image(img(f), width=CW, height=CW*ratio)]
    if cap: o.append(P(cap, "cap"))
    return o


def note(text, color=CYAN, bg="#ecfeff"):
    t = Table([[P(text, "cell")]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor(bg)),
                           ("LINEBEFORE", (0,0), (0,-1), 2.5, color),
                           ("BOX", (0,0), (-1,-1), .5, colors.HexColor("#cbd5e1")),
                           ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
                           ("LEFTPADDING", (0,0), (-1,-1), 9), ("RIGHTPADDING", (0,0), (-1,-1), 9)]))
    return [t, Spacer(1, 7)]


def tbl(rows, widths, header=True):
    t = Table(rows, colWidths=widths)
    sty = [("GRID", (0,0), (-1,-1), .5, colors.HexColor("#cbd5e1")),
           ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
           ("TOPPADDING", (0,0), (-1,-1), 4.5), ("BOTTOMPADDING", (0,0), (-1,-1), 4.5),
           ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5)]
    if header:
        sty += [("BACKGROUND", (0,0), (-1,0), SLATE),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT])]
    t.setStyle(TableStyle(sty))
    return t


def cover(cv):
    cv.saveState()
    cv.setFillColor(SLATE); cv.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    cv.setStrokeColor(CYAN); cv.setLineWidth(1.4); cv.setStrokeAlpha(.20)
    x, y = 20*mm, PAGE_H-200*mm
    for s in [0, 14, -6, 20, 10, -4, 16, 8, 12]:
        nx = x + 17*mm
        cv.line(x, y, nx, y); cv.line(nx, y, nx, y+s*mm); x, y = nx, y+s*mm
    cv.setStrokeAlpha(1)
    cv.setStrokeColor(CYAN); cv.setLineWidth(2)
    cv.line(25*mm, PAGE_H-52*mm, PAGE_W-25*mm, PAGE_H-52*mm)
    cv.setLineWidth(.7); cv.line(25*mm, PAGE_H-53.5*mm, PAGE_W-25*mm, PAGE_H-53.5*mm)
    cv.setFillColor(CYAN); cv.setFont("MalgunBd", 11.5)
    cv.drawCentredString(PAGE_W/2, PAGE_H-44*mm, "Panelogue 턴별 입장 변화 · 두 패키지 통합 분석")
    cv.setFillColor(colors.white); cv.setFont("MalgunBd", 25)
    cv.drawCentredString(PAGE_W/2, PAGE_H-70*mm, "'대부분 완화된다'는 결론은")
    cv.drawCentredString(PAGE_W/2, PAGE_H-82*mm, "초기값 설계의 산물이었다")
    cv.setFont("Malgun", 10.5); cv.setFillColor(colors.HexColor("#94a3b8"))
    cv.drawCentredString(PAGE_W/2, PAGE_H-95*mm,
                         "A 머스크·VAR 52건 + B 사회자 없는 3주제 133건 = 총 185건 · 5주제 · 13개 실행")
    kk = [("185건", "통합 입장 변화 사건"), ("5주제", "13개 실행 / 600턴"),
          ("0%", "경계 고착 21건의 강화율"), ("동일", "코드북·스크립트")]
    bw, gap = 40*mm, 3*mm
    x0 = (PAGE_W-(bw*4+gap*3))/2; y0 = PAGE_H-134*mm
    for i, (n, l) in enumerate(kk):
        x = x0 + i*(bw+gap)
        cv.setFillColor(colors.HexColor("#334155")); cv.roundRect(x, y0, bw, 24*mm, 2.5*mm, stroke=0, fill=1)
        cv.setFillColor(CYAN); cv.rect(x, y0+22*mm, bw, 2*mm, stroke=0, fill=1)
        cv.setFillColor(colors.white); cv.setFont("MalgunBd", 15)
        cv.drawCentredString(x+bw/2, y0+13*mm, n)
        cv.setFillColor(colors.HexColor("#94a3b8")); cv.setFont("Malgun", 7.6)
        cv.drawCentredString(x+bw/2, y0+6.5*mm, l)
    cv.saveState(); cv.translate(PAGE_W/2, 74*mm)
    cv.setStrokeColor(CYAN); cv.setLineWidth(1.6)
    cv.roundRect(-76*mm, -14*mm, 152*mm, 28*mm, 3*mm, stroke=1, fill=0)
    cv.setFillColor(colors.white); cv.setFont("MalgunBd", 11.5)
    cv.drawCentredString(0, 4*mm, "초기값 |0|→|25|→|71|→|100| 에서 강화율은")
    cv.setFillColor(CYAN); cv.setFont("MalgunBd", 13)
    cv.drawCentredString(0, -6*mm, "100% → 80% → 49% → 4% 로 단조 감소한다")
    cv.restoreState()
    cv.setStrokeColor(CYAN); cv.setLineWidth(.7); cv.line(25*mm, 46*mm, PAGE_W-25*mm, 46*mm)
    cv.setFillColor(colors.HexColor("#94a3b8")); cv.setFont("Malgun", 9.5)
    cv.drawCentredString(PAGE_W/2, 38*mm, "작성일: 2026년 9월 1일 · 분석엔진 analyze_turn_dynamics.py(팀원 제작) 무수정 적용")
    cv.drawCentredString(PAGE_W/2, 32*mm, "아이펠톤 프로젝트 〈인간시대〉 · Panelogue 팀")
    for i, c in enumerate([RED, BLUE, CYAN, GREEN]):
        cv.setFillColor(c); cv.rect(i*(PAGE_W/4), 0, PAGE_W/4, 4*mm, stroke=0, fill=1)
    cv.restoreState()


def page(cv, doc):
    if doc.page == 1:
        cover(cv); return
    cv.saveState()
    cv.setFillColor(GREY); cv.setFont("Malgun", 8)
    cv.drawString(20*mm, PAGE_H-12*mm, "Panelogue 두 패키지 통합 분석 보고서")
    cv.drawRightString(PAGE_W-20*mm, PAGE_H-12*mm, "185건 · 5주제")
    cv.setStrokeColor(CYAN); cv.setLineWidth(1)
    cv.line(20*mm, PAGE_H-14*mm, PAGE_W-20*mm, PAGE_H-14*mm)
    cv.setFillColor(GREY); cv.drawCentredString(PAGE_W/2, 11*mm, f"- {doc.page-1} -")
    for i, c in enumerate([RED, BLUE, CYAN, GREEN]):
        cv.setFillColor(c); cv.rect(i*(PAGE_W/4), 0, PAGE_W/4, 1.6*mm, stroke=0, fill=1)
    cv.restoreState()


doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm,
                        topMargin=22*mm, bottomMargin=20*mm,
                        title="Panelogue 통합 분석 보고서", author="Panelogue 팀")
story = [PageBreak()]

# ═══ 01 통합 개요 ═══
story += sect("01", "통합 개요", "두 패키지를 왜, 어떻게 합쳤나")
story += [P("Panelogue 턴별 입장 변화 분석은 지금까지 두 벌 만들어졌다. 두 패키지는 "
            "<b>동일한 분석 스크립트(analyze_turn_dynamics.py)와 동일한 코드북 v1</b>을 사용했으므로 "
            "트리거 카테고리와 반응 패턴 라벨이 그대로 호환된다. 따라서 별도 매핑 없이 185건을 한 표에 놓을 수 있다.")]

rows = [[P("구분", "hcell"), P("A 패키지", "hcell"), P("B 패키지", "hcell")],
        [P("<b>주제</b>", "cell"), P("일론 머스크 평가 · VAR·AI 심판", "cellsm"),
         P("세계 평화 정상 대토론 · 꼰대 어벤져스 · 운동장 대토론", "cellsm")],
        [P("<b>실행 구조</b>", "cell"), P("2주제 × 5회 반복 = 10런", "cellsm"), P("3주제 × 1회 = 3런", "cellsm")],
        [P("<b>초기 입장</b>", "cell"), P(f'<font color="{hexs(RED)}"><b>±100 (척도 경계)</b></font>', "cellsm"),
         P(f'<font color="{hexs(BLUE)}"><b>+71 / −71 / 0 / −25</b></font>', "cellsm")],
        [P("<b>사회자</b>", "cell"), P("있음 — 트리거의 63%(33/52)", "cellsm"), P("없음 — 전원 패널 발언", "cellsm")],
        [P("<b>입장 변화 사건</b>", "cell"), P("52건", "cellc"), P("133건", "cellc")],
        [P("<b>강화 방향 변화</b>", "cell"), P("2건 (3.8%)", "cellc"), P("83건 (62.4%)", "cellc")],
        [P("<b>극성 전환</b>", "cell"), P("0건", "cellc"), P("2건", "cellc")]]
story += [tbl(rows, [30*mm, (CW-30*mm)/2, (CW-30*mm)/2]), Spacer(1, 9)]

story += note("<b>통합의 목적</b><br/>두 패키지는 같은 도구로 만들어졌지만 결과가 정반대다. A는 변화의 96%가 "
              "'중앙으로 완화'였고, B는 62%가 '기존 방향 강화'였다. 이 차이가 <b>토론의 성질</b>인지 "
              "<b>초기값 설계의 산물</b>인지 가르는 것이 본 통합 분석의 목적이다.", GOLD, "#fdf6ec")
story += [PageBreak()]

# ═══ 02 핵심 검정 ═══
story += sect("02", "핵심 검정", "강화는 왜 A에서 사라졌나")
story += [P("<b>가설</b> — 입장 지수는 ±100으로 제한된 척도다. 직전 입장이 이미 ±100이면 "
            "|입장|을 더 키울 수 없으므로 <b>'강화'가 수학적으로 불가능</b>하다. "
            "이를 정량화하기 위해 <b>강화 여지(headroom) = 100 − |직전 입장|</b> 을 정의했다.")]
story += fimg("M2_headroom_vs_hardening.png", 3.9/9.2,
              "그림 1. headroom이 0인 21건은 전부 A패키지이며, 강화율이 정확히 0%다. "
              "headroom이 생기는 순간 강화율은 42~65%로 뛴다.")
story += [PageBreak()]
story += [P("<b>더 강한 근거 — 패키지 교란이 없는 내부 비교</b>", "h2")]
story += [P("초기값 |0|, |25|, |71| 은 <b>모두 B패키지 안에 있다</b>. 즉 패키지·사회자·주제 차이 없이 "
            "초기값만 다른 조건인데, 여기서도 강화율이 단조 감소한다.")]
story += fimg("M1_initial_vs_hardening.png", 3.9/9.2,
              "그림 2. |초기값| 0→25→71→100에서 강화율 100% → 80.4% → 49.4% → 3.8%. "
              "앞의 세 구간은 모두 B패키지 내부이므로 패키지 교란이 없다.")
story += note("<b>1차 결론</b><br/>척도 경계 효과는 <b>실재한다</b>. A패키지에서 관찰된 '변화의 96%가 완화'라는 "
              "패턴은 토론의 성질이라기보다 <b>±100 초기값이 강화 방향을 사전에 차단한 결과</b>로 보는 것이 "
              "타당하다. 따라서 이 수치를 '멀티에이전트 토론은 대체로 입장을 누그러뜨린다'는 근거로 "
              "인용해서는 안 된다.", GREEN, "#f0fdf4")
story += [PageBreak()]

# ═══ 03 그러나 ═══
story += sect("03", "그러나 — 초기값만으로는 부족하다", "층화 후에도 남는 격차")
story += [P("초기값 효과가 확인됐다고 해서 두 패키지 차이가 전부 설명되는 것은 아니다. "
            "headroom이 <b>같은 구간</b>에 속한 사건만 골라 다시 비교하면 격차가 여전히 남는다.")]
story += fimg("M3_stratified_comparison.png", 3.6/9.2,
              "그림 3. headroom 10~30 구간에서 A는 26건 중 강화 0건(0%), B는 41건 중 28건(68.3%). "
              "강화가 가능한 여지가 같았는데도 결과가 갈렸다.")
story += [Spacer(1, 4)]
story += [P("<b>잔차의 후보 요인 — 모두 A/B와 완전히 교란</b>", "h2")]
rows = [[P("요인", "hcell"), P("headroom 10~30 구간 내 분포", "hcell"), P("분리 가능?", "hcell")],
        [P("<b>사회자</b>", "cell"), P("있음 0/26 강화 · 없음 28/41 강화", "cellsm"),
         P("불가 — 사회자는 A에만 존재", "cellsm")],
        [P("<b>주제</b>", "cell"), P("머스크 0/23 · 운동장 13/22 · 꼰대 10/13 · 평화 5/6 · VAR 0/3", "cellsm"),
         P("불가 — 주제가 패키지에 종속", "cellsm")],
        [P("<b>모델</b>", "cell"), P("gpt-5.5 0/15 · claude-opus-5 10/10 · grok-4.20 7/28", "cellsm"),
         P("불가 — 모델·페르소나 고정 결합", "cellsm")],
        [P("<b>반복 횟수</b>", "cell"), P("A는 5회 반복, B는 1회", "cellsm"),
         P("불가 — 설계 자체가 다름", "cellsm")]]
story += [tbl(rows, [24*mm, CW-24*mm-38*mm, 38*mm]), Spacer(1, 9)]
story += note("<b>2차 결론</b><br/>초기값 경계 효과는 A의 극단적 결과(3.8%)를 상당 부분 설명하지만, "
              "<b>전부 설명하지는 못한다</b>. 남은 격차는 사회자 유무·주제·모델·반복 설계와 완전히 교란되어 "
              "본 자료로는 원인을 분리할 수 없다. 이것이 바로 논문 §7이 제안한 "
              "<b>4×4 라틴 스퀘어 + 초기값 ±60 대칭 배정</b>이 필요한 이유다. 두 패키지의 통합은 "
              "그 필요성을 <b>사후 데이터로 뒷받침</b>하는 데까지가 한계다.", RED, "#fef2f2")
story += [PageBreak()]

# ═══ 04 코드북 핵심 질문 ═══
story += sect("04", "코드북 §4 핵심 질문의 복원", "부정당하면 반발하는가")
story += [P("코드북 §4는 <b>\u201c기존 페르소나를 부정하는 말을 들었을 때 입장을 바꾸는가, 오히려 더 강하게 "
            "반발하는가\u201d</b>를 직접 비교하겠다고 선언한다. 그러나 A패키지 단독으로는 이 비교가 성립하지 "
            "않았다 — '반발·페르소나 재강화' 칸이 <b>0건</b>이었기 때문이다(초기값이 ±100이라 반발할 여지가 없었다).")]
rows = [[P("자료", "hcell"), P("반대 입력 사건", "hcell"), P("수용·완화", "hcell"),
         P("반발·재강화", "hcell"), P("판정", "hcell")],
        [P("A 머스크·VAR", "cell"), P("15", "cellc"), P("15", "cellc"), P("<b>0</b>", "cellc"),
         P(f'<font color="{hexs(RED)}">검정 불가</font>', "cellsm")],
        [P("B 사회자 없음", "cell"), P("70", "cellc"), P("50", "cellc"), P("<b>18</b>", "cellc"),
         P("수용 74%", "cellsm")],
        [P("<b>통합</b>", "cell"), P("<b>85</b>", "cellc"), P("<b>65</b>", "cellc"), P("<b>18</b>", "cellc"),
         P(f'<font color="{hexs(GREEN)}"><b>수용 78%</b></font>', "cellsm")]]
story += [tbl(rows, [34*mm, 26*mm, 24*mm, 26*mm, CW-110*mm]), Spacer(1, 9)]
story += [P("B패키지가 합류하면서 <b>코드북이 정의한 여섯 반응 패턴이 모두 관측</b>됐다(A 단독 4개). "
            "통합 85건 기준으로는 자기 전제를 부정당했을 때 <b>약 4건 중 3건이 상대 방향으로 완화</b>했고, "
            "나머지 1건이 반발로 굳었다. 다만 이 비율 역시 초기값 분포에 영향을 받으므로 "
            "고정된 상수로 인용해서는 안 된다.")]
story += [Spacer(1, 4)]
story += fimg("M4_trigger_categories_merged.png", 4.2/9.2,
              "그림 4. 트리거 카테고리별 통합 집계. 두 패키지가 같은 코드북을 써서 직접 합산이 가능하다. "
              "'수치·사실·근거'가 117건(63%)으로 압도적이며, A17 / B100으로 B에 편중돼 있다.")
story += [PageBreak()]

# ═══ 05 주제·모델 ═══
story += sect("05", "주제별·모델별 분포", "해석보다 경고가 필요한 구간")
story += fimg("M5_topics_overview.png", 3.8/9.6,
              "그림 5. 5개 주제의 사건 수와 강화 비율. 빨강 A패키지, 파랑 B패키지. "
              "강화 비율이 패키지 경계를 따라 정확히 갈린다(A 0~5% vs B 52~87%).")
story += [Spacer(1, 6)]
story += fimg("M6_model_warning.png", 4.0/9.2,
              "그림 6. 모델별 강화 비율. 회색은 표본 10건 미만.")
story += note("<b>모델 해석 금지</b><br/>표에서 claude-opus-5가 79%, gpt-5.5가 0%로 보이지만 이를 "
              "<b>모델 성격으로 읽으면 안 된다</b>. gpt-5.5는 A패키지 단일 주제에서 초기값 +100으로만 등장했고 "
              "(강화 자체가 불가능), claude-opus-5는 B패키지 3주제에서 초기값 −25·−71로 등장했다. "
              "모델·페르소나·주제·초기값이 한 덩어리로 묶여 있어 어떤 축의 효과인지 알 수 없다. "
              "논문 §5.4가 지적한 <b>\u201c모델 성격이 아니라 모델–역할–프롬프트 상호작용\u201d</b>이 그대로 적용된다.",
              RED, "#fef2f2")
story += [PageBreak()]

# ═══ 06 결론 ═══
story += sect("06", "결론 및 논문 반영 제안", "무엇을 쓸 수 있고 무엇을 쓸 수 없나")
story += [P("<b>말할 수 있는 것</b>", "h2")]
story += [P("① <b>척도 경계 효과가 실재한다.</b> B패키지 내부에서 초기값 |0|→|25|→|71| 에 따라 "
            "강화율이 100%→80.4%→49.4%로 단조 감소했다. 패키지·사회자·주제 교란이 없는 비교다.")]
story += [P("② <b>A패키지의 '완화 96%'는 발견이 아니라 설계 산물일 가능성이 크다.</b> headroom이 0인 21건은 "
            "강화율이 정확히 0%였고, 이는 통계가 아니라 산술이다.")]
story += [P("③ <b>코드북 §4의 핵심 비교가 통합으로 복원됐다.</b> A 단독에서 0건이던 '반발·재강화'가 "
            "18건 확보되어, 반대 입력에 대한 수용:반발이 65:18로 집계된다.")]
story += [Spacer(1, 4), P("<b>말할 수 없는 것</b>", "h2")]
story += [P("① <b>사회자 효과.</b> 사회자 트리거 33건은 전량 A패키지다. '사회자가 트리거의 63%'는 "
            "A의 기술 통계이지 사회자 유무의 효과 추정치가 아니다.")]
story += [P("② <b>모델 효과.</b> 모델·페르소나·주제·초기값이 완전 결합돼 있다.")]
story += [P("③ <b>층화 후 잔차의 원인.</b> headroom 10~30 구간에서 A 0% vs B 68%의 격차가 남지만, "
            "이를 특정 요인에 귀속할 수 없다.")]
story += [PageBreak(), P("<b>논문 반영 제안</b>", "h2")]
rows = [[P("절", "hcell"), P("현재", "hcell"), P("통합 자료로 보강 가능한 내용", "hcell")],
        [P("<b>§4.5</b>", "cellc"), P("업데이트 사건 26건 / 2세션", "cellsm"),
         P("동일 코드북 185건 / 5주제로 확장. 단 사건 비독립성 서술은 그대로 유지", "cellsm")],
        [P("<b>§6 한계</b>", "cellc"), P("천장·바닥 효과를 서술로만 언급", "cellsm"),
         P("headroom=0의 강화율 0%와 초기값별 단조 감소를 <b>수치 근거로 제시</b>", "cellsm")],
        [P("<b>§7 후속설계</b>", "cellc"), P("초기값 ±60 대칭 배정을 권고", "cellsm"),
         P("그 권고가 왜 필요한지를 <b>사후 데이터로 입증</b>. 본 통합의 가장 큰 기여", "cellsm")],
        [P("<b>§5.4</b>", "cellc"), P("모델 성격이 아니라 상호작용", "cellsm"),
         P("모델별 강화율 0~100% 표를 <b>교란의 사례</b>로 인용 가능", "cellsm")]]
story += [tbl(rows, [16*mm, 46*mm, CW-62*mm]), Spacer(1, 10)]

fin = Table([[P('본 통합 분석의 한 줄 요약:<br/><br/>'
                f'<font color="{hexs(CYAN)}" size="12"><b>\u201c두 패키지의 정반대 결과는 토론의 차이가 아니라, '
                f'상당 부분 초기값을 어디에 두었는가의 차이였다.\u201d</b></font><br/><br/>'
                '다만 초기값만으로 전부 설명되지 않으며, 남은 격차를 가르려면 모델·역할·사회자·초기값을 '
                '교차 배정한 통제 실험이 필요하다. 본 통합은 그 실험의 <b>필요성을 입증하는 데까지</b>가 역할이다.',
                "body")]], colWidths=[CW])
fin.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#ecfeff")),
                         ("BOX", (0,0), (-1,-1), 1.2, CYAN),
                         ("TOPPADDING", (0,0), (-1,-1), 12), ("BOTTOMPADDING", (0,0), (-1,-1), 12),
                         ("LEFTPADDING", (0,0), (-1,-1), 12), ("RIGHTPADDING", (0,0), (-1,-1), 12)]))
story += [fin, Spacer(1, 8)]
story += [P("모든 수치는 두 패키지의 stance-events.csv 185행을 병합해 재집계한 실측값이며, 병합 데이터는 "
            "stance-events-merged.csv(185행 × 42열)로 함께 제공한다. 트리거·반응 라벨은 규칙 기반 자동 "
            "1차 코딩이라 전건이 '사람 검토 필요' 상태이며, 논문 통계로 쓰기 전 2인 코딩과 κ 산출이 필요하다.", "small")]

doc.build(story, onFirstPage=page, onLaterPages=page)
print("PDF saved:", OUT)
