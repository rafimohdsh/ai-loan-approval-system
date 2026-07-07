# Quick Reference - Agentic Loan Approval System

## 🚀 Quick Start (2 minutes)

### 1. Install & Configure
```bash
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=mysql+pymysql://root:Tek%4012345@localhost:3306/loan_approval_db
AWS_REGION=us-east-1
API_BASE_URL=http://localhost:8000
EOF
```

### 2. Run Backend (Terminal 1)
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Run Frontend (Terminal 2)
```bash
streamlit run frontend/app.py
```

### 4. Access
- **Frontend**: http://localhost:8501 (Streamlit UI)
- **API Docs**: http://localhost:8000/docs (Swagger)
- **Health**: http://localhost:8000/health

---

## 📋 Features

### 1. Dashboard 📊
- View all applications
- See approval/rejection/pending counts
- Recent applications list

### 2. Apply Loan 💳
- Submit new application
- Automatic decision generation
- Get Application ID

### 3. Check Status 📋
- Search by Application ID
- View full details
- See risk scores

### 4. View Decision 🎯
- See final decision (APPROVED/REJECTED/UNDER_REVIEW)
- View assessment metrics
- See approval/rejection reasons

---

## 🔧 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/loans/apply` | POST | Submit application |
| `/loans/status/{id}` | GET | Check application status |
| `/loans/status` | GET | List all applications |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |

---

## 📁 Project Structure

```
agentic-loan-approval-system/
├── backend/
│   └── app/
│       ├── agents/              # AI agents (not active)
│       ├── api/endpoints/       # API routes
│       │   └── loans.py        # Loan endpoints
│       ├── database/            # DB connection
│       ├── models/              # SQLAlchemy models
│       ├── schemas/             # Pydantic schemas
│       └── services/            # Business logic
│           └── loan_service.py # Decision logic
├── frontend/
│   └── app.py                  # Streamlit UI
├── config/
│   └── settings.py            # Configuration
└── docs/
    ├── QUICK_REFERENCE.md     # This file
    ├── DATABASE_SETUP.md      # Database setup
    └── archive/               # Old documentation
```

---

## ⚙️ Configuration

**File**: `config/settings.py` (via environment variables)

### Key Settings
```
DECISION_PENDING_DURATION=300      # 5 minutes (not used)
DECISION_REVIEW_DURATION=600       # 10 minutes (not used)
```

These are configurable but currently unused - decisions show immediately.

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000
kill -9 <PID>

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't connect to API
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Check `.env` has correct `API_BASE_URL`
3. Check API logs for errors

### Database connection error
1. Ensure MySQL is running
2. Check database URL in `.env`
3. Run: `mysql -u root -p -e "SELECT 1"`

---

## 📊 Decision Logic

Applications are automatically evaluated based on:

- **APPROVED** if:
  - Credit score ≥ 700 AND DTI ≤ 36%, OR
  - Credit score ≥ 650 AND DTI ≤ 43% with other factors met

- **REJECTED** if:
  - Credit score < 600, OR
  - DTI > 50%, OR
  - Loan amount > annual income

- **UNDER_REVIEW** if:
  - No credit history, OR
  - Employment tenure < 1 year, OR
  - 650 ≤ credit score < 700, OR
  - 43% < DTI ≤ 50%

---

## 📂 Navigation in Sidebar

**Left Panel (3 Options)**:
1. 📊 Dashboard - View all applications
2. 💳 Apply Loan - Submit new application
3. 📋 Check Status - Track application
4. 🎯 View Decision - See final decision

---

## 🔍 Testing Workflow

1. **Submit Application**
   - Go to "Apply Loan"
   - Fill form
   - Get Application ID

2. **Check Status**
   - Go to "Check Status"
   - Paste Application ID
   - View details

3. **View Decision**
   - Go to "View Decision"
   - Paste Application ID
   - See decision + metrics

---

## 📊 Sample Test Data

```
Name: John Smith
Email: john@example.com
Phone: +1-555-1234
Location: San Francisco, CA
Annual Income: $120,000
Loan Amount: $50,000
Loan Type: Personal
Loan Term: 60 months
Employment: Permanent Full-time
Years Employed: 7
Credit Score: 750
Existing Debt: $500/month
```

**Expected Result**: ✅ APPROVED (Good risk profile)

---

## 🚨 Important Notes

- **Decisions are immediate** - No delays, shows actual decision right away
- **Dashboard** - Shows summary and recent 10 applications
- **All statuses** - PENDING, UNDER_REVIEW, APPROVED, REJECTED
- **Database** - Auto-creates tables on first run

---

**Version**: 1.0.0  
**Last Updated**: 2026-07-02  
**Status**: Production Ready ✅
