# api/dependencies/auth.py - Authentication dependencies for FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from api.config import settings
from api.dependencies.db import get_db
from api.models.user import UserInDB, TokenData

# OAuth2 password bearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
    """
    Dependency to get the current authenticated user

    Args:
        token: JWT token extracted from request
        db: Database session

    Returns:
        UserInDB object for the authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Create token data
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Get user from database
    user = get_user_from_db(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def validate_admin(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependency to validate the user has admin privileges

    Args:
        current_user: Current authenticated user

    Returns:
        UserInDB object if user has admin privileges

    Raises:
        HTTPException: If user lacks admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


def get_user_from_db(db: Session, username: str) -> Optional[UserInDB]:
    """
    Get user from database

    Args:
        db: Database session
        username: Username to lookup

    Returns:
        UserInDB object or None if user not found
    """
    from db.models.user import User as UserModel

    # Convert generator to session if needed
    try:
        if hasattr(db, "__next__"):
            db = next(db)
    except StopIteration:
        # If the generator is empty, create a new session
        from db.database import SessionLocal

        db = SessionLocal()

    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return None

    return UserInDB(id=user.id, username=user.username, email=user.email, hashed_password=user.hashed_password, full_name=user.full_name, is_admin=user.is_admin, is_active=user.is_active)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches a hashed password

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user with username and password

    Args:
        db: Database session
        username: Username
        password: Plain text password

    Returns:
        UserInDB object if authentication succeeds, None otherwise
    """
    user = get_user_from_db(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt
