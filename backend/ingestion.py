import json
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from backend.models import ElementSelector, DocumentMetadata
from backend.utils import clean_text, chunk_text
from backend.config import Config


class DocumentParser:
    """Parse different document formats"""
    
    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """Parse file based on extension"""
        ext = Path(file_path).suffix.lower()
        
        parsers = {
            '.html': DocumentParser.parse_html,
            '.htm': DocumentParser.parse_html,
            '.md': DocumentParser.parse_markdown,
            '.txt': DocumentParser.parse_txt,
            '.json': DocumentParser.parse_json,
            '.pdf': DocumentParser.parse_pdf
        }
        
        parser = parsers.get(ext)
        if not parser:
            raise ValueError(f"Unsupported file type: {ext}")
        
        return parser(file_path)
    
    @staticmethod
    def parse_html(file_path: str) -> Dict[str, Any]:
        """Parse HTML file and extract text and structure"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        text = clean_text(text)
        
        # Extract selectors
        selectors = HTMLParser.extract_selectors(content)
        
        return {
            "text": text,
            "raw_html": content,
            "selectors": selectors,
            "type": "html"
        }
    
    @staticmethod
    def parse_markdown(file_path: str) -> Dict[str, Any]:
        """Parse Markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "text": clean_text(content),
            "type": "markdown"
        }
    
    @staticmethod
    def parse_txt(file_path: str) -> Dict[str, Any]:
        """Parse text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "text": clean_text(content),
            "type": "text"
        }
    
    @staticmethod
    def parse_json(file_path: str) -> Dict[str, Any]:
        """Parse JSON file and convert to readable text"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to readable text format
        text = json.dumps(data, indent=2)
        
        return {
            "text": text,
            "data": data,
            "type": "json"
        }
    
    @staticmethod
    def parse_pdf(file_path: str) -> Dict[str, Any]:
        """Parse PDF file using pymupdf"""
        doc = fitz.open(file_path)
        text_parts = []
        
        for page in doc:
            text_parts.append(page.get_text())
        
        text = "\n".join(text_parts)
        text = clean_text(text)
        
        return {
            "text": text,
            "type": "pdf"
        }


class HTMLParser:
    """Extract structure and selectors from HTML"""
    
    @staticmethod
    def extract_selectors(html_content: str) -> List[Dict[str, Any]]:
        """Extract all relevant selectors from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        selectors = []
        
        # Elements to extract
        target_elements = ['input', 'button', 'select', 'textarea', 'a', 'form']
        
        for element_type in target_elements:
            elements = soup.find_all(element_type)
            
            for idx, elem in enumerate(elements):
                selector_info = HTMLParser._create_selector_info(elem, element_type, idx)
                if selector_info:
                    selectors.append(selector_info)
        
        return selectors
    
    @staticmethod
    def _create_selector_info(elem, element_type: str, idx: int) -> Dict[str, Any]:
        """Create selector information for an element"""
        elem_id = elem.get('id', '')
        elem_name = elem.get('name', '')
        elem_class = ' '.join(elem.get('class', []))
        elem_type = elem.get('type', '')
        text_content = elem.get_text(strip=True)[:100] if elem.get_text(strip=True) else ''
        
        # Build CSS selector
        css_selector = HTMLParser._build_css_selector(
            element_type, elem_id, elem_name, elem_class, elem_type
        )
        
        # Build XPath
        xpath = HTMLParser._build_xpath(elem)
        
        # Get all attributes
        attributes = dict(elem.attrs)
        
        return {
            "element_type": element_type,
            "element_id": elem_id,
            "element_name": elem_name,
            "element_class": elem_class,
            "input_type": elem_type,
            "css_selector": css_selector,
            "xpath": xpath,
            "text_content": text_content,
            "attributes": attributes,
            "placeholder": elem.get('placeholder', ''),
            "value": elem.get('value', '')
        }
    
    @staticmethod
    def _build_css_selector(element_type: str, elem_id: str, elem_name: str, 
                           elem_class: str, elem_type: str) -> str:
        """Build CSS selector for element"""
        if elem_id:
            return f"#{elem_id}"
        elif elem_name:
            return f"{element_type}[name='{elem_name}']"
        elif elem_type:
            return f"{element_type}[type='{elem_type}']"
        elif elem_class:
            class_selector = '.'.join(elem_class.split())
            return f"{element_type}.{class_selector}"
        else:
            return element_type
    
    @staticmethod
    def _build_xpath(elem) -> str:
        """Build XPath for element"""
        if elem.get('id'):
            return f"//*[@id='{elem.get('id')}']"
        elif elem.get('name'):
            return f"//{elem.name}[@name='{elem.get('name')}']"
        else:
            # Build a more specific XPath
            path_parts = []
            current = elem
            while current.parent and current.name != '[document]':
                siblings = [s for s in current.parent.children if s.name == current.name]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    path_parts.insert(0, f"{current.name}[{index}]")
                else:
                    path_parts.insert(0, current.name)
                current = current.parent
            return "//" + "/".join(path_parts)


class TextChunker:
    """Chunk documents for embedding"""
    
    @staticmethod
    def chunk_document(file_path: str, doc_type: str, text: str) -> List[Dict[str, Any]]:
        """Chunk a document with metadata"""
        filename = Path(file_path).name
        
        # Handle empty text
        if not text or not text.strip():
            return []
        
        chunks_text = chunk_text(text, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
        
        chunks = []
        for idx, chunk_content in enumerate(chunks_text):
            chunks.append({
                "text": chunk_content,
                "metadata": {
                    "source": filename,
                    "type": doc_type,
                    "chunk_index": idx,
                    "total_chunks": len(chunks_text)
                }
            })
        
        return chunks
    
    @staticmethod
    def chunk_selectors(selectors: List[Dict[str, Any]], filename: str) -> List[Dict[str, Any]]:
        """Create chunks for HTML selectors"""
        chunks = []
        
        for idx, selector in enumerate(selectors):
            # Create a text representation of the selector
            text_parts = [
                f"Element Type: {selector['element_type']}",
            ]
            
            if selector['element_id']:
                text_parts.append(f"ID: {selector['element_id']}")
            if selector['element_name']:
                text_parts.append(f"Name: {selector['element_name']}")
            if selector['placeholder']:
                text_parts.append(f"Placeholder: {selector['placeholder']}")
            if selector['text_content']:
                text_parts.append(f"Text: {selector['text_content']}")
            
            text = " | ".join(text_parts)
            
            # Flatten metadata - ChromaDB only accepts str, int, float, bool
            chunks.append({
                "text": text,
                "metadata": {
                    "source": filename,
                    "type": "html_selector",
                    "element_type": selector['element_type'],
                    "element_id": selector.get('element_id', ''),
                    "element_name": selector.get('element_name', ''),
                    "css_selector": selector['css_selector'],
                    "xpath": selector['xpath'],
                    "placeholder": selector.get('placeholder', ''),
                    "input_type": selector.get('input_type', '')
                }
            })
        
        return chunks
