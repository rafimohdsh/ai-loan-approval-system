from sqlalchemy.orm import Session
from ..models import LoanApplication, LoanStatus, LoanDecision, DecisionStatus
from ..schemas import LoanApplicationCreate, LoanApplicationUpdate, LoanApprovalDecision
from uuid import uuid4
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import settings


class LoanService:
    @staticmethod
    def create_application(db: Session, loan_data: LoanApplicationCreate) -> LoanApplication:
        """Create a new loan application."""
        db_loan = LoanApplication(
            application_id=str(uuid4()),
            applicant_name=loan_data.applicant_name,
            applicant_email=loan_data.applicant_email,
            applicant_phone=loan_data.applicant_phone,
            location=loan_data.location,
            loan_amount=loan_data.loan_amount,
            loan_type=loan_data.loan_type,
            loan_term_months=loan_data.loan_term_months,
            annual_income=loan_data.annual_income,
            employment_status=loan_data.employment_status,
            years_employed=loan_data.years_employed,
            credit_score=loan_data.credit_score,
            existing_debt=loan_data.existing_debt,
            status=LoanStatus.PENDING
        )
        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        return db_loan

    @staticmethod
    def get_application(db: Session, application_id: str) -> LoanApplication:
        """Get a loan application by ID."""
        return db.query(LoanApplication).filter(
            LoanApplication.application_id == application_id
        ).first()

    @staticmethod
    def get_application_by_db_id(db: Session, db_id: int) -> LoanApplication:
        """Get a loan application by database ID."""
        return db.query(LoanApplication).filter(
            LoanApplication.id == db_id
        ).first()

    @staticmethod
    def update_application(
        db: Session,
        application_id: str,
        update_data: LoanApplicationUpdate
    ) -> LoanApplication:
        """Update a loan application."""
        db_loan = LoanService.get_application(db, application_id)
        if not db_loan:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_loan, key, value)

        db.commit()
        db.refresh(db_loan)
        return db_loan

    @staticmethod
    def set_approval_decision(
        db: Session,
        application_id: str,
        decision: LoanApprovalDecision
    ) -> LoanApplication:
        """Set approval decision for a loan application."""
        db_loan = LoanService.get_application(db, application_id)
        if not db_loan:
            return None

        db_loan.status = LoanStatus.APPROVED if decision.approved else LoanStatus.REJECTED
        db_loan.risk_score = decision.risk_score
        db_loan.approval_probability = decision.approval_probability
        db_loan.approval_reason = decision.reasoning if decision.approved else None
        db_loan.rejection_reason = decision.reasoning if not decision.approved else None
        db_loan.agent_notes = f"Conditions: {', '.join(decision.conditions)}" if decision.conditions else None
        db_loan.processed_at = datetime.utcnow()

        db.commit()
        db.refresh(db_loan)
        return db_loan

    @staticmethod
    def list_applications(
        db: Session,
        status: LoanStatus = None,
        skip: int = 0,
        limit: int = 10
    ) -> list[LoanApplication]:
        """List loan applications with optional filtering."""
        query = db.query(LoanApplication)
        if status:
            query = query.filter(LoanApplication.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_applications(db: Session, status: LoanStatus = None) -> int:
        """Count loan applications with optional filtering."""
        query = db.query(LoanApplication)
        if status:
            query = query.filter(LoanApplication.status == status)
        return query.count()

    @staticmethod
    def create_decision(db: Session, application: LoanApplication) -> LoanDecision:
        """Create loan decision based on application data."""
        # Simple rule-based decision logic
        dti_ratio = (application.existing_debt * 12) / application.annual_income if application.annual_income > 0 else 0

        # Decision logic
        if application.credit_score is None:
            decision_status = DecisionStatus.PENDING
            risk_score = 0.6
            approval_prob = 0.5
            reasoning = "No credit history - requires manual review"
        elif application.credit_score < 600:
            decision_status = DecisionStatus.REJECTED
            risk_score = 0.9
            approval_prob = 0.05
            reasoning = "Credit score below acceptable threshold"
        elif dti_ratio > 0.50:
            decision_status = DecisionStatus.REJECTED
            risk_score = 0.85
            approval_prob = 0.1
            reasoning = "Debt-to-income ratio exceeds acceptable limit"
        elif (application.annual_income / application.loan_amount) < 1.0 if application.loan_amount > 0 else False:
            decision_status = DecisionStatus.REJECTED
            risk_score = 0.8
            approval_prob = 0.15
            reasoning = "Loan amount exceeds annual income"
        elif application.years_employed < 1:
            decision_status = DecisionStatus.PENDING
            risk_score = 0.65
            approval_prob = 0.55
            reasoning = "Employment tenure less than 1 year - requires review"
        elif application.credit_score < 650 or dti_ratio > 0.43:
            decision_status = DecisionStatus.PENDING
            risk_score = 0.55
            approval_prob = 0.65
            reasoning = "Multiple risk factors - requires manual review"
        elif application.credit_score >= 700 and dti_ratio <= 0.36:
            decision_status = DecisionStatus.APPROVED
            risk_score = 0.2
            approval_prob = 0.95
            reasoning = "Strong financial profile with good credit and low DTI"
        else:
            decision_status = DecisionStatus.APPROVED
            risk_score = 0.4
            approval_prob = 0.80
            reasoning = "Application meets loan approval criteria"

        # Create decision record
        decision = LoanDecision(
            decision_id=str(uuid4()),
            loan_application_id=application.id,
            decision_status=decision_status,
            risk_score=risk_score,
            approval_probability=approval_prob,
            agent_analysis=reasoning,
            decision_made_by="System_Agent",
            decision_made_at=datetime.utcnow()
        )
        db.add(decision)

        # Update application with decision results
        application.risk_score = risk_score
        application.approval_probability = approval_prob
        if decision_status == DecisionStatus.APPROVED:
            application.status = LoanStatus.APPROVED
            application.approval_reason = reasoning
        elif decision_status == DecisionStatus.REJECTED:
            application.status = LoanStatus.REJECTED
            application.rejection_reason = reasoning
        else:
            application.status = LoanStatus.UNDER_REVIEW
            application.agent_notes = reasoning

        db.commit()
        db.refresh(decision)
        return decision
