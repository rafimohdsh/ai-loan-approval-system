"""API endpoints for reviewer operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.services.reviewer_service import ReviewerService
from backend.app.schemas.review import (
    ReviewerProfileCreate,
    ReviewerProfileResponse,
    ReviewerAssignmentCreate,
    ReviewerAssignmentResponse,
    ReviewActionCreate,
    QueueItemResponse,
    ReviewStatsResponse,
    AuditHistoryResponse,
    ReviewStatus,
    ReviewPriority,
)
from backend.app.models import ReviewerAssignment, ReviewStatus as ModelReviewStatus

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reviewer", tags=["reviewer"])


@router.post("/profiles", response_model=ReviewerProfileResponse, status_code=201)
def create_reviewer_profile(
    profile: ReviewerProfileCreate,
    db: Session = Depends(get_db),
):
    """Create a new reviewer profile."""
    try:
        created_profile = ReviewerService.create_reviewer_profile(db, profile)
        return created_profile
    except Exception as e:
        logger.error(f"Error creating reviewer profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{reviewer_id}", response_model=ReviewerProfileResponse)
def get_reviewer_profile(
    reviewer_id: str,
    db: Session = Depends(get_db),
):
    """Get reviewer profile."""
    profile = ReviewerService.get_reviewer_profile(db, reviewer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Reviewer not found")
    return profile


@router.get("/profiles", response_model=List[ReviewerProfileResponse])
def list_active_reviewers(db: Session = Depends(get_db)):
    """List all active reviewers."""
    reviewers = ReviewerService.list_active_reviewers(db)
    return reviewers


@router.get("/queue", response_model=List[QueueItemResponse])
def get_review_queue(
    status: str = None,
    priority: str = None,
    db: Session = Depends(get_db),
):
    """Get applications in review queue."""
    try:
        status_enum = ModelReviewStatus[status] if status else None
        priority_enum = ReviewPriority(priority) if priority else None

        assignments = ReviewerService.get_queue(db, status_enum, priority_enum)

        queue_items = []
        for assignment in assignments:
            from backend.app.models import LoanApplication
            app = db.query(LoanApplication).filter(
                LoanApplication.id == assignment.loan_application_id
            ).first()

            if app:
                queue_items.append(QueueItemResponse(
                    assignment_id=assignment.assignment_id,
                    loan_application_id=assignment.loan_application_id,
                    applicant_name=app.applicant_name,
                    applicant_email=app.applicant_email,
                    loan_amount=app.loan_amount,
                    annual_income=app.annual_income,
                    credit_score=app.credit_score,
                    status=ReviewStatus[assignment.status.value],
                    priority=ReviewPriority(assignment.priority.value),
                    assigned_reviewer=assignment.reviewer_name,
                    assigned_at=assignment.assigned_at,
                    risk_score=app.risk_score,
                ))

        return queue_items
    except Exception as e:
        logger.error(f"Error getting review queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/reviewer/{reviewer_id}", response_model=List[QueueItemResponse])
def get_reviewer_queue(
    reviewer_id: str,
    db: Session = Depends(get_db),
):
    """Get applications assigned to a reviewer."""
    try:
        assignments = ReviewerService.get_reviewer_queue(db, reviewer_id)

        queue_items = []
        for assignment in assignments:
            from backend.app.models import LoanApplication
            app = db.query(LoanApplication).filter(
                LoanApplication.id == assignment.loan_application_id
            ).first()

            if app:
                queue_items.append(QueueItemResponse(
                    assignment_id=assignment.assignment_id,
                    loan_application_id=assignment.loan_application_id,
                    applicant_name=app.applicant_name,
                    applicant_email=app.applicant_email,
                    loan_amount=app.loan_amount,
                    annual_income=app.annual_income,
                    credit_score=app.credit_score,
                    status=ReviewStatus[assignment.status.value],
                    priority=ReviewPriority(assignment.priority.value),
                    assigned_reviewer=assignment.reviewer_name,
                    assigned_at=assignment.assigned_at,
                    risk_score=app.risk_score,
                ))

        return queue_items
    except Exception as e:
        logger.error(f"Error getting reviewer queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign", response_model=ReviewerAssignmentResponse, status_code=201)
def assign_reviewer(
    assignment: ReviewerAssignmentCreate,
    db: Session = Depends(get_db),
):
    """Assign a reviewer to an application."""
    try:
        priority_enum = ReviewPriority(assignment.priority.value) if assignment.priority else ReviewPriority.MEDIUM
        created_assignment = ReviewerService.assign_reviewer(
            db,
            assignment.loan_application_id,
            assignment.reviewer_id,
            priority_enum,
        )
        return created_assignment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error assigning reviewer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assignments/{assignment_id}", response_model=ReviewerAssignmentResponse)
def get_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    """Get assignment details."""
    assignment = ReviewerService.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.patch("/assignments/{assignment_id}/start", response_model=ReviewerAssignmentResponse)
def start_review(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    """Start reviewing an application."""
    try:
        assignment = ReviewerService.start_review(db, assignment_id)
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assignments/{assignment_id}/approve")
def approve_application(
    assignment_id: str,
    review_notes: str,
    reviewer_id: str,
    db: Session = Depends(get_db),
):
    """Approve an application."""
    try:
        assignment, action = ReviewerService.approve_application(
            db,
            assignment_id,
            review_notes,
            reviewer_id,
        )
        return {
            "assignment": ReviewerAssignmentResponse.from_orm(assignment),
            "action": {
                "action_id": action.action_id,
                "action_type": action.action_type,
                "action_status": action.action_status,
                "timestamp": action.action_timestamp,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error approving application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assignments/{assignment_id}/reject")
def reject_application(
    assignment_id: str,
    rejection_reason: str,
    reviewer_id: str,
    db: Session = Depends(get_db),
):
    """Reject an application."""
    try:
        assignment, action = ReviewerService.reject_application(
            db,
            assignment_id,
            rejection_reason,
            reviewer_id,
        )
        return {
            "assignment": ReviewerAssignmentResponse.from_orm(assignment),
            "action": {
                "action_id": action.action_id,
                "action_type": action.action_type,
                "action_status": action.action_status,
                "timestamp": action.action_timestamp,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error rejecting application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assignments/{assignment_id}/re-decision")
def request_re_decision(
    assignment_id: str,
    review_notes: str,
    reviewer_id: str,
    db: Session = Depends(get_db),
):
    """Request re-decision from automated workflow."""
    try:
        assignment, action = ReviewerService.request_re_decision(
            db,
            assignment_id,
            review_notes,
            reviewer_id,
        )
        return {
            "assignment": ReviewerAssignmentResponse.from_orm(assignment),
            "action": {
                "action_id": action.action_id,
                "action_type": action.action_type,
                "action_status": action.action_status,
                "timestamp": action.action_timestamp,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error requesting re-decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/{loan_application_id}", response_model=List[AuditHistoryResponse])
def get_audit_history(
    loan_application_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get audit history for an application."""
    try:
        history = ReviewerService.get_audit_history(db, loan_application_id, limit)
        return history
    except Exception as e:
        logger.error(f"Error getting audit history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/reviewer/{reviewer_id}", response_model=List[AuditHistoryResponse])
def get_reviewer_audit_history(
    reviewer_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get audit history for a reviewer."""
    try:
        history = ReviewerService.get_reviewer_history(db, reviewer_id, limit)
        return history
    except Exception as e:
        logger.error(f"Error getting reviewer history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=ReviewStatsResponse)
def get_review_stats(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Get review statistics."""
    try:
        stats = ReviewerService.get_review_stats(db, days)
        return stats
    except Exception as e:
        logger.error(f"Error getting review stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
