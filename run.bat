@echo off
echo Starting Autonomous QA Agent...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and add your GEMINI_API_KEY
    pause
    exit /b 1
)

echo [1/2] Starting FastAPI Backend on http://localhost:8000
start "QA Agent - Backend" cmd /k "venv\Scripts\activate && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo [2/2] Starting Streamlit Frontend on http://localhost:8501
start "QA Agent - Frontend" cmd /k "venv\Scripts\activate && streamlit run frontend/app.py"

echo.
echo ========================================
echo   Autonomous QA Agent is starting...
echo ========================================
echo   Frontend: http://localhost:8501
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit this window (services will keep running)
pause >nul
