from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Index, JSON
from sqlalchemy.sql import func
from .base import Base
import enum
from datetime import datetime


class ActionType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    APPROVE = "approve"
    REJECT = "reject"
    ASSIGN = "assign"
    COMMENT = "comment"
    EXPORT = "export"
    SYSTEM_ACTION = "system_action"


class EntityType(str, enum.Enum):
    CUSTOMER = "customer"
    LOAN_APPLICATION = "loan_application"
    LOAN_DECISION = "loan_decision"
    AUDIT_LOG = "audit_log"
    SYSTEM = "system"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String(50), unique=True, nullable=False, index=True)

    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    entity_id = Column(String(50), nullable=False, index=True)
    action_type = Column(Enum(ActionType), nullable=False, index=True)

    user_id = Column(String(100), nullable=True, index=True)  # User or agent who performed action
    user_role = Column(String(50), nullable=True)  # admin, agent, user, system
    user_name = Column(String(255), nullable=True)

    old_values = Column(Text, nullable=True)  # JSON string of previous values
    new_values = Column(Text, nullable=True)  # JSON string of new values
    changes_description = Column(Text, nullable=True)

    action_reason = Column(Text, nullable=True)  # Why the action was taken
    agent_notes = Column(Text, nullable=True)  # Additional notes from agent or user

    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)

    status = Column(String(50), default="success")  # success, failed, partial
    error_message = Column(Text, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    extra_context = Column(Text, nullable=True)  # JSON for additional context

    related_audit_log_id = Column(Integer, ForeignKey('audit_logs.id'), nullable=True)

    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_action_timestamp', 'action_type', 'timestamp'),
        Index('idx_audit_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, audit_id={self.audit_id}, action={self.action_type}, entity={self.entity_type})>"
