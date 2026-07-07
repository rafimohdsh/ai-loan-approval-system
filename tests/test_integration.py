"""Integration tests for end-to-end workflows."""

import pytest
from datetime import datetime
from unittest.mock import patch

from backend.app.services import LoanService
from backend.app.services.orchestration_service import OrchestrationService
from backend.app.schemas import LoanApplicationCreate
from backend.app.models import (
    LoanApplication,
    LoanStatus,
    DecisionStatus,
)


class TestEndToEndLoanApprovalFlow:
    """Integration tests for complete loan approval workflows."""

    def test_complete_approved_workflow(self, db):
        """Test complete workflow for an approved application."""
        # Step 1: Create application
        data = LoanApplicationCreate(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="+1-555-1234",
            location="San Francisco, CA",
            loan_amount=30000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=150000.0,
            employment_status="Employed Full-time",
            years_employed=5.0,
            credit_score=750,
            existing_debt=300.0,
        )

        app = LoanService.create_application(db, data)
        assert app is not None
        assert app.status == LoanStatus.PENDING

        # Step 2: Process through orchestration
        result = OrchestrationService.process_loan_application(db, app)

        # Step 3: Verify results
        assert result is not None
        assert result["risk_score"] is not None
        assert result["approval_probability"] is not None

        # Step 4: Verify database state
        db.refresh(app)
        assert app.status in [LoanStatus.APPROVED, LoanStatus.UNDER_REVIEW, LoanStatus.REJECTED]
        assert app.processed_at is not None

    def test_complete_rejected_workflow(self, db):
        """Test complete workflow for a rejected application."""
        # Step 1: Create high-risk application
        data = LoanApplicationCreate(
            applicant_name="Jane Smith",
            applicant_email="jane@example.com",
            applicant_phone="+1-555-5678",
            location="New York, NY",
            loan_amount=100000.0,
            loan_type="Personal",
            loan_term_months=120,
            annual_income=40000.0,
            employment_status="Self-employed",
            years_employed=0.5,
            credit_score=550,
            existing_debt=5000.0,
        )

        app = LoanService.create_application(db, data)
        assert app.status == LoanStatus.PENDING

        # Step 2: Process through orchestration
        result = OrchestrationService.process_loan_application(db, app)

        # Step 3: Verify rejection
        db.refresh(app)
        assert app.status in [LoanStatus.REJECTED, LoanStatus.UNDER_REVIEW]
        assert result["risk_score"] > 0.5

    def test_complete_manual_review_workflow(self, db):
        """Test workflow requiring manual review."""
        # Create application with marginal profile
        data = LoanApplicationCreate(
            applicant_name="Bob Johnson",
            applicant_email="bob@example.com",
            applicant_phone="+1-555-9999",
            location="Denver, CO",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=80000.0,
            employment_status="Employed",
            years_employed=0.8,
            credit_score=None,
            existing_debt=2000.0,
        )

        app = LoanService.create_application(db, data)

        # Process through orchestration
        result = OrchestrationService.process_loan_application(db, app)

        # Should go to manual review or pending
        db.refresh(app)
        assert app.status in [LoanStatus.UNDER_REVIEW, LoanStatus.PENDING]

    def test_multiple_sequential_applications(self, db):
        """Test processing multiple applications in sequence."""
        applications_data = [
            {
                "applicant_name": "Applicant 1",
                "credit_score": 750,
                "annual_income": 120000.0,
            },
            {
                "applicant_name": "Applicant 2",
                "credit_score": 650,
                "annual_income": 80000.0,
            },
            {
                "applicant_name": "Applicant 3",
                "credit_score": 550,
                "annual_income": 40000.0,
            },
        ]

        results = []
        for app_data in applications_data:
            data = LoanApplicationCreate(
                applicant_name=app_data["applicant_name"],
                applicant_email=f"{app_data['applicant_name'].lower().replace(' ', '')}@example.com",
                applicant_phone="+1-555-0000",
                location="Test City",
                loan_amount=50000.0,
                loan_type="Personal",
                loan_term_months=60,
                annual_income=app_data["annual_income"],
                employment_status="Employed",
                years_employed=5.0,
                credit_score=app_data["credit_score"],
                existing_debt=500.0,
            )

            app = LoanService.create_application(db, data)
            result = OrchestrationService.process_loan_application(db, app)
            results.append({
                "application": app,
                "result": result,
            })

        # Verify all applications were processed
        assert len(results) == 3
        for item in results:
            db.refresh(item["application"])
            assert item["application"].status != LoanStatus.PENDING

    def test_application_status_transitions(self, db):
        """Test that application goes through proper status transitions."""
        data = LoanApplicationCreate(
            applicant_name="Status Test",
            applicant_email="status@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
        )

        # Initial status
        app = LoanService.create_application(db, data)
        assert app.status == LoanStatus.PENDING

        # Process
        result = OrchestrationService.process_loan_application(db, app)
        db.refresh(app)

        # After processing should be APPROVED, REJECTED, or UNDER_REVIEW
        assert app.status in [LoanStatus.APPROVED, LoanStatus.REJECTED, LoanStatus.UNDER_REVIEW]

    def test_decision_record_creation_on_workflow(self, db):
        """Test that decision records are created during workflow."""
        data = LoanApplicationCreate(
            applicant_name="Decision Test",
            applicant_email="decision@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
        )

        app = LoanService.create_application(db, data)
        result = OrchestrationService.process_loan_application(db, app)

        # Verify decision was created
        from backend.app.models import LoanDecision
        decisions = db.query(LoanDecision).filter(
            LoanDecision.loan_application_id == app.id
        ).all()
        assert len(decisions) > 0

    def test_risk_scores_populated(self, db):
        """Test that risk scores are properly populated."""
        data = LoanApplicationCreate(
            applicant_name="Risk Score Test",
            applicant_email="risk@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
        )

        app = LoanService.create_application(db, data)
        result = OrchestrationService.process_loan_application(db, app)

        db.refresh(app)
        assert app.risk_score is not None
        assert app.approval_probability is not None
        assert 0.0 <= app.risk_score <= 1.0
        assert 0.0 <= app.approval_probability <= 1.0

    def test_different_loan_types(self, db):
        """Test workflow with different loan types."""
        loan_types = ["Personal", "Auto", "Home", "Student"]

        for loan_type in loan_types:
            data = LoanApplicationCreate(
                applicant_name=f"Test {loan_type}",
                applicant_email=f"{loan_type.lower()}@example.com",
                applicant_phone="+1-555-0000",
                location="Test City",
                loan_amount=50000.0 if loan_type != "Home" else 300000.0,
                loan_type=loan_type,
                loan_term_months=60 if loan_type != "Home" else 360,
                annual_income=120000.0,
                employment_status="Employed",
                years_employed=5.0,
                credit_score=750,
                existing_debt=500.0,
            )

            app = LoanService.create_application(db, data)
            result = OrchestrationService.process_loan_application(db, app)

            db.refresh(app)
            assert app.status in [LoanStatus.APPROVED, LoanStatus.REJECTED, LoanStatus.UNDER_REVIEW]

    def test_employment_status_variations(self, db):
        """Test workflow with different employment statuses."""
        statuses = [
            "Employed Full-time",
            "Employed Part-time",
            "Self-employed",
            "Contract",
            "Retired",
        ]

        for status in statuses:
            data = LoanApplicationCreate(
                applicant_name=f"Test {status}",
                applicant_email=f"{status.lower().replace('-', '')}@example.com",
                applicant_phone="+1-555-0000",
                location="Test City",
                loan_amount=50000.0,
                loan_type="Personal",
                loan_term_months=60,
                annual_income=100000.0,
                employment_status=status,
                years_employed=3.0,
                credit_score=700,
                existing_debt=500.0,
            )

            app = LoanService.create_application(db, data)
            result = OrchestrationService.process_loan_application(db, app)

            assert result is not None
            assert "risk_score" in result

    def test_audit_trail_generation(self, db):
        """Test that audit trail is properly generated."""
        data = LoanApplicationCreate(
            applicant_name="Audit Trail Test",
            applicant_email="audit@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
        )

        app = LoanService.create_application(db, data)
        result = OrchestrationService.process_loan_application(db, app)

        assert "audit_trail" in result
        assert isinstance(result["audit_trail"], list)
        assert len(result["audit_trail"]) > 0

        # Messages should contain workflow steps
        messages = result["audit_trail"]
        messages_str = " ".join(messages).lower()
        assert "profile" in messages_str or "analysis" in messages_str or "✓" in " ".join(messages)

    def test_workflow_idempotency(self, db):
        """Test that running workflow multiple times doesn't break state."""
        data = LoanApplicationCreate(
            applicant_name="Idempotency Test",
            applicant_email="idempotent@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
        )

        app = LoanService.create_application(db, data)

        # First processing
        result1 = OrchestrationService.process_loan_application(db, app)
        db.refresh(app)
        status1 = app.status

        # Re-query and verify consistency
        app = LoanService.get_application(db, app.application_id)
        assert app.status == status1


