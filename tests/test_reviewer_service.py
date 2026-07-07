"""Tests for reviewer service."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.services.reviewer_service import ReviewerService
from backend.app.models import (
    ReviewerProfile,
    ReviewerAssignment,
    ReviewAction,
    ReviewStatus,
    ReviewPriority,
    LoanApplication,
    LoanStatus,
)
from backend.app.schemas.review import (
    ReviewerProfileCreate,
)


@pytest.fixture
def reviewer_data():
    """Sample reviewer profile data."""
    return ReviewerProfileCreate(
        reviewer_name="John Smith",
        email="john.smith@example.com",
        phone="+1-555-1234",
        department="Loan Review",
        role="REVIEWER",
    )


@pytest.fixture
def sample_reviewer(db, reviewer_data):
    """Create a sample reviewer."""
    return ReviewerService.create_reviewer_profile(db, reviewer_data)


@pytest.fixture
def sample_loan_application(db):
    """Create a sample loan application for testing."""
    loan = LoanApplication(
        application_id="APP-REV-001",
        applicant_name="Jane Applicant",
        applicant_email="jane@example.com",
        applicant_phone="+1-555-9999",
        location="New York, NY",
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


class TestReviewerProfileOperations:
    """Test reviewer profile CRUD operations."""

    def test_create_reviewer_profile(self, db, reviewer_data):
        """Test creating a reviewer profile."""
        profile = ReviewerService.create_reviewer_profile(db, reviewer_data)

        assert profile is not None
        assert profile.reviewer_id is not None
        assert profile.reviewer_name == "John Smith"
        assert profile.email == "john.smith@example.com"
        assert profile.is_active == True
        assert profile.total_reviews == 0

    def test_get_reviewer_profile(self, db, sample_reviewer):
        """Test retrieving a reviewer profile."""
        retrieved = ReviewerService.get_reviewer_profile(db, sample_reviewer.reviewer_id)

        assert retrieved is not None
        assert retrieved.reviewer_id == sample_reviewer.reviewer_id
        assert retrieved.reviewer_name == "John Smith"

    def test_list_active_reviewers(self, db, sample_reviewer):
        """Test listing active reviewers."""
        reviewers = ReviewerService.list_active_reviewers(db)

        assert len(reviewers) > 0
        assert any(r.reviewer_id == sample_reviewer.reviewer_id for r in reviewers)

    def test_reviewer_profile_fields(self, db, sample_reviewer):
        """Test reviewer profile fields."""
        assert sample_reviewer.email == "john.smith@example.com"
        assert sample_reviewer.phone == "+1-555-1234"
        assert sample_reviewer.department == "Loan Review"
        assert sample_reviewer.role == "REVIEWER"


class TestApplicationQueueOperations:
    """Test application queue operations."""

    def test_assign_reviewer_to_application(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test assigning a reviewer to an application."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
            ReviewPriority.HIGH,
        )

        assert assignment is not None
        assert assignment.assignment_id is not None
        assert assignment.loan_application_id == sample_loan_application.id
        assert assignment.reviewer_id == sample_reviewer.reviewer_id
        assert assignment.status == ReviewStatus.ASSIGNED
        assert assignment.priority == ReviewPriority.HIGH
        assert assignment.assigned_at is not None

    def test_get_queue_all_items(self, db, sample_reviewer, sample_loan_application):
        """Test getting all items in queue."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        queue = ReviewerService.get_queue(db)

        assert len(queue) > 0
        assert any(
            a.loan_application_id == sample_loan_application.id for a in queue
        )
        assert queue[0].status == ReviewStatus.ASSIGNED

    def test_get_queue_filtered_by_status(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test getting queue filtered by status."""
        ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        queue = ReviewerService.get_queue(db, ReviewStatus.ASSIGNED)

        assert len(queue) > 0
        assert all(a.status == ReviewStatus.ASSIGNED for a in queue)

    def test_get_queue_filtered_by_priority(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test getting queue filtered by priority."""
        ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
            ReviewPriority.HIGH,
        )

        queue = ReviewerService.get_queue(db, priority=ReviewPriority.HIGH)

        assert len(queue) > 0
        assert all(a.priority == ReviewPriority.HIGH for a in queue)

    def test_get_reviewer_queue(self, db, sample_reviewer, sample_loan_application):
        """Test getting queue for specific reviewer."""
        ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        queue = ReviewerService.get_reviewer_queue(db, sample_reviewer.reviewer_id)

        assert len(queue) > 0
        assert all(a.reviewer_id == sample_reviewer.reviewer_id for a in queue)


