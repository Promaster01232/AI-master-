"""Training routes"""

from fastapi import APIRouter

router = APIRouter(tags=["training"])


@router.get("/training")
async def get_training():
    """Get training endpoint"""
    return {"message": "Training endpoint"}
