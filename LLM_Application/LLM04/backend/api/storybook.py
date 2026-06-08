from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from backend.agents import storybook_agent
from pathlib import Path
import json

router = APIRouter()
OUTPUT_PATH = Path(__file__).parent.parent.parent / 'outputs' / 'storybook' / 'storybook_result.json'


class Memory(BaseModel):
    text: str
    category: Optional[str] = '감정긍정'


class StorybookRequest(BaseModel):
    memories: List[Memory]


@router.post('/storybook')
async def generate_storybook(req: StorybookRequest):
    memories = [m.dict() for m in req.memories]
    result = storybook_agent.generate_storybook(memories)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result
