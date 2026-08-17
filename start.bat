@echo off
chcp 65001 >nul
cd /d %~dp0
start "C学习平台" /min cmd /c ".venv\Scripts\python -m uvicorn app.main:app --port 8000"
timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000
