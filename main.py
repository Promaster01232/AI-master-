from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from src.core.ai_engine import ai_service
from src.services.vector_service import vector_service
from src.database.db import db
from src.api.routes import chat, models, documents, training
from src.api.middleware.auth import create_default_admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting AI Platform...")
    
    # Create necessary directories
    Path("./logs").mkdir(exist_ok=True)
    Path("./database").mkdir(exist_ok=True)
    Path("./documents/raw").mkdir(parents=True, exist_ok=True)
    Path("./documents/processed").mkdir(parents=True, exist_ok=True)
    Path("./uploads").mkdir(exist_ok=True)
    
    # Initialize services
    try:
        await db.connect()
        await ai_service.initialize()
        await vector_service.initialize()
        
        # Create default admin user
        create_default_admin()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Platform...")
    await db.disconnect()
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="My AI Platform",
    description="A complete, self-hosted AI platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-platform",
        "version": "1.0.0"
    }

# Include routers
app.include_router(chat.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(training.router, prefix="/api/v1")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve frontend in production
@app.get("/")
async def serve_frontend():
    """Serve frontend application"""
    return {"message": "AI Platform API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )

