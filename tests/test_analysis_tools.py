"""Tests for analysis tools."""
import pytest
from backend.app.agents.tools import (
    calculate_debt_to_income_ratio,
    calculate_income_to_loan_ratio,
    calculate_monthly_payment,
    assess_employment_stability,
    interpret_credit_score
)


def test_calculate_debt_to_income_ratio():
    """Test DTI ratio calculation."""
    dti = calculate_debt_to_income_ratio(2000, 8000)
    assert dti == 0.25


def test_calculate_income_to_loan_ratio():
    """Test income-to-loan ratio calculation."""
    ratio = calculate_income_to_loan_ratio(100000, 50000)
    assert ratio == 2.0


def test_calculate_monthly_payment():
    """Test monthly payment calculation."""
    payment = calculate_monthly_payment(50000, 5.0, 60)
    assert payment > 0
    assert payment < 1000  # Approximate check


def test_assess_employment_stability():
    """Test employment stability assessment."""
    result = assess_employment_stability(5.0, "Full-time Employed")
    assert result["stability_score"] > 80
    assert result["tenure_years"] == 5.0


def test_interpret_credit_score():
    """Test credit score interpretation."""
    # Good credit
    result = interpret_credit_score(750)
    assert result["risk_level"] == "low"

    # Fair credit
    result = interpret_credit_score(680)
    assert result["risk_level"] == "medium"

    # Poor credit
    result = interpret_credit_score(580)
    assert result["risk_level"] == "high"
