# 🤖 Autonomous QA Agent

An intelligent QA agent that generates grounded test cases and executable Selenium scripts from e-commerce checkout documentation. The system uses RAG (Retrieval-Augmented Generation) with vector embeddings to ensure all generated test cases are strictly grounded in provided documents - **no hallucinations!**

## 🎯 Features

- **Document Ingestion**: Parse HTML, PDF, Markdown, TXT, and JSON files
- **Vector Knowledge Base**: ChromaDB-powered semantic search with sentence embeddings
- **Test Case Generation**: Create comprehensive, grounded test cases using Google Gemini
- **Selenium Script Generation**: Generate executable Python Selenium scripts with actual HTML selectors
- **Strict Grounding**: All test cases reference source documents with full traceability
- **Modern UI**: Streamlit frontend with intuitive workflow
- **REST API**: FastAPI backend with comprehensive endpoints

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Example Assets](#example-assets)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## ⚙️ Prerequisites

- **Python**: 3.9 or higher
- **API Key**: Google Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))
- **RAM**: Minimum 4GB (for embedding model)
- **OS**: Windows, macOS, or Linux

## 🚀 Installation

### 1. Clone or Download the Repository

```bash
cd c:\d\Projects\qa-agent
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (backend server)
- Streamlit (frontend UI)
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- google-generativeai (LLM)
- BeautifulSoup4, pymupdf (document parsing)
- Selenium (script generation)

## 🔑 Configuration

### 1. Set Up Environment Variables

Copy the example environment file:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### 2. Add Your Gemini API Key

Open `.env` file and add your API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

**To get a Gemini API key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in `.env`

### 3. Optional Configuration

You can customize these settings in `.env`:

```env
# Directories
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
UPLOAD_DIRECTORY=./data/uploads
GENERATED_SCRIPTS_DIRECTORY=./data/generated_scripts

# Model Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096

# Chunking Settings
CHUNK_SIZE=750
CHUNK_OVERLAP=100
TOP_K_RETRIEVAL=10
```

## 🎮 Running the Application

The application consists of two parts: Backend (FastAPI) and Frontend (Streamlit).

### Option 1: Run Both Services (Recommended)

**Terminal 1 - Start Backend:**

```bash
cd c:\d\Projects\qa-agent
venv\Scripts\activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**

```bash
cd c:\d\Projects\qa-agent
venv\Scripts\activate
streamlit run frontend/app.py
```

### Option 2: Quick Start Script

Create a `run.bat` file (Windows):

```batch
@echo off
start cmd /k "venv\Scripts\activate && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
timeout /t 3
start cmd /k "venv\Scripts\activate && streamlit run frontend/app.py"
```

For macOS/Linux, create `run.sh`:

```bash
#!/bin/bash
source venv/bin/activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 3
streamlit run frontend/app.py
```

### Access the Application

- **Streamlit UI**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## 📖 Usage Guide

### Step 1: Upload Documents

1. Open the Streamlit UI at http://localhost:8501
2. Go to the **"Upload Documents"** tab
3. Upload 1-5 support documents (MD, TXT, PDF, or JSON)
4. Upload your checkout HTML file
5. Click the respective upload buttons

**Example documents included in `assets/docs/`:**
- `product_specs.md` - Product and feature specifications
- `ui_ux_guide.txt` - UI/UX design guidelines
- `api_endpoints.json` - API endpoint documentation

### Step 2: Build Knowledge Base

1. Go to the **"Build Knowledge Base"** tab
2. Click **"Build Knowledge Base"** button
3. Wait for processing (usually 10-30 seconds)
4. View statistics showing chunks created

**What happens:**
- Documents are parsed and chunked (750 chars with 100 char overlap)
- HTML elements are extracted with selectors
- Embeddings are generated using sentence-transformers
- Data is stored in ChromaDB vector database

### Step 3: Generate Test Cases

1. Go to the **"Generate Test Cases"** tab
2. Enter a feature query, for example:
   - "discount code validation"
   - "checkout form validation"
   - "shopping cart functionality"
   - "payment processing"
3. Set the number of test cases (1-10)
4. Click **"Generate Test Cases"**
5. Wait 10-20 seconds for generation

**Example Output:**
```
Test ID: TC_001
Feature: Discount Code Validation
Scenario: Apply valid discount code SAVE15
Test Type: Positive

Steps:
1. Add products to cart
2. Enter promo code "SAVE15" in the promo code field
3. Click "Apply" button

Expected Result: 
Discount of 15% is applied to subtotal and displayed

Grounded In: product_specs.md, checkout.html
```

### Step 4: Generate Selenium Script

1. Select a test case from the expanded list
2. Click **"Generate Script for [Test ID]"**
3. Go to the **"Generate Scripts"** tab
4. Click **"Generate Selenium Script"**
5. Wait 10-20 seconds for generation
6. View the generated Python script
7. Click **"Download Script"** to save the file

**Generated Script Example:**
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

def test_apply_discount_code_save15(driver):
    # Test implementation with actual selectors
    driver.get("file:///path/to/checkout.html")
    
    # Add product to cart
    add_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-add-cart"))
    )
    add_button.click()
    
    # Apply promo code
    promo_input = driver.find_element(By.ID, "promo-code")
    promo_input.send_keys("SAVE15")
    
    apply_button = driver.find_element(By.ID, "apply-promo")
    apply_button.click()
    
    # Verify discount applied
    discount_elem = driver.find_element(By.ID, "discount")
    assert float(discount_elem.text) > 0
```

## 📁 Project Structure

```
qa-agent/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints
│   ├── config.py              # Configuration
│   ├── models.py              # Pydantic models
│   ├── utils.py               # Utility functions
│   ├── ingestion.py           # Document parsing
│   ├── vector_store.py        # ChromaDB interface
│   ├── rag.py                 # RAG pipeline
│   ├── test_case_agent.py     # Test case generation
│   └── script_agent.py        # Selenium script generation
├── frontend/                   # Streamlit frontend
│   └── app.py                 # UI application
├── assets/                     # Example files
│   ├── checkout.html          # Sample checkout page
│   └── docs/                  # Support documents
│       ├── product_specs.md
│       ├── ui_ux_guide.txt
│       └── api_endpoints.json
├── data/                       # Runtime data (created automatically)
│   ├── chroma_db/             # Vector database
│   ├── uploads/               # Uploaded files
│   └── generated_scripts/     # Generated scripts
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment variables
├── .env                      # Your environment variables (create this)
└── README.md                 # This file
```

## 🎯 Example Assets

The `assets/` directory contains a complete example checkout system:

### checkout.html

A fully functional e-commerce checkout page with:
- **3 Products**: Wireless Headphones ($79.99), Smart Watch ($199.99), Laptop Stand ($49.99)
- **Shopping Cart**: Add/remove items, update quantities
- **Promo Codes**: SAVE15 (15% off), SAVE20 (20% off), FREESHIP
- **Customer Form**: Name, email, phone, address validation
- **Shipping Options**: Standard (free) or Express ($10)
- **Payment Methods**: Credit Card or PayPal
- **JavaScript**: Client-side validation and cart management

### Support Documents

1. **product_specs.md**
   - Product catalog with prices and IDs
   - Discount code specifications
   - Shipping method details
   - Form validation rules
   - Order calculation logic

2. **ui_ux_guide.txt**
   - Design principles and color scheme
   - Button and form field guidelines
   - Error and success message formats
   - Component specifications
   - Accessibility requirements

3. **api_endpoints.json**
   - REST API endpoint documentation
   - Request/response schemas
   - Data models
   - Error codes
   - Valid promo codes

## 🔌 API Documentation

### Health Check
```http
GET /health
```

### Upload Documents
```http
POST /upload_docs
Content-Type: multipart/form-data

files: List[File]  # Max 5 files: .md, .txt, .pdf, .json
```

### Upload HTML
```http
POST /upload_html
Content-Type: multipart/form-data

file: File  # Single .html file
```

### Build Knowledge Base
```http
POST /build_kb?clear_existing=false
```

### Generate Test Cases
```http
POST /generate_test_cases
Content-Type: application/json

{
  "feature_query": "discount code validation",
  "num_test_cases": 5
}
```

### Generate Selenium Script
```http
POST /generate_script
Content-Type: application/json

