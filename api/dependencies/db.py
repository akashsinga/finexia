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

def get_db_session() -> Session:
    """
    Get a non-generator database session
    
    Returns:
        Session: SQLAlchemy database session object
        
    Note:
        This should be used in service functions that need direct
        access to a session object rather than a generator
    """
    db = SessionLocal()
    return db