import asyncio
import logging
from typing import Dict, List, Optional
import chromadb
from chromadb.config import Settings
import numpy as np

logger = logging.getLogger(__name__)

class VectorService:
    """Service for vector database operations"""
    
    def __init__(self, persist_directory: str = "./database/vector/chromadb"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
    async def initialize(self):
        """Initialize the vector database"""
        try:
            # Create client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(allow_reset=True, anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection("documents")
                logger.info("Loaded existing vector collection")
            except:
                self.collection = self.client.create_collection(
                    name="documents",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Created new vector collection")
            
            logger.info(f"Vector service initialized with {self.collection.count()} embeddings")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise
    
    async def add_chunk(
        self,
        document_id: str,
        chunk_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict
    ):
        """Add a chunk to the vector database"""
        try:
            # Convert embedding to list if it's numpy array
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            # Add to collection
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    **metadata
                }]
            )
            
            logger.debug(f"Added chunk {chunk_id} to vector database")
            
        except Exception as e:
            logger.error(f"Failed to add chunk to vector database: {e}")
            raise
    
    async def search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Search for similar content"""
        try:
            if not self.collection:
                await self.initialize()
            
            # Create query embedding
            from src.core.ai_engine import ai_service
            query_embedding = await ai_service.engine.embed(query)
            
            # Prepare filter
            where_filter = None
            if document_ids:
                where_filter = {"document_id": {"$in": document_ids}}
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "chunk_id": results['ids'][0][i],
                        "document_id": results['metadatas'][0][i].get("document_id"),
                        "document_name": results['metadatas'][0][i].get("document_name", "Unknown"),
                        "content": results['documents'][0][i],
                        "score": 1 - results['distances'][0][i]  # Convert distance to similarity
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        try:
            if not self.collection:
                await self.initialize()
            
            # Delete from vector database
            self.collection.delete(where={"document_id": document_id})
            
            logger.info(f"Deleted document {document_id} from vector database")
            
        except Exception as e:
            logger.error(f"Failed to delete document from vector database: {e}")
    
    async def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            if not self.collection:
                await self.initialize()
            
            count = self.collection.count()
            
            # Get unique document count
            results = self.collection.get(
                include=["metadatas"],
                limit=count
            )
            
            unique_docs = set()
            for metadata in results['metadatas']:
                if metadata and 'document_id' in metadata:
                    unique_docs.add(metadata['document_id'])
            
            return {
                "total_chunks": count,
                "unique_documents": len(unique_docs),
                "collection_name": "documents"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "total_chunks": 0,
                "unique_documents": 0,
                "collection_name": "documents"
            }

# Global vector service instance
vector_service = VectorService()