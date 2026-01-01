from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict

from src.core.model_loader import model_manager
from src.core.ai_engine import ai_service
from src.api.middleware.auth import get_current_user

router = APIRouter(prefix="/models", tags=["models"])

@router.get("/")
async def list_models(user: Dict = Depends(get_current_user)):
    """List all available models"""
    try:
        # Get models from both sources
        local_models = model_manager.list_available_models()
        loaded_models = await ai_service.get_available_models()
        
        return {
            "local_models": local_models,
            "loaded_models": loaded_models,
            "default_model": "qwen2.5:7b"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load/{model_name}")
async def load_model(model_name: str, user: Dict = Depends(get_current_user)):
    """Load a specific model"""
    try:
        success = await ai_service.engine.load_model(model_name)
        if success:
            return {"message": f"Model {model_name} loaded successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to load model {model_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unload/{model_name}")
async def unload_model(model_name: str, user: Dict = Depends(get_current_user)):
    """Unload a model"""
    try:
        # Note: Ollama doesn't have explicit unload, but we can track state
        return {"message": f"Model {model_name} marked as unloaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def model_status(user: Dict = Depends(get_current_user)):
    """Get current model status"""
    try:
        return {
            "current_model": ai_service.engine.current_model,
            "available_memory": "TODO",  # Implement memory check
            "gpu_available": False,  # Implement GPU check
            "performance": "good"  # Implement performance metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/{model_name}")
async def download_model(model_name: str, user: Dict = Depends(get_current_user)):
    """Download a model"""
    try:
        success = await model_manager.download_model(model_name)
        if success:
            return {"message": f"Model {model_name} download initiated"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to download model {model_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))