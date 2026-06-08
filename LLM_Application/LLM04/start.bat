@echo off
cd /d "%~dp0"
pip install -r requirements.txt -q
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
