# scripts/create_admin.py
import argparse
import sys
import os
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from passlib.context import CryptContext

# Load environment variables if needed
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment with fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/finexia")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base model
Base = declarative_base()


# Define User model directly in this script
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Password hash context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user(username, email, password, full_name=None):
    """Create admin user with the given credentials"""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # Check if user already exists
        existing = session.query(User).filter((User.username == username) | (User.email == email)).first()

        if existing:
            print(f"Error: User with username '{username}' or email '{email}' already exists.")
            return False

        # Hash the password
        hashed_password = pwd_context.hash(password)

        # Create user
        user = User(username=username, email=email, hashed_password=hashed_password, full_name=full_name, is_admin=True, is_active=True)

        session.add(user)
        session.commit()
        print(f"Admin user '{username}' created successfully.")
        return True

    except sqlalchemy.exc.SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {str(e)}")
        return False
    except Exception as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--full-name", help="Admin's full name")

    args = parser.parse_args()

    success = create_admin_user(username=args.username, email=args.email, password=args.password, full_name=args.full_name)

    sys.exit(0 if success else 1)
