import os
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))
    return _client


COMMON_NEGATIVE = """
피해야 할 요소: 글자, 로고, 워터마크, 서명, 깨진 얼굴, 이상한 손가락,
기괴한 표정, 무서운 분위기, 과한 만화풍, 너무 어두운 색감, 저화질, 흐릿한 얼굴.
"""


@router.post('/image/generate')
async def generate_watercolor(
    file: UploadFile = File(...),
    prompt: str = Form('첨부한 원본 이미지를 16:9 비율의 따뜻한 수채화 일러스트로 변환해줘. 부드러운 붓터치, 은은한 종이 질감, 한국적인 정서.'),
):
    try:
        content = await file.read()
        result = _get_client().images.edit(
            model='gpt-image-2',
            image=content,
            prompt=prompt + '\n\n' + COMMON_NEGATIVE,
            size='1536x1024',
            quality='medium',
        )
        image_bytes = base64.b64decode(result.data[0].b64_json)
        return Response(content=image_bytes, media_type='image/png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel

class TextImageRequest(BaseModel):
    story_text: str
    page: int = 1

@router.post('/image/from-story')
async def generate_image_from_story(req: TextImageRequest):
    """스토리 텍스트를 기반으로 수채화 일러스트 생성"""
    prompt = f"""
아래 한국 어르신의 인생 이야기를 바탕으로 따뜻하고 감성적인 수채화 일러스트를 그려줘.

이야기: {req.story_text}

스타일:
- 한국 전통 수채화 일러스트 (Korean watercolor illustration)
- 부드러운 붓터치, 은은한 종이 질감
- 따뜻한 황금빛·크림색·테라코타 색감
- 한옥, 한국 시골 풍경, 가족 정서
- 감성적인 그림책 삽화 스타일
- 텍스트, 글자, 로고, 워터마크 없음
- 16:9 가로 비율
"""
    try:
        result = _get_client().images.generate(
            model='gpt-image-2',
            prompt=prompt,
            size='1536x1024',
            quality='medium',
            n=1,
        )
        image_bytes = base64.b64decode(result.data[0].b64_json)
        return Response(content=image_bytes, media_type='image/png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
