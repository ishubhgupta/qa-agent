@echo off
echo ========================================
echo   Autonomous QA Agent - Setup
echo ========================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created

echo.
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

echo.
echo [3/5] Installing dependencies...
echo This may take a few minutes...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [4/5] Creating .env file...
if exist .env (
    echo .env file already exists, skipping...
) else (
    copy .env.example .env
    echo ✓ .env file created
)

echo.
echo [5/5] Creating data directories...
if not exist data\chroma_db mkdir data\chroma_db
if not exist data\uploads mkdir data\uploads
if not exist data\generated_scripts mkdir data\generated_scripts
echo ✓ Data directories created

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Edit .env file and add your GEMINI_API_KEY
echo    Get your key from: https://makersuite.google.com/app/apikey
echo.
echo 2. Run the application:
echo    run.bat
echo.
echo 3. Or run manually:
echo    Terminal 1: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
echo    Terminal 2: streamlit run frontend/app.py
echo.
echo ========================================
pause
