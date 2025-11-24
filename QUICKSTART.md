# Quick Start Guide

## 5-Minute Setup

### Step 1: Get Gemini API Key (2 minutes)

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

### Step 2: Setup Project (2 minutes)

**Windows:**
```bash
cd c:\d\Projects\qa-agent
setup.bat
```

**macOS/Linux:**
```bash
cd /path/to/qa-agent
chmod +x setup.sh
./setup.sh
```

### Step 3: Add API Key (30 seconds)

Edit `.env` file:
```env
GEMINI_API_KEY=your_key_here
```

### Step 4: Run Application (30 seconds)

**Windows:**
```bash
run.bat
```

**macOS/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**Or manually:**
```bash
# Terminal 1
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
streamlit run frontend/app.py
```

### Step 5: Use the Application

1. Open http://localhost:8501
2. Upload docs from `assets/docs/` folder
3. Upload `assets/checkout.html`
4. Click "Build Knowledge Base"
5. Generate test cases for "discount code validation"
6. Generate Selenium script for a test case

## Troubleshooting

### "GEMINI_API_KEY not set"
→ Edit `.env` file and add your API key

### "Backend not reachable"
→ Make sure backend is running on port 8000
→ Check http://localhost:8000/health

### "Module not found"
→ Activate virtual environment:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```
→ Install dependencies:
```bash
pip install -r requirements.txt
```

## What to Test

Try these feature queries:
- "discount code validation"
- "shopping cart functionality"
- "checkout form validation"
- "payment processing"
- "shipping method selection"

## Demo Flow

1. **Upload** (1 min)
   - Upload all 3 docs from `assets/docs/`
   - Upload `checkout.html`

2. **Build KB** (30 sec)
   - Click build button
   - Check statistics

3. **Generate Tests** (20 sec)
   - Query: "discount code validation"
   - Get 5 test cases

4. **Generate Script** (20 sec)
   - Select TC_001
   - Generate Selenium script
   - Download the file

## Key Features to Highlight

✅ **Strict Grounding** - All test cases cite source documents
✅ **Real Selectors** - Scripts use actual HTML element IDs/classes
✅ **No Hallucinations** - Only uses provided documentation
✅ **RAG Pipeline** - Vector search with semantic embeddings
✅ **Modern Stack** - FastAPI + Streamlit + ChromaDB + Gemini
✅ **Production Ready** - Proper error handling, validation, logging

## Next Steps

After basic testing:
- Try with your own HTML and docs
- Customize prompts in `test_case_agent.py` and `script_agent.py`
- Adjust chunk size in `.env`
- Explore API at http://localhost:8000/docs
