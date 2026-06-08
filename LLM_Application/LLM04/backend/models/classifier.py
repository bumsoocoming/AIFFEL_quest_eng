import re
import numpy as np
from .preprocess import clean_text

POSITIVE_CUES = ['기쁘', '행복', '좋았', '즐겁', '감사', '고맙', '뿌듯', '자랑', '축하', '반갑', '웃음']
NEGATIVE_CUES = ['슬프', '힘들', '외롭', '무섭', '불안', '후회', '억울', '속상', '아프', '무너', '그립', '눈물']
POSITIVE_OVERRIDE_PATTERNS = [
    r'기뻐서\s*눈물',
    r'행복해서\s*눈물',
    r'좋아서\s*눈물',
    r'감사.*눈물',
    r'감격.*눈물',
]

_pipe_lr = None
_cat_encoder = None


def load_model(pipeline, encoder):
    global _pipe_lr, _cat_encoder
    _pipe_lr = pipeline
    _cat_encoder = encoder


def _emotion_override(text: str):
    for pattern in POSITIVE_OVERRIDE_PATTERNS:
        if re.search(pattern, text):
            return '감정긍정'
    pos = sum(c in text for c in POSITIVE_CUES)
    neg = sum(c in text for c in NEGATIVE_CUES)
    if pos > 0 and pos >= neg:
        return '감정긍정'
    if neg > 0 and pos == 0:
        return '감정부정'
    return None


def classify(text: str, min_confidence: float = 0.45) -> dict:
    cleaned = clean_text(text)
    override = _emotion_override(cleaned)

    if _pipe_lr is None:
        return {
            'text': text,
            'cleaned_text': cleaned,
            'model_used': 'none',
            'raw_category': '감정긍정',
            'final_category': override or '감정긍정',
            'confidence': None,
            'reason': 'model_not_loaded',
        }

    raw_enc = _pipe_lr.predict([cleaned])[0]
    raw_category = _cat_encoder.inverse_transform([raw_enc])[0]
    confidence = None
    if hasattr(_pipe_lr.named_steps.get('lr'), 'predict_proba'):
        confidence = float(np.max(_pipe_lr.predict_proba([cleaned])[0]))

    final_category = raw_category
    reason = 'model_prediction'

    if override:
        final_category = override
        reason = 'emotion_safety_override'
    elif confidence is not None and confidence < min_confidence:
        reason = 'low_confidence_model_prediction'

    return {
        'text': text,
        'cleaned_text': cleaned,
        'model_used': 'tfidf_lr',
        'raw_category': raw_category,
        'final_category': final_category,
        'confidence': confidence,
        'reason': reason,
    }
