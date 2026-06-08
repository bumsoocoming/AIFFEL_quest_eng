import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))

STORYBOOK_STRUCTURE = [
    ('인생의 시작', '태어난 곳, 어린 시절 환경'),
    ('꿈과 희망', '어릴 때 꿈, 하고 싶었던 것'),
    ('첫 번째 도전', '학교, 첫 직장, 새로운 시작'),
    ('사랑과 가족', '결혼, 자녀, 가족과의 추억'),
    ('기쁨의 순간들', '가장 행복했던 기억들'),
    ('고난과 극복', '힘들었던 시절, 이겨낸 이야기'),
    ('소중한 인연들', '친구, 스승, 잊지 못할 사람들'),
    ('고향과 추억', '고향 풍경, 어린 시절 놀이터'),
    ('인생의 지혜', '살면서 깨달은 것들'),
    ('미래 세대에게', '자손들에게 전하고 싶은 말'),
]

# 사용량 초과 시 순서대로 시도할 모델들
MODELS = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-1.5-flash']

# 10개 페이지 각각에 매핑할 답변(기억) 인덱스 (8개 답변 기준)
PAGE_TO_MEMORY = [0, 1, 2, 3, 4, 5, 6, 0, 7, 7]


def _build_local_story(memories: list) -> dict:
    """Gemini 없이도 어르신의 실제 답변으로 따뜻한 글을 구성한다."""
    texts = [str(m.get('text', '')).strip() for m in memories]
    pages = []
    for i, (title, desc) in enumerate(STORYBOOK_STRUCTURE):
        mi = PAGE_TO_MEMORY[i] if i < len(PAGE_TO_MEMORY) else None
        answer = texts[mi] if (mi is not None and mi < len(texts) and texts[mi]) else ''
        if answer:
            body = (
                f'"{answer}"\n\n'
                '그 순간의 마음과 풍경은 세월이 흘러도 변치 않는 소중한 기억으로 남아 있습니다.'
            )
        else:
            body = '어르신의 삶의 한 페이지가 이 자리에 따뜻하게 새겨집니다.'
        pages.append({
            'page': i + 1,
            'title': title,
            'theme': desc.split(',')[0].strip(),
            'body': body,
        })
    return {'title': '나의 소중한 인생 이야기', 'pages': pages}


def generate_storybook(memories: list) -> dict:
    memories_text = '\n'.join(
        f"- [{m.get('category', '')}] {m.get('text', '')}"
        for m in memories
    )
    pages_spec = '\n'.join(
        f"{i+1}페이지: {title} ({desc})"
        for i, (title, desc) in enumerate(STORYBOOK_STRUCTURE)
    )

    prompt = f"""아래 어르신의 구술 기억들을 바탕으로 10페이지 인생 스토리북을 만들어주세요.

[수집된 기억들]
{memories_text}

[페이지 구조]
{pages_spec}

[출력 형식 - 반드시 유효한 JSON으로만 출력]
{{
  "title": "스토리북 제목",
  "pages": [
    {{
      "page": 1,
      "title": "페이지 제목",
      "theme": "짧은 테마 키워드",
      "body": "3~5문장의 따뜻하고 문학적인 본문"
    }}
  ]
}}

조건:
- 어르신의 실제 발화 내용을 최대한 반영
- 문어체, 감성적이고 따뜻한 문체
- 각 페이지 본문은 3~5문장
- JSON 외 다른 텍스트 출력 금지"""

    # 여러 모델 순서대로 시도
    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            data = json.loads(text)
            if data.get('pages'):
                return data
        except Exception as e:
            print(f'[storybook] {model_name} 실패: {type(e).__name__} - {str(e)[:120]}')
            continue

    # 모든 모델 실패(사용량 초과 등) -> 실제 답변으로 로컬 구성
    print('[storybook] Gemini 사용 불가 -> 로컬 구성으로 대체')
    return _build_local_story(memories)
