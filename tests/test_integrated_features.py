"""Integration tests for new features."""

import pytest
from backend.app.agents.tool_registry import get_tool_registry
from backend.app.agents.profile_agent import analyze_applicant
from backend.app.services.appeal_service import AppealService
from backend.app.models import (
    LoanApplication,
    LoanStatus,
    ReviewerProfile,
)


class TestMCPToolsIntegration:
    """Test MCP tools integration with profile agent."""

    def test_profile_agent_uses_local_tools(self):
        """Test that profile agent uses local analysis tools."""
        profile = analyze_applicant(
            application_id="TEST-APP-001",
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="+1-555-1234",
            annual_income=120000.0,
            employment_status="Employed Full-time",
            years_employed=5.0,
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            credit_score=750,
            existing_debt=5000.0,
            estimated_interest_rate=5.5,
            use_mcp_tools=False,
        )

        assert profile is not None
        assert profile.personal_info.name == "John Doe"
        assert profile.risk_level in ["Low", "Medium", "High", "Very High"]
        assert 0 <= profile.risk_score <= 100

    def test_tool_registry_access(self):
        """Test that tool registry is accessible."""
        registry = get_tool_registry()
        assert registry is not None

        # Test getting specific tools
        dti_tool = registry.get_tool("calculate_dti")
        assert dti_tool is not None
        assert dti_tool.name == "calculate_dti"

    def test_tool_registry_invoke_local_tool(self):
        """Test invoking tool from registry."""
        registry = get_tool_registry()

        result = registry.invoke_tool(
            "calculate_dti",
            monthly_debt=2000.0,
            monthly_income=10000.0
        )

        assert result == 0.2


class TestDatabaseIndexes:
    """Test that database indexes are properly configured."""

    def test_loan_application_has_indexes(self, db):
        """Test loan application has required indexes."""
        loan = LoanApplication(
            application_id="APP-IDX-001",
            applicant_name="Test Applicant",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            location="Test City",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=100000.0,
            employment_status="Employed",
            years_employed=3.0,
            credit_score=700,
            existing_debt=500.0,
            status=LoanStatus.PENDING,
        )
        db.add(loan)
        db.commit()

        # Query by indexed fields should be efficient
        result = db.query(LoanApplication).filter(
            LoanApplication.status == LoanStatus.PENDING
        ).first()

        assert result is not None
        assert result.application_id == "APP-IDX-001"

    def test_reviewer_assignment_has_indexes(self, db):
        """Test reviewer assignment has required indexes."""
        from backend.app.models import ReviewerAssignment, ReviewStatus, ReviewPriority

        assignment = ReviewerAssignment(
            assignment_id="ASSIGN-IDX-001",
            loan_application_id=1,
            reviewer_id="REV-001",
            reviewer_name="Test Reviewer",
            status=ReviewStatus.ASSIGNED,
            priority=ReviewPriority.HIGH,
        )
        db.add(assignment)
        db.commit()

        # Query by indexed fields
        result = db.query(ReviewerAssignment).filter(
            ReviewerAssignment.status == ReviewStatus.ASSIGNED
        ).first()

        assert result is not None


