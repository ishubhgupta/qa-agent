import json
import time
import google.generativeai as genai
from typing import List, Dict, Any
from backend.models import TestCase
from backend.config import Config
from backend.utils import extract_json_from_text


class TestCaseAgent:
    """Agent for generating grounded test cases"""
    
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def generate_test_cases(
        self,
        feature_query: str,
        context: str,
        num_test_cases: int = 5
    ) -> List[TestCase]:
        """Generate test cases with strict grounding"""
        
        prompt = self._build_prompt(feature_query, context, num_test_cases)
        
        # Call LLM with retry logic
        response_text = self._call_llm_with_retry(prompt)
        
        # Parse response into test cases
        test_cases = self._parse_test_cases(response_text)
        
        return test_cases
    
    def _build_prompt(self, feature_query: str, context: str, num_test_cases: int) -> str:
        """Build prompt for test case generation"""
        
        prompt = f"""You are an expert QA test case generator. Your role is to create comprehensive, grounded test cases based strictly on provided documentation.

CRITICAL GROUNDING RULES:
1. Use ONLY information from the RETRIEVED CONTEXT below
2. Every test case MUST include "grounded_in" field with source document names
3. If information is missing, respond: "Not specified in documents"
4. Do NOT use general knowledge or assumptions
5. Generate both POSITIVE and NEGATIVE test scenarios
6. Each test case must be realistic and executable

{context}

FEATURE QUERY: {feature_query}

OUTPUT FORMAT:
Generate a JSON array of test cases. Each test case must follow this exact schema:

{{
  "test_id": "TC_XXX",
  "feature": "Feature name",
  "test_scenario": "Clear description of what is being tested",
  "preconditions": "Required setup or initial state",
  "steps": ["Step 1", "Step 2", "Step 3"],
  "expected_result": "What should happen when test passes",
  "grounded_in": ["source_file1.md", "source_file2.html"],
  "test_type": "positive" or "negative"
}}

REQUIREMENTS:
- Generate {num_test_cases} test cases
- Include at least 60% positive and 40% negative scenarios
- Each test case must reference specific elements/features from the context
- Steps must be clear, actionable, and sequential
- Expected results must be specific and verifiable
- grounded_in field must list actual source documents from the context

Generate the test cases now as a JSON array:"""
        
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
    
    def _parse_test_cases(self, response_text: str) -> List[TestCase]:
        """Parse LLM response into TestCase objects"""
        
        try:
            # Extract JSON from response
            json_text = extract_json_from_text(response_text)
            
            # Parse JSON
            test_cases_data = json.loads(json_text)
            
            # Ensure it's a list
            if not isinstance(test_cases_data, list):
                test_cases_data = [test_cases_data]
            
            # Convert to TestCase objects
            test_cases = []
            for idx, tc_data in enumerate(test_cases_data):
                try:
                    # Ensure required fields exist
                    if "test_id" not in tc_data:
                        tc_data["test_id"] = f"TC_{idx + 1:03d}"
                    
                    if "grounded_in" not in tc_data or not tc_data["grounded_in"]:
                        tc_data["grounded_in"] = ["Not specified"]
                    
                    if "test_type" not in tc_data:
                        tc_data["test_type"] = "positive"
                    
                    # Create TestCase object
                    test_case = TestCase(**tc_data)
                    test_cases.append(test_case)
                    
                except Exception as e:
                    print(f"Error parsing test case {idx}: {e}")
                    continue
            
            return test_cases
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            raise Exception(f"Failed to parse test cases from LLM response: {e}")
    
    def validate_test_case(self, test_case: TestCase, context_sources: List[str]) -> bool:
        """Validate if test case is properly grounded"""
        
        # Check if grounded_in field is populated
        if not test_case.grounded_in or test_case.grounded_in == ["Not specified"]:
            return False
        
        # Check if at least one source exists in context
        for source in test_case.grounded_in:
            if any(source.lower() in context_source.lower() for context_source in context_sources):
                return True
        
        return False
