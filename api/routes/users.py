"""
Users API routes for FairClaimRCM

Handles user management and authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.models.database import get_db
from api.models.schemas import User, UserCreate, UserUpdate, UserResponse
from api.services.user_service import UserService

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get list of users with optional filtering.
    """
    user_service = UserService(db)
    
    try:
        users = user_service.get_users(skip=skip, limit=limit, role=role, active=active)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    """
    user_service = UserService(db)
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    """
    user_service = UserService(db)
    
    try:
        # Check if user with email already exists
        existing_user = user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        user = user_service.create_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing user.
    """
    user_service = UserService(db)
    
    # Check if user exists
    existing_user = user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    try:
        updated_user = user_service.update_user(user_id, user_data)
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a user (soft delete - deactivate).
    """
    user_service = UserService(db)
    
    # Check if user exists
    existing_user = user_service.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    try:
        user_service.delete_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Activate a deactivated user.
    """
    user_service = UserService(db)
    
    try:
        user = user_service.activate_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )

@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Deactivate an active user.
    """
    user_service = UserService(db)
    
    try:
        user = user_service.deactivate_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )

@router.get("/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get user activity summary.
    """
    user_service = UserService(db)
    
    try:
        activity = user_service.get_user_activity(user_id, days)
        return {
            "user_id": user_id,
            "period": f"Last {days} days",
            "activity": activity,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user activity: {str(e)}"
        )

@router.get("/roles/available")
async def get_available_roles():
    """
    Get list of available user roles.
    """
    roles = [
        {
            "name": "admin",
            "display_name": "Administrator",
            "description": "Full system access and user management"
        },
        {
            "name": "coder",
            "display_name": "Medical Coder",
            "description": "Can review and code medical claims"
        },
        {
            "name": "analyst",
            "display_name": "Data Analyst",
            "description": "Can view analytics and generate reports"
        },
        {
            "name": "viewer",
            "display_name": "Viewer",
            "description": "Read-only access to claims and reports"
        }
    ]
    
    return {"roles": roles}
