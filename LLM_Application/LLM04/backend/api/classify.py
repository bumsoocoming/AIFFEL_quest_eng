from fastapi import APIRouter
from pydantic import BaseModel
from backend.models import classifier

router = APIRouter()


class ClassifyRequest(BaseModel):
    text: str
    min_confidence: float = 0.45


@router.post('/classify')
async def classify_utterance(req: ClassifyRequest):
    result = classifier.classify(req.text, req.min_confidence)
    return result
