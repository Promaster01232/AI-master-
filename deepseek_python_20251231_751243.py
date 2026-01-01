from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
import shutil
from pathlib import Path
import uuid

from src.api.middleware.auth import get_current_user
from src.services.rag_service import RAGService

router = APIRouter(prefix="/documents", tags=["documents"])
rag_service = RAGService()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    process_now: bool = Form(True),
    user: Dict = Depends(get_current_user)
):
    """Upload a document"""
    try:
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Save file
        upload_dir = Path("./documents/raw")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to database
        document_id = await rag_service.add_document(
            filename=file.filename,
            filepath=str(file_path),
            user_id=user.get('id'),
            process_now=process_now
        )
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "message": "Document uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

@router.get("/")
async def list_documents(
    limit: int = 50,
    offset: int = 0,
    processed_only: bool = False,
    user: Dict = Depends(get_current_user)
):
    """List documents"""
    try:
        documents = await rag_service.list_documents(
            user_id=user.get('id'),
            limit=limit,
            offset=offset,
            processed_only=processed_only
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_document(document_id: str, user: Dict = Depends(get_current_user)):
    """Get document details"""
    try:
        document = await rag_service.get_document(document_id, user.get('id'))
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: str, user: Dict = Depends(get_current_user)):
    """Delete a document"""
    try:
        success = await rag_service.delete_document(document_id, user.get('id'))
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/process")
async def process_document(document_id: str, user: Dict = Depends(get_current_user)):
    """Process a document for RAG"""
    try:
        await rag_service.process_document(document_id, user.get('id'))
        return {"message": "Document processing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    limit: int = 100,
    offset: int = 0,
    user: Dict = Depends(get_current_user)
):
    """Get chunks from a document"""
    try:
        chunks = await rag_service.get_document_chunks(
            document_id=document_id,
            user_id=user.get('id'),
            limit=limit,
            offset=offset
        )
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))