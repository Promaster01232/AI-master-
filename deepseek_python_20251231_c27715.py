import asyncio
import json
import logging
from typing import Dict, List, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import ollama
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class AIEngine(ABC):
    """Abstract AI Engine Interface"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        pass

class OllamaEngine(AIEngine):
    """Ollama-based AI Engine"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.client = ollama.AsyncClient(host=host)
        self.embedding_model = None
        self.current_model = None
        
    async def load_model(self, model_name: str) -> bool:
        """Load a specific model"""
        try:
            await self.client.pull(model_name)
            self.current_model = model_name
            logger.info(f"Model {model_name} loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response"""
        model = kwargs.get('model', self.current_model or 'qwen2.5:7b')
        options = {
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.9),
            'max_tokens': kwargs.get('max_tokens', 4096),
            'seed': kwargs.get('seed'),
        }
        
        try:
            response = await self.client.generate(
                model=model,
                prompt=prompt,
                options={k: v for k, v in options.items() if v is not None}
            )
            return response['response']
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream a response"""
        model = kwargs.get('model', self.current_model or 'qwen2.5:7b')
        options = {
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.9),
            'max_tokens': kwargs.get('max_tokens', 4096),
        }
        
        try:
            stream = await self.client.generate(
                model=model,
                prompt=prompt,
                options=options,
                stream=True
            )
            
            async for chunk in stream:
                if 'response' in chunk:
                    yield chunk['response']
        except Exception as e:
            logger.error(f"Stream generation failed: {e}")
            yield f"Error: {str(e)}"
    
    async def embed(self, text: str) -> List[float]:
        """Create embeddings for text"""
        try:
            # Use Ollama for embeddings
            response = await self.client.embeddings(
                model='nomic-embed-text',
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            # Fallback to sentence-transformers
            if self.embedding_model is None:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            return self.embedding_model.encode(text).tolist()
    
    async def list_models(self) -> List[Dict]:
        """List available models"""
        try:
            models = await self.client.list()
            return [
                {
                    'name': model['name'],
                    'size': model.get('size', 'Unknown'),
                    'modified': model.get('modified_at')
                }
                for model in models['models']
            ]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

class AIService:
    """Main AI Service"""
    
    def __init__(self):
        self.engine = OllamaEngine()
        self.available_models = []
        
    async def initialize(self):
        """Initialize the AI service"""
        try:
            self.available_models = await self.engine.list_models()
            if not self.available_models:
                # Load default model
                await self.engine.load_model('qwen2.5:7b')
                self.available_models = await self.engine.list_models()
            
            logger.info(f"AI Service initialized with {len(self.available_models)} models")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        """Create a chat completion"""
        # Format messages for the model
        prompt = self._format_messages(messages)
        
        # Generate response
        response = await self.engine.generate(prompt, **kwargs)
        
        return {
            'id': f"chatcmpl-{hash(prompt)}",
            'object': 'chat.completion',
            'created': int(asyncio.get_event_loop().time()),
            'model': kwargs.get('model', 'qwen2.5:7b'),
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': response
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': len(prompt.split()),
                'completion_tokens': len(response.split()),
                'total_tokens': len(prompt.split()) + len(response.split())
            }
        }
    
    async def stream_chat_completion(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completion"""
        prompt = self._format_messages(messages)
        
        async for chunk in self.engine.stream_generate(prompt, **kwargs):
            yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}]})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Format messages for the model"""
        formatted = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                formatted.append(f"System: {content}")
            elif role == 'user':
                formatted.append(f"User: {content}")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}")
        
        return "\n".join(formatted) + "\nAssistant:"
    
    async def get_available_models(self) -> List[Dict]:
        """Get available models"""
        return self.available_models

# Global AI service instance
ai_service = AIService()