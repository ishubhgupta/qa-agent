import json
import time
import google.generativeai as genai
from typing import Dict, Any
from backend.models import TestCase
from backend.config import Config


class ScriptAgent:
    """Agent for generating Selenium test scripts"""
    
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def generate_selenium_script(
        self,
        test_case: TestCase,
        html_selectors: Dict[str, Any],
        context: str = ""
    ) -> str:
        """Generate executable Selenium Python script"""
        
        prompt = self._build_prompt(test_case, html_selectors, context)
        
        # Call LLM with retry logic
        response_text = self._call_llm_with_retry(prompt)
        
        # Extract Python code from response
        script = self._extract_python_code(response_text)
        
        return script
    
    def _build_prompt(
        self,
        test_case: TestCase,
        html_selectors: Dict[str, Any],
        context: str
    ) -> str:
        """Build prompt for Selenium script generation"""
        
        # Format test case as JSON for clarity
        test_case_json = json.dumps(test_case.dict(), indent=2)
        
        # Format selectors as JSON
        selectors_json = json.dumps(html_selectors, indent=2)
        
        prompt = f"""Generate a complete Python Selenium pytest script following this EXACT template structure.

TEST CASE:
{test_case_json}

HTML SELECTORS:
{selectors_json}

CONTEXT:
{context}

```python
# STEP 1: Imports (ALWAYS include these)
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "file:///c:/d/Projects/qa-agent/assets/checkout.html"

# STEP 2: Driver fixture (ALWAYS same)
@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# STEP 3: Test function (adapt name and steps to test case)
def test_discount_code_validation(driver):
    wait = WebDriverWait(driver, 10)
    try:
        # Navigate to page
        driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located((By.ID, "checkout-form")))
        
        # BEFORE applying promo: Get initial subtotal
        subtotal_elem = wait.until(EC.presence_of_element_located((By.ID, "subtotal")))
        initial_subtotal = float(subtotal_elem.text)
        
        # Add product (adjust data-id based on test case)
        add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-id='3'] .btn-add-cart")))
        add_btn.click()
        time.sleep(0.5)
        
        # Enter promo code
        promo_input = wait.until(EC.presence_of_element_located((By.ID, "promo-code")))
        promo_input.send_keys("SAVE15")
        
        # Apply promo
        apply_btn = wait.until(EC.element_to_be_clickable((By.ID, "apply-promo")))
        apply_btn.click()
        time.sleep(0.5)
        
        # Check success message (flexible checking)
        msg_elem = wait.until(EC.visibility_of_element_located((By.ID, "promo-message")))
        assert "success" in msg_elem.text.lower() or "applied" in msg_elem.text.lower()
        
        # Verify discount amount (NOT subtotal - subtotal stays same!)
        disc_elem = wait.until(EC.presence_of_element_located((By.ID, "discount")))
        disc_amount = float(disc_elem.text)
        expected_disc = round(initial_subtotal * 0.15, 2)
        assert disc_amount == expected_disc
        
        print("✅ TEST PASSED")
    except Exception as e:
        driver.save_screenshot(f"failure_{time.time()}.png")
        raise

# STEP 4: Main block (ALWAYS same)
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
```

CRITICAL RULES:
1. Get initial_subtotal BEFORE applying promo (it's needed for expected discount calculation)
2. Selenium syntax: (By.ID, "value") is a TUPLE - use parentheses and comma
3. Success message: assert "success" in msg_elem.text.lower() - NEVER check exact text
4. Validate discount element (By.ID, "discount") - NOT subtotal (subtotal never changes)
5. Product buttons: [data-id='X'] .btn-add-cart where X is 1, 2, or 3
6. Add time.sleep(0.5) after clicks
7. Include 'import time' at top

OUTPUT: Raw Python code only, no markdown fences, no explanations
2. COMPLETE script - imports, BASE_URL, fixture, test function, exception handling, if __name__ block
3. Must be 100+ lines for a proper test with all steps, assertions, and error handling
4. Include ALL imports at top, ALL test steps in order, ALL assertions
5. End with: if __name__ == "__main__": pytest.main([__file__, "-v", "-s"])

Generate the COMPLETE executable script now:"""
        
        return prompt
    
    def _call_llm_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Call Gemini API with retry logic"""
        
        for attempt in range(max_retries):
            try:
                # Use higher token limit for script generation (scripts are longer)
                max_tokens = 8192  # Increased from 4096 for complete scripts
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=Config.LLM_TEMPERATURE,
                        max_output_tokens=max_tokens,
                    )
                )
                
                # Handle different response types - check candidates first
                # This avoids the "response.text quick accessor" error for multi-part responses
                if response.candidates and len(response.candidates) > 0:
                    # Extract text from all parts in the first candidate
                    if hasattr(response.candidates[0], 'content'):
                        parts = response.candidates[0].content.parts
                        text = ''.join(part.text for part in parts if hasattr(part, 'text'))
                        if text.strip():
                            return text.strip()
                
                # Fallback to direct text access (for simple responses)
                try:
                    if hasattr(response, 'text'):
                        text = response.text
                        if text and text.strip():
                            return text.strip()
                except Exception as e:
                    print(f"Warning: response.text accessor failed: {e}")
                
                # If we get here, we couldn't extract text
                raise Exception(f"Could not extract text from LLM response. Response type: {type(response)}")
                
            except Exception as e:
                print(f"LLM API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise Exception(f"Failed to call LLM API after {max_retries} attempts: {e}")
    
    def _extract_python_code(self, response_text: str) -> str:
        """Extract Python code from LLM response"""
        
        import re
        
        # Remove any leading/trailing markdown artifacts
        cleaned_text = response_text.strip()
        
        # Try to find code in markdown code blocks with 'python' specifier
        code_match = re.search(r'```python\s*(.*?)\s*```', cleaned_text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Try to find code without language specifier
        code_match = re.search(r'```\s*(.*?)\s*```', cleaned_text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Remove any stray backticks at the start/end
        cleaned_text = re.sub(r'^```python\s*', '', cleaned_text)
        cleaned_text = re.sub(r'^```\s*', '', cleaned_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
        
        # If no code blocks found, return the cleaned response
        return cleaned_text.strip()
    
    def validate_script_syntax(self, script: str) -> bool:
        """Validate Python syntax of generated script"""
        try:
            compile(script, '<string>', 'exec')
            return True
        except SyntaxError as e:
            print(f"Syntax error in generated script: {e}")
            return False
    
    def generate_script_filename(self, test_case: TestCase) -> str:
        """Generate a descriptive filename for the script"""
        # Sanitize test_id for filename
        safe_id = test_case.test_id.replace(" ", "_").replace("/", "_")
        
        # Create a short description from feature
        safe_feature = test_case.feature.replace(" ", "_").replace("/", "_")
        safe_feature = safe_feature[:30]  # Limit length
        
        return f"test_{safe_id}_{safe_feature}.py"
