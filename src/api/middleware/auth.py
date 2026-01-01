"""Authentication middleware"""

from fastapi import HTTPException, status
from typing import Dict


def create_default_admin():
    """Create default admin user"""
    pass


async def get_current_user() -> Dict:
    """Get current authenticated user"""
    # Mock implementation - replace with actual auth logic
    return {
        "id": "user_123",
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin"
    }
