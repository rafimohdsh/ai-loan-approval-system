# Decision Agent - Quick Reference

## What It Does

Makes final loan decisions using AWS Bedrock Claude.

**Outputs:** `APPROVED` | `REJECTED` | `MANUAL_REVIEW`

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `backend/app/agents/decision_agent.py` | 160 | Core implementation |
| `backend/app/agents/test_decision_agent.py` | 51 | Test scenarios (3) |
| `backend/app/api/endpoints/loans.py` | Modified | API endpoint |

## Usage

### Python (Mock - No Bedrock)
```python
from backend.app.agents.decision_agent import make_decision_mock

decision = make_decision_mock(
    applicant_name="John Smith",
    annual_income=120000,
    credit_score=750,
    dti_ratio=0.25,
    loan_amount=50000,
    employment_years=7,
    employment_status="Permanent Full-time",
    existing_debt=500,
)

print(decision.decision)  # "approved"
```

### Python (With Bedrock)
```python
from backend.app.agents.decision_agent import make_decision

# Requires AWS credentials and Bedrock access
decision = make_decision(...)
```

### API
```bash
curl -X POST "http://localhost:8000/loans/decision?applicant_name=John%20Smith&annual_income=120000&dti_ratio=0.25&loan_amount=50000&employment_years=7&employment_status=Permanent%20Full-time&credit_score=750"
```

### Test
```bash
python backend/app/agents/test_decision_agent.py
```

Output:
```
✓ Strong applicant: approved
✓ Poor credit: rejected
✓ No credit history: manual_review

✓ All decision scenarios passed
```

## API Endpoint

**POST** `/loans/decision`

**Parameters:**
- `applicant_name: str` - Applicant name
- `annual_income: float` - Annual income
- `dti_ratio: float` - Debt-to-income ratio
- `loan_amount: float` - Loan amount
- `employment_years: float` - Years employed
- `employment_status: str` - Employment status
- `credit_score: int` (optional) - Credit score
- `existing_debt: float` (optional) - Monthly debt

**Returns:** `LoanDecision`

## Decision Logic

### APPROVED
- Good credit (≥700)
- DTI ≤ 36%
- Income-to-loan ≥ 3x
- Stable employment

### REJECTED
- Credit score < 600
- DTI > 50%
- Loan exceeds annual income
- High risk profile

### MANUAL_REVIEW
- No credit history
- Employment < 1 year
- Borderline metrics
- Multiple risk factors

## Output Example

```json
{
  "decision": "approved",
  "confidence": 0.95,
  "reasoning": "Strong financial profile - credit score good, DTI acceptable, income-to-loan ratio favorable",
  "conditions": "Standard loan terms apply"
}
```

## Bedrock Configuration

To use actual Bedrock Claude:

1. Set AWS credentials
```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

2. Use `make_decision()` instead of `make_decision_mock()`

3. Model: `anthropic.claude-3-5-sonnet-20241022`

## Models Available

| Model | Speed | Cost |
|-------|-------|------|
| Claude 3.5 Sonnet | Fast | Low |
| Claude 3 Opus | Slow | High |
| Claude 3 Haiku | Fastest | Lowest |

Current: **Claude 3.5 Sonnet**

## Status

✅ Production Ready
✅ Mock mode for testing
✅ Bedrock integration ready
✅ Type-safe output
✅ 3 test scenarios

**Version:** 1.0.0
