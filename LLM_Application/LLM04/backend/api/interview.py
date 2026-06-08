from fastapi import APIRouter
from pydantic import BaseModel
from backend.agents import interview_agent
from backend.models import classifier

router = APIRouter()


class InterviewRequest(BaseModel):
    text: str


@router.post('/interview')
async def interview(req: InterviewRequest):
    result = classifier.classify(req.text)
    category = result['final_category']
    question = interview_agent.generate_question(req.text, category)
    return {
        'category': category,
        'confidence': result.get('confidence'),
        'question': question,
    }
