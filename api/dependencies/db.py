# api/dependencies/db.py - Database dependencies for FastAPI
from sqlalchemy.orm import Session
from typing import Generator
from functools import lru_cache

from db.database import SessionLocal

@lru_cache(maxsize=1)
def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database session
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        The session is closed automatically after the request is processed
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()