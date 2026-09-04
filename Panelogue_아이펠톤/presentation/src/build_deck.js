const pptxgen = require("pptxgenjs");
const path = require("path");
const D = path.join(__dirname, "deck");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";              // 13.3 x 7.5
pres.author = "인간시대의 끝이 도래했다";
pres.title = "Panelogue — 이질적 LLM 멀티에이전트 토론";

// ── 팔레트 : 전면 라이트 · 크림슨 + 틸 ────────────────────
const WHITE  = "FFFFFF";  // 모든 슬라이드 배경
const SOFT   = "F4F4F7";  // 옅은 면
const LINE   = "E4E2EA";
const TEXT   = "26242E";
const MUT    = "6E6B7B";
const FAINT  = "A6A2B2";
const CRIM   = "C8102E";  // 주 강조
const CRIM_L = "FCEFF1";  // 크림슨 옅은 면
const CRIM_P = "FBD9DE";  // 크림슨 면 위의 보조 글자
const TEAL   = "0F8B8D";  // 보조
const TEAL_L = "E6F4F4";
const PURP   = "6B4E9B";
// 제목은 세리프, 본문·숫자는 산세리프 (둘 다 시스템 설치 확인)
// 제목·본문·차트 모두 한산뜻돋움 (Regular/Bold 실파일 보유)
const HEAD = "Han Santteut Dotum", BODY = "Han Santteut Dotum";

// ── 공통 헬퍼 ─────────────────────────────────────────────
const light = (s) => { s.background = { color: WHITE }; };
const dark  = light;   // 이전 다크 슬라이드도 라이트로

function title(s, t, sub) {
  s.addText(t, {
    x: 0.62, y: 0.44, w: 11.9, h: 0.7, isTextBox: true,
    fontFace: HEAD, fontSize: 32, bold: true, color: TEXT, margin: 0,
  });
  if (sub) s.addText(sub, {
    x: 0.62, y: 1.16, w: 11.9, h: 0.4, isTextBox: true,
    fontFace: BODY, fontSize: 14.5, color: MUT, margin: 0,
  });
}
function eyebrow(s, txt) {          // 좌측 상단 섹션 라벨
  s.addText(txt, {
    x: 0.62, y: 0.40, w: 6, h: 0.28, isTextBox: true,
    fontFace: BODY, fontSize: 12.5, bold: true, color: CRIM,
    charSpacing: 1.8, margin: 0,
  });
}
function tag(s, txt) {
  s.addShape(pres.ShapeType.roundRect, {
    x: 11.32, y: 0.46, w: 1.4, h: 0.34, fill: { color: CRIM_L },
    line: { color: CRIM, width: 1 }, rectRadius: 0.17,
  });
  s.addText(txt, {
    x: 11.32, y: 0.46, w: 1.4, h: 0.34, isTextBox: true, align: "center",
    fontFace: BODY, fontSize: 10.5, bold: true, color: CRIM, margin: 0,
  });
}
function statCard(s, x, y, w, big, label, accent) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h: 1.5, fill: { color: SOFT }, line: { color: LINE, width: 1 },
    rectRadius: 0.1,
  });
  s.addText(big, {
    x, y: y + 0.16, w, h: 0.72, isTextBox: true, align: "center",
    fontFace: BODY, fontSize: 30, bold: true, color: accent || TEXT, margin: 0,
  });
  s.addText(label, {
    x: x + 0.1, y: y + 0.94, w: w - 0.2, h: 0.44, isTextBox: true, align: "center",
    fontFace: BODY, fontSize: 11.5, color: MUT, margin: 0,
  });
}
function foot(s, t) {
  s.addText(t, {
    x: 0.62, y: 6.88, w: 11.9, h: 0.3, isTextBox: true,
    fontFace: BODY, fontSize: 10, color: MUT, margin: 0,
  });
}
function band(s, y, text, sub) {
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h: sub ? 1.2 : 0.9, fill: { color: CRIM_L },
    line: { color: CRIM, width: 1.5 }, rectRadius: 0.1,
  });
  if (sub) s.addText(sub, {
    x: 1.0, y: y + 0.18, w: 11.3, h: 0.32, isTextBox: true,
    fontFace: BODY, fontSize: 12, bold: true, color: CRIM, margin: 0,
  });
  s.addText(text, {
    x: 1.0, y: y + (sub ? 0.56 : 0.2), w: 11.3, h: 0.5, isTextBox: true,
    fontFace: HEAD, fontSize: 19, bold: true, color: TEXT, margin: 0,
  });
}

let s;

// ══ 1. 표지 ═══════════════════════════════════════════════
s = pres.addSlide(); dark(s);
s.addText("AIFFEL 아이펠톤  ·  Panelogue 프로젝트", {
  x: 0.9, y: 1.46, w: 11.5, h: 0.34, isTextBox: true,
  fontFace: BODY, fontSize: 12.5, bold: true, color: FAINT, charSpacing: 1.5, margin: 0,
});
s.addShape(pres.ShapeType.roundRect, {
  x: 0.9, y: 1.98, w: 4.6, h: 0.52, fill: { color: CRIM }, rectRadius: 0.24,
});
s.addText("팀  인간시대의 끝이 도래했다", {
  x: 0.9, y: 1.98, w: 4.6, h: 0.52, isTextBox: true, align: "center",
  fontFace: BODY, fontSize: 14.5, bold: true, color: WHITE, margin: 0,
});
s.addText("여러 AI를 토론시키면\n합의에 도달할까", {
  x: 0.9, y: 2.78, w: 11.5, h: 1.9, isTextBox: true,
  fontFace: HEAD, fontSize: 44, bold: true, color: TEXT, lineSpacing: 56, margin: 0,
});
s.addText("이질적 LLM 멀티에이전트 토론 8주제·16세션 760턴 탐색적 사례 연구", {
  x: 0.9, y: 4.82, w: 11.5, h: 0.42, isTextBox: true,
  fontFace: BODY, fontSize: 16, color: MUT, margin: 0,
});
s.addText([
  { text: "김범수", options: { bold: true, color: TEXT } },
  { text: "   ·   ", options: { color: LINE } },
  { text: "박대건", options: { bold: true, color: TEXT } },
  { text: "   ·   ", options: { color: LINE } },
  { text: "이종현", options: { bold: true, color: TEXT } },
  { text: "   ·   ", options: { color: LINE } },
  { text: "김동건", options: { bold: true, color: TEXT } },
], {
  x: 0.9, y: 5.82, w: 11.5, h: 0.4, isTextBox: true,
  fontFace: BODY, fontSize: 15, margin: 0,
});
s.addText("2026. 09. 09", {
  x: 0.9, y: 6.3, w: 11.5, h: 0.36, isTextBox: true,
  fontFace: BODY, fontSize: 12.5, color: MUT, margin: 0,
});
[["8", "토론 주제"], ["16", "세션"], ["760", "전체 턴"]].forEach((c, i) => {
  const y = 2.12 + i * 1.22;
  s.addShape(pres.ShapeType.roundRect, {
    x: 8.9, y, w: 3.5, h: 1.02, fill: { color: i === 2 ? CRIM_L : SOFT },
    line: { color: i === 2 ? CRIM : LINE, width: i === 2 ? 1.5 : 1 }, rectRadius: 0.1,
  });
  s.addText(c[0], {
    x: 9.24, y: y + 0.13, w: 1.5, h: 0.52, isTextBox: true,
    fontFace: BODY, fontSize: 25, bold: true, color: i === 2 ? CRIM : TEXT, margin: 0,
  });
  s.addText(c[1], {
    x: 9.24, y: y + 0.63, w: 2.86, h: 0.28, isTextBox: true,
    fontFace: BODY, fontSize: 11.5, color: MUT, margin: 0,
  });
});
s.addNotes(
  "[0:00-0:38] 안녕하세요, 팀 인간시대의 끝이 도래했다입니다.\n" +
  "팀 이름이 좀 셀 수도 있는데요. 그런데 연구를 하면서 진짜 인간시대의 끝이 보일 수도 있겠다는 생각이 들었습니다.\n" +
  "오늘 질문은 딱 하나예요. AI 여러 개를 모아놓고 토론시키면 합의에 도달할까.\n" +
  "답부터 말씀드리면, 저희 실험에서는 한 번도 안 됐습니다. 근데 왜 안 됐는지 파보니까 그게 더 재밌더라고요.\n" +
  "영상 하나만 보고 시작하겠습니다."
);

