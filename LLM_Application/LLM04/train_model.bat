@echo off
chcp 65001 > nul
echo ========================================
echo   HERO 분류 모델 학습
echo ========================================
echo.
echo train_5cat.csv 를 data/ 폴더에 넣은 후 실행하세요.
echo.
echo 학습 중... (약 2~3분 소요)
curl -X POST http://localhost:8000/api/train -H "Content-Type: application/json" -d "{}"
echo.
echo 학습 완료! 브라우저를 새로고침하세요.
pause
