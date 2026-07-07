"""Notification Agent - Generates notifications and audit entries."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class NotificationType(str, Enum):
    """Notification types."""
    DECISION = "decision"
    APPROVAL = "approval"
    REJECTION = "rejection"
    MANUAL_REVIEW = "manual_review"
    DOCUMENT_REQUEST = "document_request"
    STATUS_UPDATE = "status_update"


class NotificationChannel(str, Enum):
    """Notification channels."""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class AuditEntry(BaseModel):
    """Audit log entry."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    application_id: str = Field(..., description="Application ID")
    event_type: str = Field(..., description="Event type")
    actor: str = Field(..., description="Who performed action (system/user)")
    details: str = Field(..., description="Event details")


class Notification(BaseModel):
    """Notification entry."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    application_id: str = Field(..., description="Application ID")
    recipient_email: str = Field(..., description="Recipient email")
    notification_type: NotificationType = Field(..., description="Notification type")
    subject: str = Field(..., description="Email subject")
    message: str = Field(..., description="Message body")
    channels: list[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.EMAIL])
    sent: bool = Field(default=False, description="Whether sent")


def create_decision_notification(
    application_id: str,
    applicant_name: str,
    applicant_email: str,
    decision: str,
    reasoning: str,
    conditions: Optional[str] = None,
) -> Notification:
    """Create notification for loan decision."""
    if decision == "approved":
        subject = f"Loan Application {application_id} - APPROVED ✓"
        message = f"""Dear {applicant_name},

Your loan application has been APPROVED.

Details:
- Application ID: {application_id}
- Status: APPROVED
- Reason: {reasoning}"""
        if conditions:
            message += f"\n- Conditions: {conditions}"
        message += "\n\nThank you for choosing us!"
        notif_type = NotificationType.APPROVAL
    elif decision == "rejected":
        subject = f"Loan Application {application_id} - REJECTED"
        message = f"""Dear {applicant_name},

Unfortunately, your loan application has been REJECTED.

Details:
- Application ID: {application_id}
- Status: REJECTED
- Reason: {reasoning}

Please contact us for more information."""
        notif_type = NotificationType.REJECTION
    else:  # manual_review
        subject = f"Loan Application {application_id} - UNDER REVIEW"
        message = f"""Dear {applicant_name},

Your loan application requires manual review by our team.

Details:
- Application ID: {application_id}
- Status: MANUAL REVIEW
- Reason: {reasoning}

We will contact you shortly."""
        notif_type = NotificationType.MANUAL_REVIEW

    return Notification(
        application_id=application_id,
        recipient_email=applicant_email,
        notification_type=notif_type,
        subject=subject,
        message=message,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
    )


def create_status_notification(
    application_id: str,
    applicant_name: str,
    applicant_email: str,
    old_status: str,
    new_status: str,
) -> Notification:
    """Create notification for status change."""
    return Notification(
        application_id=application_id,
        recipient_email=applicant_email,
        notification_type=NotificationType.STATUS_UPDATE,
        subject=f"Application {application_id} Status Updated",
        message=f"""Dear {applicant_name},

Your loan application status has been updated.

- Application ID: {application_id}
- Previous Status: {old_status}
- New Status: {new_status}

Log in to check details.""",
        channels=[NotificationChannel.EMAIL],
    )


def create_document_request_notification(
    application_id: str,
    applicant_name: str,
    applicant_email: str,
    documents_needed: list[str],
    deadline_days: int = 7,
) -> Notification:
    """Create notification requesting documents."""
    docs_list = "\n".join([f"- {doc}" for doc in documents_needed])
    return Notification(
        application_id=application_id,
        recipient_email=applicant_email,
        notification_type=NotificationType.DOCUMENT_REQUEST,
        subject=f"Documents Required for Application {application_id}",
        message=f"""Dear {applicant_name},

We need the following documents to process your loan application:

{docs_list}

Please submit by: {deadline_days} days from now

Upload at: [portal link]""",
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
    )


def create_audit_entry(
    application_id: str,
    event_type: str,
    actor: str,
    details: str,
) -> AuditEntry:
    """Create audit entry."""
    return AuditEntry(
        application_id=application_id,
        event_type=event_type,
        actor=actor,
        details=details,
    )


def generate_notifications_and_audit(
    application_id: str,
    applicant_name: str,
    applicant_email: str,
    event_type: str,
    decision: Optional[str] = None,
    reasoning: Optional[str] = None,
    conditions: Optional[str] = None,
    old_status: Optional[str] = None,
    new_status: Optional[str] = None,
) -> dict:
    """
    Generate notifications and audit entries for loan events.

    Args:
        application_id: Application ID
        applicant_name: Applicant name
        applicant_email: Applicant email
        event_type: Type of event (decision, status_change, document_request)
        decision: Loan decision (approved/rejected/manual_review) if applicable
        reasoning: Reason for decision if applicable
        conditions: Conditions if approved
        old_status: Previous status if applicable
        new_status: New status if applicable

    Returns:
        Dict with notifications and audit entries
    """
    notifications = []
    audit_entries = []

    # Generate notification based on event type
    if event_type == "decision" and decision:
        notification = create_decision_notification(
            application_id,
            applicant_name,
            applicant_email,
            decision,
            reasoning or "Application reviewed",
            conditions,
        )
        notifications.append(notification)

        audit_entries.append(
            create_audit_entry(
                application_id,
                "decision_made",
                "system",
                f"Decision: {decision}, Reasoning: {reasoning}",
            )
        )

    elif event_type == "status_change" and old_status and new_status:
        notification = create_status_notification(
            application_id,
            applicant_name,
            applicant_email,
            old_status,
            new_status,
        )
        notifications.append(notification)

        audit_entries.append(
            create_audit_entry(
                application_id,
                "status_changed",
                "system",
                f"Status changed from {old_status} to {new_status}",
            )
        )

    elif event_type == "document_request":
        notification = create_document_request_notification(
            application_id,
            applicant_name,
            applicant_email,
            ["Bank Statement", "ID Proof", "Employment Letter"],
        )
        notifications.append(notification)

        audit_entries.append(
            create_audit_entry(
                application_id,
                "document_requested",
                "system",
                "Documents requested from applicant",
            )
        )

    return {
        "notifications": [n.model_dump() for n in notifications],
        "audit_entries": [a.model_dump() for a in audit_entries],
    }
