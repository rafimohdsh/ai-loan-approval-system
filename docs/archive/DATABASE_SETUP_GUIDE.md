# Database Setup Guide - Agentic Loan Approval System

## Quick Start

### Step 1: Open MySQL Workbench
- Launch MySQL Workbench
- Connect to your MySQL Server

### Step 2: Create Database and Tables
1. Open a new SQL query tab (File → New Query Tab or Ctrl+T)
2. Open the file: `DATABASE_SQL_SETUP.sql`
3. Select ALL content (Ctrl+A)
4. Execute (Ctrl+Shift+Enter or lightning bolt icon)

**Expected Result:**
- Database `loan_approval_db` is created
- 4 tables are created: customers, loan_applications, loan_decisions, audit_logs
- 6 test customers are inserted
- 6 test loan applications are inserted
- 6 loan decisions are created
- 12+ audit log entries are recorded

### Step 3: Verify Data
Run these verification queries in a new tab:

```sql
-- Count records in each table
SELECT 'Customers' as table_name, COUNT(*) as record_count FROM loan_approval_db.customers
UNION ALL
SELECT 'Loan Applications', COUNT(*) FROM loan_approval_db.loan_applications
UNION ALL
SELECT 'Loan Decisions', COUNT(*) FROM loan_approval_db.loan_decisions
UNION ALL
SELECT 'Audit Logs', COUNT(*) FROM loan_approval_db.audit_logs;
```

**Expected Output:**
```
table_name          | record_count
--------------------|-------------
Customers           | 6
Loan Applications   | 6
Loan Decisions      | 6
Audit Logs          | 12
```

---

## Test Scenarios Overview

### Scenario 1: APPROVED - High Credit, Good Income
- **Application ID:** APP-001
- **Applicant:** John Smith
- **Credit Score:** 750 (Excellent)
- **Annual Income:** $150,000
- **Loan Amount:** $50,000
- **Existing Debt:** $5,000
- **DTI Ratio:** 4% (Excellent)
- **Expected Decision:** ✅ APPROVED
- **Risk Score:** 0.15 (Low)
- **Approval Probability:** 95%

**Test Query:**
```sql
SELECT * FROM loan_approval_db.loan_applications WHERE application_id = 'APP-001';
SELECT * FROM loan_approval_db.loan_decisions WHERE decision_id = 'DEC-001';
```

---

### Scenario 2: REJECTED - Low Credit, High Debt
- **Application ID:** APP-002
- **Applicant:** Jane Doe
- **Credit Score:** 550 (Poor)
- **Annual Income:** $35,000
- **Loan Amount:** $45,000
- **Existing Debt:** $18,000
- **DTI Ratio:** 62% (Very High)
- **Expected Decision:** ❌ REJECTED
- **Risk Score:** 0.78 (High)
- **Approval Probability:** 5%

**Test Query:**
```sql
SELECT * FROM loan_approval_db.loan_applications WHERE application_id = 'APP-002';
SELECT * FROM loan_approval_db.loan_decisions WHERE decision_id = 'DEC-002';
```

---

### Scenario 3: MANUAL REVIEW - New Employment
- **Application ID:** APP-003
- **Applicant:** Michael Johnson
- **Credit Score:** 650 (Fair)
- **Annual Income:** $85,000
- **Years Employed:** 1.5 (New)
- **Loan Amount:** $60,000
- **Expected Decision:** 🔄 MANUAL REVIEW
- **Risk Score:** 0.45 (Medium)
- **Approval Probability:** 55%
- **Reason:** New employment, borderline credit

**Test Query:**
```sql
SELECT * FROM loan_approval_db.loan_applications WHERE application_id = 'APP-003';
SELECT * FROM loan_approval_db.loan_decisions WHERE decision_id = 'DEC-003';
```

---

