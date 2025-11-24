"""
Verify that all dependencies and configuration are correct
"""
import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required. Current:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "streamlit",
        "chromadb",
        "sentence_transformers",
        "google.generativeai",
        "bs4",
        "pymupdf",
        "selenium",
        "pydantic",
        "requests"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    return len(missing) == 0

def check_env_file():
    """Check if .env file exists and has API key"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Run: copy .env.example .env")
        return False
    
    print("✅ .env file exists")
    
    # Check for API key
    with open(env_path) as f:
        content = f.read()
        if "your_gemini_api_key_here" in content or "GEMINI_API_KEY=" not in content:
            print("⚠️  Warning: GEMINI_API_KEY not set in .env")
            print("   Get your key from: https://makersuite.google.com/app/apikey")
            return False
    
    print("✅ GEMINI_API_KEY configured")
    return True

def check_directories():
    """Check if required directories exist"""
    dirs = [
        "data/chroma_db",
        "data/uploads",
        "data/generated_scripts",
        "assets/docs"
    ]
    
    all_exist = True
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_assets():
    """Check if example assets exist"""
    assets = [
        "assets/checkout.html",
        "assets/docs/product_specs.md",
        "assets/docs/ui_ux_guide.txt",
        "assets/docs/api_endpoints.json"
    ]
    
    all_exist = True
    for asset in assets:
        path = Path(asset)
        if path.exists():
            print(f"✅ {asset}")
        else:
            print(f"❌ {asset} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("  Autonomous QA Agent - Setup Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    print("Checking Python version...")
    checks.append(check_python_version())
    print()
    
    print("Checking dependencies...")
    checks.append(check_dependencies())
    print()
    
    print("Checking environment configuration...")
    checks.append(check_env_file())
    print()
    
    print("Checking directories...")
    checks.append(check_directories())
    print()
    
    print("Checking example assets...")
    checks.append(check_assets())
    print()
    
    print("=" * 60)
    if all(checks):
        print("✅ All checks passed! You're ready to run the application.")
        print()
        print("To start:")
        print("  Windows: run.bat")
        print("  macOS/Linux: ./run.sh")
        print()
        print("Or manually:")
        print("  Terminal 1: python -m uvicorn backend.main:app --port 8000")
        print("  Terminal 2: streamlit run frontend/app.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print()
        print("To setup:")
        print("  Windows: setup.bat")
        print("  macOS/Linux: ./setup.sh")
    print("=" * 60)

if __name__ == "__main__":
    main()
