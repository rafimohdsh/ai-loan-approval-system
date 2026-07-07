"""Pydantic schemas for appeal operations."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AppealCreate(BaseModel):
    """Schema for creating an appeal."""
    loan_application_id: int = Field(..., description="Loan application ID")
    applicant_id: str = Field(..., description="Applicant ID")
    applicant_name: str = Field(..., description="Applicant name")
    applicant_email: str = Field(..., description="Applicant email")
    appeal_reason: str = Field(..., description="Reason for appeal")
    supporting_evidence: Optional[str] = Field(None, description="Supporting evidence")
    priority: Optional[str] = Field("medium", description="Appeal priority")


class AppealUpdate(BaseModel):
    """Schema for updating an appeal."""
    status: Optional[str] = None
    assigned_to_reviewer: Optional[str] = None
    appeal_decision: Optional[str] = None
    appeal_review_notes: Optional[str] = None
    appeal_decision_reason: Optional[str] = None


class AppealResponse(BaseModel):
    """Response schema for appeal."""
    appeal_id: str
    loan_application_id: int
    applicant_id: str
    applicant_name: str
    applicant_email: str
    status: str
    priority: str
    original_decision: str
    original_rejection_reason: Optional[str]
    original_decision_date: Optional[datetime]
    appeal_reason: str
    supporting_evidence: Optional[str]
    submitted_at: datetime
    assigned_to_reviewer: Optional[str]
    review_started_at: Optional[datetime]
    review_completed_at: Optional[datetime]
    appeal_decision: Optional[str]
    appeal_review_notes: Optional[str]
    appeal_decision_reason: Optional[str]

    class Config:
        from_attributes = True


class AppealNoteCreate(BaseModel):
    """Schema for creating appeal note."""
    added_by: str = Field(..., description="User adding note")
    added_by_type: str = Field(..., description="Type of user (applicant, reviewer, admin)")
    note_content: str = Field(..., description="Note content")
    note_type: Optional[str] = Field("communication", description="Type of note")


class AppealNoteResponse(BaseModel):
    """Response schema for appeal note."""
    note_id: str
    appeal_id: int
    added_by: str
    added_by_type: str
    note_content: str
    note_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class AppealHistoryResponse(BaseModel):
    """Response schema for appeal history."""
    history_id: str
    appeal_id: int
    action_type: str
    from_status: Optional[str]
    to_status: Optional[str]
    changed_by: str
    change_reason: Optional[str]
    change_timestamp: datetime

    class Config:
        from_attributes = True


class AppealNotificationResponse(BaseModel):
    """Response schema for appeal notification."""
    notification_id: str
    appeal_id: int
    recipient_email: str
    recipient_type: str
    notification_type: str
    notification_subject: str
    notification_body: str
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    delivery_status: str

    class Config:
        from_attributes = True


class AppealStatisticsResponse(BaseModel):
    """Response schema for appeal statistics."""
    total_appeals: int
    approved: int
    rejected: int
    pending: int
    approval_rate: float
    avg_resolution_days: Optional[float]