{
  "test_case": {
    "test_id": "TC_001",
    "feature": "Discount Code",
    "test_scenario": "Apply valid code",
    "steps": [...],
    "expected_result": "...",
    "grounded_in": [...],
    "test_type": "positive"
  }
}
```

### Get KB Statistics
```http
GET /kb_stats
```

Full API documentation available at: http://localhost:8000/docs

## 🐛 Troubleshooting

### Backend Won't Start

**Error: "GEMINI_API_KEY not set"**
- Solution: Add your API key to `.env` file

**Error: "Module not found"**
- Solution: Ensure virtual environment is activated and dependencies installed:
  ```bash
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

### Frontend Connection Issues

**Error: "Backend not reachable"**
- Solution: Ensure backend is running on port 8000
- Check: http://localhost:8000/health

**Error: "Connection Error"**
- Solution: Disable firewall or allow localhost connections

### Knowledge Base Issues

**Error: "No relevant context found"**
- Solution: Ensure you've built the knowledge base after uploading documents
- Try different query terms

**Error: "ChromaDB error"**
- Solution: Delete `data/chroma_db/` folder and rebuild KB

### Generation Issues

**Test cases take too long**
- Normal: 10-20 seconds is expected for LLM generation
- Check internet connection for API calls

**Generated script has issues**
- **Problem**: Script contains triple backticks (```python) at the start
- **Solution**: Fixed in latest version - script_agent.py now strips markdown
- **Workaround**: Use the WORKING version in `data/generated_scripts/test_TC_001_Discount_Code_WORKING.py`
- **Test**: Run `python test_selenium_script.py` to verify scripts work

### General Tips

1. **First Run**: Initial setup downloads embedding model (~80MB)
2. **API Limits**: Gemini API has rate limits (check Google AI Studio)
3. **Port Conflicts**: Change ports if 8000 or 8501 are in use
4. **Memory**: Close other applications if system is slow

## 🧪 Running Generated Selenium Scripts

Once you've generated Selenium scripts via the UI:

### Quick Test
```bash
# Verify the working example script
python test_selenium_script.py
```

### Run Specific Script
```bash
# Navigate to scripts directory
cd data/generated_scripts

# Run a specific test
pytest test_TC_001_Discount_Code_WORKING.py -v -s

# Run all tests
pytest test_*.py -v -s
```

### Requirements for Selenium
- **ChromeDriver**: Must be installed and in PATH
- **Chrome Browser**: Compatible version with ChromeDriver
- **pytest**: Already in requirements.txt

### Troubleshooting Selenium

**ChromeDriver version mismatch**
```bash
# Check Chrome version
chrome --version

# Download matching ChromeDriver from:
# https://chromedriver.chromium.org/downloads
```

**Script assertions fail**
- Check that `checkout.html` is accessible
- Verify BASE_URL in script points to correct path
- Clear browser cache/cookies
- Check element selectors match actual HTML

## 🔧 Development

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=backend
```

### Code Style
```bash
# Install formatting tools
pip install black flake8

# Format code
black backend/ frontend/

# Lint
flake8 backend/ frontend/
```

## 📝 Notes

- **Grounding**: All test cases include `grounded_in` field citing source documents
- **Selectors**: Generated scripts use actual HTML element selectors from uploaded page
- **Case-Insensitive**: Promo codes work in any case (SAVE15 = save15)
- **Validation**: Form validation matches HTML5 rules in checkout page
- **Persistence**: ChromaDB data persists between sessions

## 🎥 Demo Video Script

**Suggested recording flow:**

1. **Introduction** (30s)
   - Show project structure
   - Explain the problem (hallucinated tests)
   - Explain the solution (grounded RAG)

2. **Upload Documents** (1 min)
   - Show the 3 support documents
   - Show checkout.html
   - Upload all files via UI

3. **Build KB** (1 min)
   - Click build button
   - Show statistics
   - Explain what's happening

4. **Generate Test Cases** (2 min)
   - Query: "discount code validation"
   - Show 5 generated test cases
   - Highlight grounding citations

5. **Generate Script** (2 min)
   - Select a test case
   - Generate Selenium script
   - Show the actual selectors used
   - Download the script

6. **Conclusion** (30s)
   - Recap key features
   - Show API docs
   - Mention extensibility

## 📄 License

This project is provided as-is for educational and evaluation purposes.

## 🙋 Support

For issues or questions:
1. Check this README first
2. Review API documentation at http://localhost:8000/docs
3. Check console logs for detailed error messages

---

**Built with:** FastAPI • Streamlit • ChromaDB • Gemini • Sentence Transformers • Selenium
