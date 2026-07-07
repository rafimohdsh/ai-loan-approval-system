# FastMCP Server - Complete Guide

## Overview

The FastMCP Server provides a comprehensive set of tools for AI agents to interact with the loan approval system. It offers tools for customer profile management, credit assessment, loan decision processing, and notifications.

## Architecture

```
FastMCP Server (Port 8001)
       ↓
Tool Categories:
  ├── Customer Tools (4 tools)
  ├── Credit Tools (4 tools)
  ├── Decision Tools (5 tools)
  ├── Notification Tools (6 tools)
  └── Loan Analysis Tools (3 tools)
       ↓
Backend Services (Database, Models)
       ↓
MySQL Database
```

## Tool Categories

### 1. Customer Tools (4)

Tools for managing customer profiles and information.

#### get_customer_profile
Retrieve complete customer profile with all information.

```json
{
  "customer_id": "CUST-001"
}
```

Returns customer details including personal info, employment, financial status, and credit information.

#### validate_customer_identity
Validate customer identity against stored information.

```json
{
  "customer_id": "CUST-001",
  "email": "john@example.com",
  "phone": "555-1234"
}
```

Returns validation results with matches on each field.

#### get_customer_applications
Get all loan applications for a customer.

```json
{
  "customer_id": "CUST-001"
}
```

Returns list of all applications with status, amounts, and risk scores.

#### update_customer_contact
Update customer contact information.

```json
{
  "customer_id": "CUST-001",
  "email": "newemail@example.com",
  "phone": "555-5678",
  "address": {
    "street": "456 Oak Ave",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90001"
  }
}
```

### 2. Credit Tools (4)

Tools for credit score analysis and creditworthiness assessment.

#### get_credit_score_details
Get comprehensive credit score analysis.

```json
{
  "credit_score": 750
}
```

Returns rating (Excellent/Very Good/Good/Fair/Poor), interest rate adjustments, and approval likelihood.

#### calculate_credit_risk_profile
Calculate comprehensive credit risk profile (0-100 scale).

```json
{
  "credit_score": 750,
  "credit_history_months": 120,
  "payment_history": "excellent",
  "accounts_in_good_standing": 5,
  "delinquencies": 0
}
```

#### get_credit_improvement_recommendations
Get recommendations to improve credit score.

```json
{
  "credit_score": 620
}
```

Returns tailored recommendations based on score and timeline for improvement.

#### assess_credit_worthiness
Assess overall creditworthiness (combines credit score, DTI, and history).

```json
{
  "credit_score": 750,
  "debt_to_income_ratio": 0.35,
  "credit_history_months": 120
}
```

Returns overall creditworthiness score (0-100) with recommendation.

### 3. Decision Tools (5)

Tools for managing loan decisions.

#### save_loan_decision
Save a new loan decision to the database.

```json
{
  "loan_application_id": 1,
  "decision_status": "approved",
  "risk_score": 0.25,
  "approval_probability": 0.92,
  "approved_amount": 50000.0,
  "approved_term_months": 60,
  "interest_rate": 6.5,
  "agent_analysis": "Applicant meets all criteria",
  "primary_reasons": ["good_income_to_debt", "stable_employment"],
  "decision_reason": "good_income_to_debt",
  "recommendation_confidence": 0.95
}
```

Returns decision ID and confirmation.

#### update_loan_decision
Update an existing decision.

```json
{
  "decision_id": "DEC-001",
  "decision_status": "approved",
  "interest_rate": 6.75
}
```

#### get_decision_by_application
Get decision for a specific application.

```json
{
  "application_id": 1
}
```

#### get_decisions_by_status
Get decisions filtered by status.

```json
{
  "status": "approved",
  "limit": 50
}
```

#### export_decision_report
Export decision report with optional filters.

```json
{
  "start_date": "2024-07-01T00:00:00",
  "end_date": "2024-07-31T23:59:59",
  "status_filter": "approved"
}
```

