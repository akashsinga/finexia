# api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.models.user import Token, UserInDB
from api.dependencies.db import get_db
from api.dependencies.auth import authenticate_user, create_access_token, get_current_user
from api.config import settings

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.utcnow() + access_token_expires

    access_token = create_access_token(data={"sub": user.username, "is_admin": user.is_admin}, expires_delta=access_token_expires)

    print(f"Token created for {user.username}, is_admin: {user.is_admin}")

    return Token(access_token=access_token, token_type="bearer", expires_at=expires_at)


@router.get("/verify", response_model=dict)
async def verify_token(current_user: UserInDB = Depends(get_current_user)):
    """Verify is the token is valid and return user info"""
    user_data = {"id": current_user.id, "username": current_user.username, "email": current_user.email, "full_name": current_user.full_name, "is_admin": current_user.is_admin, "is_active": current_user.is_active}
    return {"valid": True, "user": user_data}
