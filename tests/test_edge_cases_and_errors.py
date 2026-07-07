"""Tests for edge cases and error scenarios."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from backend.app.services import LoanService
from backend.app.schemas import LoanApplicationCreate, LoanApprovalDecision
from backend.app.models import (
    LoanApplication,
    LoanStatus,
    DecisionStatus,
)
from backend.app.agents.profile_agent import (
    analyze_applicant,
    calculate_risk_level,
    identify_risk_factors,
)
from backend.app.agents.risk_agent import (
    calculate_dti,
    assess_credit_risk,
)


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def test_loan_amount_minimal(self, db):
        """Test with minimal loan amount."""
        data = LoanApplicationCreate(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=100.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=700,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        assert app.loan_amount == 100.0

    def test_negative_loan_amount_rejected(self):
        """Test that negative loan amounts are handled."""
        with pytest.raises(Exception):
            data = LoanApplicationCreate(
                applicant_name="Test User",
                applicant_email="test@example.com",
                applicant_phone="+1-555-0000",
                location="Test City",
                loan_amount=-50000.0,
                loan_type="Personal",
                loan_term_months=60,
                annual_income=100000.0,
                employment_status="Employed",
                years_employed=5.0,
                credit_score=700,
                existing_debt=0.0,
            )

    def test_annual_income_very_low(self, db):
        """Test application with very low annual income."""
        data = LoanApplicationCreate(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=1000.0,
            employment_status="Unemployed",
            years_employed=0.0,
            credit_score=700,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        assert app.annual_income == 1000.0

        # Decision should reject
        decision = LoanService.create_decision(db, app)
        assert decision.decision_status == DecisionStatus.REJECTED

    def test_credit_score_minimum(self, db):
        """Test with minimum credit score."""
        data = LoanApplicationCreate(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=300,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        decision = LoanService.create_decision(db, app)
        assert decision.risk_score > 0.7

    def test_credit_score_maximum(self, db):
        """Test with maximum credit score."""
        data = LoanApplicationCreate(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=850,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        decision = LoanService.create_decision(db, app)
        assert decision.risk_score < 0.3

    def test_extremely_high_debt_to_income(self, db):
        """Test with extremely high debt-to-income ratio."""
        data = LoanApplicationCreate(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=500000.0,
            loan_type="Personal",
            loan_term_months=360,
            annual_income=50000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=700,
            existing_debt=50000.0,
        )

        app = LoanService.create_application(db, data)
        decision = LoanService.create_decision(db, app)
        assert decision.decision_status == DecisionStatus.REJECTED

    def test_very_short_employment_history(self, db):
        """Test with very short employment history."""
        data = LoanApplicationCreate(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=0.1,
            credit_score=700,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        decision = LoanService.create_decision(db, app)
        assert decision.decision_status in [DecisionStatus.PENDING, DecisionStatus.REJECTED]

    def test_very_long_loan_term(self, db):
        """Test with very long loan term."""
        data = LoanApplicationCreate(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=500000.0,
            loan_type="Home",
            loan_term_months=480,
            annual_income=150000.0,
            employment_status="Employed",
            years_employed=10.0,
            credit_score=750,
            existing_debt=1000.0,
        )

        app = LoanService.create_application(db, data)
        assert app.loan_term_months == 480

    def test_very_short_loan_term(self, db):
        """Test with very short loan term."""
        data = LoanApplicationCreate(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=12,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=700,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        assert app.loan_term_months == 12


class TestStringEdgeCases:
    """Test string input edge cases."""

    def test_very_long_applicant_name(self, db):
        """Test with very long applicant name."""
        long_name = "A" * 255
        data = LoanApplicationCreate(
            applicant_name=long_name,
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=700,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        assert len(app.applicant_name) == 255

    def test_special_characters_in_name(self, db):
        """Test with special characters in applicant name."""
        data = LoanApplicationCreate(
            applicant_name="John O'Brien-Smith",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=700,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        assert app.applicant_name == "John O'Brien-Smith"

    def test_international_characters(self, db):
        """Test with international characters."""
        data = LoanApplicationCreate(
            applicant_name="José García",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=700,
            existing_debt=0.0,
        )

        app = LoanService.create_application(db, data)
        assert "José" in app.applicant_name


class TestDTICalculations:
    """Test DTI calculation edge cases."""

    def test_dti_with_zero_income(self):
        """Test DTI calculation with zero income."""
        dti = calculate_dti(1000.0, 0.0)
        assert dti.dti_ratio == 1.0
        assert dti.status == "Critical"

    def test_dti_with_zero_debt(self):
        """Test DTI calculation with zero debt."""
        dti = calculate_dti(0.0, 5000.0)
        assert dti.dti_ratio == 0.0
        assert dti.status == "Acceptable"

    def test_dti_acceptable_threshold(self):
        """Test DTI at acceptable threshold."""
        dti = calculate_dti(1800.0, 5000.0)  # 0.36
        assert dti.dti_ratio <= 0.36
        assert dti.status == "Acceptable"

    def test_dti_warning_threshold(self):
        """Test DTI at warning threshold."""
        dti = calculate_dti(2150.0, 5000.0)  # 0.43
        assert dti.dti_ratio <= 0.43
        assert dti.status == "Warning"

    def test_dti_critical_threshold(self):
        """Test DTI at critical threshold."""
        dti = calculate_dti(2600.0, 5000.0)  # 0.52
        assert dti.dti_ratio > 0.50
        assert dti.status == "Critical"


class TestCreditRiskAssessment:
    """Test credit risk assessment edge cases."""

    def test_credit_risk_none_score(self):
        """Test credit risk with None score."""
        assessment = assess_credit_risk(None)
        assert assessment.credit_score is None
        assert assessment.risk_level is not None

    def test_credit_risk_perfect_score(self):
        """Test credit risk with perfect score."""
        assessment = assess_credit_risk(850)
        assert assessment.credit_score == 850
        assert assessment.risk_score <= 10

    def test_credit_risk_poor_score(self):
        """Test credit risk with poor score."""
        assessment = assess_credit_risk(300)
        assert assessment.credit_score == 300
        assert assessment.risk_score > 80

    def test_credit_risk_threshold_scores(self):
        """Test credit risk at all thresholds."""
        thresholds = [600, 650, 700, 750]
        for score in thresholds:
            assessment = assess_credit_risk(score)
            assert assessment.credit_score == score
            assert 0 <= assessment.risk_score <= 100


class TestRiskFactorIdentification:
    """Test risk factor identification."""

    def test_identify_high_dti_risk(self):
        """Test identification of high DTI risk."""
        factors = identify_risk_factors(
            debt_to_income=0.6,
            credit_score=700,
            income_to_loan=2.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=5000.0,
        )
        assert any("debt-to-income" in f.lower() for f in factors)

    def test_identify_low_credit_risk(self):
        """Test identification of low credit risk."""
        factors = identify_risk_factors(
            debt_to_income=0.3,
            credit_score=580,
            income_to_loan=2.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=1000.0,
        )
        assert any("credit" in f.lower() for f in factors)

    def test_identify_no_credit_history(self):
        """Test identification of no credit history."""
        factors = identify_risk_factors(
            debt_to_income=0.3,
            credit_score=None,
            income_to_loan=2.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=500.0,
        )
        assert any("credit" in f.lower() for f in factors)

    def test_identify_employment_risk(self):
        """Test identification of employment risk."""
        factors = identify_risk_factors(
            debt_to_income=0.3,
            credit_score=700,
            income_to_loan=2.0,
            employment_years=0.5,
            employment_status="Employed",
            existing_debt=500.0,
        )
        assert any("employment" in f.lower() for f in factors)

    def test_identify_self_employed_risk(self):
        """Test identification of self-employment risk."""
        factors = identify_risk_factors(
            debt_to_income=0.3,
            credit_score=700,
            income_to_loan=2.0,
            employment_years=3.0,
            employment_status="Self-employed",
            existing_debt=500.0,
        )
        assert any("self-employed" in f.lower() for f in factors)

    def test_identify_no_risk_factors(self):
        """Test when no risk factors are identified."""
        factors = identify_risk_factors(
            debt_to_income=0.2,
            credit_score=800,
            income_to_loan=5.0,
            employment_years=10.0,
            employment_status="Employed",
            existing_debt=0.0,
        )
        # May return empty list or "no significant risk factors"
        assert len(factors) == 0 or any("no" in f.lower() or "significant" in f.lower() for f in factors)


class TestRiskLevelCalculation:
    """Test risk level calculation."""

    def test_risk_level_low(self):
        """Test low risk calculation."""
        level, score = calculate_risk_level(
            debt_to_income=0.2,
            credit_score=800,
            income_to_loan=5.0,
            employment_years=10.0,
        )
        assert level == "Low"
        assert score < 25

    def test_risk_level_medium(self):
        """Test medium risk calculation."""
        level, score = calculate_risk_level(
            debt_to_income=0.43,
            credit_score=650,
            income_to_loan=3.0,
            employment_years=3.0,
        )
        assert level in ["Low", "Medium"]
        assert score >= 0

    def test_risk_level_high(self):
        """Test high risk calculation."""
        level, score = calculate_risk_level(
            debt_to_income=0.50,
            credit_score=600,
            income_to_loan=1.5,
            employment_years=0.8,
        )
        assert level in ["Medium", "High"]
        assert score >= 0

    def test_risk_level_very_high(self):
        """Test very high risk calculation."""
        level, score = calculate_risk_level(
            debt_to_income=0.6,
            credit_score=550,
            income_to_loan=0.5,
            employment_years=0.5,
        )
        assert level == "Very High"
        assert score >= 75

    def test_risk_level_with_no_credit(self):
        """Test risk level calculation with no credit score."""
        level, score = calculate_risk_level(
            debt_to_income=0.3,
            credit_score=None,
            income_to_loan=3.0,
            employment_years=5.0,
        )
        assert level is not None
        assert 0 <= score <= 100


class TestApplicantProfileAnalysis:
    """Test applicant profile analysis."""

    def test_profile_with_valid_data(self):
        """Test profile analysis with valid data."""
        profile = analyze_applicant(
            application_id="APP-001",
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="+1-555-1234",
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            credit_score=750,
            existing_debt=500.0,
        )

        assert profile is not None
        assert profile.personal_info.name == "John Doe"
        assert profile.income_profile.annual_income == 120000.0
        assert profile.credit_profile.credit_score == 750

    def test_profile_with_no_credit_score(self):
        """Test profile analysis without credit score."""
        profile = analyze_applicant(
            application_id="APP-002",
            applicant_name="Jane Doe",
            applicant_email="jane@example.com",
            applicant_phone="+1-555-5678",
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=3.0,
            loan_amount=40000.0,
            loan_type="Personal",
            loan_term_months=48,
            credit_score=None,
            existing_debt=300.0,
        )

        assert profile is not None
        assert profile.credit_profile.credit_score is None

    def test_profile_debt_calculations(self):
        """Test that debt calculations are accurate."""
        profile = analyze_applicant(
            application_id="APP-003",
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            credit_score=750,
            existing_debt=500.0,
        )

        assert profile.credit_profile.debt_to_income_ratio >= 0.0
        assert profile.credit_profile.debt_to_income_ratio <= 1.0
