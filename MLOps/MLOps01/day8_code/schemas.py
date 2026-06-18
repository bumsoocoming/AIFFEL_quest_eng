"""
Day 8 자율 프로젝트 - 한국어 감정 분석 서비스 입출력 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional


class PredictRequest(BaseModel):
    """감정 분석 요청"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="감정을 분석할 한국어 문장 (1~2000자)",
        examples=["오늘 주가가 크게 올랐습니다"],
    )


class PredictResponse(BaseModel):
    """감정 분석 응답"""
    success: bool = Field(default=True, description="요청 처리 성공 여부")
    label: str = Field(description="예측 감정 (positive / negative / neutral)")
    confidence: float = Field(description="예측 확신도 (0.0~1.0)")
    scores: Optional[dict] = Field(
        default=None,
        description="감정별 전체 점수 {'positive': 0.9, ...}",
    )
    user: str = Field(description="인증된 사용자")
