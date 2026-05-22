# AIFFEL Campus Online Code Peer Review Templete
- 코더 : 김범수
- 리뷰어 : 김범수


# PRT(Peer Review Template)
- [X]  **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
    - klue/bert-base 모델을 NSMC 데이터셋으로 fine-tuning하여 정상 작동을 확인했습니다.
         STEP 4와 STEP 5 모두 완성된 코드가 실행되었고, 최종 결과물이 출력되었습니다.
        - 중요! 해당 조건을 만족하는 부분을 캡쳐해 근거로 첨부
    
- [X]  **2. 전체 코드에서 가장 핵심적이거나 가장 복잡하고 이해하기 어려운 부분에 작성된 
주석 또는 doc string을 보고 해당 코드가 잘 이해되었나요?**
    transform_custom 함수와 DataCollatorWithPadding 적용 부분이
가장 핵심적인 코드이며, 주석이 명확하게 작성되어 있습니다.

**잘 작성된 주석 예시**
```python
# Dynamic Padding용 토크나이징
# padding 제거 → DataCollatorWithPadding이 배치마다 동적으로 패딩
def tokenize_nsmc_bucket(batch):
    return klue_tokenizer(
        batch['document'],
        truncation=True,      # 최대 길이 초과시 자르기
        max_length=128,       # 최대 길이 제한
        # padding 없음 → DataCollatorWithPadding이 동적으로 처리
    )
```
각 인자의 역할과 존재 이유가 명확하게 기술되어 있어 이해하기 쉬웠습니다.
        
- [X]  **3. 에러가 난 부분을 디버깅하여 문제를 해결한 기록을 남겼거나
새로운 시도 또는 추가 실험을 수행해봤나요?**
여러 버전 충돌 문제를 직접 해결한 기록이 남아있습니다.

**해결한 문제들**
- `pyarrow` 버전 불일치 → 재설치로 해결
- `group_by_length` 인자 제거 → TrainingArguments에서 삭제
- `tokenizer` 인자 제거 → `DataCollatorWithPadding`으로 대체
- `e9t/nsmc` 로드 불가 → GitHub raw 파일로 직접 로드

특히 NSMC 데이터를 GitHub raw 파일로 직접 로드하는
창의적인 우회 방법이 인상적이었습니다.

```python
nsmc_dataset = load_dataset(
    'csv',
    data_files={
        'train': 'https://raw.githubusercontent.com/e9t/nsmc/master/ratings_train.txt',
        'test': 'https://raw.githubusercontent.com/e9t/nsmc/master/ratings_test.txt'
    },
    delimiter='\t'
)
```

        
- [X]  **4. 회고를 잘 작성했나요?**
 
잘한 점, 배운 점, 어려웠던 점, 아쉬운 점, 느낀 점으로
구조적으로 잘 작성되어 있습니다.

특히 어려웠던 점에서 구체적인 오류명과 해결 방법을
명시한 부분이 인상적이었습니다.

> "라이브러리 버전 충돌 문제가 가장 힘들었습니다.
> pyarrow 버전 불일치, group_by_length 인자 제거 등
> 교재 코드와 현재 버전 사이의 차이를 하나씩 해결해나갔습니다."부
        
- [X]  **5. 코드가 간결하고 효율적인가요?**
함수화가 잘 되어있고 코드 중복이 최소화되어 있습니다.

**잘 작성된 부분**
```python
def clean_text(text):
    """노이즈 제거 전처리 함수"""
    if text is None:
        return ""
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```
전처리 함수가 모듈화되어 있고 docstring도 달려있어
재사용성이 높습니다.


# 회고(참고 링크 및 코드 개선)
```
버전 충돌 문제를 스스로 해결하면서 단순히 코드를 실행하는 것을
넘어 framework 전반에 대한 이해를 높인 점이 인상적이었습니다.
STEP 4와 STEP 5의 성능 비교 분석이 체계적으로 이루어졌고,
두 방식의 trade-off를 명확히 파악한 점이 좋았습니다.
```
