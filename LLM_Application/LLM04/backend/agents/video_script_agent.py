import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))

MODELS = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-1.5-flash']


def _fallback_script(page: dict) -> dict:
    body = str(page.get('body', '')).replace('\n', ' ').strip()
    title = page.get('title', '')
    return {
        'page': page.get('page', 1),
        'title': title,
        'narration': body if body else f'{title}의 이야기입니다.',
        'subtitle': title,
        'image_prompt': 'warm Korean watercolor illustration, traditional hanok, soft sunset light',
        'scene_direction': '따뜻한 수채화 풍경 위로 어르신의 목소리가 흐르는 장면',
    }


def generate_video_script(storybook: dict) -> list:
    scripts = []
    pages = storybook.get('pages', [])
    gemini_ok = True  # 한 번 사용량 초과되면 이후엔 바로 fallback

    for page in pages:
        if not gemini_ok:
            scripts.append(_fallback_script(page))
            continue

        prompt = f"""아래 스토리북 페이지를 영상 대본으로 변환해주세요.

페이지 제목: {page.get('title', '')}
본문: {page.get('body', '')}

[출력 형식 - 유효한 JSON만 출력]
{{
  "page": {page.get('page', 1)},
  "title": "{page.get('title', '')}",
  "narration": "내레이션 2~3문장 (감동적이고 따뜻한 문체)",
  "subtitle": "자막용 핵심 문장 1줄 (20자 이내)",
  "image_prompt": "AI 이미지 생성용 영문 프롬프트 (수채화 스타일, 한국 전통 배경)",
  "scene_direction": "장면 연출 설명 (한국어, 1~2문장)"
}}"""

        result = None
        for model_name in MODELS:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = response.text.strip()
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                result = json.loads(text)
                break
            except Exception as e:
                print(f'[video] {model_name} 실패: {type(e).__name__}')
                continue

        if result:
            scripts.append(result)
            time.sleep(0.5)
        else:
            gemini_ok = False  # 이후 페이지는 바로 fallback
            scripts.append(_fallback_script(page))

    return scripts
