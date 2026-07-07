"""Tests for database operations and repositories."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from backend.app.models import (
    LoanApplication,
    LoanDecision,
    LoanStatus,
    DecisionStatus,
    Customer,
    AuditLog,
)
from backend.app.services import LoanService
from backend.app.schemas import (
    LoanApplicationCreate,
    LoanApplicationUpdate,
    LoanApprovalDecision,
)


class TestLoanApplicationDatabase:
    """Test loan application database operations."""

    def test_create_loan_application(self, db):
        """Test creating a loan application."""
        data = LoanApplicationCreate(
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
        )

        app = LoanService.create_application(db, data)

        assert app is not None
        assert app.applicant_name == "John Doe"
        assert app.application_id is not None
        assert app.status == LoanStatus.PENDING
        assert app.id is not None

    def test_create_loan_application_uniqueness(self, db):
        """Test that application IDs are unique."""
        data = LoanApplicationCreate(
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
        )

        app1 = LoanService.create_application(db, data)
        app2 = LoanService.create_application(db, data)

        assert app1.application_id != app2.application_id

    def test_get_application_by_id(self, db):
        """Test retrieving application by application ID."""
        data = LoanApplicationCreate(
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
        )

        created = LoanService.create_application(db, data)
        retrieved = LoanService.get_application(db, created.application_id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.application_id == created.application_id

    def test_get_application_not_found(self, db):
        """Test retrieving non-existent application."""
        result = LoanService.get_application(db, "non-existent-id")
        assert result is None

    def test_get_application_by_db_id(self, db):
        """Test retrieving application by database ID."""
        data = LoanApplicationCreate(
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
        )

        created = LoanService.create_application(db, data)
        retrieved = LoanService.get_application_by_db_id(db, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_update_application(self, db):
        """Test updating application."""
        data = LoanApplicationCreate(
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
        )

        app = LoanService.create_application(db, data)

        update_data = LoanApplicationUpdate(agent_notes="Good applicant")
        updated = LoanService.update_application(db, app.application_id, update_data)

        assert updated.agent_notes == "Good applicant"
        assert updated.id == app.id

    def test_update_application_not_found(self, db):
        """Test updating non-existent application."""
        update_data = LoanApplicationUpdate(agent_notes="Update")
        result = LoanService.update_application(db, "non-existent", update_data)
        assert result is None

    def test_list_applications(self, db):
        """Test listing applications."""
        data1 = LoanApplicationCreate(
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
        )
        data2 = LoanApplicationCreate(
            applicant_name="Jane Smith",
            applicant_email="jane@example.com",
            applicant_phone="+1-555-5678",
            location="New York, NY",
            loan_amount=75000.0,
            loan_type="Home",
            loan_term_months=360,
            annual_income=150000.0,
            employment_status="Employed Full-time",
            years_employed=3.0,
            credit_score=700,
            existing_debt=1000.0,
        )

        LoanService.create_application(db, data1)
        LoanService.create_application(db, data2)

        apps = LoanService.list_applications(db)
        assert len(apps) >= 2

    def test_list_applications_with_pagination(self, db):
        """Test pagination in list applications."""
        for i in range(5):
            data = LoanApplicationCreate(
                applicant_name=f"Applicant {i}",
                applicant_email=f"app{i}@example.com",
                applicant_phone="+1-555-0000",
                location="San Francisco, CA",
                loan_amount=50000.0,
                loan_type="Personal",
                loan_term_months=60,
                annual_income=120000.0,
                employment_status="Employed Full-time",
                years_employed=5.0,
                credit_score=750,
                existing_debt=500.0,
            )
            LoanService.create_application(db, data)

        page1 = LoanService.list_applications(db, skip=0, limit=2)
        page2 = LoanService.list_applications(db, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id

    def test_count_applications(self, db):
        """Test counting applications."""
        for i in range(3):
            data = LoanApplicationCreate(
                applicant_name=f"Applicant {i}",
                applicant_email=f"app{i}@example.com",
                applicant_phone="+1-555-0000",
                location="San Francisco, CA",
                loan_amount=50000.0,
                loan_type="Personal",
                loan_term_months=60,
                annual_income=120000.0,
                employment_status="Employed Full-time",
                years_employed=5.0,
                credit_score=750,
                existing_debt=500.0,
            )
            LoanService.create_application(db, data)

        count = LoanService.count_applications(db)
        assert count >= 3

    def test_set_approval_decision(self, db):
        """Test setting approval decision."""
        data = LoanApplicationCreate(
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
        )

        app = LoanService.create_application(db, data)

        decision = LoanApprovalDecision(
            application_id=app.application_id,
            approved=True,
            risk_score=0.3,
            approval_probability=0.95,
            reasoning="Excellent profile",
            conditions=["Standard terms"],
        )

        updated = LoanService.set_approval_decision(db, app.application_id, decision)

        assert updated.status == LoanStatus.APPROVED
        assert updated.risk_score == 0.3
        assert updated.approval_probability == 0.95

    def test_create_decision_approved(self, db):
        """Test creating approved decision."""
        app = LoanApplication(
            application_id="APP-TEST-APPROVE",
            applicant_name="Good Applicant",
            applicant_email="good@example.com",
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
            status=LoanStatus.PENDING,
        )
        db.add(app)
        db.commit()
        db.refresh(app)

        decision = LoanService.create_decision(db, app)

        assert decision is not None
        assert decision.decision_status == DecisionStatus.APPROVED

    def test_create_decision_rejected_low_credit(self, db):
        """Test creating rejected decision for low credit score."""
        app = LoanApplication(
            application_id="APP-TEST-REJECT",
            applicant_name="Bad Credit",
            applicant_email="badcredit@example.com",
            applicant_phone="+1-555-1234",
            location="San Francisco, CA",
            loan_amount=50000.0,
            loan_type="Personal",
            loan_term_months=60,
            annual_income=50000.0,
            employment_status="Employed Full-time",
            years_employed=1.0,
            credit_score=580,
            existing_debt=500.0,
            status=LoanStatus.PENDING,
        )
        db.add(app)
        db.commit()
        db.refresh(app)

        decision = LoanService.create_decision(db, app)

        assert decision.decision_status == DecisionStatus.REJECTED

    def test_create_decision_pending_high_dti(self, db):
        """Test creating pending decision for high DTI."""
        app = LoanApplication(
            application_id="APP-TEST-PENDING",
            applicant_name="High DTI",
            applicant_email="dti@example.com",
            applicant_phone="+1-555-1234",
            location="San Francisco, CA",
            loan_amount=100000.0,
            loan_type="Personal",
            loan_term_months=120,
            annual_income=60000.0,
            employment_status="Employed Full-time",
            years_employed=1.0,
            credit_score=650,
            existing_debt=4000.0,
            status=LoanStatus.PENDING,
        )
        db.add(app)
        db.commit()
        db.refresh(app)

        decision = LoanService.create_decision(db, app)

        assert decision.decision_status in [DecisionStatus.PENDING, DecisionStatus.REJECTED]


class TestLoanDecisionDatabase:
    """Test loan decision database operations."""

    def test_create_loan_decision(self, db):
        """Test creating a loan decision."""
        app = LoanApplication(
            application_id="APP-DECISION-TEST",
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
        db.add(app)
        db.commit()
        db.refresh(app)

        decision = LoanDecision(
            decision_id="DEC-001",
            loan_application_id=app.id,
            decision_status=DecisionStatus.APPROVED,
            risk_score=0.3,
            approval_probability=0.95,
            agent_analysis="Good profile",
            decision_made_by="test_agent",
            decision_made_at=datetime.utcnow(),
        )
        db.add(decision)
        db.commit()

        assert decision.id is not None
        assert decision.decision_id == "DEC-001"

    def test_decision_decision_id_uniqueness(self, db):
        """Test that decision IDs are unique."""
        app = LoanApplication(
            application_id="APP-UNI-TEST",
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
        db.add(app)
        db.commit()
        db.refresh(app)

        decision1 = LoanDecision(
            decision_id="DEC-UNI-001",
            loan_application_id=app.id,
            decision_status=DecisionStatus.APPROVED,
            risk_score=0.3,
            approval_probability=0.95,
            agent_analysis="Good profile",
            decision_made_by="test_agent",
            decision_made_at=datetime.utcnow(),
        )
        db.add(decision1)
        db.commit()

        with pytest.raises(IntegrityError):
            decision2 = LoanDecision(
                decision_id="DEC-UNI-001",  # Same ID
                loan_application_id=app.id,
                decision_status=DecisionStatus.REJECTED,
                risk_score=0.7,
                approval_probability=0.1,
                agent_analysis="Bad profile",
                decision_made_by="test_agent",
                decision_made_at=datetime.utcnow(),
            )
            db.add(decision2)
            db.commit()

    def test_query_decisions_by_application(self, db):
        """Test querying decisions by application."""
        app = LoanApplication(
            application_id="APP-QUERY-TEST",
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
        db.add(app)
        db.commit()
        db.refresh(app)

        decision = LoanDecision(
            decision_id="DEC-QUERY-001",
            loan_application_id=app.id,
            decision_status=DecisionStatus.APPROVED,
            risk_score=0.3,
            approval_probability=0.95,
            agent_analysis="Good profile",
            decision_made_by="test_agent",
            decision_made_at=datetime.utcnow(),
        )
        db.add(decision)
        db.commit()

        results = db.query(LoanDecision).filter(
            LoanDecision.loan_application_id == app.id
        ).all()
        assert len(results) > 0
        assert results[0].decision_id == "DEC-QUERY-001"

    def test_decision_with_null_optional_fields(self, db):
        """Test creating decision with null optional fields."""
        app = LoanApplication(
            application_id="APP-NULL-TEST",
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
        db.add(app)
        db.commit()
        db.refresh(app)

        decision = LoanDecision(
            decision_id="DEC-NULL-001",
            loan_application_id=app.id,
            decision_status=DecisionStatus.APPROVED,
            risk_score=0.3,
            approval_probability=0.95,
            agent_analysis=None,
            decision_made_by=None,
            decision_made_at=None,
        )
        db.add(decision)
        db.commit()

        retrieved = db.query(LoanDecision).filter(
            LoanDecision.decision_id == "DEC-NULL-001"
        ).first()
        assert retrieved is not None
        assert retrieved.agent_analysis is None
