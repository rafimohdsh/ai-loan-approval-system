from sqlalchemy.orm import Session
from typing import Optional, List
from ..database.repositories import     CustomerRepository,
    LoanApplicationRepository,
    LoanDecisionRepository,
    AuditLogRepository
)
from ..models import import uuid
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Main service for database operations"""

    def __init__(self, db: Session):
        self.db = db
        self.customers = CustomerRepository(db)
        self.loan_applications = LoanApplicationRepository(db)
        self.loan_decisions = LoanDecisionRepository(db)
        self.audit_logs = AuditLogRepository(db)

    def close(self):
        """Close the database session"""
        self.db.close()

    def commit(self):
        """Commit changes"""
        self.db.commit()

    def rollback(self):
        """Rollback changes"""
        self.db.rollback()

    def log_audit_action(
        self,
        entity_type: str,
        entity_id: str,
        action_type: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        user_name: Optional[str] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        action_reason: Optional[str] = None,
        agent_notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log an action to the audit trail"""
        audit_id = f"AUDIT-{uuid.uuid4().hex[:12].upper()}"

        audit_log = self.audit_logs.log_action(
            entity_type=entity_type,
            entity_id=entity_id,
            action_type=action_type,
            audit_id=audit_id,
            user_id=user_id,
            user_role=user_role,
            user_name=user_name,
            old_values=old_values,
            new_values=new_values,
            action_reason=action_reason,
            agent_notes=agent_notes,
            ip_address=ip_address,
            **kwargs
        )
        return audit_log

    def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get complete audit history for an entity"""
        return self.audit_logs.get_by_entity(entity_type, entity_id, limit=limit)

    def get_user_activity(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get all actions performed by a user"""
        return self.audit_logs.get_by_user(user_id, limit=limit)

    def export_audit_logs(
        self,
        start_date,
        end_date,
        entity_type: Optional[str] = None,
        action_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[AuditLog]:
        """Export audit logs for reporting"""
        logs = self.audit_logs.get_by_date_range(start_date, end_date)

        if entity_type:
            logs = [log for log in logs if log.entity_type == entity_type]
        if action_type:
            logs = [log for log in logs if log.action_type == action_type]
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]

        return logs

    def get_compliance_report(self, days: int = 30) -> dict:
        """Generate compliance report with audit summary"""
        recent_logs = self.audit_logs.get_recent(days=days)

        report = {
            "period_days": days,
            "total_actions": len(recent_logs),
            "by_action_type": {},
            "by_entity_type": {},
            "by_user": {},
            "failed_actions": [],
            "sensitive_actions": [],
        }

        for log in recent_logs:
            # Count by action type
            action = str(log.action_type)
            report["by_action_type"][action] = report["by_action_type"].get(action, 0) + 1

            # Count by entity type
            entity = str(log.entity_type)
            report["by_entity_type"][entity] = report["by_entity_type"].get(entity, 0) + 1

            # Count by user
            user = log.user_id or "system"
            report["by_user"][user] = report["by_user"].get(user, 0) + 1

            # Track failures
            if log.status == "failed":
                report["failed_actions"].append({
                    "audit_id": log.audit_id,
                    "action": action,
                    "entity": entity,
                    "error": log.error_message,
                    "timestamp": log.timestamp.isoformat()
                })

            # Track sensitive actions
            if action in ["APPROVE", "REJECT", "DELETE"]:
                report["sensitive_actions"].append({
                    "audit_id": log.audit_id,
                    "action": action,
                    "entity": entity,
                    "user": log.user_name or user,
                    "timestamp": log.timestamp.isoformat()
                })

        return report
