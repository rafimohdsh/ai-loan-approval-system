from sqlalchemy import inspect
from sqlalchemy.orm import Session
from ..models import Base
from ..database.connection import engine
import logging

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database by creating all tables"""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete")


def check_db_connection() -> bool:
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def get_db_tables() -> list[str]:
    """Get list of all tables in the database"""
    inspector = inspect(engine)
    return inspector.get_table_names()


def drop_all_tables() -> None:
    """Drop all tables from the database. Use with caution!"""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")
