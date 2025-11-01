"""
Neon PostgreSQL Database Connection (No Auth)
Simple and direct PostgreSQL connection using SQLAlchemy
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency for FastAPI routes to get database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful!")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

# Test connection on import
if __name__ != "__main__":
    test_connection()