// ══ 2. 영상 자리 ══════════════════════════════════════════
s = pres.addSlide(); dark(s);
eyebrow(s, "아이스브레이크");
// 화면(13.33 x 7.5)의 70% 16:9 틀 = 9.33 x 5.25 인치
s.addShape(pres.ShapeType.roundRect, {
  x: 2.0, y: 1.28, w: 9.33, h: 5.25, fill: { color: SOFT },
  line: { color: CRIM, width: 2 }, rectRadius: 0.14,
});
s.addText("▶", {
  x: 2.0, y: 2.94, w: 9.33, h: 1.1, isTextBox: true, align: "center",
  fontFace: BODY, fontSize: 54, color: CRIM, margin: 0,
});
s.addText("영상 삽입 위치  ·  약 1분", {
  x: 2.0, y: 4.04, w: 9.33, h: 0.44, isTextBox: true, align: "center",
  fontFace: BODY, fontSize: 17, bold: true, color: TEXT, margin: 0,
});
s.addText("매트릭스 — 뇌에 기술을 직접 내려받는 장면", {
  x: 2.0, y: 4.48, w: 9.33, h: 0.4, isTextBox: true, align: "center",
  fontFace: BODY, fontSize: 13, color: MUT, margin: 0,
});
foot(s, "이 틀에 맞춰 영상을 삽입하세요  ·  틀 크기 23.7 × 13.3 cm (9.33 × 5.25 in) = 화면의 70%, 16:9");
s.addNotes(
  "네오가 알약먹고 현실에 왔죠..  디스크로 학습을해서 유슬을 배웁니다..네오 여자친구가 헬기조종법을 배웁니다.  이제 저헬기는 트리니티 겁니다."
);

// ══ 3. 디스크를 현실로 옮기면 — 4단계 ═════════════════════
s = pres.addSlide(); light(s);
eyebrow(s, "아이스브레이크");
s.addText("그 디스크를 현실로 옮기면 4단계입니다", {
  x: 0.62, y: 0.72, w: 11.9, h: 0.58, isTextBox: true,
  fontFace: HEAD, fontSize: 30, bold: true, color: TEXT, margin: 0,
});
s.addText("능력을 심는 방법은 층이 나뉘어 있고, 층마다 심어지는 것이 다릅니다", {
  x: 0.62, y: 1.32, w: 11.9, h: 0.32, isTextBox: true,
  fontFace: BODY, fontSize: 13.5, color: MUT, margin: 0,
});
const tiers = [
  ["프롬프트 페르소나", "말투와 역할만 지정합니다. 솔직히 연기예요. 껍데기입니다.", "현재 저희 시스템", CRIM],
  ["RAG", "참고서를 옆에 놔둔 것. 지식은 정확해지는데 할 수 있는 일은 안 늘어납니다.", "", TEAL],
  ["스킬 · 툴", "절차적 능력. 실제로 새로 할 수 있는 게 생깁니다. 지금 제일 실용적인 층.", "", TEAL],
  ["파인튜닝 · LoRA", "가중치를 직접 건드립니다. LoRA 어댑터는 실제로 핫스왑됩니다.", "디스크에 가장 가까움", PURP],
];
tiers.forEach((t, i) => {
  const y = 1.76 + i * 1.07;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h: 0.95, fill: { color: i === 0 ? CRIM_L : SOFT },
    line: { color: i === 0 ? CRIM : LINE, width: i === 0 ? 1.5 : 1 }, rectRadius: 0.1,
  });
  s.addShape(pres.ShapeType.ellipse, {
    x: 0.94, y: y + 0.23, w: 0.5, h: 0.5, fill: { color: t[3] },
  });
  s.addText(String(i + 1), {
    x: 0.94, y: y + 0.23, w: 0.5, h: 0.5, isTextBox: true, align: "center",
    fontFace: HEAD, fontSize: 16, bold: true, color: WHITE, margin: 0,
  });
  s.addText(t[0], {
    x: 1.68, y: y + 0.13, w: 3.4, h: 0.36, isTextBox: true,
    fontFace: HEAD, fontSize: 16.5, bold: true, color: TEXT, margin: 0,
  });
  s.addText(t[1], {
    x: 1.68, y: y + 0.5, w: 8.3, h: 0.36, isTextBox: true,
    fontFace: BODY, fontSize: 13, color: MUT, margin: 0,
  });
  if (t[2]) {
    s.addShape(pres.ShapeType.roundRect, {
      x: 10.24, y: y + 0.28, w: 2.16, h: 0.4, fill: { color: WHITE },
      line: { color: t[3], width: 1.2 }, rectRadius: 0.2,
    });
    s.addText(t[2], {
      x: 10.24, y: y + 0.28, w: 2.16, h: 0.4, isTextBox: true, align: "center",
      fontFace: BODY, fontSize: 11, bold: true, color: t[3], margin: 0,
    });
  }
});
band(s, 6.06, "네 층 어디를 올려도 네오는 계속 네오입니다  —  인격과 능력은 별개의 축입니다");
s.addNotes(
  "[1:38-2:44] 방금  뇌에 디스크 꽂는 거. 이게 실제 기술에서는 네 층으로 나뉩니다.\n" +
  "1층이 프롬프트 페르소나예요. 말투랑 역할만 정해주는 건데, 솔직히 이건 연기죠. 껍데기고요.\n" +
  "2층 RAG는 참고서를 옆에 놔둔 거라 아는 건 정확해지는데 할 수 있는 일이 늘지는 않고요. 3층 스킬이랑 툴부터 진짜 새로 할 수 있는 게 생깁니다.\n" +
  "4층이 파인튜닝하고 LoRA예요. 가중치를 직접 건드리니까 영화 디스크로 학습시키는거와 제일 가깝죠. LoRA 어댑터는 진짜로 핫스왑이 됩니다.\n" +
  "근데 재밌는 게, 네 층 중에 뭘 올려도 네오는 계속 네오예요. 인격이랑 능력은 다른 축인 거죠.\n" +
  "그리고 저희 시스템은 아직 1층에 있습니다. 오늘 발표는, 연기하는 애들을 토론시켰더니 뭐가 나오더라, 그 얘기예요."
);

