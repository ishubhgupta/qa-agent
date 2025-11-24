import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from backend.config import Config


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.model = SentenceTransformer(self.model_name)
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return embeddings.tolist()


class VectorStore:
    """Manage ChromaDB vector database"""
    
    def __init__(self, persist_directory: str = None, collection_name: str = "qa_agent_kb"):
        self.persist_directory = persist_directory or Config.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name
        self.embedding_generator = EmbeddingGenerator()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """Add document chunks to vector store"""
        if not chunks:
            return 0
        
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_generator.embed_batch(texts)
        
        # Generate IDs
        ids = [f"doc_{i}_{chunk['metadata'].get('chunk_index', i)}" 
               for i, chunk in enumerate(chunks)]
        
        # Add to collection
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(chunks)
    
    def search(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """Search for relevant documents"""
        top_k = top_k or Config.TOP_K_RETRIEVAL
        
        # Generate query embedding
        query_embedding = self.embedding_generator.embed_text(query)
        
        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i],
                    "similarity": 1 - results['distances'][0][i]  # Convert distance to similarity
                })
        
        return {
            "results": formatted_results,
            "query": query,
            "top_k": top_k
        }
    
    def clear_collection(self):
        """Clear all documents from collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_documents": count,
            "persist_directory": self.persist_directory
        }
    
    def get_all_sources(self) -> List[str]:
        """Get list of all unique source documents"""
        try:
            # Get all documents
            results = self.collection.get(include=["metadatas"])
            
            if not results['metadatas']:
                return []
            
            # Extract unique sources
            sources = set()
            for metadata in results['metadatas']:
                if 'source' in metadata:
                    sources.add(metadata['source'])
            
            return sorted(list(sources))
        except Exception as e:
            print(f"Error getting sources: {e}")
            return []
