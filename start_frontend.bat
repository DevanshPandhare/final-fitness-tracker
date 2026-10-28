@echo off
echo ============================================
echo  NutriPulse AI - Frontend Server
echo ============================================
echo.
cd /d "%~dp0frontend"
echo Starting frontend on http://localhost:5173 ...
echo.
npm run dev
pause
