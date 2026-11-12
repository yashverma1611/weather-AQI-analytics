@echo off
title Weather and AQI Analytics Launcher
color 0b
cd /d "%~dp0"

echo =========================================================
echo    Starting Weather & Air Quality Analytics Platform
echo =========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your system PATH!
    echo.
    echo To fix this:
    echo   1. Install Python 3.12 (Check "Add Python to PATH" during installation)
    echo   2. Or run setup_environment.bat in the parent directory.
    echo   3. Or double-click demo\index.html to view the instant working demo in your browser!
    echo.
    start "" "demo\index.html"
    pause
    exit /b
)

echo Installing dependencies (Streamlit, Plotly, Scikit-learn)...
pip install -r requirements.txt

echo Starting Streamlit analytics server...
start "" "http://localhost:8501"
streamlit run app.py
pause
