from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin
import enum


class DecisionStatus(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CONDITIONAL = "CONDITIONAL"
    PENDING = "PENDING"


class DecisionReason(str, enum.Enum):
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


class LoanDecision(Base, TimestampMixin):
    __tablename__ = "loan_decisions"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(String(50), unique=True, nullable=False, index=True)

    loan_application_id = Column(Integer, ForeignKey('loan_applications.id'), nullable=False, index=True)

    decision_status = Column(Enum(DecisionStatus), nullable=False, index=True)
    decision_reason = Column(Enum(DecisionReason), nullable=True)

    risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    approval_probability = Column(Float, nullable=False)  # 0.0 to 1.0

    approved_amount = Column(Float, nullable=True)  # Actual amount approved (may differ from requested)
    approved_term_months = Column(Integer, nullable=True)
    interest_rate = Column(Float, nullable=True)

    agent_analysis = Column(Text, nullable=True)  # Detailed analysis from the agent
    primary_reasons = Column(Text, nullable=True)  # JSON array of reasons
    secondary_factors = Column(Text, nullable=True)  # Additional factors considered

    recommendation_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    requires_manual_review = Column(Boolean, default=False)

    decision_made_by = Column(String(100), nullable=True)  # Agent name or user who made decision
    decision_made_at = Column(DateTime, nullable=True)

    conditions_for_approval = Column(Text, nullable=True)  # For conditional approvals
    next_review_date = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_decision_app_id', 'loan_application_id'),
        Index('idx_decision_status', 'decision_status'),
        Index('idx_decision_risk_score', 'risk_score'),
    )

    def __repr__(self):
        return f"<LoanDecision(id={self.id}, decision_id={self.decision_id}, status={self.decision_status})>"
