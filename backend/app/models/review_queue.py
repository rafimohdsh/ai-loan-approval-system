"""Review queue model for manual application reviews."""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base, TimestampMixin


class ReviewStatus(str, Enum):
    """Status of review queue item."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class ReviewQueue(Base, TimestampMixin):
    """Queue for applications requiring manual review."""

    __tablename__ = "review_queue"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(255), ForeignKey("loan_applications.application_id"), index=True, nullable=False)
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING, index=True)
    assigned_to = Column(String(255), nullable=True)
    reason = Column(Text, nullable=False)
    priority = Column(Integer, default=3)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    application = relationship("LoanApplication", backref="review_queue_items")
