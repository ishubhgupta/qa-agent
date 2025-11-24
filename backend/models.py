from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Metadata for an uploaded document"""
    filename: str
    file_type: str
    file_size: int
    upload_time: datetime = Field(default_factory=datetime.now)


class Chunk(BaseModel):
    """Text chunk with metadata"""
    text: str
    metadata: Dict[str, Any]
    chunk_index: int


class ElementSelector(BaseModel):
    """HTML element selector information"""
    element_type: str  # 'input', 'button', 'select', etc.
    element_id: Optional[str] = None
    element_name: Optional[str] = None
    element_class: Optional[str] = None
    css_selector: str
    xpath: str
    text_content: Optional[str] = None
    attributes: Dict[str, str] = Field(default_factory=dict)


class TestCase(BaseModel):
    """Generated test case structure"""
    test_id: str
    feature: str
    test_scenario: str
    preconditions: Optional[str] = None
    steps: List[str]
    expected_result: str
    grounded_in: List[str]
    test_type: str  # 'positive' or 'negative'


class TestCaseRequest(BaseModel):
    """Request for test case generation"""
    feature_query: str
    num_test_cases: int = 5


class TestCaseResponse(BaseModel):
    """Response containing generated test cases"""
    test_cases: List[TestCase]
    context_sources: List[str]
    generation_time: float


class ScriptRequest(BaseModel):
    """Request for Selenium script generation"""
    test_case: TestCase


class ScriptResponse(BaseModel):
    """Response containing generated Selenium script"""
    script: str
    test_id: str
    filename: str
    generation_time: float


class UploadResponse(BaseModel):
    """Response for file upload operations"""
    success: bool
    message: str
    files: List[str] = Field(default_factory=list)


class KBBuildResponse(BaseModel):
    """Response for knowledge base building"""
    success: bool
    num_chunks: int
    num_documents: int
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    chroma_status: str
    timestamp: datetime = Field(default_factory=datetime.now)