### Scenario 4: APPROVED - Excellent Profile, Large Loan
- **Application ID:** APP-004
- **Applicant:** Sarah Williams
- **Credit Score:** 800 (Excellent)
- **Annual Income:** $250,000
- **Loan Amount:** $200,000
- **Employment Years:** 12 (Very Stable)
- **Expected Decision:** ✅ APPROVED
- **Risk Score:** 0.08 (Very Low)
- **Approval Probability:** 98%
- **Interest Rate:** 4.5%

**Test Query:**
```sql
SELECT * FROM loan_approval_db.loan_applications WHERE application_id = 'APP-004';
SELECT * FROM loan_approval_db.loan_decisions WHERE decision_id = 'DEC-004';
```

---

### Scenario 5: MANUAL REVIEW - Self-Employed
- **Application ID:** APP-005
- **Applicant:** David Brown
- **Employment Status:** Self-employed
- **Annual Income:** $95,000
- **Credit Score:** 680 (Good)
- **Loan Amount:** $75,000
- **Expected Decision:** 🔄 MANUAL REVIEW
- **Risk Score:** 0.42 (Medium)
- **Reason:** Self-employed requires additional documentation

**Test Query:**
```sql
SELECT * FROM loan_approval_db.loan_applications WHERE application_id = 'APP-005';
SELECT * FROM loan_approval_db.loan_decisions WHERE decision_id = 'DEC-005';
```

---

### Scenario 6: MANUAL REVIEW - No Credit History
- **Application ID:** APP-006
- **Applicant:** Emily Garcia
- **Credit Score:** NULL (No History)
- **Annual Income:** $65,000
- **Years Employed:** 1.2 (Recent Graduate)
- **Loan Amount:** $30,000
- **Expected Decision:** 🔄 MANUAL REVIEW
- **Risk Score:** 0.50 (Medium-High)
- **Reason:** No credit history available

**Test Query:**
```sql
SELECT * FROM loan_approval_db.loan_applications WHERE application_id = 'APP-006';
SELECT * FROM loan_approval_db.loan_decisions WHERE decision_id = 'DEC-006';
```

---

## Running Analysis Queries

### Query: All Decisions by Status
```sql
SELECT
    decision_status,
    COUNT(*) as count,
    ROUND(AVG(risk_score), 2) as avg_risk_score,
    ROUND(AVG(approval_probability) * 100, 0) as avg_approval_prob_percent
FROM loan_approval_db.loan_decisions
GROUP BY decision_status;
```

**Expected Output:**
```
decision_status | count | avg_risk_score | avg_approval_prob_percent
----------------|-------|----------------|------------------------
approved        | 2     | 0.12           | 97
rejected        | 1     | 0.78           | 5
pending         | 3     | 0.46           | 55
```

---

### Query: Approval Rate by Credit Score
```sql
SELECT
    CASE
        WHEN credit_score IS NULL THEN 'No History'
        WHEN credit_score < 600 THEN 'Poor'
        WHEN credit_score < 700 THEN 'Fair/Good'
        ELSE 'Very Good/Excellent'
    END as credit_category,
    COUNT(*) as applicants,
    COUNT(CASE WHEN decision_status = 'approved' THEN 1 END) as approved,
    ROUND(COUNT(CASE WHEN decision_status = 'approved' THEN 1 END) * 100.0 / COUNT(*), 0) as approval_rate_percent
FROM loan_approval_db.loan_applications a
LEFT JOIN loan_approval_db.loan_decisions d ON a.id = d.loan_application_id
GROUP BY credit_category;
```

---

### Query: Approval Rate by Income Bracket
```sql
SELECT
    CASE
        WHEN annual_income < 50000 THEN '< $50K'
        WHEN annual_income < 100000 THEN '$50K-$100K'
        WHEN annual_income < 200000 THEN '$100K-$200K'
        ELSE '> $200K'
    END as income_bracket,
    COUNT(*) as applicants,
    COUNT(CASE WHEN decision_status = 'approved' THEN 1 END) as approved,
    ROUND(COUNT(CASE WHEN decision_status = 'approved' THEN 1 END) * 100.0 / COUNT(*), 0) as approval_rate_percent
FROM loan_approval_db.loan_applications a
LEFT JOIN loan_approval_db.loan_decisions d ON a.id = d.loan_application_id
GROUP BY income_bracket;
```

