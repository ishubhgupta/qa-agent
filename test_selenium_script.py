#!/usr/bin/env python3
"""
Script to test the generated Selenium test script
Run this to verify TC_001 works correctly
"""

import subprocess
import sys
import os
from pathlib import Path

def check_selenium_setup():
    """Check if Selenium and ChromeDriver are available"""
    print("🔍 Checking Selenium setup...")
    
    try:
        import selenium
        print(f"✅ Selenium installed: {selenium.__version__}")
    except ImportError:
        print("❌ Selenium not installed")
        print("   Run: pip install selenium")
        return False
    
    try:
        from selenium import webdriver
        driver = webdriver.Chrome()
        driver.quit()
        print("✅ ChromeDriver available")
    except Exception as e:
        print(f"❌ ChromeDriver issue: {e}")
        print("   Install ChromeDriver: https://chromedriver.chromium.org/")
        return False
    
    return True

def check_pytest():
    """Check if pytest is installed"""
    print("\n🔍 Checking pytest...")
    try:
        import pytest
        print(f"✅ pytest installed: {pytest.__version__}")
        return True
    except ImportError:
        print("❌ pytest not installed")
        print("   Run: pip install pytest")
        return False

def run_test_script(script_path):
    """Run the Selenium test script"""
    print(f"\n🚀 Running test script: {script_path}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", script_path, "-v", "-s"],
            cwd=Path(script_path).parent,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n" + "="*70)
            print("✅ TEST PASSED!")
            print("="*70)
            return True
        else:
            print("\n" + "="*70)
            print("❌ TEST FAILED!")
            print("="*70)
            return False
            
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        return False

def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("🧪 QA Agent - Selenium Test Verification")
    print("="*70 + "\n")
    
    # Check prerequisites
    if not check_pytest():
        print("\n⚠️  Please install pytest first: pip install pytest")
        return False
    
    if not check_selenium_setup():
        print("\n⚠️  Please fix Selenium/ChromeDriver setup")
        return False
    
    # Find test script
    script_dir = Path(__file__).parent / "data" / "generated_scripts"
    working_script = script_dir / "test_TC_001_Discount_Code_WORKING.py"
    
    if not working_script.exists():
        print(f"\n❌ Test script not found: {working_script}")
        print("   Make sure you've generated test cases first")
        return False
    
    print(f"\n✅ Found test script: {working_script.name}")
    
    # Run the test
    success = run_test_script(str(working_script))
    
    if success:
        print("\n🎉 All tests passed! The generated Selenium script works correctly.")
        print("\n📝 You can now:")
        print("   1. Generate more test cases in the Streamlit UI")
        print("   2. Generate Selenium scripts for other test cases")
        print("   3. Run them with: pytest data/generated_scripts/<script_name>.py -v -s")
    else:
        print("\n⚠️  Tests failed. Check the output above for details.")
        print("   Common issues:")
        print("   - ChromeDriver version mismatch with Chrome browser")
        print("   - Checkout.html not accessible")
        print("   - Cart state from previous test runs")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
