from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional
import json
import asyncio

from src.core.ai_engine import ai_service
from src.api.middleware.auth import get_current_user
from src.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()

@router.post("/completions")
async def chat_completion(
    messages: List[Dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    stream: bool = False,
    user: Dict = Depends(get_current_user)
):
    """Create a chat completion"""
    try:
        if stream:
            return StreamingResponse(
                chat_service.stream_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    user_id=user.get('id')
                ),
                media_type="text/event-stream"
            )
        else:
            response = await chat_service.create_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                user_id=user.get('id')
            )
            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """WebSocket for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            messages = message_data.get('messages', [])
            model = message_data.get('model')
            temperature = message_data.get('temperature', 0.7)
            
            # Stream response via chat_service
            async for chunk in chat_service.stream_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                user_id=None
            ):
                await websocket.send_text(chunk)
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
        await websocket.close()

@router.get("/history")
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    user: Dict = Depends(get_current_user)
):
    """Get chat history for user"""
    try:
        history = await chat_service.get_history(
            user_id=user.get('id'),
            limit=limit,
            offset=offset
        )
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history")
async def clear_chat_history(user: Dict = Depends(get_current_user)):
    """Clear chat history for user"""
    try:
        await chat_service.clear_history(user_id=user.get('id'))
        return {"message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag")
async def rag_chat(
    question: str,
    document_ids: Optional[List[str]] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    user: Dict = Depends(get_current_user)
):
    """Chat with RAG (Retrieval Augmented Generation)"""
    try:
        response = await chat_service.rag_chat(
            question=question,
            document_ids=document_ids,
            model=model,
            temperature=temperature,
            user_id=user.get('id')
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))