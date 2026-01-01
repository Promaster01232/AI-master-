"""Chat routes"""

from fastapi import APIRouter

router = APIRouter(tags=["chat"])


@router.get("/chat")
async def get_chat():
    """Get chat endpoint"""
    return {"message": "Chat endpoint"}
