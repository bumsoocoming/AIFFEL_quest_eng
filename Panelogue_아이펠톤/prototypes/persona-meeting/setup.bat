@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ============================================
echo   회의 프로그램 설치 (처음 한 번만)
echo ============================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (set PY=py -3) else (set PY=python)

%PY% --version >nul 2>nul
if not %errorlevel%==0 (
  echo [실패] 파이썬이 없습니다.
  echo        https://www.python.org/downloads/ 에서 설치하세요.
  echo        설치 화면 맨 아래 "Add python.exe to PATH" 체크 필수입니다.
  pause
  exit /b 1
)

echo [1/3] 전용 공간 만드는 중...
%PY% -m venv .venv
if not %errorlevel%==0 (echo [실패] 가상환경 생성 실패 & pause & exit /b 1)

echo [2/3] 필요한 것 설치 중... (1~2분 걸립니다)
call .venv\Scripts\python.exe -m pip install --quiet --upgrade pip
call .venv\Scripts\python.exe -m pip install --quiet openai pyyaml python-dotenv
if not %errorlevel%==0 (echo [실패] 설치 실패. 인터넷 연결을 확인하세요. & pause & exit /b 1)

echo [3/3] 키 파일 확인 중...
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo   .env 파일을 만들었습니다.
  echo   메모장으로 열어서 전달받은 키를 붙여넣고 저장하세요.
  echo.
  notepad .env
)

echo.
echo 설치 완료. 이제 run.bat 을 실행하세요.
echo.
pause
