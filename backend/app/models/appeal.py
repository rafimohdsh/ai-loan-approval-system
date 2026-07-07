"""Appeal workflow models for loan applications."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin
import enum
from datetime import datetime


class AppealStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class AppealPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Appeal(Base, TimestampMixin):
    """Appeal submission for rejected/withdrawn loan applications."""
    __tablename__ = "appeals"

    id = Column(Integer, primary_key=True, index=True)
    appeal_id = Column(String(50), unique=True, nullable=False, index=True)

    loan_application_id = Column(Integer, ForeignKey('loan_applications.id'), nullable=False, index=True)
    applicant_id = Column(String(255), nullable=False, index=True)
    applicant_name = Column(String(255), nullable=False)
    applicant_email = Column(String(255), nullable=False, index=True)

    status = Column(Enum(AppealStatus), default=AppealStatus.SUBMITTED, nullable=False, index=True)
    priority = Column(Enum(AppealPriority), default=AppealPriority.MEDIUM, index=True)

    original_decision = Column(String(50), nullable=False)
    original_rejection_reason = Column(Text, nullable=True)
    original_decision_date = Column(DateTime, nullable=True)

    appeal_reason = Column(Text, nullable=False)
    supporting_evidence = Column(Text, nullable=True)
    additional_documents = Column(Text, nullable=True)

    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    assigned_to_reviewer = Column(String(100), nullable=True, index=True)
    review_started_at = Column(DateTime, nullable=True)
    review_completed_at = Column(DateTime, nullable=True)

    appeal_decision = Column(String(50), nullable=True)
    appeal_review_notes = Column(Text, nullable=True)
    appeal_decision_reason = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Appeal(id={self.id}, appeal_id={self.appeal_id}, status={self.status})>"

    __table_args__ = (
        Index("idx_appeal_applicant_status", applicant_id, status),
        Index("idx_appeal_loan_status", loan_application_id, status),
        Index("idx_appeal_reviewer_status", assigned_to_reviewer, status),
        Index("idx_appeal_submitted_status", submitted_at.desc(), status),
        Index("idx_appeal_priority_submitted", priority, submitted_at.desc()),
    )


class AppealNote(Base, TimestampMixin):
    """Notes and communication history for appeals."""
    __tablename__ = "appeal_notes"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(String(50), unique=True, nullable=False, index=True)

    appeal_id = Column(Integer, ForeignKey('appeals.id'), nullable=False, index=True)
    added_by = Column(String(255), nullable=False)
    added_by_type = Column(String(50), nullable=False)  # applicant, reviewer, admin

    note_content = Column(Text, nullable=False)
    note_type = Column(String(50), nullable=False)  # communication, decision_note, status_update

    attachments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AppealNote(id={self.id}, note_id={self.note_id})>"

    __table_args__ = (
        Index("idx_appeal_note_type", appeal_id, note_type),
        Index("idx_appeal_note_created", appeal_id, created_at.desc()),
    )


class AppealHistory(Base, TimestampMixin):
    """Audit trail of all appeal status changes and actions."""
    __tablename__ = "appeal_history"

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(String(50), unique=True, nullable=False, index=True)

    appeal_id = Column(Integer, ForeignKey('appeals.id'), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=True)

    changed_by = Column(String(255), nullable=False)
    change_reason = Column(Text, nullable=True)
    change_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AppealHistory(id={self.id}, action_type={self.action_type})>"

    __table_args__ = (
        Index("idx_appeal_hist_action", appeal_id, action_type),
        Index("idx_appeal_hist_timestamp", appeal_id, change_timestamp.desc()),
    )


class AppealNotification(Base, TimestampMixin):
    """Notification tracking for appeal decisions and updates."""
    __tablename__ = "appeal_notifications"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(50), unique=True, nullable=False, index=True)

    appeal_id = Column(Integer, ForeignKey('appeals.id'), nullable=False, index=True)
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_type = Column(String(50), nullable=False)  # applicant, reviewer, admin

    notification_type = Column(String(50), nullable=False)
    notification_subject = Column(String(255), nullable=False)
    notification_body = Column(Text, nullable=False)

    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    delivery_status = Column(String(50), default="pending")

    def __repr__(self):
        return f"<AppealNotification(id={self.id}, notification_type={self.notification_type})>"

    __table_args__ = (
        Index("idx_appeal_notif_status", appeal_id, delivery_status),
        Index("idx_appeal_recipient_sent", recipient_email, sent_at.desc()),
        Index("idx_appeal_unread", read_at, delivery_status),
    )