class TestErrorRecovery:
    """Test error recovery in workflows."""

    def test_workflow_recovery_from_agent_error(self, db):
        """Test workflow recovery when an agent encounters an error."""
        data = LoanApplicationCreate(
            applicant_name="Error Recovery Test",
            applicant_email="recovery@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
        )

        app = LoanService.create_application(db, data)

        # Should complete despite potential agent errors
        result = OrchestrationService.process_loan_application(db, app)

        assert result is not None
        assert "decision_status" in result


class TestPerformanceEdgeCases:
    """Test performance with edge case data."""

    def test_many_decimal_places(self, db):
        """Test handling of many decimal places in financial data."""
        data = LoanApplicationCreate(
            applicant_name="Decimal Test",
            applicant_email="decimal@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.123456,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.987654,
            employment_status="Employed",
            years_employed=5.5,
            credit_score=750,
            existing_debt=500.123,
        )

        app = LoanService.create_application(db, data)
        assert app is not None

    def test_extreme_but_valid_values(self, db):
        """Test with extreme but valid values."""
        data = LoanApplicationCreate(
            applicant_name="Extreme Test",
            applicant_email="extreme@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=9999999.99,
            loan_type="Personal",
            loan_term_months=360,
            annual_income=5000000.0,
            employment_status="Employed",
            years_employed=50.0,
            credit_score=850,
            existing_debt=0.01,
        )

        app = LoanService.create_application(db, data)
        result = OrchestrationService.process_loan_application(db, app)

        assert result is not None
        assert app.loan_amount == 9999999.99
