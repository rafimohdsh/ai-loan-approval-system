"""Service for managing application review queue."""

import sys
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.models.review_queue import ReviewQueue, ReviewStatus


class ReviewService:
    """Service to manage manual review queue."""

    @staticmethod
    def add_to_review_queue(db: Session, application_id: str, reason: str, priority: int = 3) -> ReviewQueue:
        """Add application to review queue.

        Args:
            db: Database session
            application_id: Application ID
            reason: Reason for manual review
            priority: Priority level (1=high, 5=low)

        Returns:
            Created ReviewQueue item
        """
        queue_item = ReviewQueue(
            application_id=application_id,
            status=ReviewStatus.PENDING,
            reason=reason,
            priority=priority,
        )
        db.add(queue_item)
        db.commit()
        db.refresh(queue_item)
        return queue_item

    @staticmethod
    def get_pending_reviews(db: Session, limit: int = 50) -> List[ReviewQueue]:
        """Get pending reviews ordered by priority.

        Args:
            db: Database session
            limit: Maximum number of results

        Returns:
            List of pending ReviewQueue items
        """
        return (
            db.query(ReviewQueue)
            .filter(ReviewQueue.status == ReviewStatus.PENDING)
            .order_by(ReviewQueue.priority, ReviewQueue.created_at)
            .limit(limit)
            .all()
        )

    @staticmethod
    def assign_review(db: Session, queue_id: int, reviewer_id: str) -> ReviewQueue:
        """Assign review to reviewer.

        Args:
            db: Database session
            queue_id: Review queue ID
            reviewer_id: Reviewer user ID

        Returns:
            Updated ReviewQueue item
        """
        item = db.query(ReviewQueue).filter(ReviewQueue.id == queue_id).first()
        if item:
            item.status = ReviewStatus.IN_REVIEW
            item.assigned_to = reviewer_id
            db.commit()
            db.refresh(item)
        return item

    @staticmethod
    def complete_review(db: Session, queue_id: int, review_notes: str) -> ReviewQueue:
        """Complete review.

        Args:
            db: Database session
            queue_id: Review queue ID
            review_notes: Notes from reviewer

        Returns:
            Updated ReviewQueue item
        """
        item = db.query(ReviewQueue).filter(ReviewQueue.id == queue_id).first()
        if item:
            item.status = ReviewStatus.RESOLVED
            item.review_notes = review_notes
            item.reviewed_at = datetime.utcnow()
            db.commit()
            db.refresh(item)
        return item
