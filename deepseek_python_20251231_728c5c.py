from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
import jwt
from datetime import datetime, timedelta
import secrets

security = HTTPBearer()

# Simple user store (replace with database)
users_db = {
    "admin": {
        "id": "1",
        "username": "admin",
        "password_hash": "hashed_password",  # In real app, use bcrypt
        "role": "admin"
    }
}

# JWT configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Get current user from token"""
    token = credentials.credentials
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if not username or username not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": users_db[username]["id"],
        "username": username,
        "role": users_db[username]["role"]
    }

def create_default_admin():
    """Create default admin user"""
    if "admin" not in users_db:
        # In production, use proper password hashing
        users_db["admin"] = {
            "id": "1",
            "username": "admin",
            "password_hash": "admin123",  # Change this!
            "role": "admin"
        }

class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if request is allowed"""
        import time
        current_time = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < 60
        ]
        
        if len(self.requests[user_id]) < self.requests_per_minute:
            self.requests[user_id].append(current_time)
            return True
        
        return False

# Global rate limiter
rate_limiter = RateLimiter()