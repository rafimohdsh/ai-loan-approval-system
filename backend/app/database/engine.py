"""
SQLAlchemy engine and Base configuration module.

This module handles:
- Engine initialization
- Table creation
- Base model configuration
- Connection lifecycle management
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import inspect
from .connection import engine
from ..models.base import Base
import logging

logger = logging.getLogger(__name__)


def create_tables() -> None:
    """Create all tables defined in models.

    This should be called after all models are imported.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise


def get_engine():
    """Get SQLAlchemy engine"""
    return engine
