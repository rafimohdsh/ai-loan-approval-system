# FastAPI Endpoints - Complete Reference

## Overview

The loan approval system has 6 main endpoints integrated with all 4 agents (Profile, Risk, Decision, Notification).

## Required Endpoints (Main)

### 1. Apply Loan
**Endpoint:** `POST /loans/apply`

**Purpose:** Submit a new loan application

**Request:**
```json
{
  "applicant_name": "John Smith",
  "applicant_email": "john@example.com",
  "applicant_phone": "+1-555-1234",
  "loan_amount": 50000,
  "loan_type": "Personal",
  "loan_term_months": 60,
  "annual_income": 120000,
  "employment_status": "Permanent Full-time",
  "years_employed": 7,
  "credit_score": 750,
  "existing_debt": 500
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "application_id": "a1b2c3d4-e5f6-7890",
  "applicant_name": "John Smith",
  "applicant_email": "john@example.com",
  "applicant_phone": "+1-555-1234",
  "loan_amount": 50000,
  "loan_type": "Personal",
  "loan_term_months": 60,
  "annual_income": 120000,
  "employment_status": "Permanent Full-time",
  "years_employed": 7,
  "credit_score": 750,
  "existing_debt": 500,
  "status": "pending",
  "risk_score": null,
  "approval_probability": null,
  "created_at": "2024-07-02T10:00:00",
  "updated_at": "2024-07-02T10:00:00"
}
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/loans/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "John Smith",
    "applicant_email": "john@example.com",
    "applicant_phone": "+1-555-1234",
    "loan_amount": 50000,
    "loan_type": "Personal",
    "loan_term_months": 60,
    "annual_income": 120000,
    "employment_status": "Permanent Full-time",
    "years_employed": 7,
    "credit_score": 750,
    "existing_debt": 500
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/loans/apply",
    json={
        "applicant_name": "John Smith",
        "applicant_email": "john@example.com",
        "applicant_phone": "+1-555-1234",
        "loan_amount": 50000,
        "loan_type": "Personal",
        "loan_term_months": 60,
        "annual_income": 120000,
        "employment_status": "Permanent Full-time",
        "years_employed": 7,
        "credit_score": 750,
        "existing_debt": 500
    }
)
application = response.json()
print(f"Application ID: {application['application_id']}")
```

---

### 2. Loan Status
**Endpoint:** `GET /loans/status/{application_id}`

**Purpose:** Check the status of a loan application

**Parameters:**
- `application_id`: The application ID (path parameter)

**Response (200 OK):**
```json
{
  "id": 1,
  "application_id": "a1b2c3d4-e5f6-7890",
  "applicant_name": "John Smith",
  "applicant_email": "john@example.com",
  "applicant_phone": "+1-555-1234",
  "loan_amount": 50000,
  "loan_type": "Personal",
  "loan_term_months": 60,
  "annual_income": 120000,
  "employment_status": "Permanent Full-time",
  "years_employed": 7,
  "credit_score": 750,
  "existing_debt": 500,
  "status": "approved",
  "risk_score": 15.2,
  "approval_probability": 0.95,
  "created_at": "2024-07-02T10:00:00",
  "updated_at": "2024-07-02T10:15:00"
}
```

**cURL:**
```bash
curl -X GET "http://localhost:8000/loans/status/a1b2c3d4-e5f6-7890"
```

**Python:**
```python
import requests

response = requests.get(
    "http://localhost:8000/loans/status/a1b2c3d4-e5f6-7890"
)
status = response.json()
print(f"Status: {status['status']}")
print(f"Risk Score: {status['risk_score']}")
```

**Error Response (404):**
```json
{
  "detail": "Application not found"
}
```

---

## Agent Integration Endpoints (Optional)

### 3. Profile Analysis
**Endpoint:** `POST /loans/profile`

Analyzes applicant information and returns comprehensive profile with risk assessment.

### 4. Risk Assessment
**Endpoint:** `POST /loans/risk`

Calculates DTI, credit risk, and loan risk metrics.

### 5. Loan Decision
**Endpoint:** `POST /loans/decision`

Makes final loan decision (APPROVED/REJECTED/MANUAL_REVIEW).

### 6. Notifications & Audit
**Endpoint:** `POST /loans/notifications`

Generates notifications and creates audit trail entries.

---

## Complete Workflow Example

### Step 1: Submit Application
```bash
curl -X POST "http://localhost:8000/loans/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "John Smith",
    "applicant_email": "john@example.com",
    "applicant_phone": "555-1234",
    "loan_amount": 50000,
    "loan_type": "Personal",
    "loan_term_months": 60,
    "annual_income": 120000,
    "employment_status": "Permanent Full-time",
    "years_employed": 7,
    "credit_score": 750,
    "existing_debt": 500
  }'
```

Response: Application created with `application_id`

### Step 2: Check Status
```bash
curl -X GET "http://localhost:8000/loans/status/{application_id}"
```

### Step 3: Get Profile Analysis
```bash
curl -X POST "http://localhost:8000/loans/profile?applicant_name=John&annual_income=120000&..."
```

### Step 4: Get Risk Assessment
```bash
curl -X POST "http://localhost:8000/loans/risk?total_monthly_debt=500&monthly_income=10000&..."
```

### Step 5: Get Decision
```bash
curl -X POST "http://localhost:8000/loans/decision?applicant_name=John&annual_income=120000&..."
```

