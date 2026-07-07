from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict
from enum import Enum


class ActionTypeEnum(str, Enum):
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


class EntityTypeEnum(str, Enum):
    CUSTOMER = "customer"
    LOAN_APPLICATION = "loan_application"
    LOAN_DECISION = "loan_decision"
    AUDIT_LOG = "audit_log"
    SYSTEM = "system"


class AuditLogBase(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: str
    action_type: ActionTypeEnum
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    user_name: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes_description: Optional[str] = None
    action_reason: Optional[str] = None
    agent_notes: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    audit_id: str = Field(..., min_length=1, max_length=50)


class AuditLogResponse(AuditLogBase):
    id: int
    audit_id: str
    timestamp: datetime
    related_audit_log_id: Optional[int] = None

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    total: int
    count: int
    logs: list[AuditLogResponse]


class AuditTrailResponse(BaseModel):
    entity_type: EntityTypeEnum
    entity_id: str
    total_events: int
    events: list[AuditLogResponse]


class ComplianceReportResponse(BaseModel):
    period_days: int
    total_actions: int
    by_action_type: Dict[str, int]
    by_entity_type: Dict[str, int]
    by_user: Dict[str, int]
    failed_actions: list[Dict[str, Any]]
    sensitive_actions: list[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditSearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[AuditLogResponse]
