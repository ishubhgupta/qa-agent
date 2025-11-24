#!/bin/bash

echo "Starting Autonomous QA Agent..."
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    echo "Then install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and add your GEMINI_API_KEY"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "[1/2] Starting FastAPI Backend on http://localhost:8000"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 5

echo "[2/2] Starting Streamlit Frontend on http://localhost:8501"
streamlit run frontend/app.py &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "  Autonomous QA Agent is running!"
echo "========================================"
echo "  Frontend: http://localhost:8501"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
