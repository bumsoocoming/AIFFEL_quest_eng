# Panelogue 턴별 입장 변화 분석 패키지

## 바로 확인하기

`turn-dynamics-dashboard.html`을 더블클릭하면 다음 내용을 확인할 수 있습니다.

- 주제·반복 실행별 입장지수 계단 그래프
- 각 변화 사건의 반응 구절과 변화 이유
- 트리거 유형별 평균 입장 변화폭
- 성격·행동 설정값과 실제 변동성의 탐색적 상관관계

## 주요 파일

- `stance-events.csv`: 입장 변화 52건과 반응 원문 구절
- `turn-stance-series.csv`: 턴별 계단 그래프용 시계열
- `agent-personality-outcomes.csv`: 성격값과 실제 행동 결과
- `trigger-persona-crosstab.csv`: 입력 유형과 페르소나 반응 교차표
- `personality-correlations.csv`: 성격값과 변화율·변화폭의 기술적 상관
- `turn-dynamics-analysis.json`: 대시보드용 통합 데이터
- `annotated-transcripts/`: 10개 실행의 전체 주석 대화록
- `분석_코드북.md`: 자동·사람 코딩 기준

## 새 JSON으로 다시 분석하기

프로젝트 루트에서 실행합니다.

```powershell
python scripts/analyze_turn_dynamics.py
```

원본 JSON은 아래 구조에 둡니다.

```text
data/[실험명]/sanitized/run-01.json
```

입장 그래프와 변화 원인을 정확히 복원하려면 JSON에 `messages`, `settings.agents`, `stanceHistory`, `influencedByMessageIds`가 포함되어야 합니다. MD 파일은 사람이 읽는 결과물로 사용할 수 있지만, 수치가 없는 MD만으로는 턴별 입장을 완전하게 복원하기 어렵습니다.

## 연구 사용 시 주의

트리거 카테고리와 페르소나 관계는 규칙 기반 자동 1차 코딩입니다. 논문 통계에는 두 명 이상의 사람이 독립 코딩한 뒤 Cohen's kappa 등으로 일치도를 확인한 값을 사용하는 것을 권장합니다.
