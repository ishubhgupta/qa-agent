#!/usr/bin/env python3
"""
Quick verification that the script generation fix is working
Run this to confirm all components are fixed
"""

import os
import re
from pathlib import Path

def check_script_agent_fix():
    """Verify script_agent.py has the fix"""
    print("🔍 Checking script_agent.py fix...")
    
    script_agent = Path("backend/script_agent.py")
    if not script_agent.exists():
        print("   ❌ backend/script_agent.py not found")
        return False
    
    content = script_agent.read_text(encoding='utf-8')
    
    # Check for new prompt instruction
    if "Output ONLY the raw Python code without any markdown formatting" in content:
        print("   ✅ Prompt fix confirmed")
    else:
        print("   ❌ Old prompt still present")
        return False
    
    # Check for enhanced extraction
    if "Remove any stray backticks" in content:
        print("   ✅ Enhanced extraction confirmed")
    else:
        print("   ❌ Basic extraction still present")
        return False
    
    return True

def check_working_script():
    """Verify working example script exists and is valid"""
    print("\n🔍 Checking working example script...")
    
    script_path = Path("data/generated_scripts/test_TC_001_Discount_Code_WORKING.py")
    if not script_path.exists():
        print("   ❌ Working script not found")
        return False
    
    content = script_path.read_text(encoding='utf-8')
    
    # Check it doesn't start with backticks
    if content.strip().startswith('```'):
        print("   ❌ Script still has triple backticks")
        return False
    else:
        print("   ✅ No triple backticks")
    
    # Check for key components
    checks = {
        "import pytest": "pytest import",
        "def driver():": "WebDriver fixture",
        "def test_apply_save15_discount": "Test function",
        'By.ID, "promo-code"': "Promo code selector",
        'By.ID, "apply-promo"': "Apply button selector",
        'By.ID, "subtotal"': "Subtotal selector",
        "WebDriverWait": "Explicit waits",
        "assert": "Assertions"
    }
    
    for code, desc in checks.items():
        if code in content:
            print(f"   ✅ {desc} present")
        else:
            print(f"   ❌ {desc} missing")
            return False
    
    # Check it's complete (not truncated)
    if "if __name__ ==" in content:
        print("   ✅ Script is complete")
    else:
        print("   ⚠️  Script may be truncated")
        return False
    
    return True

def check_test_runner():
    """Verify test runner script exists"""
    print("\n🔍 Checking test runner script...")
    
    runner_path = Path("test_selenium_script.py")
    if not runner_path.exists():
        print("   ❌ test_selenium_script.py not found")
        return False
    
    content = runner_path.read_text(encoding='utf-8')
    
    if "def check_selenium_setup" in content and "def run_test_script" in content:
        print("   ✅ Test runner complete")
        return True
    else:
        print("   ❌ Test runner incomplete")
        return False

def check_documentation():
    """Verify fix is documented"""
    print("\n🔍 Checking documentation...")
    
    docs_to_check = {
        "README.md": "Generated script has issues",
        "SCRIPT_GENERATION_FIX.md": "Problem Identified",
        "SUBMISSION.md": "Script generation fixed"
    }
    
    all_present = True
    for doc, keyword in docs_to_check.items():
        doc_path = Path(doc)
        if doc_path.exists():
            content = doc_path.read_text(encoding='utf-8')
            if keyword in content:
                print(f"   ✅ {doc} documents fix")
            else:
                print(f"   ⚠️  {doc} may not document fix")
                all_present = False
        else:
            print(f"   ❌ {doc} not found")
            all_present = False
    
    return all_present

def main():
    """Run all verification checks"""
    print("="*70)
    print("🔧 SCRIPT GENERATION FIX VERIFICATION")
    print("="*70 + "\n")
    
    checks = [
        ("Script Agent Fix", check_script_agent_fix),
        ("Working Example Script", check_working_script),
        ("Test Runner Tool", check_test_runner),
        ("Documentation", check_documentation)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - Fix is complete!")
        print("="*70)
        print("\n✨ Next Steps:")
        print("1. Test the working script: python test_selenium_script.py")
        print("2. Generate new test cases via Streamlit UI")
        print("3. Verify new scripts don't have triple backticks")
        print("4. Commit and push to GitHub")
    else:
        print("⚠️  SOME CHECKS FAILED - Review output above")
        print("="*70)
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
