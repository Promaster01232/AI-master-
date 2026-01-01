import asyncio
import logging
import sqlite3
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
import aiosqlite

logger = logging.getLogger(__name__)

class Database:
    """Database manager"""
    
    def __init__(self, db_path: str = "./database/main.db"):
        self.db_path = db_path
        self.connection = None
        
    async def connect(self):
        """Connect to the database"""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            await self.connection.execute("PRAGMA foreign_keys = ON")
            await self.create_tables()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the database"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from database")
    
    async def create_tables(self):
        """Create database tables"""
        try:
            # Users table
            await self.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # Chat history
            await self.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    role TEXT CHECK(role IN ('user', 'assistant', 'system')),
                    message TEXT NOT NULL,
                    model_used TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Documents
            await self.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    filetype TEXT,
                    size INTEGER,
                    processed BOOLEAN DEFAULT 0,
                    chunks_count INTEGER DEFAULT 0,
                    processing_started TIMESTAMP,
                    processed_at TIMESTAMP,
                    processing_error TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Document chunks
            await self.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    chunk_index INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
                )
            """)
            
            # Training jobs
            await self.execute("""
                CREATE TABLE IF NOT EXISTS training_jobs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    job_name TEXT NOT NULL,
                    dataset_path TEXT,
                    model_config TEXT,
                    base_model TEXT,
                    status TEXT DEFAULT 'pending',
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Chat context (for RAG)
            await self.execute("""
                CREATE TABLE IF NOT EXISTS chat_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    document_id TEXT,
                    chunk_id TEXT,
                    relevance_score REAL,
                    FOREIGN KEY (conversation_id) REFERENCES chat_history (conversation_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            await self.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_user ON chat_history(user_id)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_conversation ON chat_history(conversation_id)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_document_chunks_document ON document_chunks(document_id)")
            await self.execute("CREATE INDEX IF NOT EXISTS idx_training_jobs_user ON training_jobs(user_id)")
            
            logger.info("Database tables created/verified")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        if not self.connection:
            await self.connect()
        
        try:
            cursor = await self.connection.execute(query, params)
            await self.connection.commit()
            return cursor
        except Exception as e:
            logger.error(f"Query failed: {query} | Error: {e}")
            raise
    
    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch a single row"""
        if not self.connection:
            await self.connect()
        
        try:
            cursor = await self.connection.execute(query, params)
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Fetch one failed: {query} | Error: {e}")
            return None
    
    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows"""
        if not self.connection:
            await self.connect()
        
        try:
            cursor = await self.connection.execute(query, params)
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Fetch all failed: {query} | Error: {e}")
            return []
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            result = await self.fetch_one(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return result is not None
        except Exception as e:
            logger.error(f"Failed to check if table exists: {e}")
            return False
    
    async def backup(self, backup_path: str):
        """Create a database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")

# Global database instance
db = Database()