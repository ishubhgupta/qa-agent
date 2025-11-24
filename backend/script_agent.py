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
        
        prompt = f"""You are a Selenium test automation expert. Generate a complete, executable Python Selenium script for the following test case.

STRICT RULES:
1. Use ONLY the provided HTML selectors below
2. Include WebDriverWait for dynamic elements (use explicit waits, not time.sleep)
3. Implement ALL test steps in sequence
4. Add assertions for expected results
5. Include proper setup and teardown
6. Use pytest framework
7. Add comments for clarity
8. Handle potential exceptions gracefully
9. Use appropriate Selenium best practices

TEST CASE:
{test_case_json}

AVAILABLE HTML SELECTORS:
{selectors_json}

CONTEXT FROM DOCUMENTATION:
{context}

Generate a complete, executable Python script using pytest and Selenium WebDriver.
Include:
- Proper imports (selenium, pytest, WebDriverWait, etc.)
- Setup fixture for WebDriver initialization
- Test function implementing all steps
- Explicit waits for elements
- Assertions for expected results
- Proper error handling
- Teardown/cleanup

IMPORTANT: Output ONLY the raw Python code without any markdown formatting, code blocks, or explanations.
Do NOT wrap the code in ```python or ``` markers. Just output the executable Python code directly."""
        
        return prompt
    
    def _call_llm_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Call Gemini API with retry logic"""
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=Config.LLM_TEMPERATURE,
                        max_output_tokens=Config.LLM_MAX_TOKENS,
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
