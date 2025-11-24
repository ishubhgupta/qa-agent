import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Directories
    BASE_DIR = Path(__file__).parent.parent
    CHROMA_PERSIST_DIRECTORY = os.getenv(
        "CHROMA_PERSIST_DIRECTORY", 
        str(BASE_DIR / "data" / "chroma_db")
    )
    UPLOAD_DIRECTORY = os.getenv(
        "UPLOAD_DIRECTORY",
        str(BASE_DIR / "data" / "uploads")
    )
    GENERATED_SCRIPTS_DIRECTORY = os.getenv(
        "GENERATED_SCRIPTS_DIRECTORY",
        str(BASE_DIR / "data" / "generated_scripts")
    )
    
    # Ensure directories exist
    Path(CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)
    Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)
    Path(GENERATED_SCRIPTS_DIRECTORY).mkdir(parents=True, exist_ok=True)
    
    # Embedding Model
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # LLM Settings
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    LLM_TIMEOUT = 30
    
    # Chunking Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "750"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
    
    # File Upload Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {
        "documents": [".md", ".txt", ".pdf", ".json"],
        "html": [".html", ".htm"]
    }
    MAX_DOCUMENTS = 5
