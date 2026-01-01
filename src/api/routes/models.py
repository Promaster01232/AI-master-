"""Models routes"""

from fastapi import APIRouter

router = APIRouter(tags=["models"])


@router.get("/models")
async def get_models():
    """Get models endpoint"""
    return {"message": "Models endpoint"}