// ══ 4. 문제 제기 ══════════════════════════════════════════
s = pres.addSlide(); light(s);
title(s, "정답이 없는 주제라면?", "멀티에이전트 토론 연구의 사각지대");
tag(s, "문제");
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.78, w: 5.9, h: 2.5, fill: { color: TEAL_L },
  line: { color: TEAL, width: 1.2 }, rectRadius: 0.1,
});
s.addText("정답이 있는 과제", {
  x: 0.92, y: 2.02, w: 5.3, h: 0.4, isTextBox: true,
  fontFace: HEAD, fontSize: 18, bold: true, color: TEAL, margin: 0,
});
s.addText([
  { text: "수학 · 사실 확인 · 추론", options: { breakLine: true, bullet: true } },
  { text: "여러 모델이 서로 비판 → 오류 감소", options: { breakLine: true, bullet: true } },
  { text: "효과가 보고된 영역", options: { bullet: true } },
], {
  x: 0.98, y: 2.54, w: 5.2, h: 1.5, isTextBox: true,
  fontFace: BODY, fontSize: 14, color: TEXT, paraSpaceAfter: 8, margin: 0,
});
s.addShape(pres.ShapeType.roundRect, {
  x: 6.82, y: 1.78, w: 5.9, h: 2.5, fill: { color: CRIM_L },
  line: { color: CRIM, width: 1.5 }, rectRadius: 0.1,
});
s.addText("정답이 없는 주제", {
  x: 7.12, y: 2.02, w: 5.3, h: 0.4, isTextBox: true,
  fontFace: HEAD, fontSize: 18, bold: true, color: CRIM, margin: 0,
});
s.addText([
  { text: "정책 · 인물 평가 · 관계 갈등", options: { breakLine: true, bullet: true } },
  { text: "같은 자료라도 가치 우선순위가 다르면 결론이 갈림", options: { breakLine: true, bullet: true } },
  { text: "합의가 목표가 맞는가?", options: { bullet: true } },
], {
  x: 7.18, y: 2.54, w: 5.2, h: 1.5, isTextBox: true,
  fontFace: BODY, fontSize: 14, color: TEXT, paraSpaceAfter: 8, margin: 0,
});
band(s, 4.66, "“합의했는가” 가 아니라 —  “합의하지 못했다면 무엇이 남았는가”", "그래서 질문을 바꿨습니다");
foot(s, "본 연구가 다루는 8개 주제는 모두 가치 갈등형입니다  ·  정답형 과제에서 보고된 성과는 본 연구의 검증 대상이 아닙니다");
s.addNotes(
  "[2:44-3:23] 멀티에이전트 토론은 원래 기대가 컸어요. 모델끼리 서로 비판하게 하면 오류가 줄지 않겠냐는 거였거든요.\n" +
  "수학이나 사실 확인처럼 정답이 있는 과제에서는 일부 조건에서 효과가 보고됐고요.\n" +
  "근데 저희가 다룬 건 정책, 인물 평가, 관계 갈등. 정답이 없습니다. 같은 자료를 봐도 뭘 중요하게 보느냐에 따라 답이 갈리거든요.\n" +
  "그래서 질문을 바꿨습니다. 합의했냐가 아니라, 합의 못 했으면 그럼 뭐가 남았냐."
);

// ══ 5. 토론 주제 8개 ══════════════════════════════════════
s = pres.addSlide(); light(s);
title(s, "저희가 돌린 8개 주제", "무거운 것부터 사소한 것까지 — 공통점은 전부 정답이 없다는 것");
tag(s, "자료");
const topics = [
  ["E1", "세계 평화 정상 대토론", "1", "100", "미달성"],
  ["E2", "운동장 대토론 (사람을 속이는 법)", "1", "100", "미달성"],
  ["E3", "대한민국 꼰대 어벤져스", "1", "100", "미달성"],
  ["E4", "깻잎 논쟁", "1", "100", "미달성"],
  ["E5", "전 연인 비밀 연락", "1", "30", "2 : 2 분할"],
  ["E6", "일론 머스크 평가", "5", "150", "0 / 5"],
  ["E7", "의대 정원 확대", "1", "30", "2 : 2 분할"],
  ["E8", "VAR · AI 심판 개입", "5", "150", "0 / 5"],
];
const hd = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: CRIM }, fontSize: 12.5 } });
const sm = (t, a) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: TEAL }, fontSize: 12.5, align: a || "left" } });
s.addTable(
  [[hd("ID"), hd("토론 주제"), hd("세션"), hd("턴"), hd("공식 합의")]].concat(
    topics.map((r, i) => r.map((c, j) => ({
      text: c,
      options: {
        fontSize: 13, bold: j === 1, align: j >= 2 ? "center" : "left",
        color: j === 4 ? CRIM : TEXT, fill: { color: i % 2 ? SOFT : WHITE },
      },
    })))
  ).concat([[sm("합계"), sm("8개 주제"), sm("16", "center"), sm("760", "center"), sm("0 / 16", "center")]]),
  {
    x: 0.62, y: 1.72, w: 12.1, colW: [0.8, 5.5, 1.2, 1.2, 3.4], rowH: 0.46,
    border: { type: "solid", color: LINE, pt: 1 }, fontFace: BODY, valign: "middle",
  }
);
foot(s, "원자료 300턴(머스크·VAR 로컬 JSON) + 내부 보고서 명시값 460턴  ·  세션 수와 턴 수는 독립 표본 수가 아닙니다");
s.addNotes(
  "[3:23-3:56] 저희가 돌린 8개 주제입니다. 세계 평화 정상회담처럼 무거운 것도 있고, 깻잎 논쟁 같은 것도 있어요.\n" +
  "공통점은 전부 정답이 없다는 겁니다.\n" +
  "머스크 평가와 VAR 심판만 다섯 번씩 돌렸고 나머지는 한 번씩. 합쳐서 16세션, 760턴이에요.\n" +
  "맨 오른쪽 보시면 표기는 갈리지만 합의에 도달한 세션은 하나도 없습니다. 0 나누기 16이에요."
);

// ══ 6. 시스템 ═════════════════════════════════════════════
s = pres.addSlide(); light(s);
title(s, "Panelogue — 사회자 1 + 패널 4", "패널마다 모델도, 성격도, 출발 입장도 다릅니다");
tag(s, "시스템");
[["6", "모델 제공사 (9종)"], ["5", "에이전트 / 세션"], ["±100", "입장 지수 범위"], ["760", "전체 시스템 턴"]]
  .forEach((c, i) => statCard(s, 0.62 + i * 3.11, 1.78, 2.86, c[0], c[1], i === 2 ? CRIM : TEXT));
