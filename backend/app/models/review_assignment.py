"""Review assignment model for loan applications."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Text, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin
import enum
from datetime import datetime


class ReviewStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RE_DECISION = "RE_DECISION"


class ReviewPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReviewerAssignment(Base, TimestampMixin):
    __tablename__ = "reviewer_assignments"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(String(50), unique=True, nullable=False, index=True)

    loan_application_id = Column(Integer, ForeignKey('loan_applications.id'), nullable=False, index=True)
    reviewer_id = Column(String(100), nullable=False, index=True)
    reviewer_name = Column(String(255), nullable=True)

    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False, index=True)
    priority = Column(Enum(ReviewPriority), default=ReviewPriority.MEDIUM, index=True)

    assigned_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)

    review_notes = Column(Text, nullable=True)
    review_reasoning = Column(Text, nullable=True)

    re_decision_count = Column(Integer, default=0)
    last_review_date = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_ra_reviewer_status", reviewer_id, status),
        Index("idx_ra_loan_status", loan_application_id, status),
        Index("idx_ra_priority_assigned", priority, assigned_at.desc()),
        Index("idx_ra_status_priority", status, priority),
    )

    def __repr__(self):
        return f"<ReviewerAssignment(id={self.id}, assignment_id={self.assignment_id}, status={self.status})>"


class ReviewAction(Base, TimestampMixin):
    __tablename__ = "review_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(50), unique=True, nullable=False, index=True)

    reviewer_assignment_id = Column(Integer, ForeignKey('reviewer_assignments.id'), nullable=False, index=True)
    loan_application_id = Column(Integer, ForeignKey('loan_applications.id'), nullable=False, index=True)

    action_type = Column(String(50), nullable=False, index=True)
    action_status = Column(String(50), nullable=False)

    reviewer_id = Column(String(100), nullable=False, index=True)
    reviewer_name = Column(String(255), nullable=True)

    action_reason = Column(Text, nullable=True)
    action_details = Column(Text, nullable=True)

    ip_address = Column(String(50), nullable=True)
    action_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("idx_ra_loan_action_type", loan_application_id, action_type),
        Index("idx_ra_reviewer_timestamp", reviewer_id, action_timestamp.desc()),
        Index("idx_ra_action_timestamp_type", action_timestamp.desc(), action_type),
    )

    def __repr__(self):
        return f"<ReviewAction(id={self.id}, action_id={self.action_id}, action_type={self.action_type})>"


class ReviewerProfile(Base, TimestampMixin):
    __tablename__ = "reviewer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(String(100), unique=True, nullable=False, index=True)
    reviewer_name = Column(String(255), nullable=False)

    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)

    department = Column(String(100), nullable=True, index=True)
    role = Column(String(50), nullable=True, index=True)

    is_active = Column(Boolean, default=True, index=True)
    total_reviews = Column(Integer, default=0)
    approved_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)

    avg_review_time_minutes = Column(Float, nullable=True)
    last_activity = Column(DateTime, nullable=True, index=True)

    __table_args__ = (
        Index("idx_active_reviews", is_active, total_reviews.desc()),
        Index("idx_department_active", department, is_active),
    )

    def __repr__(self):
        return f"<ReviewerProfile(id={self.id}, reviewer_id={self.reviewer_id}, reviewer_name={self.reviewer_name})>"
