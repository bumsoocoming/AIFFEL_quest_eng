"""
Day 8 자율 프로젝트 - 한국어 감정 분석 모델 로드 + 추론
모델: snunlp/KR-FinBert-SC (한국어 금융 감정 분류: positive/negative/neutral)
"""
from transformers import pipeline

MODEL_NAME = "snunlp/KR-FinBert-SC"


def load_model():
    """사전학습된 감정 분석 파이프라인을 로드하여 반환합니다.

    return_all_scores=True로 모든 라벨의 점수를 함께 받습니다.
    """
    clf = pipeline(
        "text-classification",
        model=MODEL_NAME,
        top_k=None,  # 모든 클래스 점수 반환 (구 return_all_scores=True)
    )
    return clf


def predict(model, text: str) -> dict:
    """텍스트를 받아 감정 분석 결과를 반환합니다.

    Returns:
        {"label": str, "confidence": float, "scores": {label: score, ...}}
    """
    outputs = model(text)
    # top_k=None이면 [[{label, score}, ...]] 형태로 반환됨
    results = outputs[0] if isinstance(outputs[0], list) else outputs
    scores = {r["label"]: round(float(r["score"]), 4) for r in results}
    # 가장 높은 점수의 라벨을 최종 예측으로
    best = max(scores, key=scores.get)
    return {
        "label": best,
        "confidence": scores[best],
        "scores": scores,
    }
