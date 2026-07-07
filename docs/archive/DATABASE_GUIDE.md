# Database Layer - Complete Guide

## Overview

The database layer for the Agentic Loan Approval System is built on **SQLAlchemy** with **MySQL** as the backend. It provides:

- **4 main tables**: Customers, Loan Applications, Loan Decisions, and Audit Logs
- **Repository pattern** for data access
- **Service layer** for business logic
- **Comprehensive audit trail** for compliance
- **Full-text search and filtering** capabilities

## Database Schema

### 1. Customers Table (`customers`)

Stores customer/applicant information.

**Fields:**
- `customer_id` (PK) - Unique customer identifier
- `first_name`, `last_name` - Personal information
- `email` (UNIQUE) - Contact email
- `phone` - Phone number
- `date_of_birth` - Date of birth
- `ssn` (UNIQUE) - Social Security Number
- `address`, `city`, `state`, `zip_code` - Address information
- `employment_status` - Employment status
- `occupation`, `employer_name` - Employment details
- `years_employed` - Years at current employer
- `annual_income` - Annual income
- `monthly_expenses` - Monthly expenses
- `credit_score` - Credit score
- `credit_history_months` - Months of credit history
- `total_debt` - Total debt amount
- `total_assets` - Total assets
- `is_active` - Account status
- `created_at`, `updated_at` - Timestamps

**Indexes:**
- customer_id, email, phone, ssn
- Composite: (email, phone), (ssn, first_name, last_name)

### 2. Loan Applications Table (`loan_applications`)

Loan application records with applicant financial data.

**Fields:**
- `application_id` (UNIQUE) - Application identifier
- `applicant_name`, `applicant_email`, `applicant_phone` - Applicant contact
- `loan_amount` - Requested loan amount
- `loan_type` - Type of loan (Personal, Home, Auto, etc.)
- `loan_term_months` - Loan term in months
- `annual_income` - Annual income
- `employment_status` - Employment status
- `years_employed` - Years employed
- `credit_score` - Credit score
- `existing_debt` - Existing debt
- `status` - Application status (PENDING, UNDER_REVIEW, APPROVED, REJECTED, WITHDRAWN)
- `agent_notes` - Notes from AI agent
- `approval_reason` - Reason for approval
- `rejection_reason` - Reason for rejection
- `risk_score` - Risk score (0.0-1.0)
- `approval_probability` - Approval probability (0.0-1.0)
- `processed_at` - Date processed
- `created_at`, `updated_at` - Timestamps

**Indexes:**
- application_id, applicant_email, status
- Composite: (applicant_email, status)

### 3. Loan Decisions Table (`loan_decisions`)

Loan approval/rejection decisions with risk analysis.

**Fields:**
- `decision_id` (UNIQUE) - Decision identifier
- `loan_application_id` (FK) - Reference to loan application
- `decision_status` - Status (APPROVED, REJECTED, CONDITIONAL, PENDING)
- `decision_reason` - Reason for decision (enum)
- `risk_score` - Risk score (0.0-1.0)
- `approval_probability` - Approval probability (0.0-1.0)
- `approved_amount` - Approved loan amount
- `approved_term_months` - Approved term
- `interest_rate` - Interest rate offered
- `agent_analysis` - Detailed agent analysis
- `primary_reasons` - Primary decision reasons (JSON)
- `secondary_factors` - Secondary factors (JSON)
- `recommendation_confidence` - Confidence level
- `requires_manual_review` - Manual review flag
- `decision_made_by` - Agent/user who made decision
- `decision_made_at` - Decision timestamp
- `conditions_for_approval` - Conditions (if conditional)
- `next_review_date` - Next review date
- `created_at`, `updated_at` - Timestamps

**Indexes:**
- decision_id, loan_application_id, decision_status, risk_score

### 4. Audit Logs Table (`audit_logs`)

Complete audit trail of all system actions.

**Fields:**
- `audit_id` (UNIQUE) - Audit log identifier
- `entity_type` - Type of entity (CUSTOMER, LOAN_APPLICATION, LOAN_DECISION, SYSTEM)
- `entity_id` - ID of affected entity
- `action_type` - Action performed (CREATE, UPDATE, DELETE, VIEW, APPROVE, REJECT, etc.)
- `user_id` - User/agent who performed action
- `user_role` - User role (admin, agent, user, system)
- `user_name` - User name
- `old_values` - Previous values (JSON)
- `new_values` - New values (JSON)
- `changes_description` - Description of changes
- `action_reason` - Reason for action
- `agent_notes` - Additional notes
- `ip_address` - IP address
- `user_agent` - User agent string
- `status` - Action status (success, failed, partial)
- `error_message` - Error message if failed
- `timestamp` - Action timestamp
- `metadata` - Additional metadata (JSON)
- `related_audit_log_id` - Reference to related audit log

**Indexes:**
- audit_id, entity_type, entity_id, user_id, timestamp, action_type
- Composite: (entity_type, entity_id), (user_id, timestamp), (action_type, timestamp)

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Edit `.env` file:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/loan_approval_db
DEBUG=False
```

### 3. Initialize Database

```python
from backend.app.database import init_db

# Create all tables
init_db()
```

Or use CLI:

```bash
python -m backend.app.database.cli init
```

## Usage Examples

### Basic Setup

```python
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, DatabaseService
from backend.app.models import Customer, LoanApplication

# Get database session
db: Session = SessionLocal()

# Create database service
db_service = DatabaseService(db)

# Use repositories
customers = db_service.customers
loan_apps = db_service.loan_applications
decisions = db_service.loan_decisions
audit_logs = db_service.audit_logs
```

### Customer Operations

```python
# Create a customer
customer_data = {
    "customer_id": "CUST-001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "date_of_birth": datetime(1990, 1, 15),
    "ssn": "123-45-6789",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "employment_status": "Employed",
    "annual_income": 75000.0,
}

customer = customers.create(customer_data)

# Get customer by email
customer = customers.get_by_email("john@example.com")

# Search customers
results = customers.search("John")

# Get active customers
active = customers.get_active_customers()

# Update customer
updated = customers.update(customer.id, {"annual_income": 80000.0})

# Log the customer update
db_service.log_audit_action(
    entity_type="customer",
    entity_id=customer.customer_id,
    action_type="update",
    user_id="admin-001",
    user_name="Admin User",
    old_values={"annual_income": 75000.0},
    new_values={"annual_income": 80000.0},
    action_reason="Income verification updated",
)
```

### Loan Application Operations

```python
# Create loan application
app_data = {
    "application_id": "LOAN-001",
    "applicant_name": "John Doe",
    "applicant_email": "john@example.com",
    "applicant_phone": "555-1234",
    "loan_amount": 50000.0,
    "loan_type": "Personal",
    "loan_term_months": 60,
    "annual_income": 75000.0,
    "employment_status": "Employed",
    "years_employed": 5.0,
    "credit_score": 750,
    "existing_debt": 10000.0,
}

app = loan_apps.create(app_data)

# Get by application ID
app = loan_apps.get_by_application_id("LOAN-001")

# Get pending applications
pending = loan_apps.get_pending_applications()

# Get recent applications (last 30 days)
recent = loan_apps.get_recent_applications(days=30)

# Get high-value applications (> $100k)
high_value = loan_apps.get_high_value_applications(min_amount=100000.0)

# Update status
loan_apps.update(app.id, {
    "status": "under_review",
    "agent_notes": "AI agent analyzing application",
})
```

### Loan Decision Operations

```python
# Create loan decision
decision_data = {
    "decision_id": "DEC-001",
    "loan_application_id": app.id,
    "decision_status": "approved",
    "decision_reason": "good_income_to_debt",
    "risk_score": 0.25,
    "approval_probability": 0.95,
    "approved_amount": 50000.0,
    "approved_term_months": 60,
    "interest_rate": 6.5,
    "agent_analysis": "Applicant meets all criteria for approval",
}

decision = decisions.create(decision_data)

# Get decision by application
decision = decisions.get_by_application_id(app.id)

# Get approved decisions
approved = decisions.get_by_status("approved")

# Get high-risk decisions
high_risk = decisions.get_high_risk(threshold=0.7)

# Get decisions requiring manual review
review_needed = decisions.get_requiring_review()
```

### Audit Log Operations

```python
# Get audit history for an entity
history = audit_logs.get_by_entity("customer", "CUST-001")

# Get user activity
activity = audit_logs.get_by_user("admin-001")

# Get recent audit logs (last 7 days)
recent = audit_logs.get_recent(days=7)

# Get logs by date range
from datetime import datetime, timedelta
start = datetime.utcnow() - timedelta(days=30)
end = datetime.utcnow()
range_logs = audit_logs.get_by_date_range(start, end)

# Search by action type
approvals = audit_logs.get_by_action_type("approve")

# Generate compliance report
report = db_service.get_compliance_report(days=30)
print(f"Total actions: {report['total_actions']}")
print(f"Actions by type: {report['by_action_type']}")
print(f"Failed actions: {len(report['failed_actions'])}")
print(f"Sensitive actions: {len(report['sensitive_actions'])}")
```

## CLI Commands

### Database Initialization

```bash
# Initialize database and create all tables
python -m backend.app.database.cli init

# Test database connection
python -m backend.app.database.cli test-connection

# Check database health
python -m backend.app.database.cli status
```

### Schema Management

```bash
# Display schema information
python -m backend.app.database.cli schema-info

# Verify schema
python -m backend.app.database.cli verify

# Create indexes
python -m backend.app.database.cli create-indexes-cmd

# List all tables
python -m backend.app.database.cli tables
```

### Data Management

```bash
# Get table statistics
python -m backend.app.database.cli stats

# Backup a table
python -m backend.app.database.cli backup --table customers

# Clean up old audit logs
python -m backend.app.database.cli cleanup-audit-logs --days 90

# Reset database (drop and recreate)
python -m backend.app.database.cli reset

# Drop all tables (destructive!)
python -m backend.app.database.cli drop-all
```

## Migration Strategy

### Creating New Fields

1. Update model in `/backend/app/models/`
2. Update Pydantic schema in `/backend/app/schemas/`
3. Run `init_db()` to create new columns
4. Update repositories as needed

### Adding New Tables

1. Create model in `/backend/app/models/`
2. Add to `Base` by importing in models `__init__.py`
3. Create Pydantic schemas
4. Create repository in `repositories.py`
5. Add to `DatabaseService`
6. Run `init_db()` to create table

## Performance Optimization

### Indexing

All critical fields are indexed:
- Primary keys
- Foreign keys
- Frequently searched fields (email, customer_id, etc.)
- Status fields
- Timestamp fields

### Query Optimization

Use repositories for efficient queries:

```python
# Good - indexed query
customer = customers.get_by_email("john@example.com")

# Good - with pagination
recent = loan_apps.get_recent_applications(days=30)

# Better - filtered results
high_value = loan_apps.get_high_value_applications(min_amount=50000.0)
```

### Connection Pooling

SQLAlchemy handles connection pooling:
- Pool size: 10
- Max overflow: 20

Adjust in `connection.py` as needed.

## Backup & Recovery

### Manual Backup

```python
from backend.app.database.migrations import backup_table

# Backup a table
backup_name = backup_table("customers")
# Returns: customers_backup_20240702_120000
```

### Scheduled Cleanup

```python
from backend.app.database.migrations import cleanup_old_audit_logs

# Delete audit logs older than 90 days
deleted = cleanup_old_audit_logs(days=90)
```

## Compliance & Audit Trail

Every action is logged to `audit_logs`:

```python
# Automatic logging through DatabaseService
db_service.log_audit_action(
    entity_type="loan_application",
    entity_id="LOAN-001",
    action_type="approve",
    user_id="agent-001",
    user_name="AI Agent",
    action_reason="Meets approval criteria",
    agent_notes="Risk score: 0.25, Probability: 0.95"
)
```

### Compliance Reports

```python
# Generate compliance report
report = db_service.get_compliance_report(days=30)

# Export audit logs
logs = db_service.export_audit_logs(
    start_date=start,
    end_date=end,
    entity_type="loan_decision",
    action_type="approve"
)
```

## Troubleshooting

### Connection Issues

```bash
python -m backend.app.database.cli test-connection
```

### Schema Verification

```bash
python -m backend.app.database.cli verify
```

### Health Check

```bash
python -m backend.app.database.cli status
```

### Checking Table Statistics

```bash
python -m backend.app.database.cli stats
```

## Environment Variables

Required environment variables:

```env
DATABASE_URL=mysql+pymysql://user:password@host:port/dbname
```

Optional:

```env
DEBUG=False              # Enable SQLAlchemy echo
LOG_LEVEL=INFO          # Logging level
LOG_FILE=logs/app.log   # Log file path
```

## Dependencies

- **sqlalchemy** (2.0.23+) - ORM and query builder
- **pymysql** (1.1.0+) - MySQL driver
- **pydantic** (2.5.0+) - Data validation
- **python-dateutil** (2.8.2+) - Date utilities

## Best Practices

1. **Always use repositories** - Don't write raw SQL queries
2. **Use transactions** - Wrap related operations in `try/except`
3. **Log actions** - Use audit trail for all entity changes
4. **Validate input** - Use Pydantic schemas
5. **Close sessions** - Always close database sessions
6. **Backup regularly** - Schedule automated backups
7. **Monitor performance** - Check table statistics regularly
8. **Clean old data** - Periodically remove old audit logs

## Architecture Diagram

```
FastAPI Routes
      ↓
Pydantic Schemas (Validation)
      ↓
Service Layer (Business Logic)
      ↓
Repositories (Data Access)
      ↓
SQLAlchemy ORM Models
      ↓
MySQL Database
```

## Related Files

- `/backend/app/models/` - SQLAlchemy models
- `/backend/app/schemas/` - Pydantic validation schemas
- `/backend/app/database/connection.py` - Database connection setup
- `/backend/app/database/repositories.py` - Data access layer
- `/backend/app/database/service.py` - Business logic layer
- `/backend/app/database/migrations.py` - Schema management
- `/backend/app/database/cli.py` - CLI commands

## Support

For issues or questions:
1. Check this guide
2. Review model definitions in `/backend/app/models/`
3. Check repository implementations in `/backend/app/database/repositories.py`
4. Run health checks: `python -m backend.app.database.cli status`
