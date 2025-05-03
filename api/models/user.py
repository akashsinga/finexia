# api/models/user.py - Pydantic models for user data
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user fields"""

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Fields required to create a user"""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Fields that can be updated"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    """User as stored in database"""

    id: int
    hashed_password: str
    is_admin: bool = False

    class Config:
        from_attributes = True


class User(UserBase):
    """User response model"""

    id: int
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str
    expires_at: datetime


class TokenData(BaseModel):
    """JWT token data"""

    username: Optional[str] = None
