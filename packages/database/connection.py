"""
Database connection and session management for SmartMeet
Shared across all services in the monorepo
"""
import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv
from .models import Base

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    # Fallback to .env.local for development
    env_local_file = project_root / ".env.local" 
    if env_local_file.exists():
        load_dotenv(env_local_file)

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://smartmeet:password@localhost:5432/smartmeet_dev"
)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite settings for testing only
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
    logger.info("Using SQLite database (testing mode)")
else:
    # PostgreSQL settings for development and production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections every hour
        pool_size=10,        # Connection pool size
        max_overflow=20,     # Max overflow connections
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
    logger.info("Using PostgreSQL database")

# Configure session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session for FastAPI
    Usage: def my_endpoint(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    Usage: 
    with get_db_session() as db:
        user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def drop_tables():
    """Drop all database tables (use with caution!)"""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped")

def reset_database():
    """Reset database by dropping and recreating all tables"""
    logger.info("Resetting database...")
    drop_tables()
    create_tables()
    logger.info("Database reset complete")

def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info(f"Database connection successful: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error(f"Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'sqlite'}")
        return False

# Database event listeners for logging
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and consistency"""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log SQL queries in debug mode"""
    if os.getenv("DEBUG", "false").lower() == "true" and logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Executing SQL: {statement}")
        if parameters:
            logger.debug(f"Parameters: {parameters}")

# Initialize database on module import
def init_database():
    """Initialize database with tables if they don't exist"""
    try:
        # Check if connection works
        if not check_database_connection():
            logger.error("Cannot initialize database - connection failed")
            return False
            
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            logger.info("No existing tables found, creating database schema...")
            create_tables()
        else:
            logger.info(f"Found existing tables: {existing_tables}")
            
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

# Auto-initialize database when module is imported
if __name__ != "__main__":
    init_database() 