@echo off
cd /d "%~dp0"
py -3.12 run.py --mode week %*
pause
