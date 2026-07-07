"""Test suite for Profile Agent."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ..agents.profile_agent import     analyze_applicant,
    ApplicantProfile,
    calculate_risk_level,
    identify_risk_factors,
)


def test_profile_agent_low_risk():
    """Test profile agent with a low-risk applicant."""
    profile = analyze_applicant(
        application_id="APP-001",
        applicant_name="John Smith",
        applicant_email="john.smith@example.com",
        applicant_phone="555-1234",
        annual_income=120000,
        employment_status="Permanent Full-time",
        years_employed=7,
        loan_amount=50000,
        loan_type="Personal",
        loan_term_months=60,
        credit_score=750,
        existing_debt=500,
        estimated_interest_rate=5.0,
    )

    assert isinstance(profile, ApplicantProfile)
    assert profile.personal_info.name == "John Smith"
    assert profile.income_profile.annual_income == 120000
    assert profile.credit_profile.credit_score == 750
    assert profile.risk_level == "Low"
    assert profile.risk_score < 25
    assert len(profile.risk_factors) > 0


def test_profile_agent_high_risk():
    """Test profile agent with a high-risk applicant."""
    profile = analyze_applicant(
        application_id="APP-002",
        applicant_name="Jane Doe",
        applicant_email="jane.doe@example.com",
        applicant_phone="555-5678",
        annual_income=40000,
        employment_status="Part-time Contract",
        years_employed=0.5,
        loan_amount=80000,
        loan_type="Home",
        loan_term_months=360,
        credit_score=580,
        existing_debt=1500,
        estimated_interest_rate=8.0,
    )

    assert isinstance(profile, ApplicantProfile)
    assert profile.personal_info.name == "Jane Doe"
    assert profile.risk_level == "High"
    assert profile.risk_score > 50
    assert len(profile.risk_factors) >= 3


def test_profile_without_credit_score():
    """Test profile agent with applicant having no credit score."""
    profile = analyze_applicant(
        application_id="APP-003",
        applicant_name="Bob Johnson",
        applicant_email="bob.johnson@example.com",
        applicant_phone="555-9999",
        annual_income=75000,
        employment_status="Permanent Full-time",
        years_employed=3,
        loan_amount=30000,
        loan_type="Auto",
        loan_term_months=60,
        credit_score=None,  # No credit score
        existing_debt=0,
        estimated_interest_rate=6.5,
    )

    assert profile.credit_profile.credit_score is None
    assert profile.credit_profile.credit_risk_level is None
    assert "No credit score available" in profile.risk_factors


def test_risk_level_calculation():
    """Test risk level calculation function."""
    # Low risk scenario
    risk_level, risk_score = calculate_risk_level(
        debt_to_income=0.30,
        credit_score=760,
        income_to_loan=3.5,
        employment_years=5,
    )
    assert risk_level == "Low"

    # High risk scenario
    risk_level, risk_score = calculate_risk_level(
        debt_to_income=0.55,
        credit_score=580,
        income_to_loan=0.8,
        employment_years=0.5,
    )
    assert risk_level in ["High", "Very High"]


def test_identify_risk_factors():
    """Test risk factor identification."""
    factors = identify_risk_factors(
        debt_to_income=0.60,
        credit_score=600,
        income_to_loan=0.5,
        employment_years=0.5,
        employment_status="Self-employed",
        existing_debt=2000,
    )

    assert "High debt-to-income ratio (>50%)" in factors
    assert "Loan amount exceeds annual income" in factors
    assert "Less than 1 year employment history" in factors
    assert "Self-employed (variable income risk)" in factors


def test_profile_structure():
    """Test the structure of returned profile."""
    profile = analyze_applicant(
        application_id="APP-004",
        applicant_name="Alice Wonder",
        applicant_email="alice@example.com",
        applicant_phone="555-0000",
        annual_income=95000,
        employment_status="Permanent Full-time",
        years_employed=4,
        loan_amount=45000,
        loan_type="Personal",
        loan_term_months=48,
        credit_score=720,
        existing_debt=400,
    )

    # Check all nested structures exist
    assert profile.personal_info is not None
    assert profile.personal_info.name == "Alice Wonder"

    assert profile.income_profile is not None
    assert profile.income_profile.monthly_income == 95000 / 12
    assert profile.income_profile.employment_stability_score > 0

    assert profile.credit_profile is not None
    assert profile.credit_profile.debt_to_income_ratio > 0
    assert profile.credit_profile.debt_to_income_status in ["Acceptable", "Warning", "High Risk"]

    assert profile.loan_profile is not None
    assert profile.loan_profile.estimated_monthly_payment > 0
    assert profile.loan_profile.income_to_loan_status in ["Acceptable", "Warning", "High Risk"]

    assert profile.risk_score >= 0
    assert profile.risk_score <= 100
    assert profile.risk_level in ["Low", "Medium", "High", "Very High"]
    assert len(profile.risk_factors) > 0
    assert profile.profile_summary != ""


def test_json_serialization():
    """Test that profile can be serialized to JSON."""
    profile = analyze_applicant(
        application_id="APP-005",
        applicant_name="Charlie Brown",
        applicant_email="charlie@example.com",
        applicant_phone="555-1111",
        annual_income=110000,
        employment_status="Permanent Full-time",
        years_employed=6,
        loan_amount=55000,
        loan_type="Personal",
        loan_term_months=60,
        credit_score=700,
    )

    # Convert to dict (used in JSON serialization)
    profile_dict = profile.model_dump()

    assert isinstance(profile_dict, dict)
    assert "personal_info" in profile_dict
    assert "income_profile" in profile_dict
    assert "credit_profile" in profile_dict
    assert "loan_profile" in profile_dict
    assert "risk_score" in profile_dict
    assert "risk_level" in profile_dict


if __name__ == "__main__":
    print("Running Profile Agent Tests...")
    test_profile_agent_low_risk()
    print("✓ Low-risk profile test passed")

    test_profile_agent_high_risk()
    print("✓ High-risk profile test passed")

    test_profile_without_credit_score()
    print("✓ No credit score test passed")

    test_risk_level_calculation()
    print("✓ Risk level calculation test passed")

    test_identify_risk_factors()
    print("✓ Risk factor identification test passed")

    test_profile_structure()
    print("✓ Profile structure test passed")

    test_json_serialization()
    print("✓ JSON serialization test passed")

    print("\nAll tests passed! ✓")
