@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYEXE=.venv\Scripts\python.exe

if not exist "%PYEXE%" (
  echo [실패] 아직 설치가 안 됐습니다. setup.bat 을 먼저 실행하세요.
  pause
  exit /b 1
)

echo.
echo ============================================
echo   회의 실행
echo ============================================
echo.
echo   1. 연습 실행  (돈 안 씀, 흐름만 확인)
echo   2. 1분 회의   (약 8턴)
echo   3. 3분 회의   (약 20턴)
echo   4. 5분 회의   (약 35턴)
echo.
set "SEL="
set /p SEL="번호를 고르세요 [1-4]: "

if "%SEL%"=="1" goto practice
if "%SEL%"=="2" goto m1
if "%SEL%"=="3" goto m3
if "%SEL%"=="4" goto m5
echo 1부터 4 사이의 번호를 입력하세요.
pause
exit /b 1

:practice
"%PYEXE%" meeting.py --dry-run --turns 4
goto done

:m1
"%PYEXE%" meeting.py --length 1min
goto done

:m3
"%PYEXE%" meeting.py --length 3min
goto done

:m5
"%PYEXE%" meeting.py --length 5min
goto done

:done
echo.
echo 대화록은 logs 폴더에 저장됐습니다.
echo.
pause
