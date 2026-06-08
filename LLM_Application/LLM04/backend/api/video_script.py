from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Any
from backend.agents import video_script_agent
from pathlib import Path
import json

router = APIRouter()
OUTPUT_PATH = Path(__file__).parent.parent.parent / 'outputs' / 'video_script' / 'video_script_result.json'


class VideoScriptRequest(BaseModel):
    storybook: Any


@router.post('/video-script')
async def generate_video_script(req: VideoScriptRequest):
    scripts = video_script_agent.generate_video_script(req.storybook)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(scripts, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'scripts': scripts}
