# analysis — 턴별 입장변화 분석

토론 로그에는 에이전트가 입장을 바꿀 때마다 **어떤 발언 때문에 바꿨는지** 메시지 ID가
기록됩니다. 이걸 발언 원문과 이어 붙이면 *"누가 무슨 말을 했을 때 누가 몇 점 움직였는가"*
인과 사슬이 복원됩니다.

```
stanceHistory  ⋈  influencedByMessageIds  ⋈  messages
```

## 세 개의 패키지

| 폴더 | 만든 사람 | 주제 | 사건 | 원자료 |
|---|---|---|---:|---|
| `turn-dynamics_머스크·VAR/` | 팀원 | 머스크 5회 · VAR 5회 | 52 | 300턴 로컬 JSON |
| `turn-dynamics_사회자없는3주제/` | — | 세계평화 · 운동장 · 꼰대 | 133 | 300턴 로컬 JSON |
| `merged_185건/` | — | 위 둘을 병합 | **185** | 5주제 · 12개 실행 |

두 패키지는 **동일한 `analyze_turn_dynamics.py` 와 동일한 코드북 v1** 을 썼습니다.
트리거 범주·반응 패턴 라벨이 그대로 호환되므로 별도 매핑 없이 병합했습니다.

> 총 13회 실행 중 VAR 3회차는 입장 변화가 0건이라, 사건이 기록된 실행은 12개입니다.

## 각 패키지 구조

```
data/<주제>/sanitized/run-0N.json   API 키를 제거한 토론 로그
data/<주제>/*.csv                    최종 입장 · 실행별 지표 · 발언 유형 등
analysis/turn-dynamics/              집계 CSV · 코드북 · 주석 트랜스크립트
analysis/charts/                     차트 PNG
scripts/                             분석 코드
README.md                            코드북과 컬럼 설명
```

## merged_185건/ 의 핵심 파일

| 파일 | 내용 |
|---|---|
| `stance-events-merged.csv` | **185행 × 42열.** 모든 분석의 원천 |
| `summary-by-initial-stance.csv` | 초기값 절대값별 강화 비율 — 척도 경계 효과의 근거 |
| `summary-by-headroom.csv` | 여지(headroom = 100 − \|직전 입장\|)별 집계 |
| `summary-by-trigger-category.csv` | 트리거 9범주별 건수·평균 이동폭 |
| `merge_analysis.py` | 병합 스크립트 (재현용) |
| `통합분석_콘솔출력.txt` | 병합 당시 콘솔 로그 |

`stance-events-merged.csv` 주요 컬럼: `dataset` `run` `agent_name` `model`
`initial_stance` `previous_stance` `new_stance` `delta` `change_type`
`trigger_clause` `primary_category_ko` `trigger_persona_relation` `persona_response`
`package` `headroom` `hardened` `softened`

## 핵심 발견

| 초기 입장 \|값\| | n | 강화 비율 | 패키지 |
|---:|---:|---:|---|
| \|0\| | 3 | 100.0% | B |
| \|25\| | 46 | 80.4% | B |
| \|71\| | 79 | 49.4% | B |
| \|100\| | 52 | **3.8%** | A |

\|0\|·\|25\|·\|71\| (n=128) 은 동일 패키지 안에서의 비교라 교란이 없습니다.
직전 입장이 경계(±100)에 있던 21건은 **강화가 정확히 0건** 입니다.
