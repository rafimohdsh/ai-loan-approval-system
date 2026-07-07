"""
Database connection manager for lifecycle management.

Handles:
- Connection initialization
- Connection cleanup
- Context managers for session handling
- Async session management
"""

from contextlib import contextmanager, asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..database.connection import from ..database.engine import from ..database.diagnostics import import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database lifecycle and operations"""

    def __init__(self):
        self.initialized = False

    def initialize(self) -> bool:
        """Initialize database (create tables, verify schema).

        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing database...")

            # Test connection
            if not DatabaseDiagnostics.test_connection():
                raise Exception("Database connection test failed")

            # Create tables
            create_tables()

            # Verify schema
            if not verify_database_schema():
                logger.warning("Schema verification found issues")

            self.initialized = True
            logger.info("✓ Database initialization complete")
            return True

        except Exception as e:
            logger.error(f"✗ Database initialization failed: {str(e)}")
            self.initialized = False
            return False

    def shutdown(self):
        """Shutdown database connections"""
        try:
            close_db()
            self.initialized = False
            logger.info("✓ Database connections closed")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

    def health_check(self) -> bool:
        """Perform health check

        Returns:
            bool: True if healthy
        """
        return DatabaseDiagnostics.test_connection()

    def get_diagnostics(self):
        """Get full diagnostic report"""
        return DatabaseDiagnostics.get_diagnostic_report()

    def print_health(self):
        """Print formatted health report"""
        DatabaseDiagnostics.print_health_report()

    @contextmanager
    def session(self):
        """Context manager for database session.

        Usage:
            with db_manager.session() as db:
                user = db.query(User).first()
        """
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error: {str(e)}")
            raise
        finally:
            db.close()

    @asynccontextmanager
    async def async_session(self):
        """Async context manager for database session.

        Usage:
            async with db_manager.async_session() as db:
                user = await db.execute(select(User))
        """
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error: {str(e)}")
            raise
        finally:
            db.close()

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            Session: SQLAlchemy session

        Note: Remember to close the session when done
        """
        return SessionLocal()


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions using global manager
def initialize_database() -> bool:
    """Initialize the database"""
    return db_manager.initialize()


def shutdown_database():
    """Shutdown database connections"""
    db_manager.shutdown()


def is_database_healthy() -> bool:
    """Check if database is healthy"""
    return db_manager.health_check()


def get_session() -> Session:
    """Get a new database session"""
    return db_manager.get_session()


@contextmanager
def session_context():
    """Context manager for session.

    Usage:
        with session_context() as db:
            user = db.query(User).first()
    """
    with db_manager.session() as db:
        yield db


def print_db_health():
    """Print database health report"""
    db_manager.print_health()


__all__ = [
    "DatabaseManager",
    "db_manager",
    "initialize_database",
    "shutdown_database",
    "is_database_healthy",
    "get_session",
    "session_context",
    "print_db_health",
]
