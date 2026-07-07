"""Service for appeal operations."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

from backend.app.models import (
    Appeal,
    AppealNote,
    AppealHistory,
    AppealNotification,
    AppealStatus,
    AppealPriority,
    LoanApplication,
    ReviewerProfile,
)
from backend.app.schemas.appeal import (
    AppealCreate,
    AppealUpdate,
    AppealNoteCreate,
)


class AppealService:
    @staticmethod
    def submit_appeal(
        db: Session,
        loan_application_id: int,
        applicant_id: str,
        applicant_name: str,
        applicant_email: str,
        appeal_reason: str,
        supporting_evidence: Optional[str] = None,
        priority: AppealPriority = AppealPriority.MEDIUM,
    ) -> Appeal:
        """Submit an appeal for a rejected/withdrawn application."""
        loan = db.query(LoanApplication).filter(
            LoanApplication.id == loan_application_id
        ).first()

        if not loan:
            logger.error(f"Loan application {loan_application_id} not found")
            raise ValueError(f"Loan application {loan_application_id} not found")

        appeal_id = str(uuid4())
        logger.info(f"Submitting appeal for loan {loan_application_id}", extra={"appeal_id": appeal_id, "applicant_id": applicant_id})

        appeal = Appeal(
            appeal_id=appeal_id,
            loan_application_id=loan_application_id,
            applicant_id=applicant_id,
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            status=AppealStatus.SUBMITTED,
            priority=priority,
            original_decision=loan.status.value if loan.status else "UNKNOWN",
            original_rejection_reason=loan.rejection_reason,
            original_decision_date=loan.processed_at,
            appeal_reason=appeal_reason,
            supporting_evidence=supporting_evidence,
            submitted_at=datetime.utcnow(),
        )
        db.add(appeal)
        db.commit()
        db.refresh(appeal)

        AppealService._create_history(
            db, appeal.id, "SUBMITTED", None, AppealStatus.SUBMITTED.value,
            applicant_name, "Appeal submitted by applicant"
        )

        AppealService._create_notification(
            db, appeal.id, applicant_email, "applicant",
            "SUBMISSION_CONFIRMATION", "Appeal Submitted",
            f"Your appeal for loan application {loan_application_id} has been submitted and is under review."
        )

        logger.info(f"Appeal {appeal_id} submitted successfully for loan {loan_application_id}")
        return appeal

    @staticmethod
    def get_appeal(db: Session, appeal_id: str) -> Optional[Appeal]:
        """Get appeal by ID."""
        return db.query(Appeal).filter(Appeal.appeal_id == appeal_id).first()

    @staticmethod
    def list_applicant_appeals(db: Session, applicant_id: str) -> List[Appeal]:
        """List all appeals for an applicant."""
        return db.query(Appeal).filter(
            Appeal.applicant_id == applicant_id
        ).order_by(desc(Appeal.submitted_at)).all()

    @staticmethod
    def list_pending_appeals(db: Session, limit: int = 50) -> List[Appeal]:
        """List pending appeals for review, ordered by priority."""
        return db.query(Appeal).filter(
            Appeal.status.in_([AppealStatus.SUBMITTED, AppealStatus.UNDER_REVIEW])
        ).order_by(
            desc(Appeal.priority),
            Appeal.submitted_at
        ).limit(limit).all()

    @staticmethod
    def assign_reviewer(
        db: Session,
        appeal_id: int,
        reviewer_id: str,
    ) -> Appeal:
        """Assign a reviewer to an appeal."""
        appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        reviewer = db.query(ReviewerProfile).filter(
            ReviewerProfile.reviewer_id == reviewer_id
        ).first()
        if not reviewer:
            raise ValueError(f"Reviewer {reviewer_id} not found")

        appeal.assigned_to_reviewer = reviewer_id
        appeal.status = AppealStatus.UNDER_REVIEW
        appeal.review_started_at = datetime.utcnow()
        db.commit()
        db.refresh(appeal)

        AppealService._create_history(
            db, appeal.id, "ASSIGNED", AppealStatus.SUBMITTED.value, AppealStatus.UNDER_REVIEW.value,
            reviewer.reviewer_name, f"Appeal assigned to {reviewer.reviewer_name}"
        )

        AppealService._create_notification(
            db, appeal.id, reviewer.email, "reviewer",
            "APPEAL_ASSIGNED", "New Appeal Assigned",
            f"Appeal {appeal.appeal_id} has been assigned to you for review."
        )

        return appeal

    @staticmethod
    def approve_appeal(
        db: Session,
        appeal_id: int,
        reviewer_id: str,
        review_notes: str,
    ) -> Appeal:
        """Approve an appeal."""
        appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        reviewer = db.query(ReviewerProfile).filter(
            ReviewerProfile.reviewer_id == reviewer_id
        ).first()

        appeal.appeal_decision = "APPROVED"
        appeal.appeal_review_notes = review_notes
        appeal.status = AppealStatus.APPROVED
        appeal.review_completed_at = datetime.utcnow()
        db.commit()
        db.refresh(appeal)

        AppealService._create_history(
            db, appeal.id, "APPROVED", AppealStatus.UNDER_REVIEW.value, AppealStatus.APPROVED.value,
            reviewer.reviewer_name if reviewer else reviewer_id,
            f"Appeal approved. Notes: {review_notes}"
        )

        AppealService._create_notification(
            db, appeal.id, appeal.applicant_email, "applicant",
            "APPEAL_APPROVED", "Your Appeal Has Been Approved",
            f"Good news! Your appeal has been approved. You will be contacted shortly with next steps."
        )

        return appeal

    @staticmethod
    def reject_appeal(
        db: Session,
        appeal_id: int,
        reviewer_id: str,
        rejection_reason: str,
    ) -> Appeal:
        """Reject an appeal."""
        appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        reviewer = db.query(ReviewerProfile).filter(
            ReviewerProfile.reviewer_id == reviewer_id
        ).first()

        appeal.appeal_decision = "REJECTED"
        appeal.appeal_decision_reason = rejection_reason
        appeal.status = AppealStatus.REJECTED
        appeal.review_completed_at = datetime.utcnow()
        db.commit()
        db.refresh(appeal)

        AppealService._create_history(
            db, appeal.id, "REJECTED", AppealStatus.UNDER_REVIEW.value, AppealStatus.REJECTED.value,
            reviewer.reviewer_name if reviewer else reviewer_id,
            f"Appeal rejected. Reason: {rejection_reason}"
        )

        AppealService._create_notification(
            db, appeal.id, appeal.applicant_email, "applicant",
            "APPEAL_REJECTED", "Appeal Decision",
            f"Your appeal has been reviewed and rejected. Reason: {rejection_reason}"
        )

        return appeal

    @staticmethod
    def add_note(
        db: Session,
        appeal_id: int,
        added_by: str,
        added_by_type: str,
        note_content: str,
        note_type: str = "communication",
    ) -> AppealNote:
        """Add a note to an appeal."""
        appeal = db.query(Appeal).filter(Appeal.id == appeal_id).first()
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        note = AppealNote(
            note_id=str(uuid4()),
            appeal_id=appeal_id,
            added_by=added_by,
            added_by_type=added_by_type,
            note_content=note_content,
            note_type=note_type,
            created_at=datetime.utcnow(),
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def get_appeal_history(db: Session, appeal_id: int) -> List[AppealHistory]:
        """Get history of appeal status changes."""
        return db.query(AppealHistory).filter(
            AppealHistory.appeal_id == appeal_id
        ).order_by(desc(AppealHistory.change_timestamp)).all()

    @staticmethod
    def get_appeal_notes(db: Session, appeal_id: int) -> List[AppealNote]:
        """Get all notes for an appeal."""
        return db.query(AppealNote).filter(
            AppealNote.appeal_id == appeal_id
        ).order_by(desc(AppealNote.created_at)).all()

    @staticmethod
    def get_appeal_statistics(db: Session, days: int = 30) -> Dict[str, Any]:
        """Get appeal statistics."""
        start_date = datetime.utcnow() - timedelta(days=days)

        total_appeals = db.query(func.count(Appeal.id)).filter(
            Appeal.submitted_at >= start_date
        ).scalar()

        approved_count = db.query(func.count(Appeal.id)).filter(
            Appeal.status == AppealStatus.APPROVED,
            Appeal.submitted_at >= start_date
        ).scalar()

        rejected_count = db.query(func.count(Appeal.id)).filter(
            Appeal.status == AppealStatus.REJECTED,
            Appeal.submitted_at >= start_date
        ).scalar()

        pending_count = db.query(func.count(Appeal.id)).filter(
            Appeal.status.in_([AppealStatus.SUBMITTED, AppealStatus.UNDER_REVIEW]),
            Appeal.submitted_at >= start_date
        ).scalar()

        avg_resolution_time = db.query(func.avg(
            func.julianday(Appeal.review_completed_at) - func.julianday(Appeal.submitted_at)
        )).filter(
            Appeal.review_completed_at != None,
            Appeal.submitted_at >= start_date
        ).scalar()

        return {
            "total_appeals": total_appeals or 0,
            "approved": approved_count or 0,
            "rejected": rejected_count or 0,
            "pending": pending_count or 0,
            "approval_rate": (approved_count / total_appeals * 100) if total_appeals else 0,
            "avg_resolution_days": float(avg_resolution_time) if avg_resolution_time else None,
        }

    @staticmethod
    def _create_history(
        db: Session,
        appeal_id: int,
        action_type: str,
        from_status: Optional[str],
        to_status: str,
        changed_by: str,
        change_reason: Optional[str] = None,
    ) -> AppealHistory:
        """Create audit history entry."""
        history = AppealHistory(
            history_id=str(uuid4()),
            appeal_id=appeal_id,
            action_type=action_type,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            change_reason=change_reason,
            change_timestamp=datetime.utcnow(),
        )
        db.add(history)
        db.commit()
        return history

    @staticmethod
    def _create_notification(
        db: Session,
        appeal_id: int,
        recipient_email: str,
        recipient_type: str,
        notification_type: str,
        subject: str,
        body: str,
    ) -> AppealNotification:
        """Create notification."""
        notification = AppealNotification(
            notification_id=str(uuid4()),
            appeal_id=appeal_id,
            recipient_email=recipient_email,
            recipient_type=recipient_type,
            notification_type=notification_type,
            notification_subject=subject,
            notification_body=body,
            delivery_status="pending",
        )
        db.add(notification)
        db.commit()
        return notification

    @staticmethod
    def mark_notification_sent(db: Session, notification_id: int) -> AppealNotification:
        """Mark notification as sent."""
        notification = db.query(AppealNotification).filter(
            AppealNotification.id == notification_id
        ).first()
        if notification:
            notification.sent_at = datetime.utcnow()
            notification.delivery_status = "sent"
            db.commit()
            db.refresh(notification)
        return notification

    @staticmethod
    def mark_notification_read(db: Session, notification_id: int) -> AppealNotification:
        """Mark notification as read."""
        notification = db.query(AppealNotification).filter(
            AppealNotification.id == notification_id
        ).first()
        if notification:
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        return notification
