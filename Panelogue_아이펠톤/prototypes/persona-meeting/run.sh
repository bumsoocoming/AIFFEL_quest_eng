#!/usr/bin/env bash
cd "$(dirname "$0")"

if [ ! -x ./.venv/bin/python ]; then
  echo "[실패] 아직 설치가 안 됐습니다. 먼저 ./setup.sh 를 실행하세요."
  exit 1
fi

echo
echo "============================================"
echo "  회의 실행"
echo "============================================"
echo
echo "  1. 연습 실행  (돈 안 씀, 흐름만 확인)"
echo "  2. 1분 회의   (약 8턴)"
echo "  3. 3분 회의   (약 20턴)"
echo "  4. 5분 회의   (약 35턴)"
echo
read -rp "번호를 고르세요 [1-4]: " SEL

case "$SEL" in
  1) ./.venv/bin/python meeting.py --dry-run --turns 4 ;;
  2) ./.venv/bin/python meeting.py --length 1min ;;
  3) ./.venv/bin/python meeting.py --length 3min ;;
  4) ./.venv/bin/python meeting.py --length 5min ;;
  *) echo "1~4 중에 고르세요." ; exit 1 ;;
esac

echo
echo "대화록은 logs 폴더에 저장됐습니다."
echo
