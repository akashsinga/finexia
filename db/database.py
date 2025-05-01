# db/database.py

import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment with fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/finexia")

# Connection pooling configuration
engine_args = {
    "pool_pre_ping": True,  # Detect disconnections
    "pool_recycle": 3600,   # Recycle connections after 1 hour
    "pool_size": 10,        # Maximum pool size
    "max_overflow": 20      # Maximum overflow connections
}

# Create database engine with optimized settings
engine = create_engine(DATABASE_URL, **engine_args)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Session:
    """Create and return a new database session with retry logic."""
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            session = SessionLocal()
            # Test the connection
            session.execute("SELECT 1")
            return session
        except OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            else:
                raise
        except Exception as e:
            raise

def check_db_connection() -> bool:
    """Check if database connection is working."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False