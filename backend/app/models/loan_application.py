from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, Index
from sqlalchemy.sql import func
from .base import Base, TimestampMixin
import enum


class LoanStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class LoanApplication(Base, TimestampMixin):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(50), unique=True, nullable=False, index=True)
    applicant_name = Column(String(255), nullable=False)
    applicant_email = Column(String(255), nullable=False, index=True)
    applicant_phone = Column(String(20), nullable=False)
    location = Column(String(255), nullable=False)

    loan_amount = Column(Float, nullable=False)
    loan_type = Column(String(50), nullable=False, index=True)
    loan_term_months = Column(Integer, nullable=False)

    annual_income = Column(Float, nullable=False)
    employment_status = Column(String(50), nullable=False)
    years_employed = Column(Float, nullable=False)

    credit_score = Column(Integer, nullable=True, index=True)
    existing_debt = Column(Float, default=0.0)

    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING, nullable=False, index=True)

    agent_notes = Column(Text, nullable=True)
    approval_reason = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    risk_score = Column(Float, nullable=True, index=True)
    approval_probability = Column(Float, nullable=True)

    processed_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    __table_args__ = (
        Index("idx_status_created", status, created_at.desc()),
        Index("idx_applicant_status", applicant_email, status),
        Index("idx_credit_risk", credit_score, risk_score),
        Index("idx_processed_status", processed_at, status),
    )

    def __repr__(self):
        return f"<LoanApplication(id={self.id}, application_id={self.application_id}, status={self.status})>"
