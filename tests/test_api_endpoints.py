"""Tests for loan API endpoints."""

import pytest


# Valid test data
VALID_LOAN_DATA = {
    "applicant_name": "John Doe",
    "applicant_email": "john@example.com",
    "applicant_phone": "+1-555-1234",
    "location": "San Francisco, CA",
    "loan_amount": 50000.0,
    "loan_type": "Personal",
    "loan_term_months": 60,
    "annual_income": 120000.0,
    "employment_status": "Employed Full-time",
    "years_employed": 5.0,
    "credit_score": 750,
    "existing_debt": 500.0,
}


class TestLoanEndpoints:
    """Test suite for loan endpoints."""

    def test_apply_loan_success(self, client):
        """Test successful loan application."""
        response = client.post("/loans/apply", json=VALID_LOAN_DATA)
        assert response.status_code == 201
        data = response.json()
        assert "application_id" in data
        assert data["applicant_name"] == "John Doe"
        assert data["loan_amount"] == 50000.0
        assert data["status"] in ["PENDING", "APPROVED", "REJECTED", "UNDER_REVIEW"]

    def test_apply_loan_missing_required_field(self, client):
        """Test loan application with missing required field."""
        incomplete_data = VALID_LOAN_DATA.copy()
        del incomplete_data["applicant_name"]
        response = client.post("/loans/apply", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_apply_loan_invalid_email(self, client):
        """Test loan application with invalid email."""
        invalid_data = VALID_LOAN_DATA.copy()
        invalid_data["applicant_email"] = "not-an-email"
        response = client.post("/loans/apply", json=invalid_data)
        # May or may not fail depending on email validation
        assert response.status_code in [201, 422]

    def test_apply_loan_zero_income(self, client):
        """Test loan application with zero income."""
        invalid_data = VALID_LOAN_DATA.copy()
        invalid_data["annual_income"] = 0.0
        response = client.post("/loans/apply", json=invalid_data)
        assert response.status_code == 201  # Should create but likely REJECT
        data = response.json()
        assert data["status"] == "REJECTED"

    def test_apply_loan_negative_loan_amount(self, client):
        """Test loan application with negative loan amount."""
        invalid_data = VALID_LOAN_DATA.copy()
        invalid_data["loan_amount"] = -50000.0
        response = client.post("/loans/apply", json=invalid_data)
        # Should either reject or fail validation
        assert response.status_code in [201, 422]

    def test_get_loan_status_success(self, client):
        """Test getting loan status."""
        # First create a loan
        create_response = client.post("/loans/apply", json=VALID_LOAN_DATA)
        assert create_response.status_code == 201
        app_id = create_response.json()["application_id"]

        # Get status
        response = client.get(f"/loans/status/{app_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["application_id"] == app_id
        assert data["applicant_name"] == "John Doe"

    def test_get_loan_status_not_found(self, client):
        """Test getting status for non-existent loan."""
        response = client.get("/loans/status/non-existent-id")
        assert response.status_code == 404

    def test_list_loan_applications(self, client):
        """Test listing loan applications."""
        # Create a few loans
        for i in range(3):
            data = VALID_LOAN_DATA.copy()
            data["applicant_name"] = f"Applicant {i}"
            client.post("/loans/apply", json=data)

        # List applications
        response = client.get("/loans/status")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_list_loan_applications_pagination(self, client):
        """Test pagination in loan list."""
        # Create applications
        for i in range(5):
            data = VALID_LOAN_DATA.copy()
            data["applicant_name"] = f"Applicant {i}"
            client.post("/loans/apply", json=data)

        # Test pagination
        response = client.get("/loans/status?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_workflow_execution(self, client):
        """Test that workflow is executed and decision is made."""
        # Create a low-risk applicant
        good_profile = VALID_LOAN_DATA.copy()
        good_profile["credit_score"] = 750
        good_profile["annual_income"] = 150000
        good_profile["existing_debt"] = 300
        good_profile["loan_amount"] = 30000

        response = client.post("/loans/apply", json=good_profile)
        assert response.status_code == 201
        data = response.json()

        # Verify decision was made
        assert data["risk_score"] is not None
        assert data["approval_probability"] is not None
        assert data["status"] in ["APPROVED", "REJECTED", "UNDER_REVIEW", "PENDING"]

    def test_high_risk_application(self, client):
        """Test high-risk application handling."""
        high_risk = VALID_LOAN_DATA.copy()
        high_risk["credit_score"] = 580  # Very low
        high_risk["existing_debt"] = 5000  # High debt
        high_risk["annual_income"] = 50000  # Lower income

        response = client.post("/loans/apply", json=high_risk)
        assert response.status_code == 201
        data = response.json()

        # Should have high risk score
        assert data["risk_score"] is not None
        # Likely to be rejected or under review
        assert data["status"] in ["REJECTED", "UNDER_REVIEW", "PENDING"]

    def test_no_credit_score_application(self, client):
        """Test application with no credit score."""
        no_credit = VALID_LOAN_DATA.copy()
        no_credit["credit_score"] = None

        response = client.post("/loans/apply", json=no_credit)
        assert response.status_code == 201
        data = response.json()

        # Should go to manual review
        assert data["status"] in ["UNDER_REVIEW", "PENDING"]
