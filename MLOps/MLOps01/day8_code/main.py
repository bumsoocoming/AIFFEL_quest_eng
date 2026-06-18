"""
Day 8 자율 프로젝트 - 한국어 감정 분석 FastAPI 서버
인증(API Key) + Pydantic 검증 + 비동기 추론(run_in_executor)
"""
import asyncio
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Depends, HTTPException

from app.auth import verify_api_key
from app.schemas import PredictRequest, PredictResponse
from app.model_service import load_model, predict, MODEL_NAME

# 추론 전용 스레드풀 (Day 3 패턴)
executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="sentiment")

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 모델을 한 번만 로드
    global model
    print(f"감정 분석 모델 로드 중... ({MODEL_NAME})")
    model = load_model()
    print("모델 로드 완료")
    yield


app = FastAPI(
    title="Korean Sentiment Analysis API",
    description="한국어 문장의 감정(긍정/부정/중립)을 분석하는 API (인증 필요)",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy" if model is not None else "loading",
        "model": MODEL_NAME,
    }


@app.post("/predict", response_model=PredictResponse, tags=["Inference"])
async def predict_sentiment(
    request: PredictRequest,
    user: str = Depends(verify_api_key),
):
    """한국어 문장의 감정을 분석합니다. X-API-Key 헤더에 유효한 키가 필요합니다."""
    if model is None:
        raise HTTPException(status_code=503, detail="모델이 아직 로드되지 않았습니다.")

    try:
        loop = asyncio.get_event_loop()
        # 무거운 추론은 옆방(스레드풀)으로 위임 → 루프는 자유
        result = await loop.run_in_executor(executor, predict, model, request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추론 실패: {str(e)}")

    return PredictResponse(
        success=True,
        label=result["label"],
        confidence=result["confidence"],
        scores=result["scores"],
        user=user,
    )
