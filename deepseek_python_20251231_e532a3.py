import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)

class ModelManager:
    """Manage AI models"""
    
    def __init__(self, model_path: str = "./ai-models"):
        self.model_path = Path(model_path)
        self.models_config = {}
        self.loaded_models = {}
        
    def load_config(self) -> bool:
        """Load model configuration"""
        config_file = self.model_path / "models.json"
        
        if not config_file.exists():
            logger.warning(f"Model config not found at {config_file}")
            return False
        
        try:
            with open(config_file, 'r') as f:
                self.models_config = json.load(f)
            logger.info(f"Loaded model configuration with {len(self.models_config.get('models', {}))} models")
            return True
        except Exception as e:
            logger.error(f"Failed to load model config: {e}")
            return False
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a model"""
        if not self.models_config:
            self.load_config()
        
        return self.models_config.get('models', {}).get(model_name)
    
    def list_available_models(self) -> List[Dict]:
        """List all available models"""
        if not self.models_config:
            self.load_config()
        
        models = []
        for model_id, info in self.models_config.get('models', {}).items():
            models.append({
                'id': model_id,
                'name': info.get('name', model_id),
                'description': info.get('description', ''),
                'size': info.get('size', 'Unknown'),
                'context': info.get('context', 2048),
                'languages': info.get('languages', ['en']),
                'recommended': info.get('recommended', False)
            })
        
        return models
    
    async def download_model(self, model_name: str) -> bool:
        """Download a model"""
        model_info = self.get_model_info(model_name)
        if not model_info:
            logger.error(f"Model {model_name} not found in config")
            return False
        
        # Check if model already exists
        model_path = Path(model_info.get('path', f"./{model_name}"))
        if model_path.exists():
            logger.info(f"Model {model_name} already exists at {model_path}")
            return True
        
        # Download model (implementation depends on model source)
        logger.info(f"Downloading model {model_name}...")
        
        # TODO: Implement actual download logic
        # This could use huggingface hub, curl, or other methods
        
        return True
    
    def validate_model(self, model_name: str) -> bool:
        """Validate that a model is properly installed"""
        model_info = self.get_model_info(model_name)
        if not model_info:
            return False
        
        model_path = Path(model_info.get('path', f"./{model_name}"))
        return model_path.exists()

class ModelRegistry:
    """Registry for managing loaded models"""
    
    _instance = None
    _models = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_model(self, model_id: str, model_instance):
        """Register a model instance"""
        self._models[model_id] = model_instance
        logger.info(f"Registered model: {model_id}")
    
    def get_model(self, model_id: str):
        """Get a registered model"""
        return self._models.get(model_id)
    
    def list_registered_models(self) -> List[str]:
        """List all registered models"""
        return list(self._models.keys())
    
    def unregister_model(self, model_id: str):
        """Unregister a model"""
        if model_id in self._models:
            del self._models[model_id]
            logger.info(f"Unregistered model: {model_id}")

# Global instances
model_manager = ModelManager()
model_registry = ModelRegistry()