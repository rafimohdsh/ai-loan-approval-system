"""Tests for loan service."""
import pytest
from backend.app.services import LoanService
from backend.app.schemas import LoanApplicationCreate, LoanApplicationUpdate


@pytest.fixture
def loan_data():
    """Sample loan application data."""
    return {
        "applicant_name": "John Doe",
        "applicant_email": "john@example.com",
        "applicant_phone": "555-1234",
        "loan_amount": 50000.0,
        "loan_type": "Personal",
        "loan_term_months": 60,
        "annual_income": 100000.0,
        "employment_status": "Full-time Employed",
        "years_employed": 5.0,
        "credit_score": 720,
        "existing_debt": 10000.0
    }


def test_create_application(db_session, loan_data):
    """Test creating a loan application."""
    schema = LoanApplicationCreate(**loan_data)
    app = LoanService.create_application(db_session, schema)

    assert app is not None
    assert app.applicant_name == loan_data["applicant_name"]
    assert app.application_id is not None


def test_get_application(db_session, loan_data):
    """Test retrieving a loan application."""
    schema = LoanApplicationCreate(**loan_data)
    created_app = LoanService.create_application(db_session, schema)

    retrieved_app = LoanService.get_application(db_session, created_app.application_id)
    assert retrieved_app is not None
    assert retrieved_app.id == created_app.id


def test_update_application(db_session, loan_data):
    """Test updating a loan application."""
    schema = LoanApplicationCreate(**loan_data)
    app = LoanService.create_application(db_session, schema)

    update_data = LoanApplicationUpdate(agent_notes="Good applicant")
    updated_app = LoanService.update_application(db_session, app.application_id, update_data)

    assert updated_app.agent_notes == "Good applicant"


def test_list_applications(db_session, loan_data):
    """Test listing loan applications."""
    schema = LoanApplicationCreate(**loan_data)
    LoanService.create_application(db_session, schema)

    apps = LoanService.list_applications(db_session)
    assert len(apps) > 0