s.addText("패널마다 다르게 부여한 것", {
  x: 0.62, y: 3.66, w: 6, h: 0.36, isTextBox: true,
  fontFace: HEAD, fontSize: 16.5, bold: true, color: TEXT, margin: 0,
});
s.addText([
  { text: "서로 다른 제공사의 LLM", options: { breakLine: true, bullet: true } },
  { text: "직업 역할 · 가치관 · 말투", options: { breakLine: true, bullet: true } },
  { text: "초기 입장 (−100 ~ +100)", options: { bullet: true } },
], {
  x: 0.68, y: 4.12, w: 5.9, h: 1.4, isTextBox: true,
  fontFace: BODY, fontSize: 14.5, color: TEXT, paraSpaceAfter: 9, margin: 0,
});
s.addShape(pres.ShapeType.roundRect, {
  x: 6.9, y: 3.6, w: 5.82, h: 2.34, fill: { color: TEAL_L },
  line: { color: TEAL, width: 1.5 }, rectRadius: 0.1,
});
s.addText("발언마다 저장되는 구조화 필드", {
  x: 7.2, y: 3.84, w: 5.3, h: 0.36, isTextBox: true,
  fontFace: HEAD, fontSize: 15.5, bold: true, color: TEAL, margin: 0,
});
s.addText([
  { text: "입장값 · 확신도 · 발언 유형", options: { breakLine: true, bullet: true } },
  { text: "어떤 발언에 영향받았는지 (메시지 ID)", options: { bullet: true, bold: true, color: TEXT } },
], {
  x: 7.26, y: 4.3, w: 5.2, h: 1.0, isTextBox: true,
  fontFace: BODY, fontSize: 14, color: TEXT, paraSpaceAfter: 9, margin: 0,
});
s.addText("← 이 필드가 뒤에서 핵심이 됩니다", {
  x: 7.26, y: 5.36, w: 5.2, h: 0.34, isTextBox: true,
  fontFace: BODY, fontSize: 12.5, bold: true, color: CRIM, margin: 0,
});
foot(s, "모델 구성은 원자료가 있는 5개 주제 기준 — 제공사 6곳 · 모델 9종  ·  세션과 주제에 따라 조합이 달라 모델 자체의 효과는 분리되지 않습니다");
s.addNotes(
  "[3:56-4:32] 패널로그는 사회자 한 명에 패널 네 명 붙여놓고 토론시키는 한국어 프로토타입입니다.\n" +
  "패널마다 모델 제공사, 직업, 가치관, 말투, 그리고 마이너스 100에서 플러스 100 사이 초기 입장까지 다 다르게 줬어요.\n" +
  "그리고 말할 때마다 입장값, 확신도, 그리고 어떤 발언 때문에 영향받았는지가 같이 저장됩니다.\n" +
  "이 마지막 거 기억해 주세요. 뒤에서 이게 핵심이에요."
);

// ══ 7. 실제 토론 한 장면 ══════════════════════════════════
s = pres.addSlide(); light(s);
title(s, "실제로는 이렇게 굴러갑니다", "대한민국 꼰대 어벤져스 — “요즘 젊은이들은 왜 우리 말을 안 듣는가”");
tag(s, "사례");
s.addText("아파트 관리 소장  ·  2턴", {
  x: 0.72, y: 1.66, w: 6, h: 0.32, isTextBox: true,
  fontFace: BODY, fontSize: 12.5, bold: true, color: PURP, margin: 0,
});
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.98, w: 7.5, h: 1.42, fill: { color: SOFT },
  line: { color: LINE, width: 1 }, rectRadius: 0.12,
});
s.addText("“젊은 입주민들이 말을 안 듣는 게 아니라 근거 없는 요구를 안 듣는 겁니다.\n분리배출 시간을 게시판에 규정 조항까지 붙여놓으면\n20대 세대가 오히려 제일 잘 지킵니다.”", {
  x: 0.94, y: 2.12, w: 6.9, h: 1.2, isTextBox: true,
  fontFace: BODY, fontSize: 14, color: TEXT, lineSpacing: 22, margin: 0,
});
s.addText("회사 부장  ·  4턴", {
  x: 5.3, y: 3.58, w: 6, h: 0.32, isTextBox: true,
  fontFace: BODY, fontSize: 12.5, bold: true, color: CRIM, margin: 0,
});
s.addShape(pres.ShapeType.roundRect, {
  x: 5.2, y: 3.90, w: 7.5, h: 1.42, fill: { color: CRIM_L },
  line: { color: CRIM, width: 1.5 }, rectRadius: 0.12,
});
s.addText("“소장님, 규정 붙여놓는다고 회사가 돌아갑니까.\n나는 과장 달 때까지 주말에도 나와 일했는데\n요즘은 워라밸이라며 6시면 컴퓨터부터 꺼버려요.”", {
  x: 5.52, y: 4.04, w: 6.9, h: 1.2, isTextBox: true,
  fontFace: BODY, fontSize: 14, color: TEXT, lineSpacing: 22, margin: 0,
});
band(s, 5.50, "바로 이 순간, 회사 부장의 입장값이  −25  →  +35  로 기록됩니다", "로그에 남은 것");
foot(s, "대한민국 꼰대 어벤져스 run-01 · 100턴 중 2턴과 4턴 · 로그 원문에서 앞뒤를 잘라낸 발췌입니다");
s.addNotes(
  "[4:32-5:30] 숫자 들어가기 전에 실제 대화를 하나만 보여드릴게요. 꼰대 어벤져스, 주제가 요즘 젊은이들은 왜 우리 말을 안 듣는가.\n" +
  "2턴에서 아파트 관리 소장이 이렇게 말해요. 젊은 입주민들이 말을 안 듣는 게 아니라 근거 없는 요구를 안 듣는 겁니다. 규정 조항까지 붙여놓으면 20대 세대가 오히려 제일 잘 지킵니다.\n" +
  "그러니까 4턴에서 회사 부장이 받아쳐요. 소장님, 규정 붙여놓는다고 회사가 돌아갑니까. 나는 과장 달 때까지 주말에도 나와 일했는데.\n" +
  "딱 이 순간에 부장 입장값이 마이너스 25에서 플러스 35로 넘어갑니다. 편이 바뀐 거예요.\n" +
  "이런 순간을 전부 찾아낸 게 저희가 한 일입니다."
);

