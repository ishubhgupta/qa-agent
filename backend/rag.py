from typing import List, Dict, Any
from pathlib import Path
from backend.vector_store import VectorStore
from backend.ingestion import DocumentParser, TextChunker
from backend.config import Config


class RAGPipeline:
    """RAG pipeline for knowledge base building and retrieval"""
    
    def __init__(self):
        self.vector_store = VectorStore()
    
    def build_knowledge_base(self, file_paths: List[str], clear_existing: bool = False) -> Dict[str, Any]:
        """Build knowledge base from uploaded documents"""
        if clear_existing:
            self.vector_store.clear_collection()
        
        all_chunks = []
        processed_files = []
        
        for file_path in file_paths:
            try:
                # Parse document
                parsed = DocumentParser.parse_file(file_path)
                doc_type = parsed["type"]
                
                # Chunk text content
                if parsed.get("text"):
                    chunks = TextChunker.chunk_document(
                        file_path,
                        doc_type,
                        parsed["text"]
                    )
                    all_chunks.extend(chunks)
                
                # Handle HTML selectors separately
                if doc_type == "html" and parsed.get("selectors"):
                    selector_chunks = TextChunker.chunk_selectors(
                        parsed["selectors"],
                        Path(file_path).name
                    )
                    all_chunks.extend(selector_chunks)
                
                processed_files.append(Path(file_path).name)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Add all chunks to vector store
        num_chunks = self.vector_store.add_documents(all_chunks)
        
        return {
            "success": True,
            "num_chunks": num_chunks,
            "num_documents": len(processed_files),
            "processed_files": processed_files
        }
    
    def retrieve_context(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """Retrieve relevant context for a query"""
        search_results = self.vector_store.search(query, top_k)
        
        # Format context with source attribution
        formatted_context = self._format_context_with_sources(search_results["results"])
        
        # Extract unique sources
        sources = list(set([
            result["metadata"].get("source", "unknown")
            for result in search_results["results"]
        ]))
        
        # Get HTML selectors if present
        html_selectors = self._extract_html_selectors(search_results["results"])
        
        return {
            "context": formatted_context,
            "sources": sources,
            "results": search_results["results"],
            "html_selectors": html_selectors
        }
    
    def _format_context_with_sources(self, results: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks with source attribution"""
        if not results:
            return "No relevant context found."
        
        formatted_parts = ["RETRIEVED CONTEXT:\n"]
        
        for idx, result in enumerate(results, 1):
            source = result["metadata"].get("source", "unknown")
            doc_type = result["metadata"].get("type", "unknown")
            similarity = result.get("similarity", 0)
            
            formatted_parts.append(
                f"[{idx}] Source: {source} | Type: {doc_type} | Relevance: {similarity:.2f}\n"
                f"{result['text']}\n"
            )
        
        return "\n".join(formatted_parts)
    
    def _extract_html_selectors(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract HTML selector information from results"""
        selectors = {}
        
        for result in results:
            if result["metadata"].get("type") == "html_selector":
                metadata = result["metadata"]
                # Reconstruct selector data from flattened metadata
                selector_data = {
                    "element_type": metadata.get("element_type", ""),
                    "element_id": metadata.get("element_id", ""),
                    "element_name": metadata.get("element_name", ""),
                    "css_selector": metadata.get("css_selector", ""),
                    "xpath": metadata.get("xpath", ""),
                    "placeholder": metadata.get("placeholder", ""),
                    "input_type": metadata.get("input_type", "")
                }
                
                # Use element ID or name as key, or create a unique key
                key = (selector_data.get("element_id") or 
                       selector_data.get("element_name") or 
                       f"{selector_data['element_type']}_{len(selectors)}")
                selectors[key] = selector_data
        
        return selectors
    
    def get_all_html_selectors(self) -> Dict[str, Any]:
        """Get all HTML selectors from the knowledge base"""
        # Search with a broad query to get HTML selectors
        search_results = self.vector_store.search("html form input button", top_k=100)
        
        selectors = {}
        for result in search_results["results"]:
            if result["metadata"].get("type") == "html_selector":
                metadata = result["metadata"]
                # Reconstruct selector data from flattened metadata
                selector_data = {
                    "element_type": metadata.get("element_type", ""),
                    "element_id": metadata.get("element_id", ""),
                    "element_name": metadata.get("element_name", ""),
                    "css_selector": metadata.get("css_selector", ""),
                    "xpath": metadata.get("xpath", ""),
                    "placeholder": metadata.get("placeholder", ""),
                    "input_type": metadata.get("input_type", "")
                }
                
                key = (selector_data.get("element_id") or 
                       selector_data.get("element_name") or 
                       f"{selector_data['element_type']}_{len(selectors)}")
                selectors[key] = selector_data
        
        return selectors
    
    def validate_grounding(self, generated_text: str, context_results: List[Dict[str, Any]]) -> bool:
        """Validate if generated content references source documents"""
        if not context_results:
            return False
        
        # Check if any source is mentioned in the generated text
        sources = [result["metadata"].get("source", "") for result in context_results]
        
        for source in sources:
            if source.lower() in generated_text.lower():
                return True
        
        return False
    
    def get_kb_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        stats = self.vector_store.get_collection_stats()
        sources = self.vector_store.get_all_sources()
        
        return {
            "total_chunks": stats["total_documents"],
            "unique_sources": len(sources),
            "sources": sources
        }
