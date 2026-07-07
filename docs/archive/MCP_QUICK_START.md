# FastMCP Server - Quick Start

## 🚀 Start Server

```bash
python -m mcp.server
```

Server runs on `http://localhost:8001`

## 📋 Available Tools (22 Total)

### Customer Tools (4)
```
✓ get_customer_profile          - Retrieve customer profile
✓ validate_customer_identity    - Validate customer info
✓ get_customer_applications     - Get customer's applications
✓ update_customer_contact       - Update contact info
```

### Credit Tools (4)
```
✓ get_credit_score_details              - Credit score analysis
✓ calculate_credit_risk_profile         - Risk assessment (0-100)
✓ get_credit_improvement_recommendations - Improvement advice
✓ assess_credit_worthiness              - Overall creditworthiness
```

### Decision Tools (5)
```
✓ save_loan_decision          - Save new decision
✓ update_loan_decision        - Update decision
✓ get_decision_by_application - Get decision for app
✓ get_decisions_by_status     - Filter by status
✓ export_decision_report      - Generate report
```

### Notification Tools (6)
```
✓ send_decision_notification      - Email decision
✓ send_application_status_update  - Status email
✓ send_alert_to_support          - Support alert
✓ create_notification_log        - Log notification
✓ get_notification_history       - Get history
✓ send_batch_notifications       - Batch send
```

### Loan Analysis Tools (3)
```
✓ analyze_financial_profile    - Analyze finances
✓ calculate_risk_factors       - Calculate risk
✓ generate_approval_decision   - Generate decision
```

## 💻 Quick Examples

### Get Customer Profile
```bash
curl -X POST http://localhost:8001/tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_customer_profile",
    "arguments": {"customer_id": "CUST-001"}
  }'
```

### Save Loan Decision
```bash
curl -X POST http://localhost:8001/tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "save_loan_decision",
    "arguments": {
      "loan_application_id": 1,
      "decision_status": "approved",
      "risk_score": 0.25,
      "approval_probability": 0.92
    }
  }'
```

### Send Decision Notification
```bash
curl -X POST http://localhost:8001/tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "send_decision_notification",
    "arguments": {
      "customer_email": "john@example.com",
      "customer_name": "John Doe",
      "application_id": "LOAN-001",
      "decision_status": "approved",
      "loan_amount": 50000,
      "approved_amount": 50000,
      "interest_rate": 6.5
    }
  }'
```

## 🔍 List All Tools

```bash
curl http://localhost:8001/tools
```

## 📊 Tool Reference Quick Table

| Category | Tool | Usage |
|----------|------|-------|
| Customer | get_customer_profile | Profile retrieval |
| Customer | validate_customer_identity | ID validation |
| Customer | get_customer_applications | List applications |
| Customer | update_customer_contact | Update contact |
| Credit | get_credit_score_details | Score analysis |
| Credit | calculate_credit_risk_profile | Risk profile |
| Credit | get_credit_improvement_recommendations | Improvement tips |
| Credit | assess_credit_worthiness | Overall assessment |
| Decision | save_loan_decision | Create decision |
| Decision | update_loan_decision | Modify decision |
| Decision | get_decision_by_application | Retrieve decision |
| Decision | get_decisions_by_status | Filter decisions |
| Decision | export_decision_report | Generate report |
| Notification | send_decision_notification | Send email |
| Notification | send_application_status_update | Status email |
| Notification | send_alert_to_support | Support alert |
| Notification | create_notification_log | Log entry |
| Notification | get_notification_history | View history |
| Notification | send_batch_notifications | Bulk send |
| Analysis | analyze_financial_profile | Financial analysis |
| Analysis | calculate_risk_factors | Risk calculation |
| Analysis | generate_approval_decision | Decision generation |

## 🔐 Configuration

Update `.env`:
```env
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
```

## ✅ Verify Installation

```bash
# Test server is running
curl http://localhost:8001/health

# List available tools
curl http://localhost:8001/tools | jq '.[].name'
```

## 📝 Tool Input Examples

### Customer Profile
```json
{
  "customer_id": "CUST-001"
}
```

### Credit Assessment
```json
{
  "credit_score": 750,
  "credit_history_months": 120,
  "debt_to_income_ratio": 0.35
}
```

### Save Decision
```json
{
  "loan_application_id": 1,
  "decision_status": "approved",
  "risk_score": 0.25,
  "approval_probability": 0.92,
  "approved_amount": 50000,
  "approved_term_months": 60,
  "interest_rate": 6.5
}
```

### Send Notification
```json
{
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "application_id": "LOAN-001",
  "decision_status": "approved",
  "loan_amount": 50000,
  "approved_amount": 50000,
  "interest_rate": 6.5
}
```

## 🎯 Common Workflows

### Approve Loan
1. `assess_credit_worthiness` - Check creditworthiness
2. `analyze_financial_profile` - Analyze finances
3. `calculate_risk_factors` - Calculate risk
4. `save_loan_decision` - Save decision
5. `send_decision_notification` - Notify customer

### Review Application
1. `get_customer_profile` - Get applicant info
2. `get_customer_applications` - Get history
3. `calculate_credit_risk_profile` - Risk analysis
4. `get_credit_improvement_recommendations` - Get advice

### Reject Application
1. `save_loan_decision` - Save rejection decision
2. `send_decision_notification` - Notify customer
3. `send_alert_to_support` - Alert support if needed

## 📊 Response Examples

### Success Response
```json
{
  "success": true,
  "data": {...},
  "timestamp": "2024-07-02T12:00:00Z"
}
```

### Error Response
```json
{
  "error": "Customer not found",
  "timestamp": "2024-07-02T12:00:00Z"
}
```

## 🚨 Common Errors

| Error | Solution |
|-------|----------|
| Connection refused | Start server first |
| Tool not found | Check tool name spelling |
| Missing required field | Verify all required parameters |
| Invalid credit score | Credit score must be 300-850 |
| Database error | Check MySQL connection |

## 📚 Documentation

- **Complete Guide:** [MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)
- **Tool Implementation:** `/mcp/tools/`
- **Server Code:** `/mcp/server.py`

## 💡 Tips

- Use `/tools` endpoint to see all available tools
- All responses are JSON
- Each tool has comprehensive error handling
- Audit logs track all operations
- Batch operations available for notifications

## 🎓 Integration Example

```python
import requests
import json

# Configuration
MCP_SERVER = "http://localhost:8001"

# Get customer profile
response = requests.post(f"{MCP_SERVER}/tool", json={
    "name": "get_customer_profile",
    "arguments": {"customer_id": "CUST-001"}
})

profile = response.json()
print(f"Customer: {profile['name']}")
print(f"Income: ${profile['financial']['annual_income']}")

# Check creditworthiness
creditworthiness = requests.post(f"{MCP_SERVER}/tool", json={
    "name": "assess_credit_worthiness",
    "arguments": {
        "credit_score": profile["credit"]["score"],
        "debt_to_income_ratio": 0.35,
        "credit_history_months": profile["credit"]["history_months"]
    }
}).json()

print(f"Creditworthiness: {creditworthiness['overall_assessment']}")
```

---

**Server:** Active on port 8001  
**Tools:** 22 available  
**Status:** ✅ Ready to use
