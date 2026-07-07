# Decision Timing Configuration

## Overview
The loan decision display follows a time-based workflow:
- **0-5 minutes**: Display as PENDING
- **5-10 minutes**: Display as UNDER_REVIEW
- **After 10 minutes**: Display final decision (APPROVED/REJECTED/MANUAL_REVIEW)

## Configuration

### Location
`config/settings.py`

### Configuration Parameters

```python
# Decision Timing Configuration (in seconds)
DECISION_PENDING_DURATION: int = 300        # 5 minutes until UNDER_REVIEW
DECISION_REVIEW_DURATION: int = 600         # 10 minutes until FINAL DECISION
DECISION_FINAL_DURATION: int = 600          # Total time for processing
```

### Changing Timing via Environment Variables

Edit your `.env` file:

```env
# Set decision timing (in seconds)
DECISION_PENDING_DURATION=300      # 5 minutes
DECISION_REVIEW_DURATION=600       # 10 minutes total
DECISION_FINAL_DURATION=600        # Same as review duration
```

Or set in `.env` before starting backend:

```bash
export DECISION_PENDING_DURATION=600    # 10 minutes for PENDING phase
export DECISION_REVIEW_DURATION=1200    # 20 minutes for UNDER_REVIEW phase
```

## How It Works

### Timeline Example

```
Application Submitted at 14:00:00
├── 14:00:00 to 14:05:00 (0-300 seconds)
│   └── Status: PENDING ⏳
│
├── 14:05:00 to 14:10:00 (300-600 seconds)
│   └── Status: UNDER_REVIEW 🔍
│
└── After 14:10:00 (600+ seconds)
    └── Status: APPROVED ✅ / REJECTED ❌ / MANUAL_REVIEW 📋
```

### Testing Different Timings

**Quick Testing (30 seconds total):**
```env
DECISION_PENDING_DURATION=10        # 10 seconds
DECISION_REVIEW_DURATION=20         # 20 seconds total
```

**Production (5-10 minutes):**
```env
DECISION_PENDING_DURATION=300       # 5 minutes
DECISION_REVIEW_DURATION=600        # 10 minutes total
```

**Extended Review (15-30 minutes):**
```env
DECISION_PENDING_DURATION=900       # 15 minutes
DECISION_REVIEW_DURATION=1800       # 30 minutes total
```

## Decision Logic After 10 Minutes

Once the UNDER_REVIEW phase ends, the actual decision displays based on criteria:

✅ **APPROVED** if:
- Credit Score ≥ 700 AND DTI ≤ 36%
- OR Credit Score ≥ 650 AND DTI ≤ 43% AND meets other criteria

❌ **REJECTED** if:
- Credit Score < 600
- OR DTI > 50%
- OR Loan Amount > Annual Income

🔍 **MANUAL_REVIEW** if:
- No Credit History
- Employment < 1 year
- 650 ≤ Credit Score < 700
- 43% < DTI ≤ 50%

## Implementation Details

### File: `config/settings.py`
- Contains configuration parameters
- Can be overridden via environment variables

### File: `backend/app/services/loan_service.py`
- `get_application()` method applies time-based status updates
- Checks elapsed time since application creation
- Updates status accordingly before returning

## User Experience

### In Streamlit UI

**Immediate (0-5 mins):**
```
Status: PENDING ⏳
Message: Your application is being processed...
```

**Mid-processing (5-10 mins):**
```
Status: UNDER_REVIEW 🔍
Message: Our team is reviewing your application...
```

**Final Decision (after 10 mins):**
```
Status: APPROVED ✅
Loan Amount: $50,000
Approval Reason: Strong financial profile
```

## Configuration Change Workflow

1. Edit `.env` file:
   ```bash
   nano .env
   ```

2. Update timing values:
   ```env
   DECISION_PENDING_DURATION=300    # Change this
   DECISION_REVIEW_DURATION=600     # And this
   ```

3. Restart backend:
   ```bash
   python -m uvicorn backend.app.main:app --reload --port 8000
   ```

4. Changes take effect immediately for new applications

## Verification

Test the timing with a new application:

1. Submit application at time: `T`
2. Check status at `T + 2 min` → Should show **PENDING**
3. Check status at `T + 7 min` → Should show **UNDER_REVIEW**
4. Check status at `T + 12 min` → Should show actual decision

## No Code Changes Needed

To change timing, only update `.env` file. No code modifications required!

---

**Last Updated:** 2026-07-02
**Version:** 1.0
