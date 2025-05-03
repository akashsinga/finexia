# api/dependencies/db.py - Database dependencies for FastAPI
from sqlalchemy.orm import Session
from fastapi import Request

def get_db(request: Request) -> Session:
    """
    Dependency for database session
    
    Returns:
        Session: SQLAlchemy database session
    """
    return request.state.db