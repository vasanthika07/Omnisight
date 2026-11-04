@echo off
setlocal
echo ===============================================================================
echo                 OMNISIGHT: MULTIMODAL UI SELF-HEALING SYSTEM
echo ===============================================================================
echo Starting OmniSight Backend and Frontend Services...
echo.

cd /d "%~dp0"

REM 1. Verify Virtual Environment
if not exist ".\.venv\Scripts\python.exe" (
    echo [SETUP] Creating Python virtual environment...
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
    .\.venv\Scripts\python.exe -m playwright install chromium
)

REM 2. Verify Frontend Dependencies
if not exist "frontend\node_modules" (
    echo [SETUP] Installing frontend node dependencies...
    cd frontend && npm install && cd ..
)

REM 3. Launch Backend Server
echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "OmniSight Backend (Port 8000)" cmd /k ".\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 2 /nobreak >nul

REM 4. Launch Frontend Dev Server
echo [2/2] Starting Vite React Dashboard on http://127.0.0.1:5173 ...
start "OmniSight Dashboard (Port 5173)" cmd /k "cd frontend && npm run dev"
timeout /t 2 /nobreak >nul

REM 5. Open Default Browser
start http://127.0.0.1:5173

echo.
echo ===============================================================================
echo OmniSight Services are now running!
echo - QA Dashboard:    http://127.0.0.1:5173
echo - API Server:      http://127.0.0.1:8000
echo - API Docs:        http://127.0.0.1:8000/docs
echo - Staging Store:   http://127.0.0.1:8000/test-app/index.html
echo ===============================================================================
