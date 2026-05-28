# AIFFEL Campus Online Code Peer Review Templete
- 코더 :김범수
- 리뷰어 :김범수


# PRT(Peer Review Template)
- [x]  **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
     KorQuAD v1과 KLUE-MRC 두 벤치마크에서 Naive RAG와 Advanced RAG 파이프라인을 완성하고, RAGAS 4대 지표로 정량 비교까지 완료하였습니다.

  **RAGAS 평가 결과 (KorQuAD)**
  | 지표 | Naive RAG | Advanced RAG | Delta |
  |---|---|---|---|
  | faithfulness | 0.625 | 0.825 | +0.200 |
  | answer_relevancy | 0.304 | 0.248 | -0.055 |
  | context_precision | 0.650 | 0.800 | +0.150 |
  | context_recall | 0.700 | 0.800 | +0.100 |
        - 중요! 해당 조건을 만족하는 부분을 캡쳐해 근거로 첨부
    
- [x]  **2. 전체 코드에서 가장 핵심적이거나 가장 복잡하고 이해하기 어려운 부분에 작성된 
주석 또는 doc string을 보고 해당 코드가 잘 이해되었나요?**
    `rerank` 함수와 `reciprocal_rank_fusion` 함수에 doc string과 인라인 주석이 잘 작성되어 있습니다.

```python
  def rerank(query, docs, top_k=3):
      """검색된 docs 를 cross-encoder 로 다시 점수화해 상위 top_k 만 반환"""
      pairs = [(query, d.page_content) for d in docs]
      scores = reranker.predict(pairs)
      ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
      return [d for d, _ in ranked[:top_k]]
```

  Cross-Encoder가 (질문, 문서) 쌍을 함께 보면서 관련도를 재점수화한다는 동작 원리가 코드와 주석으로 명확히 표현되어 있습니다.
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
        
- [x]  **3. 에러가 난 부분을 디버깅하여 문제를 해결한 기록을 남겼거나
새로운 시도 또는 추가 실험을 수행해봤나요?**
      다음 세 가지 추가 시도가 확인됩니다.

  **① Self-RAG 프롬프트 직접 구현**
  교재에서 TODO로 남긴 `RETRIEVE_DECISION_PROMPT`와 `CRITIQUE_PROMPT`를 직접 설계하여 검색 필요성 판단과 답변 자가 비평 루프를 구현하였습니다.

  **② RAG-Fusion RRF 함수 직접 구현**
  `reciprocal_rank_fusion` 함수를 힌트 코드를 바탕으로 직접 완성하여 다중 쿼리 검색 결과를 통합하였습니다.

  **③ Paired t-test로 통계적 유의성 검정**
```python
  from scipy import stats
  t_stat, p_val = stats.ttest_rel(naive_df["faithfulness"], adv_df["faithfulness"])
  # 결과: p=0.042 → faithfulness 개선이 통계적으로 유의
```
  단순 평균 비교를 넘어 통계 검정으로 Advanced RAG의 효과를 검증한 점이 인상적입니다
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
        
- [x]  **4. 회고를 잘 작성했나요?**
    실습 말미에 배운 것, 어려웠던 것, 수치로 본 성과, 다음에 해볼 것을 구체적으로 기록하였습니다. 특히 KorQuAD와 KLUE-MRC 두 도메인의 결과를 비교 분석한 점과, 단순 수치가 아닌 통계 검정까지 수행한 점이 회고의 완성도를 높였습니다.
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
        
- [x]  **5. 코드가 간결하고 효율적인가요?**
     반복되는 RAG 실행 로직을 `advanced_rag()`, `advanced_rag_klue()` 함수로 모듈화하여 재사용성을 높였습니다. 또한 `make_dataset()` 함수로 RAGAS 데이터셋 생성을 추상화하여 KorQuAD와 KLUE-MRC 두 도메인에서 동일한 코드를 재사용하였습니다.

```python
  def make_dataset(answers, contexts):
      return Dataset.from_dict({
          "user_input":         questions,
          "response":           answers,
          "retrieved_contexts": contexts,
          "reference":          ground_truths,
      })
```
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부


# 회고(참고 링크 및 코드 개선)
```
- Self-RAG 프롬프트에서 from_template 대신 from_messages([("human", ...)])
  형식을 사용해야 변수가 정상적으로 전달됨을 확인
- Advanced RAG 평가 시 질문 수를 20개 → 5개로 줄여 Colab 세션 타임아웃 방지
- Paired t-test 추가로 단순 평균 비교의 한계를 보완
```
```