### 4. Notification Tools (6)

Tools for sending notifications and managing communication.

#### send_decision_notification
Send decision notification to customer.

```json
{
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "application_id": "LOAN-001",
  "decision_status": "approved",
  "loan_amount": 50000.0,
  "approved_amount": 50000.0,
  "interest_rate": 6.5,
  "reason": "Strong credit profile and income"
}
```

#### send_application_status_update
Send status update notification.

```json
{
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "application_id": "LOAN-001",
  "status": "under_review",
  "message": "Your application is being reviewed by our team"
}
```

#### send_alert_to_support
Send alert to support team.

```json
{
  "alert_type": "manual_review_needed",
  "application_id": "LOAN-001",
  "message": "Application requires additional review",
  "severity": "warning"
}
```

#### create_notification_log
Create a notification log entry.

```json
{
  "notification_type": "email",
  "recipient": "john@example.com",
  "content": "Your loan decision notification",
  "status": "pending"
}
```

#### get_notification_history
Get notification history for application.

```json
{
  "application_id": "LOAN-001",
  "notification_type": "email",
  "limit": 50
}
```

#### send_batch_notifications
Send multiple notifications at once.

```json
{
  "notifications": [
    {
      "recipient_email": "john@example.com",
      "recipient_name": "John Doe",
      "application_id": "LOAN-001",
      "decision_status": "approved",
      "loan_amount": 50000
    },
    {
      "recipient_email": "jane@example.com",
      "recipient_name": "Jane Smith",
      "application_id": "LOAN-002",
      "decision_status": "rejected",
      "loan_amount": 75000,
      "reason": "Insufficient income"
    }
  ]
}
```

### 5. Loan Analysis Tools (3)

Core tools for financial analysis and decision making.

#### analyze_financial_profile
Analyze applicant's financial profile.

```json
{
  "annual_income": 75000.0,
  "existing_debt": 15000.0,
  "loan_amount": 50000.0
}
```

#### calculate_risk_factors
Calculate risk factors based on credit and employment.

```json
{
  "credit_score": 750,
  "years_employed": 5.0,
  "debt_to_income_ratio": 0.35,
  "employment_stability": "stable"
}
```

#### generate_approval_decision
Generate final approval decision.

```json
{
  "risk_score": 80.0,
  "financial_health": 85.0,
  "compliance_status": "approved"
}
```

## Running the MCP Server

### Configuration

Set in `.env`:
```env
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
```

### Start Server

```bash
python -m mcp.server
```

Server runs on `http://localhost:8001`

### Verify Server

```bash
curl http://localhost:8001/tools
```

## Tool Categories Summary

| Category | Tools | Purpose |
|----------|-------|---------|
| Customer | 4 | Profile retrieval, identity validation, contact updates |
| Credit | 4 | Credit score analysis, risk assessment, recommendations |
| Decision | 5 | Decision CRUD operations, status filtering, reporting |
| Notification | 6 | Email notifications, alerts, notification logging |
| Loan Analysis | 3 | Financial analysis, risk calculation, decision generation |

## Data Flow

```
Agent Request
    ↓
MCP Server (server.py)
    ↓
Tool Router (call_tool)
    ↓
Tool Implementation (customer_tools.py, credit_tools.py, etc.)
    ↓
Database Layer (SessionLocal, DatabaseService)
    ↓
MySQL Database
    ↓
Response to Agent (JSON)
```

## Error Handling

All tools include error handling:

```python
try:
    # Execute tool
    result = some_tool(...)
except Exception as e:
    logger.error(f"Error: {str(e)}")
    raise
```

Errors are logged and returned as exceptions for client handling.

## Audit Trail

All tools automatically create audit log entries:

- Customer updates logged with old/new values
- Decisions logged with full analysis
- Notifications tracked for compliance
- All actions include user/agent identification

## Security Features

