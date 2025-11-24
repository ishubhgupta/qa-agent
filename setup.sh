#!/bin/bash

echo "========================================"
echo "  Autonomous QA Agent - Setup"
echo "========================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created"

echo ""
echo "[2/5] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "[3/5] Installing dependencies..."
echo "This may take a few minutes..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"

echo ""
echo "[4/5] Creating .env file..."
if [ -f ".env" ]; then
    echo ".env file already exists, skipping..."
else
    cp .env.example .env
    echo "✓ .env file created"
fi

echo ""
echo "[5/5] Creating data directories..."
mkdir -p data/chroma_db
mkdir -p data/uploads
mkdir -p data/generated_scripts
echo "✓ Data directories created"

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "NEXT STEPS:"
echo "1. Edit .env file and add your GEMINI_API_KEY"
echo "   Get your key from: https://makersuite.google.com/app/apikey"
echo ""
echo "2. Make run.sh executable:"
echo "   chmod +x run.sh"
echo ""
echo "3. Run the application:"
echo "   ./run.sh"
echo ""
echo "4. Or run manually:"
echo "   Terminal 1: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
echo "   Terminal 2: streamlit run frontend/app.py"
echo ""
echo "========================================"
