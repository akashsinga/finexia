# api/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.models.user import User, UserCreate, UserUpdate
from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user, validate_admin
from api.services.user_service import create_user, update_user, get_users, get_user

router = APIRouter()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db), current_user=Depends(validate_admin)):  # Only admins can create users
    return create_user(db, user)


@router.get("/me", response_model=User)
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[User])
async def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(validate_admin)):  # Only admins can list users
    return get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(validate_admin)):  # Only admins can view specific users
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=User)
async def update_user_info(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user=Depends(validate_admin)):  # Only admins can update users
    db_user = update_user(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
