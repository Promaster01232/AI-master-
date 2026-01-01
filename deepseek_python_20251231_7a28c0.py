import asyncio
import json
import logging
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime
import uuid

from src.core.ai_engine import ai_service
from src.core.prompt_manager import prompt_manager
from src.services.vector_service import VectorService
from src.database.db import db

logger = logging.getLogger(__name__)

class ChatService:
    """Service for chat operations"""
    
    def __init__(self):
        self.db = db
        self.vector_service = VectorService()
    
    async def create_completion(
        self,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        user_id: Optional[str] = None
    ) -> Dict:
        """Create a chat completion"""
        try:
            # Get response from AI
            response = await ai_service.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Save to history
            if user_id:
                await self.save_to_history(
                    user_id=user_id,
                    messages=messages,
                    response=response,
                    model=model
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def stream_completion(
        self,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion"""
        full_response = ""
        
        async for chunk in ai_service.stream_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield chunk
            
            # Extract content from SSE
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if data != "[DONE]":
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        full_response += content
                except:
                    pass
        
        # Save to history
        if user_id and full_response:
            await self.save_to_history(
                user_id=user_id,
                messages=messages,
                response={"choices": [{"message": {"content": full_response}}]},
                model=model
            )
    
    async def rag_chat(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        user_id: Optional[str] = None
    ) -> Dict:
        """Chat with RAG"""
        try:
            # Retrieve relevant context
            context = await self.vector_service.search(
                query=question,
                document_ids=document_ids,
                limit=5
            )
            
            # Format context for prompt
            context_text = "\n\n".join([
                f"Document: {item['document_name']}\nContent: {item['content'][:500]}..."
                for item in context
            ])
            
            # Create prompt
            prompt = prompt_manager.get_template("rag_qa")
            if prompt:
                messages = [
                    {
                        "role": "user",
                        "content": prompt.format(
                            context=context_text,
                            question=question
                        )
                    }
                ]
            else:
                messages = [
                    {"role": "system", "content": "Answer based on the provided context."},
                    {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
                ]
            
            # Get response
            response = await ai_service.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature
            )
            
            # Save to history
            if user_id:
                await self.save_to_history(
                    user_id=user_id,
                    messages=[{"role": "user", "content": question}],
                    response=response,
                    model=model,
                    context_sources=context
                )
            
            return {
                "response": response,
                "sources": context
            }
            
        except Exception as e:
            logger.error(f"RAG chat failed: {e}")
            raise
    
    async def save_to_history(
        self,
        user_id: str,
        messages: List[Dict],
        response: Dict,
        model: Optional[str] = None,
        context_sources: Optional[List] = None
    ):
        """Save chat to history"""
        try:
            conversation_id = str(uuid.uuid4())
            
            # Save user messages
            for message in messages:
                if message["role"] == "user":
                    await self.db.execute(
                        """
                        INSERT INTO chat_history 
                        (user_id, conversation_id, role, message, model_used, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            conversation_id,
                            "user",
                            message["content"],
                            model,
                            datetime.utcnow()
                        )
                    )
            
            # Save assistant response
            assistant_content = response["choices"][0]["message"]["content"]
            await self.db.execute(
                """
                INSERT INTO chat_history 
                (user_id, conversation_id, role, message, model_used, tokens_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    conversation_id,
                    "assistant",
                    assistant_content,
                    model,
                    response.get("usage", {}).get("total_tokens", 0),
                    datetime.utcnow()
                )
            )
            
            # Save context sources if provided
            if context_sources:
                for source in context_sources:
                    await self.db.execute(
                        """
                        INSERT INTO chat_context 
                        (conversation_id, document_id, chunk_id, relevance_score)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            conversation_id,
                            source.get("document_id"),
                            source.get("chunk_id"),
                            source.get("score", 0.0)
                        )
                    )
            
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
    
    async def get_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get chat history for user"""
        try:
            rows = await self.db.fetch_all(
                """
                SELECT * FROM chat_history 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
                """,
                (user_id, limit, offset)
            )
            
            # Group by conversation
            conversations = {}
            for row in rows:
                conv_id = row["conversation_id"]
                if conv_id not in conversations:
                    conversations[conv_id] = {
                        "conversation_id": conv_id,
                        "messages": [],
                        "created_at": row["created_at"]
                    }
                
                conversations[conv_id]["messages"].append({
                    "role": row["role"],
                    "content": row["message"],
                    "timestamp": row["created_at"]
                })
            
            return list(conversations.values())
            
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return []
    
    async def clear_history(self, user_id: str) -> bool:
        """Clear chat history for user"""
        try:
            await self.db.execute(
                "DELETE FROM chat_history WHERE user_id = ?",
                (user_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to clear chat history: {e}")
            return False