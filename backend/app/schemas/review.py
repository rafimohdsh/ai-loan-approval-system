"""Schemas for reviewer operations."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RE_DECISION = "RE_DECISION"


class ReviewPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReviewerProfileCreate(BaseModel):
    reviewer_name: str = Field(..., description="Reviewer name")
    email: str = Field(..., description="Reviewer email")
    phone: Optional[str] = Field(None, description="Reviewer phone")
    department: Optional[str] = Field(None, description="Department")
    role: Optional[str] = Field(None, description="Role")


class ReviewerProfileResponse(BaseModel):
    reviewer_id: str
    reviewer_name: str
    email: str
    phone: Optional[str]
    department: Optional[str]
    role: Optional[str]
    is_active: bool
    total_reviews: int
    approved_count: int
    rejected_count: int
    avg_review_time_minutes: Optional[float]
    last_activity: Optional[datetime]

    class Config:
        from_attributes = True


class ReviewerAssignmentCreate(BaseModel):
    loan_application_id: int = Field(..., description="Loan application ID")
    reviewer_id: str = Field(..., description="Reviewer ID")
    priority: ReviewPriority = Field(default=ReviewPriority.MEDIUM, description="Priority level")


class ReviewerAssignmentResponse(BaseModel):
    assignment_id: str
    loan_application_id: int
    reviewer_id: str
    reviewer_name: Optional[str]
    status: ReviewStatus
    priority: ReviewPriority
    assigned_at: Optional[datetime]
    completed_at: Optional[datetime]
    review_notes: Optional[str]
    review_reasoning: Optional[str]
    re_decision_count: int
    last_review_date: Optional[datetime]

    class Config:
        from_attributes = True


class ReviewActionCreate(BaseModel):
    assignment_id: str = Field(..., description="Assignment ID")
    action_type: str = Field(..., description="Action type: APPROVE, REJECT, RE_DECISION")
    reason: Optional[str] = Field(None, description="Action reason")
    reviewer_id: str = Field(..., description="Reviewer ID")


class ReviewActionResponse(BaseModel):
    action_id: str
    reviewer_assignment_id: int
    loan_application_id: int
    action_type: str
    action_status: str
    reviewer_id: str
    reviewer_name: Optional[str]
    action_reason: Optional[str]
    action_timestamp: datetime

    class Config:
        from_attributes = True


class QueueItemResponse(BaseModel):
    assignment_id: str
    loan_application_id: int
    applicant_name: str
    applicant_email: str
    loan_amount: float
    annual_income: float
    credit_score: Optional[int]
    status: ReviewStatus
    priority: ReviewPriority
    assigned_reviewer: Optional[str]
    assigned_at: Optional[datetime]
    risk_score: Optional[float]

    class Config:
        from_attributes = True


class ReviewStatsResponse(BaseModel):
    period_days: int
    total_reviews: int
    approved: int
    rejected: int
    re_decisions: int
    approval_rate: float


class AuditHistoryResponse(BaseModel):
    action_id: str
    action_type: str
    action_status: str
    reviewer_id: str
    reviewer_name: Optional[str]
    action_reason: Optional[str]
    action_timestamp: datetime

    class Config:
        from_attributes = True
