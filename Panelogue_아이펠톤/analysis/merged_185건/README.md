# Panelogue 두 패키지 통합 분석

A(머스크·VAR, 52건) + B(사회자 없는 3주제, 133건) = **185건 / 5주제 / 13개 실행**

두 패키지가 **동일한 analyze_turn_dynamics.py와 동일한 코드북 v1**을 사용했으므로
트리거 카테고리·반응 패턴 라벨이 그대로 호환되며, 별도 매핑 없이 병합했다.

## 핵심 결과

| 초기값 절대값 | n | 강화율 | 패키지 |
|---:|---:|---:|---|
| 0 | 3 | 100.0% | B |
| 25 | 46 | 80.4% | B |
| 71 | 79 | 49.4% | B |
| 100 | 52 | 3.8% | A |

**|초기값| 0→25→71 구간은 모두 B패키지 내부**이므로 패키지·사회자·주제 교란 없이
단조 감소가 확인된다. 강화 여지(headroom = 100 − |직전 입장|)가 0인 21건은
강화율이 정확히 0%이며, 이는 통계가 아니라 산술이다.

다만 headroom을 맞춰 층화해도 격차가 남는다(10~30 구간에서 A 0% vs B 68.3%).
잔차는 사회자 유무·주제·모델·반복 설계와 완전히 교란되어 원인을 분리할 수 없다.

## 파일

- `stance-events-merged.csv` — 병합 원장 185행 × 42열
  (원본 34열 + package / topic_ko / initial_kind / moderator_setting / runs_in_topic /
   headroom / hardened / softened)
- `summary-by-initial-stance.csv` — 초기값별 강화율
- `summary-by-headroom.csv` — 강화 여지 구간별 강화율
- `summary-by-trigger-category.csv` — 트리거 카테고리별 통합 집계
- `통합분석_콘솔출력.txt` — 7개 검정 전체 출력
- `charts/` — 통합 차트 7종

## 재현

```powershell
python merge_analysis.py      # 병합 + 7개 검정
python merged_charts.py       # 차트 7종
python make_merged_report.py  # PDF 보고서
```

## 해석 제한

- 트리거·반응 라벨은 규칙 기반 자동 1차 코딩이며 185건 전건이 사람 검토 전 상태다.
- 사회자 트리거 33건은 전량 A패키지다. "사회자가 트리거의 63%"는 A의 기술 통계이지
  사회자 유무의 효과 추정치가 아니다.
- 모델·페르소나·주제·초기값이 고정 결합되어 모델별 수치를 "모델 성격"으로 읽으면 안 된다.
- A는 5회 반복, B는 1회 실행이라 반복 안정성 축이 비대칭이다.
