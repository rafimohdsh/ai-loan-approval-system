# Database Quick Reference Card

## 🚀 Quick Start (30 seconds)

```python
from backend.app.database import SessionLocal, DatabaseService, init_db

# Initialize
init_db()

# Create service
db = SessionLocal()
db = DatabaseService(db)

# Create customer
customer = db.customers.create({
    "customer_id": "CUST-001",
    "first_name": "John",
    "email": "john@example.com",
    # ... other fields
})

# Log action
db.log_audit_action(
    entity_type="customer",
    entity_id=customer.customer_id,
    action_type="create",
    user_id="admin",
)
```

## 📊 4 Core Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **customers** | Applicant info | customer_id, email, ssn, credit_score |
| **loan_applications** | Loan requests | application_id, loan_amount, status |
| **loan_decisions** | Approvals/rejections | decision_id, decision_status, risk_score |
| **audit_logs** | Action tracking | audit_id, entity_type, action_type, user_id |

## 🔧 CLI Commands (30 seconds setup)

```bash
# Initialize
python -m backend.app.database.cli init

# Health check
python -m backend.app.database.cli status

# See statistics
python -m backend.app.database.cli stats

# Verify schema
python -m backend.app.database.cli verify
```

## 💾 Repository Methods

### Customers
```python
db.customers.create(data)                    # Create
db.customers.get(id)                         # Get by ID
db.customers.get_by_email(email)             # Get by email
db.customers.get_by_customer_id(cust_id)     # Get by customer_id
db.customers.search("John")                  # Search by name
db.customers.get_active_customers()          # Get all active
db.customers.update(id, data)                # Update
db.customers.delete(id)                      # Delete
```

### Loan Applications
```python
db.loan_applications.create(data)                        # Create
db.loan_applications.get_by_application_id(app_id)      # Get by ID
db.loan_applications.get_pending_applications()         # Get pending
db.loan_applications.get_recent_applications(days=30)   # Last N days
db.loan_applications.get_high_value_applications(50000) # > amount
db.loan_applications.get_by_status("pending")           # By status
```

### Loan Decisions
```python
db.loan_decisions.create(data)                          # Create
db.loan_decisions.get_by_decision_id(dec_id)            # Get by ID
db.loan_decisions.get_by_application_id(app_id)         # Get for app
db.loan_decisions.get_by_status("approved")             # By status
db.loan_decisions.get_high_risk(threshold=0.7)          # High risk
db.loan_decisions.get_requiring_review()                # Need review
```

### Audit Logs
```python
db.audit_logs.get_by_entity("customer", "CUST-001")     # Entity history
db.audit_logs.get_by_user("admin-001")                  # User activity
db.audit_logs.get_by_action_type("approve")             # By action
db.audit_logs.get_recent(days=7)                        # Last N days
db.audit_logs.log_action(...)                           # Log action
```

## 📈 Service Methods

```python
# Log action
db.log_audit_action(
    entity_type="customer",
    entity_id="CUST-001",
    action_type="update",
    user_id="admin",
    old_values={"income": 50000},
    new_values={"income": 60000},
)

# Get history
history = db.get_entity_history("customer", "CUST-001")

# Get user activity
activity = db.get_user_activity("admin-001")

# Get compliance report
report = db.get_compliance_report(days=30)

# Export audit logs
logs = db.export_audit_logs(start_date, end_date)
```

## 🔍 Common Queries

```python
# Find customer by email
customer = db.customers.get_by_email("john@example.com")

# Get all pending loans
pending = db.loan_applications.get_pending_applications()

# Get loans from last week
recent = db.loan_applications.get_recent_applications(days=7)

# Find high-risk decisions
risky = db.loan_decisions.get_high_risk(threshold=0.8)

# Get all approvals from today
approvals = db.audit_logs.get_by_action_type("approve")

# Search for customer
results = db.customers.search("John Smith")

# Get compliance report
report = db.get_compliance_report(days=90)
```

## 🏗️ File Locations

```
Models:         /backend/app/models/
  ├── customer.py
  ├── loan_application.py
  ├── loan_decision.py
  └── audit_log.py

Database:       /backend/app/database/
  ├── connection.py
  ├── base.py
  ├── repositories.py
  ├── service.py
  ├── cli.py
  └── example_usage.py

Schemas:        /backend/app/schemas/
  ├── customer.py
  ├── loan_decision.py
  └── audit_log.py

Docs:
  ├── DATABASE_GUIDE.md
  ├── DATABASE_IMPLEMENTATION_SUMMARY.md
  ├── DATABASE_SETUP_CHECKLIST.md
  └── QUICK_DATABASE_REFERENCE.md
```

## 🎯 Use Cases

### Create Customer
```python
customer = db.customers.create({
    "customer_id": "CUST-001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "date_of_birth": datetime(1990, 1, 1),
    "ssn": "123-45-6789",
    "address": "123 Main St",
    "city": "NYC",
    "state": "NY",
    "zip_code": "10001",
    "employment_status": "Employed",
    "annual_income": 75000.0,
    "credit_score": 750,
})
```

### Create Loan Application
```python
app = db.loan_applications.create({
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
})
```

### Create Loan Decision
```python
decision = db.loan_decisions.create({
    "decision_id": "DEC-001",
    "loan_application_id": app.id,
    "decision_status": "approved",
    "decision_reason": "good_income_to_debt",
    "risk_score": 0.25,
    "approval_probability": 0.92,
    "approved_amount": 50000.0,
    "approved_term_months": 60,
    "interest_rate": 6.5,
    "agent_analysis": "Applicant meets all criteria",
})
```

## 📋 Environment Setup

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/loan_approval_db
DEBUG=False
LOG_LEVEL=INFO
```

## ⚡ Performance Tips

1. **Use indexes** - All frequent queries are indexed
2. **Paginate** - Use limit/offset for large queries
3. **Pool connections** - Pool size=10, overflow=20
4. **Batch operations** - Group related operations
5. **Clean old logs** - Run cleanup periodically

## 🔒 Security

- ✅ Parameterized queries (SQL injection prevention)
- ✅ Complete audit trail
- ✅ User/agent tracking
- ✅ Action logging
- ✅ Pydantic validation

## 📚 Full Documentation

- **DATABASE_GUIDE.md** - Complete reference (2500+ lines)
- **DATABASE_IMPLEMENTATION_SUMMARY.md** - Overview
- **DATABASE_SETUP_CHECKLIST.md** - Setup guide
- **example_usage.py** - Working code examples

## 🆘 Troubleshooting

```bash
# Test connection
python -m backend.app.database.cli test-connection

# Check health
python -m backend.app.database.cli status

# Verify schema
python -m backend.app.database.cli verify

# View statistics
python -m backend.app.database.cli stats
```

## 🎓 Learning Path

1. Read **QUICK_DATABASE_REFERENCE.md** (this file) - 5 min
2. Read **DATABASE_GUIDE.md** - 30 min
3. Run **example_usage.py** - 10 min
4. Try creating records yourself - 30 min
5. Review **repositories.py** source - 30 min

---

**Everything you need is here.** Start with initialization, then use the repositories to manage data. Full docs available in DATABASE_GUIDE.md.
