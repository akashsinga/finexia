# api/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.models.user import User, UserCreate, UserUpdate
from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user, validate_admin
from api.services.user_service import create_user, update_user, get_users

router = APIRouter()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db), current_user=Depends(validate_admin)):  # Only admins can create users
    return create_user(db, user)


@router.get("/me", response_model=User)
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(validate_admin)):  # Only admins can list users
    return get_users(db, skip=skip, limit=limit)
