"""Orchestration service for multi-agent loan approval workflow."""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.agents.workflows.loan_approval_graph import (
    create_loan_approval_graph,
    AgentState,
)
from backend.app.models import LoanApplication, LoanDecision, LoanStatus, DecisionStatus
from backend.app.schemas import LoanApplicationCreate

logger = logging.getLogger(__name__)


class OrchestrationService:
    """Service to orchestrate multi-agent loan approval workflow."""

    @staticmethod
    def process_loan_application(db: Session, loan_app: LoanApplication) -> Dict[str, Any]:
        """
        Execute multi-agent workflow for loan application.

        Args:
            db: Database session
            loan_app: LoanApplication model instance

        Returns:
            Dictionary with workflow results and audit trail
        """
        # Create initial state from application data
        state = AgentState(
            application_id=loan_app.application_id,
            applicant_name=loan_app.applicant_name,
            applicant_email=loan_app.applicant_email,
            applicant_phone=loan_app.applicant_phone,
            loan_amount=loan_app.loan_amount,
            loan_type=loan_app.loan_type,
            loan_term_months=loan_app.loan_term_months,
            annual_income=loan_app.annual_income,
            employment_status=loan_app.employment_status,
            years_employed=loan_app.years_employed,
            credit_score=loan_app.credit_score,
            existing_debt=loan_app.existing_debt,
            started_at=datetime.utcnow(),
            messages=[],
        )

        logger.info(f"Starting workflow for application {loan_app.application_id}")

        # Execute workflow graph
        try:
            graph = create_loan_approval_graph()
            result = graph.invoke(state)
            logger.info(f"Workflow completed: {result.get('reasoning')}")
        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}", exc_info=True)
            result = {
                "approved": False,
                "reasoning": f"Workflow error: {str(e)}",
                "risk_score": 1.0,
                "approval_probability": 0.0,
                "messages": [f"Workflow execution failed: {str(e)}"],
            }

        # Determine decision status from workflow result
        decision_status = DecisionStatus.APPROVED
        app_status = LoanStatus.APPROVED

        if not result.get("approved"):
            if "manual" in result.get("reasoning", "").lower() or "review" in result.get("reasoning", "").lower():
                decision_status = DecisionStatus.PENDING
                app_status = LoanStatus.UNDER_REVIEW
            else:
                decision_status = DecisionStatus.REJECTED
                app_status = LoanStatus.REJECTED

        # Create decision record
        decision = LoanDecision(
            decision_id=str(uuid4()),
            loan_application_id=loan_app.id,
            decision_status=decision_status.value,
            risk_score=result.get("risk_score", 0.5),
            approval_probability=result.get("approval_probability", 0.5),
            agent_analysis="\n".join(result.get("messages", [])),
            decision_made_by="multi_agent_workflow",
            decision_made_at=datetime.utcnow(),
        )
        db.add(decision)

        # Update application status
        loan_app.status = app_status.value
        loan_app.risk_score = result.get("risk_score", 0.5)
        loan_app.approval_probability = result.get("approval_probability", 0.5)
        loan_app.processed_at = datetime.utcnow()

        # Set approval/rejection reason
        if decision_status == DecisionStatus.APPROVED:
            loan_app.approval_reason = result.get("reasoning", "Approved by workflow")
        elif decision_status == DecisionStatus.REJECTED:
            loan_app.rejection_reason = result.get("reasoning", "Rejected by workflow")
        else:
            loan_app.agent_notes = result.get("reasoning", "Requires manual review")

        # Commit changes
        db.commit()

        logger.info(
            f"Application {loan_app.application_id} decision: {decision_status.value} "
            f"(risk: {result.get('risk_score', 0.5):.1f}, probability: {result.get('approval_probability', 0.5):.0%})"
        )

        return {
            "decision_status": decision_status.value,
            "risk_score": result.get("risk_score", 0.5),
            "approval_probability": result.get("approval_probability", 0.5),
            "reasoning": result.get("reasoning", ""),
            "audit_trail": result.get("messages", []),
            "workflow_result": result,
        }
