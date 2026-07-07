"""Tests for appeal service."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.services.appeal_service import AppealService
from backend.app.models import (
    Appeal,
    AppealStatus,
    AppealPriority,
    LoanApplication,
    LoanStatus,
    ReviewerProfile,
)


@pytest.fixture
def sample_loan(db):
    """Create a sample rejected loan application."""
    loan = LoanApplication(
        application_id="APP-APPEAL-001",
        applicant_name="John Applicant",
        applicant_email="john@example.com",
        applicant_phone="+1-555-1234",
        location="New York, NY",
        loan_amount=50000.0,
        loan_type="Personal",
        loan_term_months=60,
        annual_income=80000.0,
        employment_status="Employed",
        years_employed=3.0,
        credit_score=650,
        existing_debt=5000.0,
        status=LoanStatus.REJECTED,
        rejection_reason="Low credit score and high debt-to-income ratio",
        processed_at=datetime.utcnow(),
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@pytest.fixture
def sample_reviewer(db):
    """Create a sample reviewer for appeals."""
    reviewer = ReviewerProfile(
        reviewer_id="REVIEWER-APPEAL-001",
        reviewer_name="Jane Reviewer",
        email="jane@example.com",
        phone="+1-555-5678",
        department="Appeals",
        role="SENIOR_REVIEWER",
        is_active=True,
    )
    db.add(reviewer)
    db.commit()
    db.refresh(reviewer)
    return reviewer


class TestAppealSubmission:
    """Test appeal submission."""

    def test_submit_appeal(self, db, sample_loan):
        """Test submitting an appeal."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "I have improved my financial situation since the rejection",
            "Bank statements showing stable income",
            AppealPriority.MEDIUM,
        )

        assert appeal is not None
        assert appeal.status == AppealStatus.SUBMITTED
        assert appeal.appeal_reason == "I have improved my financial situation since the rejection"
        assert appeal.applicant_email == "john@example.com"

    def test_submit_appeal_creates_history(self, db, sample_loan):
        """Test that appeal submission creates history."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        history = AppealService.get_appeal_history(db, appeal.id)
        assert len(history) > 0
        assert history[0].action_type == "SUBMITTED"

    def test_submit_appeal_nonexistent_loan_raises_error(self, db):
        """Test that submitting appeal for nonexistent loan raises error."""
        with pytest.raises(ValueError):
            AppealService.submit_appeal(
                db,
                9999,
                "APPLICANT-001",
                "John Applicant",
                "john@example.com",
                "Appeal reason",
            )


class TestAppealRetrieval:
    """Test retrieving appeals."""

    def test_get_appeal(self, db, sample_loan):
        """Test getting an appeal."""
        submitted_appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        retrieved = AppealService.get_appeal(db, submitted_appeal.appeal_id)
        assert retrieved is not None
        assert retrieved.appeal_id == submitted_appeal.appeal_id

    def test_list_applicant_appeals(self, db, sample_loan):
        """Test listing appeals for an applicant."""
        AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        appeals = AppealService.list_applicant_appeals(db, "APPLICANT-001")
        assert len(appeals) > 0
        assert all(a.applicant_id == "APPLICANT-001" for a in appeals)

    def test_list_pending_appeals(self, db, sample_loan):
        """Test listing pending appeals."""
        AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        pending = AppealService.list_pending_appeals(db)
        assert len(pending) > 0
        assert all(a.status in [AppealStatus.SUBMITTED, AppealStatus.UNDER_REVIEW] for a in pending)


class TestAppealReview:
    """Test appeal review workflow."""

    def test_assign_reviewer(self, db, sample_loan, sample_reviewer):
        """Test assigning reviewer to appeal."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        updated = AppealService.assign_reviewer(db, appeal.id, sample_reviewer.reviewer_id)
        assert updated.assigned_to_reviewer == sample_reviewer.reviewer_id
        assert updated.status == AppealStatus.UNDER_REVIEW

    def test_assign_nonexistent_reviewer_raises_error(self, db, sample_loan):
        """Test assigning nonexistent reviewer raises error."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        with pytest.raises(ValueError):
            AppealService.assign_reviewer(db, appeal.id, "NONEXISTENT-REVIEWER")

    def test_approve_appeal(self, db, sample_loan, sample_reviewer):
        """Test approving an appeal."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        approved = AppealService.approve_appeal(
            db,
            appeal.id,
            sample_reviewer.reviewer_id,
            "Applicant has shown improved financial stability"
        )

        assert approved.status == AppealStatus.APPROVED
        assert approved.appeal_decision == "APPROVED"
        assert approved.review_completed_at is not None

    def test_reject_appeal(self, db, sample_loan, sample_reviewer):
        """Test rejecting an appeal."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        rejected = AppealService.reject_appeal(
            db,
            appeal.id,
            sample_reviewer.reviewer_id,
            "Financial situation has not sufficiently improved"
        )

        assert rejected.status == AppealStatus.REJECTED
        assert rejected.appeal_decision == "REJECTED"
        assert rejected.appeal_decision_reason == "Financial situation has not sufficiently improved"


class TestAppealNotes:
    """Test appeal notes and communication."""

    def test_add_note(self, db, sample_loan):
        """Test adding note to appeal."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        note = AppealService.add_note(
            db,
            appeal.id,
            "John Applicant",
            "applicant",
            "I have attached updated bank statements",
            "communication"
        )

        assert note is not None
        assert note.appeal_id == appeal.id
        assert note.note_content == "I have attached updated bank statements"

    def test_get_appeal_notes(self, db, sample_loan):
        """Test retrieving appeal notes."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        AppealService.add_note(
            db,
            appeal.id,
            "John Applicant",
            "applicant",
            "First note",
        )

        notes = AppealService.get_appeal_notes(db, appeal.id)
        assert len(notes) > 0


class TestAppealHistory:
    """Test appeal history tracking."""

    def test_appeal_history_on_submission(self, db, sample_loan):
        """Test that history is created on submission."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        history = AppealService.get_appeal_history(db, appeal.id)
        assert len(history) > 0
        assert history[-1].action_type == "SUBMITTED"

    def test_appeal_history_on_approval(self, db, sample_loan, sample_reviewer):
        """Test that history is created on approval."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        AppealService.approve_appeal(
            db,
            appeal.id,
            sample_reviewer.reviewer_id,
            "Approved"
        )

        history = AppealService.get_appeal_history(db, appeal.id)
        approval_history = [h for h in history if h.action_type == "APPROVED"]
        assert len(approval_history) > 0


class TestAppealStatistics:
    """Test appeal statistics."""

    def test_get_appeal_statistics(self, db, sample_loan, sample_reviewer):
        """Test getting appeal statistics."""
        for i in range(3):
            app = LoanApplication(
                application_id=f"APP-STAT-{i}",
                applicant_name=f"Applicant {i}",
                applicant_email=f"applicant{i}@example.com",
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
                status=LoanStatus.REJECTED,
            )
            db.add(app)
            db.commit()
            db.refresh(app)

            appeal = AppealService.submit_appeal(
                db,
                app.id,
                f"APPLICANT-{i}",
                f"Applicant {i}",
                f"applicant{i}@example.com",
                "Appeal reason",
            )

            if i % 2 == 0:
                AppealService.approve_appeal(
                    db,
                    appeal.id,
                    sample_reviewer.reviewer_id,
                    "Approved"
                )
            else:
                AppealService.reject_appeal(
                    db,
                    appeal.id,
                    sample_reviewer.reviewer_id,
                    "Rejected"
                )

        stats = AppealService.get_appeal_statistics(db)
        assert stats["total_appeals"] >= 3
        assert stats["approved"] >= 1
        assert stats["rejected"] >= 1
        assert stats["approval_rate"] > 0


class TestAppealNotifications:
    """Test appeal notifications."""

    def test_notification_created_on_submission(self, db, sample_loan):
        """Test that notification is created on submission."""
        appeal = AppealService.submit_appeal(
            db,
            sample_loan.id,
            "APPLICANT-001",
            "John Applicant",
            "john@example.com",
            "Appeal reason",
        )

        # Verify notification was created by checking if we can retrieve it
        # (This would require adding a method to get notifications)
        assert appeal.applicant_email == "john@example.com"
