# Panelogue 턴별 입장 변화 분석 패키지 — 사회자 없는 3주제

머스크·VAR 반복실험 패키지와 **동일한 스크립트·동일한 코드북**으로,
사회자가 없는 3개 주제(세계 평화 정상 대토론 · 대한민국 꼰대 어벤져스 · 운동장 대토론)를 분석한 결과다.

## 바로 확인하기

`analysis/turn-dynamics-dashboard.html`을 더블클릭하면 다음 내용을 확인할 수 있다.

- 주제별 입장지수 계단 그래프
- 각 변화 사건의 반응 구절과 변화 이유
- 트리거 유형별 평균 입장 변화폭
- 성격·행동 설정값과 실제 변동성의 탐색적 상관관계

정적 이미지만 필요하면 `analysis/charts/00_graph_contact_sheet.png` 한 장으로 전체 그래프를 볼 수 있다.

## 이 패키지의 존재 이유

기존 머스크·VAR 패키지는 **모든 패널의 초기 입장이 ±100(척도 경계)** 이었다.
경계에서 출발하면 강화가 수학적으로 불가능하므로, 변화의 96%가 "중앙으로 완화"로 나오고
코드북 §4의 핵심 질문(*페르소나를 부정당했을 때 반발하는가?*)을 검정할 수 없었다.

본 패키지의 3주제는 초기값이 **+71 / −71 / 0 / −25** 로 경계에서 떨어져 있고 사회자도 없다.
따라서 두 패키지를 함께 쓰면 아래 두 요인을 분리해 볼 수 있다.

| 구분 | 머스크·VAR 패키지 | 본 패키지 |
|---|---|---|
| 초기 입장 | ±100 (경계값) | +71 / −71 / 0 / −25 |
| 사회자 | 있음 (트리거의 63%) | **없음** (전원 패널) |
| 실행 구조 | 2주제 × 5회 반복 | 3주제 × 1회 |
| 입장 변화 사건 | 52건 | **133건** |
| 강화 방향 변화 | 2건 (3.8%) | **82건 (61.7%)** |
| 극성 전환 | 0건 | **2건** |
| 반발·페르소나 재강화 | **0건 (검정 불가)** | **18건** |

## 주요 파일

- `analysis/turn-dynamics/stance-events.csv`: 입장 변화 133건과 반응 원문 구절
- `analysis/turn-dynamics/turn-stance-series.csv`: 턴별 계단 그래프용 시계열
- `analysis/turn-dynamics/agent-personality-outcomes.csv`: 성격값과 실제 행동 결과
- `analysis/turn-dynamics/trigger-persona-crosstab.csv`: 입력 유형과 페르소나 반응 교차표
- `analysis/turn-dynamics/personality-correlations.csv`: 성격값과 변화율·변화폭의 기술적 상관
- `analysis/turn-dynamics/turn-dynamics-analysis.json`: 대시보드용 통합 데이터
- `analysis/turn-dynamics/annotated-transcripts/`: 3개 주제의 전체 주석 대화록
- `analysis/turn-dynamics/분석_코드북.md`: 자동·사람 코딩 기준
- `analysis/charts/`: 그래프 12종 PNG

## 새 JSON으로 다시 분석하기

프로젝트 루트에서 순서대로 실행한다.

```powershell
python scripts/analyze_turn_dynamics.py --data-root data --output analysis/turn-dynamics
python scripts/build_turn_dynamics_visual.py analysis/turn-dynamics/turn-dynamics-analysis.json analysis/turn-dynamics-fragment.html
python scripts/render_turn_dynamics_charts.py analysis/turn-dynamics analysis/charts
```

원본 JSON은 아래 구조에 둔다.

```text
data/[주제명]/sanitized/run-01.json
```

입장 그래프와 변화 원인을 정확히 복원하려면 JSON에 `messages`, `settings.agents`,
`stanceHistory`, `influencedByMessageIds`가 포함되어야 한다.

`analyze_turn_dynamics.py`와 `build_turn_dynamics_visual.py`는 머스크·VAR 패키지의 원본을
그대로 사용했다. `render_turn_dynamics_charts.py`만 본 패키지에서 새로 추가했다.

## 연구 사용 시 주의

- 입장 변화 수치와 영향 메시지 ID는 원본 로그에서 직접 가져왔다.
- 반응 구절은 기록된 변화 이유와 어휘가 가장 겹치는 문장을 자동 선택한 것이다.
- 트리거·페르소나 카테고리는 규칙 기반 1차 코딩이며, 논문 통계에는 2인 이상의 사람 코딩과
  Cohen's κ가 필요하다. 전체 133건의 `coding_status`는 `자동 1차 코딩—사람 검토 필요`다.
- **각 주제가 1회 실행이므로 회차 간 반복 안정성은 평가할 수 없다.** 반복 안정성은 머스크·VAR
  패키지가, 초기값 변량과 사회자 부재 조건은 본 패키지가 담당한다.
- 모델과 페르소나가 고정 결합되어 있어 성격 효과와 모델 효과를 분리할 수 없다.
  후속 실험은 모델–페르소나 라틴 스퀘어 배치를 권장한다.
- 세 주제는 주제 성격(국제 정책 / 세대 갈등 / 관계·기만)이 서로 달라 주제 간 직접 비교보다
  주제 내 궤적 비교에 사용해야 한다.
- 원본 JSON에 포함돼 있던 API 키는 `data/*/sanitized/`로 옮기며 모두 `[REDACTED]` 처리했다.
  잔존 키 패턴 검사 결과 3개 파일 모두 0건이다.
