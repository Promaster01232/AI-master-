import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path
import uuid
from datetime import datetime

from src.core.ai_engine import ai_service
from src.services.vector_service import VectorService
from src.database.db import db
from src.utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

class RAGService:
    """Service for RAG operations"""
    
    def __init__(self):
        self.db = db
        self.vector_service = VectorService()
        self.file_handler = FileHandler()
    
    async def add_document(
        self,
        filename: str,
        filepath: str,
        user_id: str,
        process_now: bool = True
    ) -> str:
        """Add a document to the system"""
        try:
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Get file info
            file_path = Path(filepath)
            file_size = file_path.stat().st_size
            file_type = file_path.suffix.lower()
            
            # Save to database
            await self.db.execute(
                """
                INSERT INTO documents 
                (id, user_id, filename, filepath, filetype, size, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    user_id,
                    filename,
                    str(filepath),
                    file_type,
                    file_size,
                    datetime.utcnow()
                )
            )
            
            # Process document if requested
            if process_now:
                asyncio.create_task(self.process_document(document_id, user_id))
            
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    async def process_document(self, document_id: str, user_id: str):
        """Process a document for RAG"""
        try:
            # Get document info
            document = await self.db.fetch_one(
                "SELECT * FROM documents WHERE id = ? AND user_id = ?",
                (document_id, user_id)
            )
            
            if not document:
                raise ValueError("Document not found")
            
            # Update status
            await self.db.execute(
                "UPDATE documents SET processing_started = ? WHERE id = ?",
                (datetime.utcnow(), document_id)
            )
            
            # Extract text
            text = await self.file_handler.extract_text(document["filepath"])
            
            # Split into chunks
            chunks = await self.file_handler.split_text(text)
            
            # Create embeddings and store in vector DB
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                
                # Create embedding
                embedding = await ai_service.embed(chunk)
                
                # Store in vector database
                await self.vector_service.add_chunk(
                    document_id=document_id,
                    chunk_id=chunk_id,
                    content=chunk,
                    embedding=embedding,
                    metadata={
                        "document_name": document["filename"],
                        "chunk_index": i,
                        "user_id": user_id
                    }
                )
                
                # Save to database
                await self.db.execute(
                    """
                    INSERT INTO document_chunks 
                    (id, document_id, content, chunk_index, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (chunk_id, document_id, chunk, i, datetime.utcnow())
                )
            
            # Update document status
            await self.db.execute(
                """
                UPDATE documents 
                SET processed = 1, chunks_count = ?, processed_at = ?
                WHERE id = ?
                """,
                (len(chunks), datetime.utcnow(), document_id)
            )
            
            logger.info(f"Document {document_id} processed with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            
            # Update error status
            await self.db.execute(
                "UPDATE documents SET processing_error = ? WHERE id = ?",
                (str(e), document_id)
            )
    
    async def list_documents(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        processed_only: bool = False
    ) -> List[Dict]:
        """List documents for user"""
        try:
            query = "SELECT * FROM documents WHERE user_id = ?"
            if processed_only:
                query += " AND processed = 1"

            query += " ORDER BY uploaded_at DESC LIMIT ? OFFSET ?"
            params = (user_id, limit, offset)

            rows = await self.db.fetch_all(query, params)
            return rows
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Dict]:
        """Get document details"""
        try:
            row = await self.db.fetch_one(
                "SELECT * FROM documents WHERE id = ? AND user_id = ?",
                (document_id, user_id)
            )
            return row
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {e}")
            return None
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document"""
        try:
            # Remove from vector database
            await self.vector_service.delete_document(document_id)
            
            # Delete chunks
            await self.db.execute(
                "DELETE FROM document_chunks WHERE document_id = ?",
                (document_id,)
            )
            
            # Delete document
            result = await self.db.execute(
                "DELETE FROM documents WHERE id = ? AND user_id = ?",
                (document_id, user_id)
            )
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def get_document_chunks(
        self,
        document_id: str,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Get chunks from a document"""
        try:
            # Verify document belongs to user
            document = await self.get_document(document_id, user_id)
            if not document:
                return []
            
            rows = await self.db.fetch_all(
                """
                SELECT * FROM document_chunks 
                WHERE document_id = ? 
                ORDER BY chunk_index 
                LIMIT ? OFFSET ?
                """,
                (document_id, limit, offset)
            )
            return rows
            
        except Exception as e:
            logger.error(f"Failed to get document chunks: {e}")
            return []
    
    async def search_documents(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Search across user's documents"""
        try:
            # Get document IDs for user
            user_docs = await self.db.fetch_all(
                "SELECT id FROM documents WHERE user_id = ? AND processed = 1",
                (user_id,)
            )
            
            document_ids = [doc["id"] for doc in user_docs]
            
            # Search in vector database
            results = await self.vector_service.search(
                query=query,
                document_ids=document_ids,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []