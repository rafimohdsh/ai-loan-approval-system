"""
Example usage of the database layer.
This file demonstrates how to use the database models, repositories, and services.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database import from ..models import     Customer, LoanApplication, LoanDecision, AuditLog,
    LoanStatus, DecisionStatus
)


def example_create_customer():
    """Example: Create a customer"""
    db = SessionLocal()
    db_service = DatabaseService(db)

    # Create customer
    customer_data = {
        "customer_id": "CUST-20240702-001",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@example.com",
        "phone": "555-123-4567",
        "date_of_birth": datetime(1985, 3, 15),
        "ssn": "123-45-6789",
        "address": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "USA",
        "employment_status": "Employed",
        "occupation": "Software Engineer",
        "employer_name": "Tech Company Inc",
        "years_employed": 7.5,
        "annual_income": 120000.0,
        "monthly_expenses": 4500.0,
        "credit_score": 760,
        "credit_history_months": 120,
        "total_debt": 25000.0,
        "total_assets": 250000.0,
        "notes": "Good credit history, stable employment",
    }

    customer = db_service.customers.create(customer_data)

    # Log the creation
    db_service.log_audit_action(
        entity_type="customer",
        entity_id=customer.customer_id,
        action_type="create",
        user_id="system",
        user_name="System",
        new_values=customer_data,
        action_reason="New customer registration",
    )

    db.close()
    return customer


def example_create_loan_application():
    """Example: Create a loan application"""
    db = SessionLocal()
    db_service = DatabaseService(db)

    # Get customer
    customer = db_service.customers.get_by_email("john.smith@example.com")

    if not customer:
        print("Customer not found")
        db.close()
        return

    # Create loan application
    app_data = {
        "application_id": "LOAN-20240702-001",
        "applicant_name": customer.first_name + " " + customer.last_name,
        "applicant_email": customer.email,
        "applicant_phone": customer.phone,
        "loan_amount": 50000.0,
        "loan_type": "Personal",
        "loan_term_months": 60,
        "annual_income": customer.annual_income,
        "employment_status": customer.employment_status,
        "years_employed": customer.years_employed,
        "credit_score": customer.credit_score,
        "existing_debt": customer.total_debt,
        "status": "pending",
    }

    app = db_service.loan_applications.create(app_data)

    # Log the creation
    db_service.log_audit_action(
        entity_type="loan_application",
        entity_id=app.application_id,
        action_type="create",
        user_id="system",
        user_name="System",
        new_values=app_data,
        action_reason="Loan application submitted",
    )

    db.close()
    return app


def example_create_loan_decision():
    """Example: Create a loan decision"""
    db = SessionLocal()
    db_service = DatabaseService(db)

    # Get loan application
    app = db_service.loan_applications.get_by_application_id("LOAN-20240702-001")

    if not app:
        print("Application not found")
        db.close()
        return

    # Create decision
    decision_data = {
        "decision_id": "DEC-20240702-001",
        "loan_application_id": app.id,
        "decision_status": "approved",
        "decision_reason": "good_income_to_debt",
        "risk_score": 0.25,
        "approval_probability": 0.92,
        "approved_amount": 50000.0,
        "approved_term_months": 60,
        "interest_rate": 6.5,
        "agent_analysis": (
            "Applicant meets approval criteria: "
            "Strong credit score (760), Stable employment (7.5 years), "
            "Good income-to-debt ratio (4.8x)"
        ),
        "primary_reasons": '["good_income_to_debt", "stable_employment", "excellent_credit"]',
        "secondary_factors": '["long_credit_history", "low_risk_profile"]',
        "recommendation_confidence": 0.95,
        "decision_made_by": "AI-Agent-LoanAnalyzer-v1",
    }

    decision = db_service.loan_decisions.create(decision_data)

    # Update application status
    db_service.loan_applications.update(app.id, {
        "status": "approved",
        "agent_notes": "AI agent analysis completed - Approved",
        "risk_score": 0.25,
        "approval_probability": 0.92,
        "processed_at": datetime.utcnow(),
    })

    # Log the decision
    db_service.log_audit_action(
        entity_type="loan_decision",
        entity_id=decision.decision_id,
        action_type="approve",
        user_id="AI-Agent-LoanAnalyzer-v1",
        user_role="agent",
        new_values=decision_data,
        action_reason="Loan approved by AI analysis",
        agent_notes=decision.agent_analysis,
    )

    # Log application status update
    db_service.log_audit_action(
        entity_type="loan_application",
        entity_id=app.application_id,
        action_type="update",
        user_id="AI-Agent-LoanAnalyzer-v1",
        user_role="agent",
        old_values={"status": "pending"},
        new_values={"status": "approved"},
        action_reason="Application approved by AI agent",
    )

    db.close()
    return decision


def example_query_operations():
    """Example: Various query operations"""
    db = SessionLocal()
    db_service = DatabaseService(db)

    print("\n=== Query Examples ===\n")

    # 1. Get pending applications
    print("1. Pending Applications:")
    pending = db_service.loan_applications.get_pending_applications(limit=5)
    for app in pending:
        print(f"  - {app.application_id}: ${app.loan_amount}")

    # 2. Get recent applications (last 7 days)
    print("\n2. Recent Applications (last 7 days):")
    recent = db_service.loan_applications.get_recent_applications(days=7, limit=5)
    for app in recent:
        print(f"  - {app.application_id}: {app.created_at.date()}")

    # 3. Get high-value applications
    print("\n3. High-value Applications (> $40,000):")
    high_value = db_service.loan_applications.get_high_value_applications(
        min_amount=40000.0, limit=5
    )
    for app in high_value:
        print(f"  - {app.application_id}: ${app.loan_amount}")

    # 4. Get customer audit history
    print("\n4. Customer Audit History:")
    history = db_service.audit_logs.get_by_entity("customer", "CUST-20240702-001", limit=5)
    for log in history:
        print(f"  - {log.action_type}: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    # 5. Get high-risk decisions
    print("\n5. High-risk Decisions (risk_score > 0.7):")
    high_risk = db_service.loan_decisions.get_high_risk(threshold=0.7, limit=5)
    for decision in high_risk:
        print(f"  - {decision.decision_id}: Risk={decision.risk_score}")

    # 6. Search customers by name
    print("\n6. Search Customers (name='John'):")
    results = db_service.customers.search("John")
    for customer in results:
        print(f"  - {customer.first_name} {customer.last_name}: {customer.email}")

    # 7. Get compliance report
    print("\n7. Compliance Report (last 30 days):")
    report = db_service.get_compliance_report(days=30)
    print(f"  Total Actions: {report['total_actions']}")
    print(f"  Actions by Type: {report['by_action_type']}")
    print(f"  Failed Actions: {len(report['failed_actions'])}")
    print(f"  Sensitive Actions: {len(report['sensitive_actions'])}")

    db.close()


def example_transaction_handling():
    """Example: Transaction handling with rollback"""
    db = SessionLocal()
    db_service = DatabaseService(db)

    try:
        # Create customer
        customer_data = {
            "customer_id": "CUST-20240702-002",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone": "555-987-6543",
            "date_of_birth": datetime(1990, 6, 20),
            "ssn": "987-65-4321",
            "address": "456 Oak Avenue",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "employment_status": "Employed",
            "annual_income": 95000.0,
            "credit_score": 720,
        }

        customer = db_service.customers.create(customer_data)
        print(f"Customer created: {customer.customer_id}")

        # Log the action
        db_service.log_audit_action(
            entity_type="customer",
            entity_id=customer.customer_id,
            action_type="create",
            user_id="admin",
            new_values=customer_data,
        )

        db_service.commit()
        print("Transaction committed successfully")

    except Exception as e:
        db_service.rollback()
        print(f"Transaction rolled back: {str(e)}")

    finally:
        db.close()


def example_export_audit_logs():
    """Example: Export audit logs for compliance"""
    db = SessionLocal()
    db_service = DatabaseService(db)

    # Get audit logs from last 7 days
    start_date = datetime.utcnow() - timedelta(days=7)
    end_date = datetime.utcnow()

    logs = db_service.export_audit_logs(
        start_date=start_date,
        end_date=end_date,
        entity_type="loan_decision",
        action_type="approve",
    )

    print(f"\n=== Audit Log Export ===")
    print(f"Period: {start_date.date()} to {end_date.date()}")
    print(f"Total Records: {len(logs)}\n")

    for log in logs:
        print(f"Audit ID: {log.audit_id}")
        print(f"Action: {log.action_type} on {log.entity_type}:{log.entity_id}")
        print(f"User: {log.user_name} ({log.user_id})")
        print(f"Timestamp: {log.timestamp}")
        print(f"Status: {log.status}")
        print("-" * 50)

    db.close()


def main():
    """Run all examples"""
    print("Database Layer Examples\n")

    # Initialize database
    print("Initializing database...")
    init_db()
    print("✓ Database initialized\n")

    # Run examples
    print("Creating customer...")
    customer = example_create_customer()
    print(f"✓ Customer created: {customer.customer_id}\n")

    print("Creating loan application...")
    app = example_create_loan_application()
    print(f"✓ Application created: {app.application_id}\n")

    print("Creating loan decision...")
    decision = example_create_loan_decision()
    print(f"✓ Decision created: {decision.decision_id}\n")

    # Query examples
    example_query_operations()

    # Transaction example
    print("\n=== Transaction Handling Example ===")
    example_transaction_handling()

    # Export example
    example_export_audit_logs()

    print("\n✓ All examples completed")


if __name__ == "__main__":
    main()