// ══ 8. 결과 1 — 합의 0/16 ═════════════════════════════════
s = pres.addSlide(); light(s);
title(s, "합의는 16번 모두 실패했습니다", "그러나 실패와 무산출은 같은 말이 아니었다");
tag(s, "결과 1");
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.82, w: 3.5, h: 3.9, fill: { color: CRIM }, rectRadius: 0.1,
});
s.addText("0 / 16", {
  x: 0.62, y: 2.5, w: 3.5, h: 1.0, isTextBox: true, align: "center",
  fontFace: HEAD, fontSize: 48, bold: true, color: WHITE, margin: 0,
});
s.addText("공식 합의 달성 세션", {
  x: 0.62, y: 3.5, w: 3.5, h: 0.34, isTextBox: true, align: "center",
  fontFace: BODY, fontSize: 13.5, color: CRIM_P, margin: 0,
});
s.addText([
  { text: "부호 역전  0건", options: { breakLine: true } },
  { text: "반박  84.6% / 85.4%", options: { breakLine: true } },
  { text: "양보  2건 / 1건", options: {} },
], {
  x: 0.92, y: 4.14, w: 2.9, h: 1.2, isTextBox: true, align: "center",
  fontFace: BODY, fontSize: 13.5, color: WHITE, lineSpacing: 22, margin: 0,
});
s.addText("머스크 / VAR 반복 10회 기준", {
  x: 0.92, y: 5.26, w: 2.9, h: 0.3, isTextBox: true, align: "center",
  fontFace: BODY, fontSize: 10.5, color: CRIM_P, margin: 0,
});
s.addText("그런데 사후 코딩에서 나온 것", {
  x: 4.5, y: 1.9, w: 8.2, h: 0.4, isTextBox: true,
  fontFace: HEAD, fontSize: 18, bold: true, color: CRIM, margin: 0,
});
[["세계 평화 토론", "7개 조문의 조약 골격 — 발동 기준, 자동 발효, 대칭 정지"],
 ["의대 정원 토론", "인증 · 재정 · 지역배분 · 노동조건을 담은 조건부 정책안"],
 ["VAR 토론", "판정 로그 공개 · 개입 시간 제한 · 이의제기 절차"]].forEach((o, i) => {
  const y = 2.46 + i * 1.06;
  s.addShape(pres.ShapeType.roundRect, {
    x: 4.5, y, w: 8.22, h: 0.9, fill: { color: SOFT },
    line: { color: LINE, width: 1 }, rectRadius: 0.08,
  });
  s.addText(o[0], {
    x: 4.78, y: y + 0.13, w: 2.5, h: 0.32, isTextBox: true,
    fontFace: BODY, fontSize: 13.5, bold: true, color: TEAL, margin: 0,
  });
  s.addText(o[1], {
    x: 4.78, y: y + 0.46, w: 7.6, h: 0.34, isTextBox: true,
    fontFace: BODY, fontSize: 12.5, color: MUT, margin: 0,
  });
});
s.addText("→ 마지막 부호 하나로 토론을 평가하면, 이 산출물이 전부 지워집니다.", {
  x: 4.5, y: 5.72, w: 8.22, h: 0.36, isTextBox: true,
  fontFace: BODY, fontSize: 13.5, bold: true, color: TEXT, margin: 0,
});
s.addNotes(
  "[5:30-6:10] 결과 1번 보면 공식 합의 기준은 16개 세션 전부에서 미달성이었습니다. 반복 실험 열 번에서도 부호가 뒤집힌 게 한 건도 없었고요.\n" +
  "머스크랑 VAR만 보면 반박이 84.6%와 85.4%인데 양보는 2건과 1건이에요.\n" +
  "근데 보고서를 다시 코딩해보니 다른 게 남아 있더라고요. 세계 평화 토론은 7개 조문짜리 조약 골격, 의대 정원 토론은 조건부 정책안을 냈어요.\n" +
  "합의 못 한 거랑 아무것도 안 나온 거는 다른 얘기였던 겁니다."
);

// ══ 9. 결과 2 — 평균 0의 함정 ═════════════════════════════
s = pres.addSlide(); light(s);
title(s, "평균 0의 함정", "중립처럼 보이는 숫자가 사실은 양극단의 상쇄");
tag(s, "결과 2");
s.addImage({ path: path.join(D, "pc4_average_trap.png"), x: 0.62, y: 1.70, w: 7.9, h: 3.70 });
[["−1.45", "집단 평균 (부호 있음)", TEXT],
 ["95.55", "평균 절대 입장 (5회 평균)", CRIM],
 ["2 : 2", "찬반 분할 (5회 모두)", TEXT]].forEach((c, i) => {
  statCard(s, 9.1, 1.78 + i * 1.62, 3.62, c[0], c[1], c[2]);
});
s.addText("부호 있는 평균 하나만 보면 정반대로 읽게 됩니다.", {
  x: 0.62, y: 5.54, w: 8.2, h: 0.36, isTextBox: true,
  fontFace: BODY, fontSize: 14, bold: true, color: TEXT, margin: 0,
});
foot(s, "VAR·AI 심판 토론 5회 반복 · 막대는 run-metrics 실측값 · 5회 모두 최종 범위는 척도 최대치인 200, 찬반 2:2");
s.addNotes(
  "[6:10-6:41] 결과2는  숫자를 잘못 읽으면 어떻게 되는지 보여드릴게요.\n" +
  "VAR 토론을 다섯 번 돌렸습니다. 최종 집단 평균이 마이너스 1.45예요.\n" +
  "거의 0이죠. 이것만 보면 \"아, 다들 중간에서 만났구나\" 싶습니다.\n" +
  "그런데 실제로는 이랬어요.\n" +
  "매번 두 명은 찬성 쪽 끝에, 두 명은 반대 쪽 끝에 있었습니다.\n" +
  "다섯 번 전부 2 대 2로 갈렸어요. 플러스랑 마이너스가 서로 지워져서 0이 된 겁니다.\n" +
  "부호를 떼고 세기만 보면 평균 95.55입니다. 척도 최대가 100인데요.\n" +
  "제일 찬성하는 사람과 제일 반대하는 사람 사이 거리도 200. 끝에서 끝이었습니다.\n" +
  "그러니까 평균 0은 합의가 아니었어요. 제일 심하게 갈라진 상태였습니다.\n" +
  "평균 하나로 평가하면 정반대로 읽게 되는 거죠."
);

// ══ 10. 방법 — 인과 사슬 복원 ═════════════════════════════
s = pres.addSlide(); light(s);
title(s, "누가 무슨 말을 했을 때 누가 움직였나", "로그에서 인과 사슬을 복원하는 법");
tag(s, "방법");
[["stanceHistory", "입장이 바뀐 시점과\n변경 사유"],
 ["influencedBy\nMessageIds", "그 변화를 일으킨\n메시지 ID"],
 ["messages", "해당 발언의\n원문 텍스트"]].forEach((f, i) => {
  const x = 0.62 + i * 4.28;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 1.86, w: 3.62, h: 1.6, fill: { color: TEAL_L },
    line: { color: TEAL, width: 1.5 }, rectRadius: 0.1,
  });
  s.addText(f[0], {
    x, y: 2.06, w: 3.62, h: 0.56, isTextBox: true, align: "center",
    fontFace: BODY, fontSize: 14, bold: true, color: TEAL, margin: 0,
  });
  s.addText(f[1], {
    x, y: 2.66, w: 3.62, h: 0.66, isTextBox: true, align: "center",
    fontFace: BODY, fontSize: 12.5, color: TEXT, margin: 0,
  });
  if (i < 2) s.addText("+", {
    x: x + 3.72, y: 2.32, w: 0.46, h: 0.5, isTextBox: true, align: "center",
    fontFace: HEAD, fontSize: 24, bold: true, color: MUT, margin: 0,
  });
});
band(s, 3.84, "= “어떤 구절이 누구의 입장을 몇 점 움직였는가” 를 전건 복원",
     "5개 주제 · 입장 변화 185건 · 트리거 구절 전건 연결");
[["185건", "복원된 입장 변화"], ["5주제", "12개 실행"], ["9범주", "트리거 자동 분류"]]
  .forEach((c, i) => statCard(s, 0.62 + i * 4.28, 5.20, 3.62, c[0], c[1], i === 0 ? CRIM : TEXT));
foot(s, "총 13회 실행 중 VAR 3회차는 입장 변화가 0건이어서, 사건이 기록된 실행은 12개입니다");
s.addNotes(
  "[6:41-7:09] 이번에 저희가 찾은 건데, 어떻게 봤는지부터 말씀드릴게요.\n" +
  "아까 기억해 달라고 한 그 필드, 영향받은 메시지 ID를 발언 원문이랑 이어 붙이면 누가 무슨 말 했을 때 누가 몇 점 움직였는지가 그대로 나옵니다.\n" +
  "이 방식으로 5개 주제에서 입장 변화 185건을 전부 재구성했어요."
);