✅ Database connection pooling  
✅ SQL injection prevention (parameterized queries)  
✅ Audit trail for all changes  
✅ Session management  
✅ Error logging without sensitive data exposure  

## Performance Characteristics

- Connection pooling: 10 + 20 overflow
- Average response time: < 500ms
- Batch operations: Up to 1000 notifications
- Database queries optimized with indexes
- JSON serialization for responses

## Usage Examples

### Customer Profile Retrieval

```python
from mcp.tools import get_customer_profile

profile = get_customer_profile(customer_id="CUST-001")
print(profile["financial"]["annual_income"])
```

### Credit Assessment

```python
from mcp.tools import assess_credit_worthiness

assessment = assess_credit_worthiness(
    credit_score=750,
    debt_to_income_ratio=0.35,
    credit_history_months=120
)
print(assessment["overall_creditworthiness_score"])
```

### Decision Management

```python
from mcp.tools import save_loan_decision

decision = save_loan_decision(
    loan_application_id=1,
    decision_status="approved",
    risk_score=0.25,
    approval_probability=0.92
)
print(decision["decision_id"])
```

### Notifications

```python
from mcp.tools import send_decision_notification

result = send_decision_notification(
    customer_email="john@example.com",
    customer_name="John Doe",
    application_id="LOAN-001",
    decision_status="approved",
    loan_amount=50000.0,
    approved_amount=50000.0,
    interest_rate=6.5
)
```

## Tool Statistics

| Category | Tools | Methods | Lines |
|----------|-------|---------|-------|
| Customer | 4 | 5 | 180 |
| Credit | 4 | 4 | 250 |
| Decision | 5 | 7 | 280 |
| Notification | 6 | 8 | 320 |
| Loan Analysis | 3 | 3 | 120 |
| **Total** | **22** | **27** | **~1150** |

## File Structure

```
mcp/
├── server.py              # FastMCP server implementation
├── __init__.py
└── tools/
    ├── __init__.py        # Tool exports
    ├── loan_tools.py      # Loan analysis (existing)
    ├── customer_tools.py  # Customer tools (new)
    ├── credit_tools.py    # Credit tools (new)
    ├── decision_tools.py  # Decision tools (new)
    └── notification_tools.py # Notifications (new)
```

## API Response Format

All responses are JSON:

```json
{
  "success": true,
  "data": {...},
  "timestamp": "2024-07-02T12:00:00Z"
}
```

On error:
```json
{
  "error": "Error message",
  "timestamp": "2024-07-02T12:00:00Z"
}
```

## Integration with AI Agents

The MCP server is designed for AI agent integration:

1. **Agent Discovery** - `/tools` endpoint lists all available tools
2. **Tool Execution** - `POST /tool` with tool name and arguments
3. **Schema Validation** - Input schemas prevent invalid calls
4. **Error Handling** - Consistent error responses for debugging

## Monitoring & Logging

All operations are logged:

```
[INFO] Customer profile retrieved for CUST-001
[INFO] Decision saved DEC-001 for application LOAN-001
[WARNING] High severity alert ALERT-001 created
[ERROR] Database error in save_loan_decision: Connection timeout
```

Log location: `logs/app.log`

## Troubleshooting

**Connection Error**
```
Error: Cannot connect to database
Solution: Verify DATABASE_URL in .env and MySQL is running
```

**Tool Not Found**
```
Error: Unknown tool: save_customer
Solution: Check tool name spelling and ensure it's exported from __init__.py
```

**Timeout**
```
Error: Request timeout
Solution: Check database connection pool status, may need to increase pool size
```

## Next Steps

1. ✅ Start MCP server
2. ✅ List available tools
3. ✅ Integrate with AI agents
4. ✅ Monitor logs and audit trails
5. ✅ Scale based on usage

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** 2024-07-02  
**Tools:** 22 | **Methods:** 27 | **Code:** ~1150 lines
