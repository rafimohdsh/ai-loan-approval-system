from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Generic, TypeVar
from datetime import datetime, timedelta
from ..models import     Customer, LoanApplication, LoanDecision, AuditLog,
    ActionType, EntityType
)
import json
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""

    def __init__(self, db: Session, model: type[T]):
        self.db = db
        self.model = model

    def create(self, obj_in: dict) -> T:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get(self, id: int) -> Optional[T]:
        """Get record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: int, obj_in: dict) -> Optional[T]:
        """Update a record"""
        db_obj = self.get(id)
        if db_obj:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """Delete a record"""
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False


class CustomerRepository(BaseRepository[Customer]):
    """Repository for Customer model"""

    def __init__(self, db: Session):
        super().__init__(db, Customer)

    def get_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        return self.db.query(Customer).filter(Customer.email == email).first()

    def get_by_customer_id(self, customer_id: str) -> Optional[Customer]:
        """Get customer by customer_id"""
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()

    def get_by_ssn(self, ssn: str) -> Optional[Customer]:
        """Get customer by SSN"""
        return self.db.query(Customer).filter(Customer.ssn == ssn).first()

    def get_active_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get all active customers"""
        return self.db.query(Customer).filter(Customer.is_active == True).offset(skip).limit(limit).all()

    def search(self, query: str) -> List[Customer]:
        """Search customers by name or email"""
        search_pattern = f"%{query}%"
        return self.db.query(Customer).filter(
            (Customer.first_name.like(search_pattern)) |
            (Customer.last_name.like(search_pattern)) |
            (Customer.email.like(search_pattern))
        ).all()


class LoanApplicationRepository(BaseRepository[LoanApplication]):
    """Repository for LoanApplication model"""

    def __init__(self, db: Session):
        super().__init__(db, LoanApplication)

    def get_by_application_id(self, application_id: str) -> Optional[LoanApplication]:
        """Get application by application_id"""
        return self.db.query(LoanApplication).filter(
            LoanApplication.application_id == application_id
        ).first()

    def get_by_applicant_email(self, email: str) -> List[LoanApplication]:
        """Get all applications by applicant email"""
        return self.db.query(LoanApplication).filter(
            LoanApplication.applicant_email == email
        ).all()

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications by status"""
        return self.db.query(LoanApplication).filter(
            LoanApplication.status == status
        ).offset(skip).limit(limit).all()

    def get_pending_applications(self, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get all pending applications"""
        from app.models import LoanStatus
        return self.get_by_status(LoanStatus.PENDING, skip, limit)

    def get_recent_applications(self, days: int = 30, limit: int = 100) -> List[LoanApplication]:
        """Get applications created in the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(LoanApplication).filter(
            LoanApplication.created_at >= cutoff_date
        ).order_by(desc(LoanApplication.created_at)).limit(limit).all()

    def get_high_value_applications(self, min_amount: float, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications above a certain loan amount"""
        return self.db.query(LoanApplication).filter(
            LoanApplication.loan_amount >= min_amount
        ).offset(skip).limit(limit).all()


class LoanDecisionRepository(BaseRepository[LoanDecision]):
    """Repository for LoanDecision model"""

    def __init__(self, db: Session):
        super().__init__(db, LoanDecision)

    def get_by_decision_id(self, decision_id: str) -> Optional[LoanDecision]:
        """Get decision by decision_id"""
        return self.db.query(LoanDecision).filter(
            LoanDecision.decision_id == decision_id
        ).first()

    def get_by_application_id(self, application_id: int) -> Optional[LoanDecision]:
        """Get decision for a loan application"""
        return self.db.query(LoanDecision).filter(
            LoanDecision.loan_application_id == application_id
        ).first()

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[LoanDecision]:
        """Get decisions by status"""
        return self.db.query(LoanDecision).filter(
            LoanDecision.decision_status == status
        ).offset(skip).limit(limit).all()

    def get_requiring_review(self, skip: int = 0, limit: int = 100) -> List[LoanDecision]:
        """Get decisions that require manual review"""
        return self.db.query(LoanDecision).filter(
            LoanDecision.requires_manual_review == True
        ).offset(skip).limit(limit).all()

    def get_high_risk(self, threshold: float = 0.7, skip: int = 0, limit: int = 100) -> List[LoanDecision]:
        """Get high-risk decisions"""
        return self.db.query(LoanDecision).filter(
            LoanDecision.risk_score >= threshold
        ).offset(skip).limit(limit).all()

    def get_by_confidence(self, min_confidence: float, skip: int = 0, limit: int = 100) -> List[LoanDecision]:
        """Get decisions with confidence above threshold"""
        return self.db.query(LoanDecision).filter(
            LoanDecision.recommendation_confidence >= min_confidence
        ).offset(skip).limit(limit).all()


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog model"""

    def __init__(self, db: Session):
        super().__init__(db, AuditLog)

    def get_by_audit_id(self, audit_id: str) -> Optional[AuditLog]:
        """Get audit log by audit_id"""
        return self.db.query(AuditLog).filter(
            AuditLog.audit_id == audit_id
        ).first()

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get all audit logs for an entity"""
        return self.db.query(AuditLog).filter(
            (AuditLog.entity_type == entity_type) &
            (AuditLog.entity_id == entity_id)
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

    def get_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get all audit logs for a user"""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

    def get_by_action_type(
        self,
        action_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by action type"""
        return self.db.query(AuditLog).filter(
            AuditLog.action_type == action_type
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

    def get_recent(self, days: int = 7, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(AuditLog).filter(
            AuditLog.timestamp >= cutoff_date
        ).order_by(desc(AuditLog.timestamp)).limit(limit).all()

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs within a date range"""
        return self.db.query(AuditLog).filter(
            (AuditLog.timestamp >= start_date) &
            (AuditLog.timestamp <= end_date)
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

    def log_action(
        self,
        entity_type: str,
        entity_id: str,
        action_type: str,
        audit_id: str,
        user_id: Optional[str] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        action_reason: Optional[str] = None,
        user_role: Optional[str] = None,
        user_name: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log an action to the audit log"""
        audit_log = AuditLog(
            audit_id=audit_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action_type=action_type,
            user_id=user_id,
            user_role=user_role,
            user_name=user_name,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            action_reason=action_reason,
            timestamp=datetime.utcnow(),
            **kwargs
        )
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        logger.info(f"Audit log created: {audit_id} - {action_type} on {entity_type}:{entity_id}")
        return audit_log
