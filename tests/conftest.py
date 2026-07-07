"""Pytest configuration and fixtures."""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ["ALLOWED_HOSTS"] = "testserver,localhost,127.0.0.1"

from backend.app.database.base import Base
from backend.app.database import get_db
from backend.app.main import app
from backend.app.models import (  # Import to register models
    LoanApplication,
    LoanDecision,
    Customer,
    AuditLog,
    ReviewerProfile,
    ReviewerAssignment,
    ReviewAction,
)

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database and session."""
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db):
    """Alias for db fixture for test compatibility."""
    return db


@pytest.fixture
def client(db):
    """Create test client with dependency override."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
