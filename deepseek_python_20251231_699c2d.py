import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "My AI Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    WORKERS: int = 4
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    JWT_SECRET: str = Field(default="your-jwt-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./database/main.db"
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    
    # AI Models
    MODEL_PATH: str = "./ai-models"
    DEFAULT_MODEL: str = "qwen2.5:7b"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    
    # Vector Database
    CHROMA_HOST: str = "http://localhost:8000"
    VECTOR_DB_PATH: str = "./database/vector/chromadb"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    DOCUMENTS_DIR: str = "./documents"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Training
    TRAINING_DIR: str = "./training"
    CHECKPOINTS_DIR: str = "./training/checkpoints"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_database_path(self) -> Path:
        """Get database path"""
        if self.DATABASE_URL.startswith("sqlite:///"):
            return Path(self.DATABASE_URL.replace("sqlite:///", ""))
        return Path("./database/main.db")
    
    def get_model_path(self) -> Path:
        """Get model path"""
        return Path(self.MODEL_PATH)
    
    def is_production(self) -> bool:
        """Check if in production mode"""
        return self.ENVIRONMENT.lower() == "production"

# Global settings instance
settings = Settings()

# Create directories on import
def create_directories():
    """Create necessary directories"""
    directories = [
        settings.get_database_path().parent,
        settings.get_model_path(),
        Path(settings.UPLOAD_DIR),
        Path(settings.DOCUMENTS_DIR),
        Path(settings.TRAINING_DIR),
        Path(settings.CHECKPOINTS_DIR),
        Path("./logs"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

create_directories()