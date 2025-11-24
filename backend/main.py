import os
import time
import shutil
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.models import (
    TestCaseRequest, TestCaseResponse,
    ScriptRequest, ScriptResponse,
    UploadResponse, KBBuildResponse, HealthResponse
)
from backend.config import Config
from backend.rag import RAGPipeline
from backend.test_case_agent import TestCaseAgent
from backend.script_agent import ScriptAgent
from backend.utils import sanitize_filename, validate_file_extension


app = FastAPI(
    title="Autonomous QA Agent API",
    description="API for generating grounded test cases and Selenium scripts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rag_pipeline = RAGPipeline()
test_case_agent = TestCaseAgent()
script_agent = ScriptAgent()

# Store uploaded file paths
uploaded_documents = []
uploaded_html = None


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        stats = rag_pipeline.get_kb_stats()
        chroma_status = "healthy" if stats["total_chunks"] >= 0 else "error"
    except Exception:
        chroma_status = "error"
    
    return HealthResponse(
        status="healthy",
        chroma_status=chroma_status
    )


@app.post("/upload_docs", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload support documents"""
    global uploaded_documents
    
    if len(files) > Config.MAX_DOCUMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {Config.MAX_DOCUMENTS} documents allowed"
        )
    
    uploaded_files = []
    
    for file in files:
        # Validate file extension
        if not validate_file_extension(file.filename, Config.ALLOWED_EXTENSIONS["documents"]):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Allowed: {Config.ALLOWED_EXTENSIONS['documents']}"
            )
        
        # Sanitize filename
        safe_filename = sanitize_filename(file.filename)
        file_path = Path(Config.UPLOAD_DIRECTORY) / safe_filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(str(file_path))
            uploaded_documents.append(str(file_path))
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error saving file {file.filename}: {str(e)}"
            )
    
    return UploadResponse(
        success=True,
        message=f"{len(uploaded_files)} document(s) uploaded successfully",
        files=[Path(f).name for f in uploaded_files]
    )


@app.post("/upload_html", response_model=UploadResponse)
async def upload_html(file: UploadFile = File(...)):
    """Upload checkout HTML file"""
    global uploaded_html
    
    # Validate file extension
    if not validate_file_extension(file.filename, Config.ALLOWED_EXTENSIONS["html"]):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.filename}. Allowed: {Config.ALLOWED_EXTENSIONS['html']}"
        )
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    file_path = Path(Config.UPLOAD_DIRECTORY) / safe_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        uploaded_html = str(file_path)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving HTML file: {str(e)}"
        )
    
    return UploadResponse(
        success=True,
        message="HTML file uploaded successfully",
        files=[safe_filename]
    )


@app.post("/build_kb", response_model=KBBuildResponse)
async def build_knowledge_base(clear_existing: bool = False):
    """Build knowledge base from uploaded documents"""
    global uploaded_documents, uploaded_html
    
    if not uploaded_documents and not uploaded_html:
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded. Please upload documents first."
        )
    
    # Combine all files
    all_files = uploaded_documents.copy()
    if uploaded_html:
        all_files.append(uploaded_html)
    
    try:
        result = rag_pipeline.build_knowledge_base(all_files, clear_existing)
        
        return KBBuildResponse(
            success=result["success"],
            num_chunks=result["num_chunks"],
            num_documents=result["num_documents"],
            message=f"Knowledge base built with {result['num_chunks']} chunks from {result['num_documents']} documents"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error building knowledge base: {str(e)}"
        )


@app.post("/generate_test_cases", response_model=TestCaseResponse)
async def generate_test_cases(request: TestCaseRequest):
    """Generate test cases for a feature query"""
    
    try:
        start_time = time.time()
        
        # Retrieve context
        context_data = rag_pipeline.retrieve_context(
            request.feature_query,
            top_k=Config.TOP_K_RETRIEVAL
        )
        
        if not context_data["context"] or context_data["context"] == "No relevant context found.":
            raise HTTPException(
                status_code=404,
                detail="No relevant context found in knowledge base. Please ensure documents are uploaded and KB is built."
            )
        
        # Generate test cases
        test_cases = test_case_agent.generate_test_cases(
            request.feature_query,
            context_data["context"],
            request.num_test_cases
        )
        
        generation_time = time.time() - start_time
        
        return TestCaseResponse(
            test_cases=test_cases,
            context_sources=context_data["sources"],
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating test cases: {str(e)}"
        )


@app.post("/generate_script", response_model=ScriptResponse)
async def generate_selenium_script(request: ScriptRequest):
    """Generate Selenium script for a test case"""
    
    try:
        start_time = time.time()
        
        # Get HTML selectors
        html_selectors = rag_pipeline.get_all_html_selectors()
        
        if not html_selectors:
            raise HTTPException(
                status_code=404,
                detail="No HTML selectors found. Please ensure checkout HTML is uploaded and KB is built."
            )
        
        # Retrieve additional context for the feature
        context_data = rag_pipeline.retrieve_context(
            request.test_case.feature,
            top_k=5
        )
        
        # Generate script
        script = script_agent.generate_selenium_script(
            request.test_case,
            html_selectors,
            context_data["context"]
        )
        
        # Validate syntax (non-blocking - just log if there are issues)
        if not script_agent.validate_script_syntax(script):
            print("Warning: Generated script may have syntax issues, but returning anyway")
        
        # Generate filename
        filename = script_agent.generate_script_filename(request.test_case)
        
        # Save script
        script_path = Path(Config.GENERATED_SCRIPTS_DIRECTORY) / filename
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
        
        generation_time = time.time() - start_time
        
        return ScriptResponse(
            script=script,
            test_id=request.test_case.test_id,
            filename=filename,
            generation_time=generation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating script: {str(e)}"
        )


@app.get("/kb_stats")
async def get_kb_stats():
    """Get knowledge base statistics"""
    try:
        stats = rag_pipeline.get_kb_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting KB stats: {str(e)}"
        )


@app.delete("/clear_uploads")
async def clear_uploads():
    """Clear uploaded files"""
    global uploaded_documents, uploaded_html
    
    try:
        # Clear file lists
        uploaded_documents = []
        uploaded_html = None
        
        # Optionally delete files from disk
        upload_dir = Path(Config.UPLOAD_DIRECTORY)
        if upload_dir.exists():
            for file in upload_dir.glob("*"):
                if file.is_file():
                    file.unlink()
        
        return JSONResponse(
            content={"success": True, "message": "Uploads cleared"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing uploads: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
