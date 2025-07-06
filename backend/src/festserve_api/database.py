# festserve/backend/src/festserve_api/database.py
"""
Database connection and session management for FestServe.
Provides SQLAlchemy engine, Base, and the get_db dependency for FastAPI.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read the database URL from environment, with a sensible default for Docker Compose
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://festserve:festserve@db:5432/festserve"
)

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models to inherit
Base = declarative_base()

# Dependency for FastAPI requests

def get_db():
    """
    Yield a database session to FastAPI endpoints and close it when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