---

### Query: DTI Analysis
```sql
SELECT
    application_id,
    applicant_name,
    annual_income,
    existing_debt,
    ROUND((existing_debt * 12) / annual_income * 100, 2) as dti_ratio_percent,
    credit_score,
    d.decision_status,
    ROUND(d.risk_score, 2) as risk_score
FROM loan_approval_db.loan_applications a
LEFT JOIN loan_approval_db.loan_decisions d ON a.id = d.loan_application_id
ORDER BY dti_ratio_percent DESC;
```

---

### Query: Audit Trail for Application
```sql
SELECT
    audit_id,
    entity_type,
    action_type,
    user_name,
    action_reason,
    status,
    timestamp
FROM loan_approval_db.audit_logs
WHERE entity_id = 'APP-001'
ORDER BY timestamp ASC;
```

---

## Comprehensive Report Query

Get a complete view of all applications with decisions:

```sql
SELECT
    a.application_id,
    a.applicant_name,
    a.loan_type,
    a.loan_amount,
    a.annual_income,
    a.credit_score,
    a.years_employed,
    ROUND((a.existing_debt * 12) / a.annual_income * 100, 2) as dti_percent,
    a.status as application_status,
    d.decision_status,
    ROUND(d.risk_score, 2) as risk_score,
    ROUND(d.approval_probability * 100, 0) as approval_prob_percent,
    d.approved_amount,
    ROUND(d.interest_rate, 2) as interest_rate,
    d.requires_manual_review,
    a.created_at
FROM loan_approval_db.loan_applications a
LEFT JOIN loan_approval_db.loan_decisions d ON a.id = d.loan_application_id
ORDER BY a.created_at DESC;
```

---

## Database Schema Summary

### customers
- 6 customers with complete profiles
- Mix of employed and self-employed
- Credit scores ranging from NULL to 800
- Income range: $35K to $250K

### loan_applications
- 6 applications
- Different loan types: Personal, Home, Auto
- Loan amounts: $30K to $200K
- Term months: 48 to 360

### loan_decisions
- 2 Approved decisions
- 1 Rejected decision
- 3 Pending (Manual Review) decisions
- Risk scores: 0.08 to 0.78

### audit_logs
- Complete audit trail for all applications
- Decision creation and update logs
- Status tracking for compliance

---

## Troubleshooting

### Issue: "Table doesn't exist" error
**Solution:** Make sure you executed the setup script completely. Check that all CREATE TABLE statements ran without errors.

### Issue: Foreign key errors
**Solution:** Make sure all parent tables (loan_applications) are created before child tables (loan_decisions).

### Issue: Duplicate key errors
**Solution:** This means data already exists. Either:
- Use a different database name
- Delete existing data and re-run the setup

To clean up:
```sql
USE loan_approval_db;
DELETE FROM audit_logs;
DELETE FROM loan_decisions;
DELETE FROM loan_applications;
DELETE FROM customers;
```

Then re-run the INSERT statements.

### Issue: Can't connect to database
**Solution:** Make sure MySQL is running and your connection settings are correct.

---

## Next Steps

1. ✅ Create all tables and test data
2. ✅ Run verification queries
3. ✅ Review all 6 test scenarios
4. ✅ Run analysis queries
5. 🚀 Start the FastAPI backend (it will use this data)
6. 🚀 Start the Streamlit frontend
7. 🚀 Test applications through the UI

---

## File References

- **DATABASE_SQL_SETUP.sql** - Complete setup script (run this first)
- **DATABASE_TEST_QUERIES.sql** - All test and analysis queries
- **DATABASE_SETUP_GUIDE.md** - This file

---

## Connection String for Application

When you run the FastAPI backend, use this connection string in `.env`:

```
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/loan_approval_db
```

Replace `root` and `password` with your actual MySQL credentials.

---

**Last Updated:** 2026-07-02  
**Status:** ✅ Ready for Testing
