import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))

_model = None

CATEGORY_PROMPTS = {
    '감정긍정': '어르신이 기쁘거나 행복한 감정의 이야기를 말씀하셨습니다. 그 감정을 더 깊이 이끌어낼 수 있는 따뜻한 후속 질문을 1문장으로 만들어주세요.',
    '감정부정': '어르신이 슬프거나 힘들었던 이야기를 말씀하셨습니다. 그 감정을 공감하고 더 이야기할 수 있도록 부드럽고 배려 있는 후속 질문을 1문장으로 만들어주세요.',
    '관계': '어르신이 가족이나 사람에 대한 이야기를 말씀하셨습니다. 그 관계에 대해 더 이야기할 수 있도록 따뜻한 후속 질문을 1문장으로 만들어주세요.',
    '장소': '어르신이 특정 장소나 공간에 대한 이야기를 말씀하셨습니다. 그 장소에 대한 기억을 더 풍부하게 이끌어낼 후속 질문을 1문장으로 만들어주세요.',
    '사물': '어르신이 특정 물건이나 사물에 대한 이야기를 말씀하셨습니다. 그 사물과 연결된 추억을 더 이끌어낼 후속 질문을 1문장으로 만들어주세요.',
}


def _get_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel('gemini-2.0-flash-lite')
    return _model


def generate_question(utterance: str, category: str) -> str:
    direction = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS['감정긍정'])
    prompt = f"""어르신의 발화: "{utterance}"

{direction}

조건:
- 시니어 어르신이 이해하기 쉬운 쉬운 한국어로 작성
- 의문문 1문장만 출력
- 따옴표 없이 질문만 출력"""

    try:
        response = _get_model().generate_content(prompt)
        return response.text.strip().strip('"').strip("'")
    except Exception as e:
        return f"그때 어떤 느낌이셨나요?"
