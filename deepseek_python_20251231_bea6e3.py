from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional
import uuid

from src.api.middleware.auth import get_current_user
from src.services.training_service import TrainingService

router = APIRouter(prefix="/training", tags=["training"])
training_service = TrainingService()

@router.post("/start")
async def start_training(
    config: Dict,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user)
):
    """Start a training job"""
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start training in background
        background_tasks.add_task(
            training_service.start_training,
            job_id=job_id,
            config=config,
            user_id=user.get('id')
        )
        
        return {
            "job_id": job_id,
            "message": "Training job started",
            "status": "queued"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def list_training_jobs(
    limit: int = 20,
    offset: int = 0,
    user: Dict = Depends(get_current_user)
):
    """List training jobs"""
    try:
        jobs = await training_service.list_jobs(
            user_id=user.get('id'),
            limit=limit,
            offset=offset
        )
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}")
async def get_training_job(job_id: str, user: Dict = Depends(get_current_user)):
    """Get training job details"""
    try:
        job = await training_service.get_job(job_id, user.get('id'))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/cancel")
async def cancel_training_job(job_id: str, user: Dict = Depends(get_current_user)):
    """Cancel a training job"""
    try:
        success = await training_service.cancel_job(job_id, user.get('id'))
        if success:
            return {"message": "Training job cancelled"}
        else:
            raise HTTPException(status_code=400, detail="Cannot cancel job")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}/logs")
async def get_training_logs(
    job_id: str,
    lines: int = 100,
    user: Dict = Depends(get_current_user)
):
    """Get training logs"""
    try:
        logs = await training_service.get_logs(job_id, user.get('id'), lines)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasets")
async def list_datasets(user: Dict = Depends(get_current_user)):
    """List available datasets"""
    try:
        datasets = await training_service.list_datasets(user.get('id'))
        return datasets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datasets/create")
async def create_dataset(
    name: str,
    description: str = "",
    data: Optional[List[Dict]] = None,
    user: Dict = Depends(get_current_user)
):
    """Create a new dataset"""
    try:
        dataset_id = await training_service.create_dataset(
            name=name,
            description=description,
            data=data,
            user_id=user.get('id')
        )
        return {
            "dataset_id": dataset_id,
            "message": "Dataset created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))