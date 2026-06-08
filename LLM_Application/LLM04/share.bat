@echo off
cd /d "%~dp0"
set CF="C:\Users\TOP\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"
echo.
echo  주소 생성 중... 20초 기다려주세요
echo.
if exist tunnel.log del tunnel.log
start /b %CF% tunnel --url http://localhost:8000 --logfile tunnel.log
timeout /t 20 /nobreak > nul
echo.
echo ================================================
findstr "trycloudflare.com" tunnel.log
echo ================================================
echo.
echo  위 https:// 주소를 팀원들에게 공유하세요!
echo  (이 창을 닫으면 주소가 끊깁니다)
echo.
pause