// ══ 11. 계단 그래프 ═══════════════════════════════════════
s = pres.addSlide(); light(s);
title(s, "턴별 입장 변화 — 계단 그래프", "수직으로 꺾이는 지점이 곧 ‘반응한 순간’, 원형은 입장 변화 사건");
tag(s, "시각화");
s.addImage({ path: path.join(D, "pc1_steps.png"), x: 2.11, y: 1.58, w: 9.08, h: 4.95 });
foot(s, "대한민국 꼰대 어벤져스 · 100턴 · 입장 변화 23건 · 회사 부장은 초기 −25에서 최종 +76 — 초기·최종 순이동 101점으로 5개 주제 전체 최대 · 인용은 로그 원문 발췌");
s.addNotes(
  "[7:09-7:58] 아까 그 장면을 100턴 전체로 펼치면 이렇게 나옵니다. 계단처럼 꺾이는 데가 반응한 순간이에요.\n" +
  "빨간 게 회사 부장인데, 아까 그 4턴에서 통째로 뒤집혔죠. 소장 말을 받아들인 게 아니라 거부하면서 넘어간 겁니다.\n" +
  "그러고는 뒤로 15계단을 계속 올라가요. 한 번 편 정하면 반박받을수록 더 굳어지는 패턴이죠.\n" +
  "나머지 셋은 다릅니다. 아버지랑 소장은 100턴 내내 10점 안쪽이었고, 동네 통장은 첫 반응에 편을 정하고는 그대로 갑니다.\n" +
  "안 움직이거나, 한 번 정하고 끝나거나 둘 중 하나였어요."
);

// ══ 12. 트리거 범주 + 교차분석 ════════════════════════════
s = pres.addSlide(); light(s);
title(s, "반응을 부른 구절을 모아 분류했습니다", "185건의 트리거 구절 자동 1차 코딩 결과");
tag(s, "시각화");
s.addText("① 어떤 범주의 구절이 많았나", {
  x: 0.62, y: 1.62, w: 6.1, h: 0.32, isTextBox: true,
  fontFace: BODY, fontSize: 13, bold: true, color: TEAL, margin: 0,
});
s.addImage({ path: path.join(D, "pc2_categories.png"), x: 0.5, y: 1.94, w: 6.1, h: 2.19 });
s.addText("② 페르소나를 건드리면 굳는가, 누그러지는가", {
  x: 6.9, y: 1.62, w: 5.82, h: 0.32, isTextBox: true,
  fontFace: BODY, fontSize: 13, bold: true, color: TEAL, margin: 0,
});
s.addImage({ path: path.join(D, "pc5_persona.png"), x: 7.31, y: 1.94, w: 5.0, h: 2.44 });
s.addText("대표 트리거 구절 — 반응을 부른 문장을 전부 모아 분류했습니다", {
  x: 0.62, y: 4.5, w: 12.1, h: 0.32, isTextBox: true,
  fontFace: BODY, fontSize: 13, bold: true, color: TEXT, margin: 0,
});
const quotes = [
  ["“규정 조항까지 붙여놓으면\n20대 세대가 오히려 제일 잘 지킵니다”", "수치·사실·근거", "117건 · 평균 5.9점", MUT],
  ["“1단 부스터 착륙시키고 다시 날려서\n발사 시장 판을 갈아엎었어”", "성과·실행 가능성", "17건 · 평균 10.0점", TEAL],
  ["“8년 넘게 반복해서 못 지킨 건\n어떻게 설명할 거야?”", "사회자 질문·선택 압박", "7건 · 평균 11.0점", CRIM],
];
quotes.forEach((q, i) => {
  const x = 0.62 + i * 4.14;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 4.88, w: 3.86, h: 1.44, fill: { color: SOFT },
    line: { color: LINE, width: 1 }, rectRadius: 0.1,
  });
  s.addText(q[0], {
    x: x + 0.24, y: 5.02, w: 3.38, h: 0.7, isTextBox: true,
    fontFace: BODY, fontSize: 13, bold: true, color: TEXT, lineSpacing: 18, margin: 0,
  });
  s.addText(q[1] + "  ·  " + q[2], {
    x: x + 0.24, y: 5.84, w: 3.38, h: 0.32, isTextBox: true,
    fontFace: BODY, fontSize: 11.5, bold: true, color: q[3], margin: 0,
  });
});
foot(s, "가장 많은 '수치·사실·근거'(117건)의 평균 이동은 5.9점으로 하위권, 가장 적은 '사회자 질문·선택 압박'(7건)이 11.0점으로 최대  ·  규칙 기반 자동 1차 코딩, 사람 검토 전  ·  인용은 로그 원문 발췌");
s.addNotes(
  "[7:58-8:56] 트리거 구절들을 전부 모아서 9개 범주로 분류했습니다.\n" +
  "왼쪽이 범주별 건수예요. 제일 흔한 게 수치·사실·근거로 117건인데, 정작 평균 이동은 5.9점입니다. 하위권이에요.\n" +
  "오히려 사회자 질문이 7건뿐인데 평균 11점으로 제일 크게 움직였어요. 다만 7건이라 단정할 수는 없어요. 사회자는 원래 지목하는 자리라 기록될 확률 자체가 높거든요.\n" +
  "오른쪽 교차분석 보시면, 페르소나를 부정하는 입력을 받은 85건 중 46%가 오히려 더 세졌어요. 반박이 절반은 굳히는 쪽으로 간 겁니다.\n" +
  "반대로 사회자 탐색 질문 35건은 89%가 누그러지는 쪽이었고요.\n" +
  "아래 세 개는 실제로 토론에서 나온 문장입니다. 길어서 앞뒤만 잘랐고, 안에 있는 말은 안 바꿨어요."
);

