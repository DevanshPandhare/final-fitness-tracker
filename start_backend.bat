@echo off
echo ============================================
echo  NutriPulse AI - Backend Server
echo ============================================
echo.

if "%GEMINI_API_KEY%"=="" (
    echo [WARNING] GEMINI_API_KEY not set. AI features will be disabled.
    echo Set it with: set GEMINI_API_KEY=eAQ.Ab8RN6JxbgIAJ_2_ZJ3HmrXwF4xoJJp0humOZWiilBP9wTzR8Qy
    echo.
)

cd /d "%~dp0backend"
echo Starting backend on http://localhost:8000 ...
echo API Docs available at: http://localhost:8000/docs
echo.

 

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