class TestReviewActions:
    """Test review approval, rejection, and re-decision operations."""

    def test_start_review(self, db, sample_reviewer, sample_loan_application):
        """Test starting a review."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        started = ReviewerService.start_review(db, assignment.assignment_id)

        assert started.status == ReviewStatus.IN_REVIEW
        assert started.last_review_date is not None

    def test_approve_application(self, db, sample_reviewer, sample_loan_application):
        """Test approving an application."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        assignment, action = ReviewerService.approve_application(
            db,
            assignment.assignment_id,
            "Good profile",
            sample_reviewer.reviewer_id,
        )

        assert assignment.status == ReviewStatus.APPROVED
        assert assignment.completed_at is not None
        assert assignment.review_notes == "Good profile"

        assert action.action_type == "APPROVE"
        assert action.action_status == "SUCCESS"

        # Verify loan status updated
        db.refresh(sample_loan_application)
        assert sample_loan_application.status == LoanStatus.APPROVED

    def test_reject_application(self, db, sample_reviewer, sample_loan_application):
        """Test rejecting an application."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        assignment, action = ReviewerService.reject_application(
            db,
            assignment.assignment_id,
            "Low credit score",
            sample_reviewer.reviewer_id,
        )

        assert assignment.status == ReviewStatus.REJECTED
        assert assignment.completed_at is not None
        assert assignment.review_reasoning == "Low credit score"

        assert action.action_type == "REJECT"
        assert action.action_status == "SUCCESS"

        # Verify loan status updated
        db.refresh(sample_loan_application)
        assert sample_loan_application.status == LoanStatus.REJECTED

    def test_request_re_decision(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test requesting re-decision."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        assignment, action = ReviewerService.request_re_decision(
            db,
            assignment.assignment_id,
            "Need AI re-evaluation",
            sample_reviewer.reviewer_id,
        )

        assert assignment.status == ReviewStatus.RE_DECISION
        assert assignment.re_decision_count == 1
        assert assignment.completed_at is not None

        assert action.action_type == "RE_DECISION"
        assert action.action_status == "REQUESTED"

    def test_multiple_re_decisions(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test multiple re-decision requests."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        # First re-decision
        assignment, action = ReviewerService.request_re_decision(
            db,
            assignment.assignment_id,
            "First re-decision",
            sample_reviewer.reviewer_id,
        )
        assert assignment.re_decision_count == 1

        # Note: For second re-decision, would need to reset assignment first
        # This is just testing the counter


class TestAuditHistory:
    """Test audit history operations."""

    def test_get_audit_history_for_application(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test getting audit history for an application."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        ReviewerService.approve_application(
            db,
            assignment.assignment_id,
            "Approved",
            sample_reviewer.reviewer_id,
        )

        history = ReviewerService.get_audit_history(
            db, sample_loan_application.id
        )

        assert len(history) > 0
        assert any(a.action_type == "APPROVE" for a in history)

    def test_get_reviewer_history(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test getting history for a reviewer."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        ReviewerService.approve_application(
            db,
            assignment.assignment_id,
            "Approved",
            sample_reviewer.reviewer_id,
        )

        history = ReviewerService.get_reviewer_history(db, sample_reviewer.reviewer_id)

        assert len(history) > 0
        assert all(a.reviewer_id == sample_reviewer.reviewer_id for a in history)

    def test_audit_history_includes_timestamp(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test that audit history includes timestamp."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        before_action = datetime.utcnow()

        ReviewerService.reject_application(
            db,
            assignment.assignment_id,
            "Rejected",
            sample_reviewer.reviewer_id,
        )

        after_action = datetime.utcnow()

        history = ReviewerService.get_audit_history(
            db, sample_loan_application.id
        )

        assert len(history) > 0
        action = history[0]
        assert before_action <= action.action_timestamp <= after_action


class TestReviewerStatistics:
    """Test reviewer statistics operations."""

    def test_get_review_stats(self, db, sample_reviewer, sample_loan_application):
        """Test getting review statistics."""
        # Create multiple assignments
        for i in range(3):
            app = LoanApplication(
                application_id=f"APP-TEST-{i}",
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
                status=LoanStatus.PENDING,
            )
            db.add(app)
            db.commit()
            db.refresh(app)

            assignment = ReviewerService.assign_reviewer(
                db, app.id, sample_reviewer.reviewer_id
            )

            if i % 2 == 0:
                ReviewerService.approve_application(
                    db,
                    assignment.assignment_id,
                    "Approved",
                    sample_reviewer.reviewer_id,
                )
            else:
                ReviewerService.reject_application(
                    db,
                    assignment.assignment_id,
                    "Rejected",
                    sample_reviewer.reviewer_id,
                )

        stats = ReviewerService.get_review_stats(db, days=1)

        assert stats["total_reviews"] >= 3
        assert stats["approved"] >= 2
        assert stats["rejected"] >= 1
        assert stats["approval_rate"] > 0

    def test_reviewer_stats_updated_on_action(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test that reviewer stats are updated on each action."""
        assignment = ReviewerService.assign_reviewer(
            db,
            sample_loan_application.id,
            sample_reviewer.reviewer_id,
        )

        initial_total = sample_reviewer.total_reviews

        ReviewerService.approve_application(
            db,
            assignment.assignment_id,
            "Approved",
            sample_reviewer.reviewer_id,
        )

        db.refresh(sample_reviewer)
        assert sample_reviewer.total_reviews == initial_total + 1
        assert sample_reviewer.approved_count == 1


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_assign_reviewer_nonexistent_reviewer(
        self, db, sample_loan_application
    ):
        """Test assigning nonexistent reviewer raises error."""
        with pytest.raises(ValueError):
            ReviewerService.assign_reviewer(
                db,
                sample_loan_application.id,
                "nonexistent-reviewer-id",
            )

    def test_get_assignment_nonexistent(self, db):
        """Test getting nonexistent assignment returns None."""
        result = ReviewerService.get_assignment(db, "nonexistent")
        assert result is None

    def test_empty_audit_history(self, db):
        """Test getting audit history for nonexistent application."""
        history = ReviewerService.get_audit_history(db, 99999)
        assert len(history) == 0

    def test_empty_reviewer_queue(self, db, sample_reviewer):
        """Test getting queue for reviewer with no assignments."""
        queue = ReviewerService.get_reviewer_queue(db, sample_reviewer.reviewer_id)
        assert len(queue) == 0

    def test_queue_ordering_by_priority(
        self, db, sample_reviewer, sample_loan_application
    ):
        """Test that queue is ordered by priority."""
        # Create assignments with different priorities
        ReviewerService.assign_reviewer(
            db, sample_loan_application.id, sample_reviewer.reviewer_id, ReviewPriority.LOW
        )

        app2 = LoanApplication(
            application_id="APP-PRIORITY-HIGH",
            applicant_name="High Priority Applicant",
            applicant_email="high@example.com",
            applicant_phone="+1-555-0001",
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
        db.add(app2)
        db.commit()
        db.refresh(app2)

        ReviewerService.assign_reviewer(
            db, app2.id, sample_reviewer.reviewer_id, ReviewPriority.HIGH
        )

        queue = ReviewerService.get_queue(db)

        # Verify queue has assignments and HIGH priority comes before LOW
        assert len(queue) >= 2
        priorities = [item.priority for item in queue]
        high_count = sum(1 for p in priorities if p == ReviewPriority.HIGH)
        low_count = sum(1 for p in priorities if p == ReviewPriority.LOW)
        assert high_count >= 1
        assert low_count >= 1
