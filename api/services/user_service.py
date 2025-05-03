# api/services/user_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext

from db.models.user import User
from api.models.user import UserCreate, UserUpdate

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    # Check if username or email already exists
    existing_username = get_user_by_username(db, user.username)
    if existing_username:
        raise ValueError(f"Username '{user.username}' already registered")

    existing_email = get_user_by_email(db, user.email)
    if existing_email:
        raise ValueError(f"Email '{user.email}' already registered")

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Create user
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password, full_name=user.full_name, is_active=user.is_active)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """Update user information"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Update fields if provided
    if user.email is not None:
        db_user.email = user.email
    if user.full_name is not None:
        db_user.full_name = user.full_name
    if user.password is not None:
        db_user.hashed_password = pwd_context.hash(user.password)

    db.commit()
    db.refresh(db_user)

    return db_user
