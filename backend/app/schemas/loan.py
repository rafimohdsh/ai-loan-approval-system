from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LoanStatus(str, Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class LoanApplicationCreate(BaseModel):
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    location: str

    loan_amount: float = Field(gt=0, description="Loan amount must be positive")
    loan_type: str
    loan_term_months: int = Field(gt=0, description="Loan term must be positive")

    annual_income: float = Field(gt=0, description="Annual income must be positive")
    employment_status: str
    years_employed: float = Field(ge=0, description="Years employed cannot be negative")

    credit_score: Optional[int] = None
    existing_debt: float = Field(default=0.0, ge=0)


class LoanApplicationUpdate(BaseModel):
    status: Optional[LoanStatus] = None
    agent_notes: Optional[str] = None
    approval_reason: Optional[str] = None
    rejection_reason: Optional[str] = None
    risk_score: Optional[float] = None
    approval_probability: Optional[float] = None


class LoanApplicationResponse(BaseModel):
    id: int
    application_id: str
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    location: str

    loan_amount: float
    loan_type: str
    loan_term_months: int

    annual_income: float
    employment_status: str
    years_employed: float

    credit_score: Optional[int]
    existing_debt: float

    status: LoanStatus
    risk_score: Optional[float]
    approval_probability: Optional[float]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoanApprovalDecision(BaseModel):
    application_id: str
    approved: bool
    risk_score: float
    approval_probability: float
    reasoning: str
    conditions: Optional[list[str]] = None
