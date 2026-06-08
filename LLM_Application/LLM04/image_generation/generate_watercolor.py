import base64
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_DIR = Path(__file__).parent.parent / "frontend" / "images" / "input"
OUTPUT_DIR = Path(__file__).parent.parent / "frontend" / "images" / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

IMAGE_SIZE = "1536x1024"
QUALITY = "medium"
MODEL = "gpt-image-2"

PROMPTS = {
    "01": """
한국인 대가족 삼대가 한옥 마루에 모여 환하게 웃고 있는 장면을
16:9 비율의 따뜻한 수채화 일러스트로 변환해줘.

원본 사진의 가족 구성, 인물 배치, 표정, 한옥 분위기는 최대한 유지해줘.
스타일은 부드러운 붓터치, 은은한 종이 질감, 따뜻한 오후 햇살,
크림색·연한 주황·부드러운 갈색·자연스러운 초록 계열의 색감.
실사 느낌보다는 감성적인 가족 포스터, 그림책 삽화 같은 분위기.
텍스트, 로고, 워터마크는 넣지 마.
""",
    "02": """
한국인 70대 할아버지와 할머니가 한옥 담장 앞 정원에서 다정하게 웃고 있는 장면을
16:9 비율의 따뜻한 수채화 일러스트로 변환해줘.

원본 사진의 두 사람의 표정, 포즈, 한복 느낌, 한옥 정원 배경은 유지해줘.
부드러운 햇살, 꽃이 핀 정원, 잔잔하고 행복한 노년의 분위기.
수채화 종이 질감, 따뜻한 색감, 섬세한 붓터치.
텍스트, 로고, 워터마크는 넣지 마.
""",
    "03": """
한국 시골 마을의 넓은 풍경을 16:9 비율의 따뜻한 수채화 풍경화로 변환해줘.

원본 사진의 논밭, 낮은 한옥 지붕, 굽이진 시골길, 먼 산맥, 노을 하늘을 유지해줘.
황금빛 노을, 조용한 농촌, 평화로운 추억 같은 분위기.
부드러운 색 번짐, 종이 질감, 감성적인 수채화 포스터 스타일.
텍스트, 로고, 워터마크는 넣지 마.
""",
    "04": """
노부부가 한옥 골목길을 천천히 걸어 내려가고,
멀리 현대적인 서울 스카이라인과 강이 보이는 장면을
16:9 비율의 따뜻한 수채화 일러스트로 변환해줘.

황금빛 노을, 부드러운 종이 질감, 따뜻한 포스터 스타일.
텍스트, 로고, 워터마크는 넣지 마.
""",
    "05": """
고요한 호수 옆 한국 전통 정자와 노을 풍경을
16:9 비율의 따뜻한 수채화 풍경화로 변환해줘.

붉고 노란 노을빛, 잔잔한 물결, 부드러운 물감 번짐,
한국적인 감성 풍경 포스터 스타일.
텍스트, 로고, 워터마크는 넣지 마.
""",
    "06": """
한옥 실내에서 할머니와 어린 손녀가 마주 앉아 웃으며 이야기하는 장면을
16:9 비율의 따뜻한 수채화 일러스트로 변환해줘.

가족의 사랑, 조용한 대화, 따뜻한 실내 빛, 감성 그림책 스타일.
텍스트, 로고, 워터마크는 넣지 마.
""",
    "07": """
한국 시골 한옥 마당에서 노부부가 나무 평상에 앉아 환하게 웃는 장면을
16:9 비율의 따뜻한 수채화 일러스트로 변환해줘.

정겨운 시골집, 행복한 노년, 따뜻한 햇살.
텍스트, 로고, 워터마크는 넣지 마.
""",
    "08": """
높은 곳에서 내려다본 한국 농촌 마을의 넓은 풍경을
16:9 비율의 따뜻한 수채화 파노라마 풍경으로 변환해줘.

평화로운 농촌, 감성적인 노을, 종이 질감, 부드러운 색 번짐.
텍스트, 로고, 워터마크는 넣지 마.
""",
    "09": """
한국인 대가족이 전통 한옥 마당에서 한복을 입고 환하게 웃고 있는 장면을
16:9 비율의 따뜻한 수채화 일러스트로 변환해줘.

명절 가족사진처럼 따뜻하고 행복한 분위기.
텍스트, 로고, 워터마크는 넣지 마.
""",
}

COMMON_NEGATIVE = """
피해야 할 요소:
글자, 로고, 워터마크, 서명, 깨진 얼굴, 이상한 손가락, 손가락 추가,
손가락 누락, 기괴한 표정, 무서운 분위기, 과한 만화풍,
너무 어두운 색감, 사이버펑크, 플라스틱 같은 질감, 저화질, 흐릿한 얼굴,
중복 인물, 깨진 한글, 이상한 글자.
"""


def get_prompt(image_path: Path) -> str:
    key = image_path.stem
    base_prompt = PROMPTS.get(
        key,
        """
첨부한 원본 이미지를 바탕으로 16:9 비율의 따뜻한 수채화 일러스트를 만들어줘.
원본의 핵심 피사체, 구도, 분위기는 유지하고,
부드러운 붓터치, 은은한 종이 질감, 따뜻한 햇살, 한국적인 정서를 살려줘.
감성적인 포스터 또는 그림책 삽화 같은 분위기.
텍스트, 로고, 워터마크는 넣지 마.
"""
    )
    return base_prompt + "\n\n" + COMMON_NEGATIVE


def generate_one_image(image_path: Path):
    output_path = OUTPUT_DIR / f"{image_path.stem}_watercolor_16x9.png"
    prompt = get_prompt(image_path)

    print(f"생성 중: {image_path.name} -> {output_path.name}")

    with open(image_path, "rb") as image_file:
        result = client.images.edit(
            model=MODEL,
            image=image_file,
            prompt=prompt,
            size=IMAGE_SIZE,
            quality=QUALITY,
        )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"저장 완료: {output_path}")


def main():
    image_files = sorted(
        list(INPUT_DIR.glob("*.png"))
        + list(INPUT_DIR.glob("*.jpg"))
        + list(INPUT_DIR.glob("*.jpeg"))
        + list(INPUT_DIR.glob("*.webp"))
    )

    if not image_files:
        print(f"이미지 없음: {INPUT_DIR}")
        print("frontend/images/input/ 폴더에 01.png ~ 09.png 를 넣어주세요.")
        return

    for image_path in image_files:
        try:
            generate_one_image(image_path)
            time.sleep(1)
        except Exception as e:
            print(f"오류 발생: {image_path.name}")
            print(e)


if __name__ == "__main__":
    main()
