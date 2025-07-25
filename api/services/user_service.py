"""
User Service for FairClaimRCM

Provides user management capabilities.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import hashlib

# Mock user data since we don't have a real User model yet
MOCK_USERS = [
    {
        "id": 1,
        "username": "sarah.johnson",
        "full_name": "Dr. Sarah Johnson",
        "email": "sarah.johnson@hospital.com",
        "role": "admin",
        "department": "Administration",
        "is_active": True,
        "created_at": "2024-01-15T10:00:00Z",
        "last_login": "2024-12-01T09:30:00Z"
    },
    {
        "id": 2,
        "username": "mike.chen", 
        "full_name": "Mike Chen",
        "email": "mike.chen@hospital.com",
        "role": "coder",
        "department": "Coding",
        "is_active": True,
        "created_at": "2024-02-01T10:00:00Z",
        "last_login": "2024-12-01T08:15:00Z"
    },
    {
        "id": 3,
        "username": "lisa.rodriguez",
        "full_name": "Lisa Rodriguez",
        "email": "lisa.rodriguez@hospital.com", 
        "role": "analyst",
        "department": "Analytics",
        "is_active": True,
        "created_at": "2024-03-10T10:00:00Z",
        "last_login": "2024-11-30T16:45:00Z"
    },
    {
        "id": 4,
        "username": "john.smith",
        "full_name": "John Smith",
        "email": "john.smith@hospital.com",
        "role": "viewer", 
        "department": "Finance",
        "is_active": False,
        "created_at": "2024-01-20T10:00:00Z",
        "last_login": "2024-11-25T14:20:00Z"
    }
]

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None, active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get list of users with optional filtering."""
        try:
            users = MOCK_USERS.copy()
            
            # Apply filters
            if role:
                users = [u for u in users if u["role"] == role]
            
            if active is not None:
                users = [u for u in users if u["active"] == active]
            
            # Apply pagination
            users = users[skip:skip + limit]
            
            return users
        except Exception as e:
            raise Exception(f"Failed to get users: {str(e)}")

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by their ID."""
        try:
            for user in MOCK_USERS:
                if user["id"] == user_id:
                    return user
            return None
        except Exception as e:
            raise Exception(f"Failed to get user: {str(e)}")

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their email."""
        try:
            for user in MOCK_USERS:
                if user["email"] == email:
                    return user
            return None
        except Exception as e:
            raise Exception(f"Failed to get user by email: {str(e)}")

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        try:
            new_user = {
                "id": str(uuid.uuid4()),
                "name": user_data.get("name"),
                "email": user_data.get("email"),
                "role": user_data.get("role", "viewer"),
                "organization": user_data.get("organization", "General Hospital"),
                "active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": None
            }
            
            # In a real implementation, this would be saved to the database
            MOCK_USERS.append(new_user)
            
            return new_user
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing user."""
        try:
            for i, user in enumerate(MOCK_USERS):
                if user["id"] == user_id:
                    # Update fields that are provided
                    if "name" in user_data:
                        user["name"] = user_data["name"]
                    if "email" in user_data:
                        user["email"] = user_data["email"]
                    if "role" in user_data:
                        user["role"] = user_data["role"]
                    if "organization" in user_data:
                        user["organization"] = user_data["organization"]
                    
                    MOCK_USERS[i] = user
                    return user
            return None
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")

    def delete_user(self, user_id: str) -> bool:
        """Delete (deactivate) a user."""
        try:
            for i, user in enumerate(MOCK_USERS):
                if user["id"] == user_id:
                    user["active"] = False
                    MOCK_USERS[i] = user
                    return True
            return False
        except Exception as e:
            raise Exception(f"Failed to delete user: {str(e)}")

    def activate_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Activate a user."""
        try:
            for i, user in enumerate(MOCK_USERS):
                if user["id"] == user_id:
                    user["active"] = True
                    MOCK_USERS[i] = user
                    return user
            return None
        except Exception as e:
            raise Exception(f"Failed to activate user: {str(e)}")

    def deactivate_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Deactivate a user."""
        try:
            for i, user in enumerate(MOCK_USERS):
                if user["id"] == user_id:
                    user["active"] = False
                    MOCK_USERS[i] = user
                    return user
            return None
        except Exception as e:
            raise Exception(f"Failed to deactivate user: {str(e)}")

    def get_user_activity(self, user_id: str, days: int) -> Dict[str, Any]:
        """Get user activity summary."""
        try:
            # Mock activity data
            activity = {
                "total_logins": 42,
                "claims_processed": 156,
                "codes_reviewed": 423,
                "avg_session_duration": "2h 15m",
                "recent_actions": [
                    {
                        "action": "Reviewed claim CLM-001",
                        "timestamp": "2024-12-01T09:30:00Z",
                        "details": "Updated ICD-10 codes"
                    },
                    {
                        "action": "Generated analytics report",
                        "timestamp": "2024-12-01T08:45:00Z",
                        "details": "Coding accuracy report"
                    },
                    {
                        "action": "Logged in",
                        "timestamp": "2024-12-01T08:30:00Z",
                        "details": "Session started"
                    }
                ],
                "productivity_metrics": {
                    "claims_per_day": 5.2,
                    "accuracy_rate": 96.8,
                    "avg_processing_time": "18 minutes"
                }
            }
            
            return activity
        except Exception as e:
            raise Exception(f"Failed to get user activity: {str(e)}")