### Step 6: Send Notifications
```bash
curl -X POST "http://localhost:8000/loans/notifications?application_id={id}&applicant_name=John&..."
```

---

## Input Validation

### Loan Application Fields

| Field | Type | Validation | Required |
|-------|------|-----------|----------|
| applicant_name | string | Non-empty | ✓ |
| applicant_email | email | Valid email format | ✓ |
| applicant_phone | string | Non-empty | ✓ |
| loan_amount | float | Must be > 0 | ✓ |
| loan_type | string | Non-empty | ✓ |
| loan_term_months | int | Must be > 0 | ✓ |
| annual_income | float | Must be > 0 | ✓ |
| employment_status | string | Non-empty | ✓ |
| years_employed | float | Must be ≥ 0 | ✓ |
| credit_score | int | 300-850 or null | ✗ |
| existing_debt | float | Must be ≥ 0 | ✗ |

---

## Status Values

| Status | Meaning |
|--------|---------|
| pending | Application submitted, awaiting review |
| under_review | Being analyzed by agents |
| approved | Loan approved |
| rejected | Loan rejected |
| withdrawn | Application withdrawn |

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Application successfully created |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Application not found |
| 500 | Internal Server Error |

---

## Example: Complete Python Application

```python
import requests
from datetime import datetime

class LoanClient:
    BASE_URL = "http://localhost:8000/loans"
    
    @staticmethod
    def apply_loan(applicant_data):
        """Submit loan application"""
        response = requests.post(
            f"{LoanClient.BASE_URL}/apply",
            json=applicant_data
        )
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_status(application_id):
        """Check loan status"""
        response = requests.get(
            f"{LoanClient.BASE_URL}/status/{application_id}"
        )
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_profile(applicant_data):
        """Get profile analysis"""
        response = requests.post(
            f"{LoanClient.BASE_URL}/profile",
            params=applicant_data
        )
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_risk(risk_data):
        """Get risk assessment"""
        response = requests.post(
            f"{LoanClient.BASE_URL}/risk",
            params=risk_data
        )
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_decision(decision_data):
        """Get loan decision"""
        response = requests.post(
            f"{LoanClient.BASE_URL}/decision",
            params=decision_data
        )
        response.raise_for_status()
        return response.json()

# Usage
if __name__ == "__main__":
    applicant = {
        "applicant_name": "John Smith",
        "applicant_email": "john@example.com",
        "applicant_phone": "555-1234",
        "loan_amount": 50000,
        "loan_type": "Personal",
        "loan_term_months": 60,
        "annual_income": 120000,
        "employment_status": "Permanent Full-time",
        "years_employed": 7,
        "credit_score": 750,
        "existing_debt": 500
    }
    
    # Apply for loan
    result = LoanClient.apply_loan(applicant)
    app_id = result['application_id']
    print(f"✓ Application submitted: {app_id}")
    
    # Check status
    status = LoanClient.get_status(app_id)
    print(f"✓ Status: {status['status']}")
    
    # Get profile
    profile = LoanClient.get_profile({
        "application_id": app_id,
        "applicant_name": applicant["applicant_name"],
        "applicant_email": applicant["applicant_email"],
        "applicant_phone": applicant["applicant_phone"],
        "annual_income": applicant["annual_income"],
        "employment_status": applicant["employment_status"],
        "years_employed": applicant["years_employed"],
        "loan_amount": applicant["loan_amount"],
        "loan_type": applicant["loan_type"],
        "loan_term_months": applicant["loan_term_months"],
        "credit_score": applicant.get("credit_score"),
    })
    print(f"✓ Profile risk level: {profile.get('risk_level')}")
    
    # Get decision
    decision = LoanClient.get_decision({
        "applicant_name": applicant["applicant_name"],
        "annual_income": applicant["annual_income"],
        "credit_score": applicant.get("credit_score"),
        "dti_ratio": 0.083,  # calculated from profile
        "loan_amount": applicant["loan_amount"],
        "employment_years": applicant["years_employed"],
        "employment_status": applicant["employment_status"],
        "existing_debt": applicant.get("existing_debt", 0),
    })
    print(f"✓ Decision: {decision['decision']}")
```

---

## OpenAPI Documentation

When FastAPI is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive testing of all endpoints.

---

## Setup & Running

### Start FastAPI Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Environment Variables
```bash
export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/loan_approval_db"
export DEBUG=True
```

### Requirements
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
```

---

## Error Handling

### Invalid Input Example
```bash
curl -X POST "http://localhost:8000/loans/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "John",
    "loan_amount": -100
  }'
```

Response (422):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "loan_amount"],
      "msg": "ensure this value is greater than 0"
    }
  ]
}
```

---

## Best Practices

1. **Always validate inputs** - Let FastAPI/Pydantic handle validation
2. **Check status codes** - Different responses have different meanings
3. **Use application_id** - Always save the application ID for tracking
4. **Handle errors** - Catch HTTP exceptions and handle gracefully
5. **Use transactions** - All database operations are atomic

---

## Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /loans/apply | POST | Submit new loan application |
| /loans/status/{id} | GET | Get application status |
| /loans/profile | POST | Analyze applicant profile |
| /loans/risk | POST | Calculate risk metrics |
| /loans/decision | POST | Make loan decision |
| /loans/notifications | POST | Send notifications & audit |

**Status:** ✅ All endpoints production-ready