// ══ 13. 척도 경계 효과 ════════════════════════════════════
s = pres.addSlide(); light(s);
title(s, "그런데 — 결론이 설계의 산물이었습니다", "초기값을 어디에 뒀느냐가 변화 방향을 미리 결정한다");
tag(s, "핵심");
s.addImage({ path: path.join(D, "pc3_initial.png"), x: 0.55, y: 1.66, w: 7.15, h: 3.6 });
s.addShape(pres.ShapeType.roundRect, {
  x: 7.94, y: 1.66, w: 4.78, h: 1.62, fill: { color: CRIM_L },
  line: { color: CRIM, width: 1.5 }, rectRadius: 0.1,
});
s.addText("21건", {
  x: 7.94, y: 1.8, w: 4.78, h: 0.6, isTextBox: true, align: "center",
  fontFace: HEAD, fontSize: 30, bold: true, color: CRIM, margin: 0,
});
s.addText("직전 입장이 ±100이던 사건 —  강화 = 정확히 0건", {
  x: 8.14, y: 2.44, w: 4.38, h: 0.62, isTextBox: true, align: "center",
  fontFace: BODY, fontSize: 12.5, color: TEXT, lineSpacing: 17, margin: 0,
});
s.addText([
  { text: "입장 지수는 ±100이 한계입니다.", options: { breakLine: true, bold: true, color: TEXT } },
  { text: "경계에서 출발하면 더 강해지는 것이", options: { breakLine: true } },
  { text: "산술적으로 불가능", options: { bold: true, color: CRIM } },
  { text: "합니다.", options: { breakLine: true } },
  { text: "", options: { breakLine: true, fontSize: 7 } },
  { text: "통계 결과가 아니라 척도 정의에서", options: { breakLine: true } },
  { text: "따라 나오는 귀결입니다.", options: {} },
], {
  x: 7.94, y: 3.5, w: 4.78, h: 1.76, isTextBox: true,
  fontFace: BODY, fontSize: 13.5, color: TEXT, lineSpacing: 20, margin: 0,
});
band(s, 5.52, "“토론하면 입장이 누그러진다” 는 관찰이, 사실은 초기값 설계가 만든 결과일 수 있습니다");
foot(s, "|0|·|25|·|71| (n=128)은 동일 패키지 내부 비교  ·  |100| (n=52)은 다른 패키지  ·  막대 4개 = 185건 중 180건  ·  운동장 세션 제외 시 100 / 65.4 / 61.1 / 3.8 (논문 §4.3 기준)");
s.addNotes(
  "[8:56-10:28] 자, 여기가 오늘 제일 중요한 부분입니다.\n" +
  "185건을 두 묶음으로 나눠서 봤는데, 결과가 정반대로 나왔어요.\n" +
  "머스크랑 VAR 실험 쪽은 96%가 중앙으로 누그러졌고,\n" +
  "나머지 세 주제 쪽은 62%가 오히려 더 세졌습니다.\n" +
  "같은 코드로 똑같이 분석했는데 왜 이러지, 하고 봤더니 답이 좀 허무했어요.\n" +
  "출발점이 달랐던 겁니다.\n" +
  "입장 지수가 플러스마이너스 100까지밖에 없거든요.\n" +
  "그런데 한쪽은 패널을 전부 100에서 출발시켰어요.\n" +
  "100에서 시작하면 더 세질 수가 없습니다. 갈 데가 없으니까요.\n" +
  "분석 결과가 아니라 그냥 산수예요.\n" +
  "실제로 직전 입장이 100이었던 21건은, 더 세진 게 정확히 0건이었습니다.\n" +
  "왼쪽 그래프 보시면, 출발점이 0에서 100으로 갈수록 막대가 쭉 낮아지죠.\n" +
  "맨 끝은 3.8퍼센트입니다.\n" +
  "그러니까 토론하면 입장이 누그러진다는 그 관찰이,\n" +
  "사실은 어디서 출발시켰느냐가 만든 결과일 수 있다는 거예요.\n" +
  "하나 덧붙이면, 논문 본문은 품질 문제가 있던 운동장 세션을 뺀 수치를 씁니다.\n" +
  "그 기준이면 65와 61이라, 가운데 두 막대 차이가 거의 없어져요.\n" +
  "그러니까 이 깔끔한 계단은 운동장을 넣었을 때 나오는 거고,\n" +
  "어느 기준에서든 확실한 건 맨 끝의 3.8퍼센트 하나입니다."
);

// ══ 14. 한계 ══════════════════════════════════════════════
s = pres.addSlide(); light(s);
title(s, "분명히 해둘 한계", "저희는 이 연구를 ‘가설 생성용 사례 연구’로 규정합니다");
tag(s, "한계");
[["완전요인 실험이 아닙니다", "주제 · 모델 · 페르소나 · 초기값 · 사회자가 함께 달라져 단일 원인의 효과를 분리할 수 없습니다"],
 ["185건 전부 자동 코딩입니다", "규칙 기반 1차 분류이며 사람 검토와 코더 간 일치도(κ)를 거치지 않았습니다"],
 ["경계 효과가 전부는 아닙니다", "여지를 맞춰 층화해도 격차가 남고, 그 잔차는 사회자·주제·모델과 교란되어 분리 불가합니다"]]
 .forEach((l, i) => {
  const y = 1.86 + i * 1.42;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h: 1.2, fill: { color: SOFT },
    line: { color: LINE, width: 1 }, rectRadius: 0.1,
  });
  s.addShape(pres.ShapeType.ellipse, { x: 0.94, y: y + 0.34, w: 0.52, h: 0.52, fill: { color: CRIM } });
  s.addText(String(i + 1), {
    x: 0.94, y: y + 0.34, w: 0.52, h: 0.52, isTextBox: true, align: "center",
    fontFace: HEAD, fontSize: 16, bold: true, color: WHITE, margin: 0,
  });
  s.addText(l[0], {
    x: 1.72, y: y + 0.2, w: 10.6, h: 0.36, isTextBox: true,
    fontFace: HEAD, fontSize: 16.5, bold: true, color: TEXT, margin: 0,
  });
  s.addText(l[1], {
    x: 1.72, y: y + 0.62, w: 10.6, h: 0.4, isTextBox: true,
    fontFace: BODY, fontSize: 13, color: MUT, margin: 0,
  });
});
foot(s, "다음 단계 — 185건의 20%인 37건을 2인이 독립 코딩하고 Cohen’s κ 를 산출하면 ②의 한계는 해소됩니다");
s.addNotes(
  "[10:28-10:59] 한계도 솔직하게 말씀드릴게요.\n" +
  "첫째, 완전요인 실험이 아닙니다. 여러 조건이 같이 달라져서 뭐가 원인인지 못 가려요.\n" +
  "둘째, 185건 전부 자동 코딩이고 사람이 검토를 안 했습니다.\n" +
  "셋째, 경계 효과를 보정해도 두 자료군 차이가 완전히 없어지지는 않았어요.\n" +
  "그래서 이걸 결론이 아니라 가설 생성용 사례 연구로 규정했습니다.\n" +
  "(사과하지 말고 담담하게)"
);

