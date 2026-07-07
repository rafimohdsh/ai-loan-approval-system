"""Appeal API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.services.appeal_service import AppealService
from backend.app.schemas.appeal import (
    AppealCreate,
    AppealResponse,
    AppealNoteCreate,
    AppealNoteResponse,
    AppealHistoryResponse,
    AppealStatisticsResponse,
)

router = APIRouter(prefix="/appeals", tags=["appeals"])


@router.post("", status_code=201)
async def submit_appeal(
    appeal_data: AppealCreate,
    db: Session = Depends(get_db)
) -> AppealResponse:
    """Submit an appeal for a rejected/withdrawn application."""
    try:
        appeal = AppealService.submit_appeal(
            db,
            appeal_data.loan_application_id,
            appeal_data.applicant_id,
            appeal_data.applicant_name,
            appeal_data.applicant_email,
            appeal_data.appeal_reason,
            appeal_data.supporting_evidence,
        )
        return appeal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{appeal_id}")
async def get_appeal(
    appeal_id: str,
    db: Session = Depends(get_db)
) -> AppealResponse:
    """Get appeal details."""
    appeal = AppealService.get_appeal(db, appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")
    return appeal


@router.get("/applicant/{applicant_id}")
async def list_applicant_appeals(
    applicant_id: str,
    db: Session = Depends(get_db)
) -> List[AppealResponse]:
    """List appeals for an applicant."""
    return AppealService.list_applicant_appeals(db, applicant_id)


@router.get("")
async def list_pending_appeals(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> List[AppealResponse]:
    """List pending appeals."""
    return AppealService.list_pending_appeals(db, limit)


@router.post("/{appeal_id}/assign")
async def assign_reviewer(
    appeal_id: int,
    reviewer_id: str = Query(...),
    db: Session = Depends(get_db)
) -> AppealResponse:
    """Assign reviewer to an appeal."""
    try:
        appeal = AppealService.assign_reviewer(db, appeal_id, reviewer_id)
        return appeal
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{appeal_id}/approve")
async def approve_appeal(
    appeal_id: int,
    reviewer_id: str = Query(...),
    review_notes: str = Query(...),
    db: Session = Depends(get_db)
) -> AppealResponse:
    """Approve an appeal."""
    try:
        appeal = AppealService.approve_appeal(db, appeal_id, reviewer_id, review_notes)
        return appeal
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{appeal_id}/reject")
async def reject_appeal(
    appeal_id: int,
    reviewer_id: str = Query(...),
    rejection_reason: str = Query(...),
    db: Session = Depends(get_db)
) -> AppealResponse:
    """Reject an appeal."""
    try:
        appeal = AppealService.reject_appeal(db, appeal_id, reviewer_id, rejection_reason)
        return appeal
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{appeal_id}/notes")
async def add_note(
    appeal_id: int,
    note_data: AppealNoteCreate,
    db: Session = Depends(get_db)
) -> AppealNoteResponse:
    """Add note to an appeal."""
    try:
        note = AppealService.add_note(
            db,
            appeal_id,
            note_data.added_by,
            note_data.added_by_type,
            note_data.note_content,
            note_data.note_type,
        )
        return note
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{appeal_id}/notes")
async def get_notes(
    appeal_id: int,
    db: Session = Depends(get_db)
) -> List[AppealNoteResponse]:
    """Get notes for an appeal."""
    return AppealService.get_appeal_notes(db, appeal_id)


@router.get("/{appeal_id}/history")
async def get_history(
    appeal_id: int,
    db: Session = Depends(get_db)
) -> List[AppealHistoryResponse]:
    """Get history for an appeal."""
    return AppealService.get_appeal_history(db, appeal_id)


@router.get("/stats")
async def get_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
) -> AppealStatisticsResponse:
    """Get appeal statistics."""
    return AppealService.get_appeal_statistics(db, days)
