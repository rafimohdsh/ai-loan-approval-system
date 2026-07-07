"""Tests for orchestration service and agent workflows."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.services.orchestration_service import OrchestrationService
from backend.app.models import (
    LoanApplication,
    LoanDecision,
    LoanStatus,
    DecisionStatus,
)
from backend.app.agents.workflows.loan_approval_graph import AgentState, create_loan_approval_graph


@pytest.fixture
def sample_loan_application(db):
    """Create a sample loan application for testing."""
    loan = LoanApplication(
        application_id="APP-001",
        applicant_name="John Doe",
        applicant_email="john@example.com",
        applicant_phone="+1-555-1234",
        location="San Francisco, CA",
        loan_amount=50000.0,
        loan_type="Personal",
        loan_term_months=60,
        annual_income=120000.0,
        employment_status="Employed Full-time",
        years_employed=5.0,
        credit_score=750,
        existing_debt=500.0,
        status=LoanStatus.PENDING,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@pytest.fixture
def high_risk_application(db):
    """Create a high-risk loan application."""
    loan = LoanApplication(
        application_id="APP-HIGHRISK",
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
        credit_score=580,
        existing_debt=5000.0,
        status=LoanStatus.PENDING,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@pytest.fixture
def no_credit_application(db):
    """Create application with no credit score."""
    loan = LoanApplication(
        application_id="APP-NOCREDIT",
        applicant_name="Bob Johnson",
        applicant_email="bob@example.com",
        applicant_phone="+1-555-9999",
        location="Denver, CO",
        loan_amount=30000.0,
        loan_type="Auto",
        loan_term_months=60,
        annual_income=80000.0,
        employment_status="Employed Full-time",
        years_employed=2.0,
        credit_score=None,
        existing_debt=300.0,
        status=LoanStatus.PENDING,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


class TestOrchestrationService:
    """Test suite for orchestration service."""

    def test_process_loan_application_creates_decision(self, db, sample_loan_application):
        """Test that processing creates a decision record."""
        result = OrchestrationService.process_loan_application(db, sample_loan_application)

        assert result is not None
        assert "decision_status" in result
        assert "risk_score" in result
        assert "approval_probability" in result
        assert "reasoning" in result

        # Verify decision was saved
        decisions = db.query(LoanDecision).filter(
            LoanDecision.loan_application_id == sample_loan_application.id
        ).all()
        assert len(decisions) > 0

    def test_process_loan_application_updates_application_status(self, db, sample_loan_application):
        """Test that application status is updated."""
        result = OrchestrationService.process_loan_application(db, sample_loan_application)

        # Refresh to get updated data
        db.refresh(sample_loan_application)
        assert sample_loan_application.status != LoanStatus.PENDING

    def test_process_loan_application_with_high_risk(self, db, high_risk_application):
        """Test workflow with high-risk applicant."""
        result = OrchestrationService.process_loan_application(db, high_risk_application)

        # High risk should have high risk score
        assert result["risk_score"] > 0.5
        # Likely rejected or pending review
        assert result["decision_status"] in ["REJECTED", "PENDING"]

    def test_process_loan_application_with_no_credit(self, db, no_credit_application):
        """Test workflow with no credit score."""
        result = OrchestrationService.process_loan_application(db, no_credit_application)

        assert result["decision_status"] in ["PENDING", "APPROVED"]
        assert result["risk_score"] is not None

    def test_process_loan_application_sets_approval_reason(self, db, sample_loan_application):
        """Test that approval reason is set for approved applications."""
        result = OrchestrationService.process_loan_application(db, sample_loan_application)

        db.refresh(sample_loan_application)
        if sample_loan_application.status == LoanStatus.APPROVED:
            assert sample_loan_application.approval_reason is not None

    def test_process_loan_application_sets_rejection_reason(self, db, high_risk_application):
        """Test that rejection reason is set for rejected applications."""
        result = OrchestrationService.process_loan_application(db, high_risk_application)

        db.refresh(high_risk_application)
        if high_risk_application.status == LoanStatus.REJECTED:
            assert high_risk_application.rejection_reason is not None

    def test_process_loan_application_sets_agent_notes_for_review(self, db, no_credit_application):
        """Test that agent notes are set for review applications."""
        result = OrchestrationService.process_loan_application(db, no_credit_application)

        db.refresh(no_credit_application)
        if no_credit_application.status == LoanStatus.UNDER_REVIEW:
            assert no_credit_application.agent_notes is not None

    @patch('backend.app.services.orchestration_service.create_loan_approval_graph')
    def test_process_loan_application_workflow_error_handling(
        self, mock_graph, db, sample_loan_application
    ):
        """Test error handling when workflow fails."""
        # Mock workflow to raise exception
        mock_instance = MagicMock()
        mock_instance.invoke.side_effect = Exception("Workflow error")
        mock_graph.return_value = mock_instance

        result = OrchestrationService.process_loan_application(db, sample_loan_application)

        assert result["decision_status"] == "REJECTED"
        assert "Workflow" in result["reasoning"] or "error" in result["reasoning"].lower()

    def test_process_loan_application_sets_risk_scores(self, db, sample_loan_application):
        """Test that risk scores are properly set."""
        result = OrchestrationService.process_loan_application(db, sample_loan_application)

        # Risk score can be 0-100 scale based on profile_agent
        assert result["risk_score"] is not None
        assert result["approval_probability"] is not None
        assert 0.0 <= result["approval_probability"] <= 1.0

    def test_process_loan_application_audit_trail(self, db, sample_loan_application):
        """Test that audit trail is generated."""
        result = OrchestrationService.process_loan_application(db, sample_loan_application)

        assert "audit_trail" in result
        assert isinstance(result["audit_trail"], list)
        assert len(result["audit_trail"]) > 0


class TestLoanApprovalGraph:
    """Test suite for loan approval workflow graph."""

    def test_create_graph_returns_compiled_graph(self):
        """Test that graph creation returns a compiled graph."""
        graph = create_loan_approval_graph()
        assert graph is not None

    def test_graph_execution_with_valid_state(self):
        """Test graph execution with valid state."""
        graph = create_loan_approval_graph()

        state = AgentState(
            application_id="APP-TEST",
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="+1-555-0000",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
            messages=[],
        )

        result = graph.invoke(state)

        assert result is not None
        assert "approved" in result
        assert "risk_score" in result
        assert "messages" in result
        assert len(result["messages"]) > 0

    def test_graph_handles_zero_income(self):
        """Test graph handles zero income edge case."""
        graph = create_loan_approval_graph()

        state = AgentState(
            application_id="APP-ZERO-INCOME",
            applicant_name="Zero Income User",
            applicant_email="zero@example.com",
            applicant_phone="+1-555-0000",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=0.0,
            employment_status="Unemployed",
            years_employed=0.0,
            credit_score=600,
            existing_debt=1000.0,
            messages=[],
        )

        result = graph.invoke(state)

        assert result is not None
        assert result["approved"] == False

    def test_graph_handles_high_dti(self):
        """Test graph handles high debt-to-income ratio."""
        graph = create_loan_approval_graph()

        state = AgentState(
            application_id="APP-HIGH-DTI",
            applicant_name="High DTI User",
            applicant_email="dti@example.com",
            applicant_phone="+1-555-0000",
            loan_amount=100000.0,
            loan_type="Personal",
            loan_term_months=120,
            annual_income=50000.0,
            employment_status="Employed",
            years_employed=3.0,
            credit_score=700,
            existing_debt=10000.0,
            messages=[],
        )

        result = graph.invoke(state)

        assert result is not None
        # High DTI should result in higher risk
        assert result["risk_score"] > 0.5

    def test_graph_workflow_progression(self):
        """Test that workflow progresses through all nodes."""
        graph = create_loan_approval_graph()

        state = AgentState(
            application_id="APP-FLOW",
            applicant_name="Flow Test",
            applicant_email="flow@example.com",
            applicant_phone="+1-555-0000",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
            messages=[],
        )

        result = graph.invoke(state)

        # Should have messages from each agent
        messages_str = " ".join(result["messages"]).lower()
        assert "profile" in messages_str or "analysis" in messages_str
        assert "credit" in messages_str or "evaluation" in messages_str
        assert "compliance" in messages_str or "check" in messages_str
        assert "decision" in messages_str

    def test_graph_sets_completed_timestamp(self):
        """Test that completed_at is set."""
        graph = create_loan_approval_graph()

        state = AgentState(
            application_id="APP-TIME",
            applicant_name="Time Test",
            applicant_email="time@example.com",
            applicant_phone="+1-555-0000",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
            messages=[],
            started_at=datetime.utcnow(),
        )

        result = graph.invoke(state)

        assert result["completed_at"] is not None
        assert result["completed_at"] >= result["started_at"]

    @patch('backend.app.agents.profile_agent.analyze_applicant')
    def test_graph_handles_profile_agent_error(self, mock_profile):
        """Test graph handles profile agent errors gracefully."""
        mock_profile.side_effect = Exception("Profile agent error")
        graph = create_loan_approval_graph()

        state = AgentState(
            application_id="APP-PROFILE-ERR",
            applicant_name="Profile Error",
            applicant_email="err@example.com",
            applicant_phone="+1-555-0000",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=120000.0,
            employment_status="Employed",
            years_employed=5.0,
            credit_score=750,
            existing_debt=500.0,
            messages=[],
        )

        result = graph.invoke(state)

        # Should still complete workflow despite error
        assert result is not None
        # Messages may contain error or continue with other steps
        assert len(result["messages"]) > 0
