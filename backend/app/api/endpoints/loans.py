from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...schemas import (
    LoanApplicationCreate,
    LoanApplicationResponse,
)
from ...services import LoanService
from ...services.orchestration_service import OrchestrationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("/apply", response_model=LoanApplicationResponse, status_code=201)
def apply_loan(application: LoanApplicationCreate, db: Session = Depends(get_db)):
    """Submit a new loan application."""
    db_loan = LoanService.create_application(db, application)

    # Execute multi-agent workflow
    try:
        workflow_result = OrchestrationService.process_loan_application(db, db_loan)
        logger.info(f"Workflow processed application {db_loan.application_id}")
    except Exception as e:
        logger.warning(f"Workflow failed for {db_loan.application_id}, using fallback: {str(e)}")
        # Fallback to rule-based decision
        LoanService.create_decision(db, db_loan)

    db.refresh(db_loan)
    return db_loan


@router.get("/status/{application_id}", response_model=LoanApplicationResponse)
def get_loan_status(application_id: str, db: Session = Depends(get_db)):
    """Get loan application status by application ID."""
    db_loan = LoanService.get_application(db, application_id)
    if not db_loan:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_loan


@router.get("/status", response_model=list[LoanApplicationResponse])
def list_loan_applications(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all loan applications."""
    apps = LoanService.list_applications(db, skip=skip, limit=limit)
    return apps
