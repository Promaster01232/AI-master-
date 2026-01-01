"""Documents routes"""

from fastapi import APIRouter

router = APIRouter(tags=["documents"])


@router.get("/documents")
async def get_documents():
    """Get documents endpoint"""
    return {"message": "Documents endpoint"}
