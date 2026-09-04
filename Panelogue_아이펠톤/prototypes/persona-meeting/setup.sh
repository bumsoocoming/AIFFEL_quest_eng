#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo
echo "============================================"
echo "  회의 프로그램 설치 (처음 한 번만)"
echo "============================================"
echo

if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python  >/dev/null 2>&1; then PY=python
else
  echo "[실패] 파이썬이 없습니다."
  echo "       맥이면 터미널에 아래를 붙여넣으세요:"
  echo "       brew install python3"
  exit 1
fi

echo "[1/3] 전용 공간 만드는 중..."
$PY -m venv .venv

echo "[2/3] 필요한 것 설치 중... (1~2분 걸립니다)"
./.venv/bin/python -m pip install --quiet --upgrade pip
./.venv/bin/python -m pip install --quiet openai pyyaml python-dotenv

echo "[3/3] 키 파일 확인 중..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo
  echo "  .env 파일을 만들었습니다."
  echo "  전달받은 키를 붙여넣고 저장하세요."
  echo
  ${EDITOR:-nano} .env
fi

chmod +x run.sh 2>/dev/null || true

echo
echo "설치 완료. 이제 ./run.sh 를 실행하세요."
echo
