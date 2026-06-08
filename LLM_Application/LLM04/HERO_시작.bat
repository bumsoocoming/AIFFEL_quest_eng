@echo off
chcp 65001 > nul
title HERO 서버 + 공유주소
cd /d "%~dp0"

echo ========================================
echo   HERO 시작 중... 잠시만 기다려주세요
echo ========================================
echo.

REM 1) 백엔드 서버 시작 (새 창)
echo [1/2] 서버 켜는 중...
start "HERO 서버" cmd /c "chcp 65001 > nul && set PYTHONIOENCODING=utf-8 && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

REM 서버가 켜질 때까지 대기
timeout /t 6 /nobreak > nul

REM 2) Cloudflare 터널 시작 + 주소 추출
echo [2/2] 공유 주소 만드는 중... (20초)
set CF="C:\Users\TOP\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"
if exist tunnel_run.log del tunnel_run.log
start "HERO 터널" /min %CF% tunnel --url http://localhost:8000 --logfile tunnel_run.log

timeout /t 18 /nobreak > nul

echo.
echo ========================================
echo   팀원 공유 주소 (아래 주소 끝에 /new 붙여서 공유)
echo ========================================
echo.
powershell -NoProfile -Command "$m=[regex]::Match((Get-Content 'tunnel_run.log' -Raw),'https://[a-z0-9\-]+\.trycloudflare\.com'); if($m.Success){ Write-Host ('   '+$m.Value+'/new') -ForegroundColor Yellow } else { Write-Host '   주소 생성 실패 - 30초 더 기다린 후 tunnel_run.log 확인' -ForegroundColor Red }"
echo.
echo ========================================
echo   * 이 창과 다른 두 창(서버/터널)을 모두 켜두세요
echo   * 끄려면 이 창들을 닫으면 됩니다
echo ========================================
echo.
pause
