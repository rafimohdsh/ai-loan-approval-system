"""
Database connection layer for SQLAlchemy ORM with MySQL.

This module provides:
- SQLAlchemy engine with connection pooling
- Session factory for database operations
- Dependency injection for FastAPI
- Connection utilities
"""

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


# SQLAlchemy Engine Configuration
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
    connect_args={
        "connect_timeout": 10,
        "charset": "utf8mb4",
    }
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Configure database connection parameters"""
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES'")
    except Exception:
        pass  # Ignore if pragma fails (e.g., SQLite doesn't support this)
    cursor.close()




# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Session:
    """Dependency for FastAPI to get database session.

    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def get_db_sync() -> Session:
    """Synchronous database session getter (for non-async contexts).

    Usage:
        db = get_db_sync()
        try:
            # do work
        finally:
            db.close()
    """
    return SessionLocal()


def close_db():
    """Close all database connections"""
    engine.dispose()
    logger.info("All database connections closed")