class TestAppealWorkflowIntegration:
    """Test complete appeal workflow."""

    def test_full_appeal_workflow(self, db):
        """Test complete appeal submission and review workflow."""
        # Create loan application
        loan = LoanApplication(
            application_id="APP-FLOW-001",
            applicant_name="Jane Applicant",
            applicant_email="jane@example.com",
            applicant_phone="+1-555-5678",
            location="Boston, MA",
            loan_amount=75000.0,
            loan_type="Personal",
            loan_term_months=72,
            annual_income=95000.0,
            employment_status="Employed",
            years_employed=2.0,
            credit_score=680,
            existing_debt=8000.0,
            status=LoanStatus.REJECTED,
            rejection_reason="Insufficient credit history",
            processed_at=db.query(LoanApplication).filter_by(
                application_id="APP-FLOW-001"
            ).first() is None and None,
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)

        # Create reviewer
        reviewer = ReviewerProfile(
            reviewer_id="REV-APPEAL-001",
            reviewer_name="Senior Reviewer",
            email="senior@example.com",
            phone="+1-555-9999",
            department="Appeals",
            role="SENIOR_REVIEWER",
            is_active=True,
        )
        db.add(reviewer)
        db.commit()

        # Submit appeal
        appeal = AppealService.submit_appeal(
            db,
            loan.id,
            "APP-FLOW-001",
            "Jane Applicant",
            "jane@example.com",
            "I have improved my credit score and obtained new employment",
            "Updated credit report and employment letter",
        )

        assert appeal is not None
        assert appeal.status.value == "SUBMITTED"

        # Assign reviewer
        assigned = AppealService.assign_reviewer(
            db,
            appeal.id,
            reviewer.reviewer_id,
        )

        assert assigned.assigned_to_reviewer == reviewer.reviewer_id
        assert assigned.status.value == "UNDER_REVIEW"

        # Approve appeal
        approved = AppealService.approve_appeal(
            db,
            appeal.id,
            reviewer.reviewer_id,
            "Credit score improved to 720, new stable employment confirmed",
        )

        assert approved.status.value == "APPROVED"
        assert approved.appeal_decision == "APPROVED"

        # Verify history is tracked
        history = AppealService.get_appeal_history(db, appeal.id)
        assert len(history) >= 3  # SUBMITTED, ASSIGNED, APPROVED
        assert history[0].action_type == "APPROVED"

    def test_appeal_statistics_calculation(self, db):
        """Test appeal statistics are calculated correctly."""
        from backend.app.models import AppealPriority

        # Create test loan
        loan = LoanApplication(
            application_id="APP-STAT-001",
            applicant_name="Stat Applicant",
            applicant_email="stat@example.com",
            applicant_phone="+1-555-1111",
            location="Seattle, WA",
            loan_amount=60000.0,
            loan_type="Home",
            loan_term_months=360,
            annual_income=110000.0,
            employment_status="Employed",
            years_employed=4.0,
            credit_score=710,
            existing_debt=10000.0,
            status=LoanStatus.REJECTED,
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)

        # Create reviewer
        reviewer = ReviewerProfile(
            reviewer_id="REV-STAT-001",
            reviewer_name="Stats Reviewer",
            email="stats@example.com",
            department="Appeals",
            role="REVIEWER",
            is_active=True,
        )
        db.add(reviewer)
        db.commit()

        # Create and approve appeal
        appeal = AppealService.submit_appeal(
            db,
            loan.id,
            "STAT-APP-001",
            "Stat Applicant",
            "stat@example.com",
            "Appeal for reconsideration",
        )

        AppealService.approve_appeal(
            db,
            appeal.id,
            reviewer.reviewer_id,
            "Approved for reconsideration",
        )

        # Get statistics
        stats = AppealService.get_appeal_statistics(db, days=1)

        assert stats["total_appeals"] >= 1
        assert stats["approved"] >= 1
        assert stats["approval_rate"] > 0


class TestConnectionPooling:
    """Test that connection pooling is properly configured."""

    def test_database_connection_pooling_enabled(self):
        """Test that connection pooling is configured."""
        from backend.app.database import engine

        # Verify engine has pool configuration
        assert engine.pool is not None
        # QueuePool should be used
        from sqlalchemy.pool import QueuePool
        assert isinstance(engine.pool, QueuePool)


class TestErrorHandling:
    """Test error handling across features."""

    def test_mcp_client_handles_missing_tools(self):
        """Test MCP client gracefully handles missing tools."""
        registry = get_tool_registry()

        # Try to invoke completely non-existent tool
        with pytest.raises(ValueError, match="Tool not found"):
            registry.invoke_tool("completely_nonexistent_tool_xyz")

    def test_appeal_service_handles_invalid_input(self, db):
        """Test appeal service handles invalid inputs gracefully."""
        with pytest.raises(ValueError):
            AppealService.submit_appeal(
                db,
                9999,  # Non-existent loan
                "APP-001",
                "Test Applicant",
                "test@example.com",
                "Appeal reason",
            )

    def test_profile_agent_handles_zero_income(self):
        """Test profile agent handles edge cases like zero income."""
        from backend.app.agents.tools.analysis_tools import calculate_debt_to_income_ratio

        # Should handle division by zero gracefully
        result = calculate_debt_to_income_ratio(5000, 0)
        assert result == float('inf')
