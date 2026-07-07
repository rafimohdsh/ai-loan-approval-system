"""Service for loan review operations."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

from backend.app.models import (
    ReviewerAssignment,
    ReviewAction,
    ReviewerProfile,
    LoanApplication,
    LoanStatus,
    ReviewStatus,
    ReviewPriority,
)
from backend.app.schemas.review import (
    ReviewerAssignmentCreate,
    ReviewActionCreate,
    ReviewerProfileCreate,
)


class ReviewerService:
    @staticmethod
    def create_reviewer_profile(db: Session, reviewer_data: ReviewerProfileCreate) -> ReviewerProfile:
        """Create a new reviewer profile."""
        reviewer_id = str(uuid4())
        logger.info(f"Creating reviewer profile: {reviewer_id}", extra={"reviewer_name": reviewer_data.reviewer_name})
        profile = ReviewerProfile(
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_data.reviewer_name,
            email=reviewer_data.email,
            phone=reviewer_data.phone,
            department=reviewer_data.department,
            role=reviewer_data.role,
            is_active=True,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        logger.info(f"Reviewer profile created successfully: {reviewer_id}")
        return profile

    @staticmethod
    def get_reviewer_profile(db: Session, reviewer_id: str) -> Optional[ReviewerProfile]:
        """Get reviewer profile by ID."""
        return db.query(ReviewerProfile).filter(
            ReviewerProfile.reviewer_id == reviewer_id
        ).first()

    @staticmethod
    def list_active_reviewers(db: Session) -> List[ReviewerProfile]:
        """Get all active reviewers."""
        return db.query(ReviewerProfile).filter(
            ReviewerProfile.is_active == True
        ).all()

    @staticmethod
    def get_queue(db: Session, status: ReviewStatus = None, priority: ReviewPriority = None) -> List[ReviewerAssignment]:
        """Get applications in review queue."""
        query = db.query(ReviewerAssignment).filter(
            ReviewerAssignment.status.in_([ReviewStatus.ASSIGNED, ReviewStatus.IN_REVIEW, ReviewStatus.RE_DECISION])
        )

        if status:
            query = query.filter(ReviewerAssignment.status == status)
        if priority:
            query = query.filter(ReviewerAssignment.priority == priority)

        return query.order_by(
            desc(ReviewerAssignment.priority),
            desc(ReviewerAssignment.assigned_at)
        ).all()

    @staticmethod
    def get_reviewer_queue(db: Session, reviewer_id: str) -> List[ReviewerAssignment]:
        """Get applications assigned to a specific reviewer."""
        return db.query(ReviewerAssignment).filter(
            ReviewerAssignment.reviewer_id == reviewer_id,
            ReviewerAssignment.status.in_([ReviewStatus.ASSIGNED, ReviewStatus.IN_REVIEW])
        ).all()

    @staticmethod
    def assign_reviewer(
        db: Session,
        loan_application_id: int,
        reviewer_id: str,
        priority: ReviewPriority = ReviewPriority.MEDIUM,
    ) -> ReviewerAssignment:
        """Assign a reviewer to a loan application."""
        reviewer = ReviewerService.get_reviewer_profile(db, reviewer_id)
        if not reviewer:
            raise ValueError(f"Reviewer {reviewer_id} not found")

        assignment = ReviewerAssignment(
            assignment_id=str(uuid4()),
            loan_application_id=loan_application_id,
            reviewer_id=reviewer_id,
            reviewer_name=reviewer.reviewer_name,
            status=ReviewStatus.ASSIGNED,
            priority=priority,
            assigned_at=datetime.utcnow(),
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def get_assignment(db: Session, assignment_id: str) -> Optional[ReviewerAssignment]:
        """Get assignment by ID."""
        return db.query(ReviewerAssignment).filter(
            ReviewerAssignment.assignment_id == assignment_id
        ).first()

    @staticmethod
    def start_review(db: Session, assignment_id: str) -> ReviewerAssignment:
        """Start reviewing an application."""
        assignment = ReviewerService.get_assignment(db, assignment_id)
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")

        assignment.status = ReviewStatus.IN_REVIEW
        assignment.last_review_date = datetime.utcnow()
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def approve_application(
        db: Session,
        assignment_id: str,
        review_notes: str,
        reviewer_id: str,
    ) -> tuple[ReviewerAssignment, ReviewAction]:
        """Approve a loan application."""
        assignment = ReviewerService.get_assignment(db, assignment_id)
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")

        assignment.status = ReviewStatus.APPROVED
        assignment.review_notes = review_notes
        assignment.completed_at = datetime.utcnow()

        loan_app = db.query(LoanApplication).filter(
            LoanApplication.id == assignment.loan_application_id
        ).first()
        if loan_app:
            loan_app.status = LoanStatus.APPROVED

        action = ReviewAction(
            action_id=str(uuid4()),
            reviewer_assignment_id=assignment.id,
            loan_application_id=assignment.loan_application_id,
            action_type="APPROVE",
            action_status="SUCCESS",
            reviewer_id=reviewer_id,
            reviewer_name=assignment.reviewer_name,
            action_reason=review_notes,
            action_timestamp=datetime.utcnow(),
        )
        db.add(action)
        db.commit()
        db.refresh(assignment)
        db.refresh(action)

        ReviewerService._update_reviewer_stats(db, reviewer_id, "APPROVED")

        return assignment, action

    @staticmethod
    def reject_application(
        db: Session,
        assignment_id: str,
        rejection_reason: str,
        reviewer_id: str,
    ) -> tuple[ReviewerAssignment, ReviewAction]:
        """Reject a loan application."""
        assignment = ReviewerService.get_assignment(db, assignment_id)
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")

        assignment.status = ReviewStatus.REJECTED
        assignment.review_reasoning = rejection_reason
        assignment.completed_at = datetime.utcnow()

        loan_app = db.query(LoanApplication).filter(
            LoanApplication.id == assignment.loan_application_id
        ).first()
        if loan_app:
            loan_app.status = LoanStatus.REJECTED
            loan_app.rejection_reason = rejection_reason

        action = ReviewAction(
            action_id=str(uuid4()),
            reviewer_assignment_id=assignment.id,
            loan_application_id=assignment.loan_application_id,
            action_type="REJECT",
            action_status="SUCCESS",
            reviewer_id=reviewer_id,
            reviewer_name=assignment.reviewer_name,
            action_reason=rejection_reason,
            action_timestamp=datetime.utcnow(),
        )
        db.add(action)
        db.commit()
        db.refresh(assignment)
        db.refresh(action)

        ReviewerService._update_reviewer_stats(db, reviewer_id, "REJECTED")

        return assignment, action

    @staticmethod
    def request_re_decision(
        db: Session,
        assignment_id: str,
        review_notes: str,
        reviewer_id: str,
    ) -> tuple[ReviewerAssignment, ReviewAction]:
        """Request re-decision from automated workflow."""
        assignment = ReviewerService.get_assignment(db, assignment_id)
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")

        assignment.status = ReviewStatus.RE_DECISION
        assignment.review_notes = review_notes
        assignment.re_decision_count += 1
        assignment.completed_at = datetime.utcnow()

        action = ReviewAction(
            action_id=str(uuid4()),
            reviewer_assignment_id=assignment.id,
            loan_application_id=assignment.loan_application_id,
            action_type="RE_DECISION",
            action_status="REQUESTED",
            reviewer_id=reviewer_id,
            reviewer_name=assignment.reviewer_name,
            action_reason=review_notes,
            action_timestamp=datetime.utcnow(),
        )
        db.add(action)
        db.commit()
        db.refresh(assignment)
        db.refresh(action)

        return assignment, action

    @staticmethod
    def get_audit_history(
        db: Session,
        loan_application_id: int,
        limit: int = 50,
    ) -> List[ReviewAction]:
        """Get audit history for an application."""
        return db.query(ReviewAction).filter(
            ReviewAction.loan_application_id == loan_application_id
        ).order_by(desc(ReviewAction.action_timestamp)).limit(limit).all()

    @staticmethod
    def get_reviewer_history(
        db: Session,
        reviewer_id: str,
        limit: int = 50,
    ) -> List[ReviewAction]:
        """Get audit history for a reviewer."""
        return db.query(ReviewAction).filter(
            ReviewAction.reviewer_id == reviewer_id
        ).order_by(desc(ReviewAction.action_timestamp)).limit(limit).all()

    @staticmethod
    def get_review_stats(db: Session, days: int = 30) -> dict:
        """Get review statistics for the past N days."""
        start_date = datetime.utcnow() - timedelta(days=days)

        total_reviews = db.query(ReviewAction).filter(
            ReviewAction.action_timestamp >= start_date
        ).count()

        approved = db.query(ReviewAction).filter(
            ReviewAction.action_type == "APPROVE",
            ReviewAction.action_timestamp >= start_date,
        ).count()

        rejected = db.query(ReviewAction).filter(
            ReviewAction.action_type == "REJECT",
            ReviewAction.action_timestamp >= start_date,
        ).count()

        re_decisions = db.query(ReviewAction).filter(
            ReviewAction.action_type == "RE_DECISION",
            ReviewAction.action_timestamp >= start_date,
        ).count()

        return {
            "period_days": days,
            "total_reviews": total_reviews,
            "approved": approved,
            "rejected": rejected,
            "re_decisions": re_decisions,
            "approval_rate": approved / total_reviews if total_reviews > 0 else 0,
        }

    @staticmethod
    def _update_reviewer_stats(db: Session, reviewer_id: str, action_type: str) -> None:
        """Update reviewer statistics."""
        reviewer = ReviewerService.get_reviewer_profile(db, reviewer_id)
        if not reviewer:
            return

        reviewer.total_reviews += 1
        if action_type == "APPROVED":
            reviewer.approved_count += 1
        elif action_type == "REJECTED":
            reviewer.rejected_count += 1

        reviewer.last_activity = datetime.utcnow()
        db.commit()