// ══ 15. 결론 ══════════════════════════════════════════════
s = pres.addSlide(); dark(s);
s.addText("결론", {
  x: 0.9, y: 0.72, w: 11.5, h: 0.5, isTextBox: true,
  fontFace: BODY, fontSize: 14, bold: true, color: CRIM, charSpacing: 1.5, margin: 0,
});
[["01", "마지막 부호 하나로\n평가하지 말 것",
  "입장 궤적 · 극단성 · 부호 분할 ·\n절차적 산출물 · 소수 의견 보존을 함께", CRIM, CRIM_L],
 ["02", "초기값을\n통제 변수로 명시할 것",
  "4×4 라틴 스퀘어 교차 ·\n초기 입장 ±60 대칭 배정", TEAL, TEAL_L]].forEach((c, i) => {
  const x = 0.9 + i * 5.92;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 1.46, w: 5.6, h: 2.6, fill: { color: c[4] },
    line: { color: c[3], width: 1.5 }, rectRadius: 0.12,
  });
  s.addText(c[0], {
    x: x + 0.34, y: 1.72, w: 1.2, h: 0.44, isTextBox: true,
    fontFace: HEAD, fontSize: 20, bold: true, color: c[3], margin: 0,
  });
  s.addText(c[1], {
    x: x + 0.34, y: 2.24, w: 5.0, h: 0.86, isTextBox: true,
    fontFace: HEAD, fontSize: 19, bold: true, color: TEXT, lineSpacing: 27, margin: 0,
  });
  s.addText(c[2], {
    x: x + 0.34, y: 3.2, w: 5.0, h: 0.7, isTextBox: true,
    fontFace: BODY, fontSize: 12.5, color: MUT, lineSpacing: 18, margin: 0,
  });
});
s.addText("네오는 디스크를 꽂아도 네오였습니다.\n능력은 심을 수 있어도, 그 능력이 무엇을 바꿨는지는 따로 재야 합니다.", {
  x: 0.9, y: 4.6, w: 11.5, h: 0.94, isTextBox: true,
  fontFace: HEAD, fontSize: 19, bold: true, color: CRIM, lineSpacing: 29, margin: 0,
});
s.addText("감사합니다.", {
  x: 0.9, y: 6.0, w: 8, h: 0.5, isTextBox: true,
  fontFace: HEAD, fontSize: 24, bold: true, color: TEXT, margin: 0,
});
s.addText("팀 인간시대의 끝이 도래했다  ·  김범수 · 박대건 · 이종현 · 김동건", {
  x: 0.9, y: 6.58, w: 11.5, h: 0.34, isTextBox: true,
  fontFace: BODY, fontSize: 11.5, color: MUT, margin: 0,
});
s.addNotes(
  "[10:59-11:48] 결론은 두 가지입니다.\n" +
  "하나, 토론 시스템을 마지막에 찬성이냐 반대냐, 그거 하나로 평가하면 안 됩니다.\n" +
  "입장이 어떻게 움직였는지, 뭘 만들어냈는지를 같이 봐야 해요.\n" +
  "둘, 출발점을 미리 정해놓고 기록해야 합니다.\n" +
  "아까 100에서 출발시키면 갈 데가 없다고 했잖아요.\n" +
  "그래서 다음 실험은 플러스마이너스 60에서 시작할 계획입니다.\n" +
  "더 세질 여지도, 누그러질 여지도 양쪽에 남겨두는 거죠.\n" +
  "또, 같은 역할을 여러 모델에 돌려가며 맡겨볼 겁니다. 모델 탓인지 역할 탓인지 가려내려고요.\n" +
  "그리고 처음 그 영상으로 돌아가면요.\n" +
  "네오는 디스크를 꽂아도 네오였습니다.\n" +
  "능력은 심을 수 있어요. 그런데 그 능력이 뭘 바꿨는지는 따로 재야 합니다.\n" +
  "저희가 만든 게 그 재는 방법입니다.\n" +
  "들어주셔서 감사합니다.\n" +
  "(마지막 세 줄은 천천히. 화면 말고 청중 보기)"
);


// ══ 16. 백업 — 질문 대응용 (발표 시간에 포함하지 않음) ════
s = pres.addSlide(); light(s);
eyebrow(s, "백업 · 질문 대응용");
s.addText("8주 동안 무엇을 했나", {
  x: 0.62, y: 0.72, w: 11.9, h: 0.58, isTextBox: true,
  fontFace: HEAD, fontSize: 30, bold: true, color: TEXT, margin: 0,
});
s.addText("발표 중에는 넘기지 말고, 물어보면 띄우세요", {
  x: 0.62, y: 1.32, w: 11.9, h: 0.32, isTextBox: true,
  fontFace: BODY, fontSize: 13.5, color: MUT, margin: 0,
});
[["95", "문서 산출물"], ["294", "저장소 전체 파일"],
 ["185", "코딩한 입장 변화"], ["760", "실행한 토론 턴"]]
  .forEach((c, i) => statCard(s, 0.62 + i * 3.11, 1.72, 2.86, c[0], c[1], i === 0 ? CRIM : TEXT));

s.addText("단계별로 한 일", {
  x: 0.62, y: 3.36, w: 7.4, h: 0.3, isTextBox: true,
  fontFace: BODY, fontSize: 13, bold: true, color: TEAL, margin: 0,
});
const stages = [
  ["실험", "8주제 · 16세션 · 760턴 실행", "결과보고서 5"],
  ["중간 점검", "버그리포트 · KPT 회고 · 중간보고서", "문서 3"],
  ["분석", "인과 사슬 복원 185건 전건 코딩", "패키지 3종"],
  ["논문", "v1 원본에서 v5까지 5차 개정", "docx 6 · pdf 4"],
  ["발표", "슬라이드 15장 · 대본 3종", "pptx 3 · md 4"],
  ["검증", "슬라이드 62 + 대본 49 항목 자동 대조", "스크립트 2"],
];
s.addTable(
  stages.map((r, i) => [
    { text: r[0], options: { bold: true, color: TEXT, fontSize: 12,
                             fill: { color: i % 2 ? SOFT : WHITE } } },
    { text: r[1], options: { color: TEXT, fontSize: 12,
                             fill: { color: i % 2 ? SOFT : WHITE } } },
    { text: r[2], options: { color: MUT, fontSize: 11.5, align: "right",
                             fill: { color: i % 2 ? SOFT : WHITE } } },
  ]),
  {
    x: 0.62, y: 3.68, w: 7.4, colW: [1.3, 4.2, 1.9], rowH: 0.42,
    border: { type: "solid", color: LINE, pt: 1 }, fontFace: BODY, valign: "middle",
  }
);

s.addText("종류별 산출물", {
  x: 8.3, y: 3.36, w: 4.42, h: 0.3, isTextBox: true,
  fontFace: BODY, fontSize: 13, bold: true, color: TEAL, margin: 0,
});
[["PDF", "15"], ["DOCX", "9"], ["PPTX", "5"], ["MD", "63"],
 ["CSV", "37"], ["JSON", "30"], ["PNG", "24"], ["Python", "69"]]
  .forEach((c, i) => {
    const x = 8.3 + (i % 2) * 2.26;
    const y = 3.68 + Math.floor(i / 2) * 0.64;
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: 2.16, h: 0.58, fill: { color: SOFT },
      line: { color: LINE, width: 1 }, rectRadius: 0.08,
    });
    s.addText(c[0], {
      x: x + 0.22, y: y + 0.13, w: 1.2, h: 0.32, isTextBox: true,
      fontFace: BODY, fontSize: 11.5, color: MUT, margin: 0,
    });
    s.addText(c[1], {
      x: x + 0.9, y: y + 0.09, w: 1.04, h: 0.4, isTextBox: true, align: "right",
      fontFace: BODY, fontSize: 17, bold: true, color: TEXT, margin: 0,
    });
  });
foot(s, "후반 주요 일정 — 8-21 버그리포트 · 8-24 KPT · 8-25~28 결과보고서 3건 · 8-28 중간보고서 · 8-31 논문 초고 · 9-01 통합분석 · 9-02 최종본과 발표자료");
s.addNotes(
  "[백업] 발표 중에는 넘기지 마세요. 질문 나올 때만 띄우는 장입니다.\n" +
  "'이거 얼마나 걸렸어요' 나 '몇 명이 했어요' 같은 게 나오면 여기로 오시면 됩니다.\n" +
  "네 명이 8주 동안 문서 95개, 저장소 전체로는 294개 파일을 만들었습니다.\n" +
  "토론 760턴 돌리고, 입장 변화 185건을 전건 코딩했고, 논문은 다섯 번 고쳤어요.\n" +
  "숫자를 쭉 읽지는 마시고, 물어본 것만 짚어서 답하시는 게 낫습니다."
);

pres.writeFile({ fileName: path.join(__dirname, "Panelogue_발표자료.pptx") })
  .then(f => console.log("생성 완료:", f));
