from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class DecisionStatusEnum(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CONDITIONAL = "CONDITIONAL"
    PENDING = "PENDING"


class DecisionReasonEnum(str, Enum):
    EXCELLENT_CREDIT = "excellent_credit"
    GOOD_INCOME_TO_DEBT = "good_income_to_debt"
    STRONG_CREDIT_HISTORY = "strong_credit_history"
    STABLE_EMPLOYMENT = "stable_employment"
    LOW_RISK_PROFILE = "low_risk_profile"
    LOW_CREDIT_SCORE = "low_credit_score"
    HIGH_DEBT_TO_INCOME = "high_debt_to_income"
    INSUFFICIENT_INCOME = "insufficient_income"
    POOR_EMPLOYMENT_HISTORY = "poor_employment_history"
    HIGH_RISK_PROFILE = "high_risk_profile"


class LoanDecisionBase(BaseModel):
    loan_application_id: int
    decision_status: DecisionStatusEnum
    decision_reason: Optional[DecisionReasonEnum] = None
    risk_score: float = Field(..., ge=0.0, le=1.0)
    approval_probability: float = Field(..., ge=0.0, le=1.0)
    approved_amount: Optional[float] = None
    approved_term_months: Optional[int] = None
    interest_rate: Optional[float] = None
    agent_analysis: Optional[str] = None
    primary_reasons: Optional[str] = None
    secondary_factors: Optional[str] = None
    recommendation_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    requires_manual_review: bool = False
    decision_made_by: Optional[str] = None
    conditions_for_approval: Optional[str] = None


class LoanDecisionCreate(LoanDecisionBase):
    decision_id: str = Field(..., min_length=1, max_length=50)


class LoanDecisionUpdate(BaseModel):
    decision_status: Optional[DecisionStatusEnum] = None
    decision_reason: Optional[DecisionReasonEnum] = None
    risk_score: Optional[float] = None
    approval_probability: Optional[float] = None
    approved_amount: Optional[float] = None
    approved_term_months: Optional[int] = None
    interest_rate: Optional[float] = None
    agent_analysis: Optional[str] = None
    primary_reasons: Optional[str] = None
    secondary_factors: Optional[str] = None
    recommendation_confidence: Optional[float] = None
    requires_manual_review: Optional[bool] = None
    conditions_for_approval: Optional[str] = None


class LoanDecisionResponse(LoanDecisionBase):
    id: int
    decision_id: str
    decision_made_at: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoanDecisionListResponse(BaseModel):
    total: int
    count: int
    decisions: list[LoanDecisionResponse]


class DecisionSummaryResponse(BaseModel):
    decision_id: str
    decision_status: DecisionStatusEnum
    risk_score: float
    approval_probability: float
    approved_amount: Optional[float]
    decision_made_at: Optional[datetime]
    requires_manual_review: bool
