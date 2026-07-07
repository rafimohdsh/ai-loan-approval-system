-- ============================================================================
-- AGENTIC LOAN APPROVAL SYSTEM - TEST QUERIES
-- ============================================================================
-- Use these queries to verify and test the data in MySQL Workbench
-- Copy and paste individual queries as needed
-- ============================================================================

USE loan_approval_db;

-- ============================================================================
-- VERIFICATION: CHECK ALL TABLES EXIST
-- ============================================================================

-- 1. List all tables
SHOW TABLES;

-- 2. Verify record counts
SELECT
    'customers' as table_name, COUNT(*) as record_count FROM customers
UNION ALL
SELECT 'loan_applications', COUNT(*) FROM loan_applications
UNION ALL
SELECT 'loan_decisions', COUNT(*) FROM loan_decisions
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs;

-- ============================================================================
-- SCENARIO 1: APPROVED APPLICATION - HIGH CREDIT, GOOD INCOME
-- ============================================================================

-- View the application
SELECT
    application_id,
    applicant_name,
    loan_amount,
    annual_income,
    credit_score,
    existing_debt,
    ROUND((existing_debt * 12) / annual_income, 2) as dti_ratio,
    status
FROM loan_applications
WHERE application_id = 'APP-001';

-- View the decision
SELECT
    d.decision_id,
    d.decision_status,
    d.decision_reason,
    ROUND(d.risk_score, 2) as risk_score,
    ROUND(d.approval_probability * 100, 0) as approval_probability_percent,
    ROUND(d.interest_rate, 2) as interest_rate,
    d.approved_amount,
    d.conditions_for_approval
FROM loan_decisions d
WHERE d.decision_id = 'DEC-001';

-- ============================================================================
-- SCENARIO 2: REJECTED APPLICATION - LOW CREDIT, HIGH DEBT
-- ============================================================================

-- View the application
SELECT
    application_id,
    applicant_name,
    loan_amount,
    annual_income,
    credit_score,
    existing_debt,
    ROUND((existing_debt * 12) / annual_income, 2) as dti_ratio,
    status
FROM loan_applications
WHERE application_id = 'APP-002';

-- View the decision
SELECT
    d.decision_id,
    d.decision_status,
    d.decision_reason,
    ROUND(d.risk_score, 2) as risk_score,
    ROUND(d.approval_probability * 100, 0) as approval_probability_percent
FROM loan_decisions d
WHERE d.decision_id = 'DEC-002';

-- View the reasoning
SELECT d.agent_analysis FROM loan_decisions d WHERE d.decision_id = 'DEC-002';

-- ============================================================================
-- SCENARIO 3: MANUAL REVIEW - NEW EMPLOYMENT, FAIR CREDIT
-- ============================================================================

-- View the application
SELECT
    application_id,
    applicant_name,
    loan_amount,
    annual_income,
    years_employed,
    credit_score,
    employment_status,
    status
FROM loan_applications
WHERE application_id = 'APP-003';

-- View the decision
SELECT
    d.decision_id,
    d.decision_status,
    ROUND(d.risk_score, 2) as risk_score,
    ROUND(d.approval_probability * 100, 0) as approval_probability_percent,
    d.requires_manual_review,
    d.agent_analysis
FROM loan_decisions d
WHERE d.decision_id = 'DEC-003';

-- ============================================================================
-- SCENARIO 4: HIGH INCOME, EXCELLENT CREDIT, LARGE LOAN
-- ============================================================================

-- View the application and customer
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.occupation,
    c.employer_name,
    c.annual_income,
    c.credit_score,
    c.total_assets,
    a.application_id,
    a.loan_amount,
    ROUND((a.loan_amount / c.annual_income) * 100, 0) as loan_to_income_percent
FROM customers c
LEFT JOIN loan_applications a ON c.email = a.applicant_email
WHERE a.application_id = 'APP-004';

-- View the decision
SELECT
    d.decision_id,
    d.decision_status,
    d.decision_reason,
    ROUND(d.risk_score, 2) as risk_score,
    ROUND(d.approval_probability * 100, 0) as approval_probability_percent,
    d.approved_amount,
    d.approved_term_months,
    ROUND(d.interest_rate, 2) as interest_rate,
    d.recommendation_confidence
FROM loan_decisions d
WHERE d.decision_id = 'DEC-004';

-- ============================================================================
-- SCENARIO 5: SELF-EMPLOYED APPLICANT
-- ============================================================================

-- View the application and customer details
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.occupation,
    c.employment_status,
    c.years_employed,
    c.annual_income,
    c.credit_score,
    a.application_id,
    a.loan_type,
    a.loan_amount
FROM customers c
LEFT JOIN loan_applications a ON c.email = a.applicant_email
WHERE a.application_id = 'APP-005';

-- View decision for self-employed
SELECT
    d.decision_id,
    d.decision_status,
    d.requires_manual_review,
    d.agent_analysis
FROM loan_decisions d
WHERE d.decision_id = 'DEC-005';

-- ============================================================================
-- SCENARIO 6: NO CREDIT HISTORY
-- ============================================================================

-- View the application
SELECT
    application_id,
    applicant_name,
    applicant_email,
    annual_income,
    years_employed,
    credit_score,
    existing_debt,
    status
FROM loan_applications
WHERE application_id = 'APP-006';

-- View decision - no credit history
SELECT
    d.decision_id,
    d.decision_status,
    d.risk_score,
    d.requires_manual_review,
    d.agent_analysis
FROM loan_decisions d
WHERE d.decision_id = 'DEC-006';

-- ============================================================================
-- AGGREGATE ANALYSIS: DECISION SUMMARY
-- ============================================================================

-- Decision distribution
SELECT
    decision_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM loan_decisions), 0) as percentage
FROM loan_decisions
GROUP BY decision_status
ORDER BY count DESC;

-- Risk analysis by decision status
SELECT
    decision_status,
    COUNT(*) as count,
    ROUND(AVG(risk_score), 2) as avg_risk_score,
    ROUND(MIN(risk_score), 2) as min_risk_score,
    ROUND(MAX(risk_score), 2) as max_risk_score,
    ROUND(AVG(approval_probability) * 100, 0) as avg_approval_prob_percent
FROM loan_decisions
GROUP BY decision_status
ORDER BY avg_risk_score DESC;

-- ============================================================================
-- AGGREGATE ANALYSIS: CREDIT SCORE ANALYSIS
-- ============================================================================

-- Credit score distribution
SELECT
    CASE
        WHEN credit_score IS NULL THEN 'No History'
        WHEN credit_score < 600 THEN 'Poor (< 600)'
        WHEN credit_score < 650 THEN 'Fair (600-649)'
        WHEN credit_score < 700 THEN 'Good (650-699)'
        WHEN credit_score < 750 THEN 'Very Good (700-749)'
        ELSE 'Excellent (750+)'
    END as credit_category,
    COUNT(*) as applicant_count,
    ROUND(AVG(annual_income), 0) as avg_income,
    COUNT(DISTINCT CASE WHEN d.decision_status = 'approved' THEN 1 END) as approved_count,
    ROUND(COUNT(DISTINCT CASE WHEN d.decision_status = 'approved' THEN 1 END) * 100.0 / COUNT(*), 0) as approval_rate_percent
FROM loan_applications a
LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
GROUP BY credit_category
ORDER BY
    CASE
        WHEN credit_score IS NULL THEN 0
        WHEN credit_score < 600 THEN 1
        WHEN credit_score < 650 THEN 2
        WHEN credit_score < 700 THEN 3
        WHEN credit_score < 750 THEN 4
        ELSE 5
    END;

-- ============================================================================
-- AGGREGATE ANALYSIS: INCOME ANALYSIS
-- ============================================================================

-- Income distribution and approval rates
SELECT
    CASE
        WHEN annual_income < 40000 THEN '< $40K'
        WHEN annual_income < 75000 THEN '$40K-$75K'
        WHEN annual_income < 150000 THEN '$75K-$150K'
        ELSE '> $150K'
    END as income_bracket,
    COUNT(*) as applicant_count,
    ROUND(AVG(loan_amount), 0) as avg_loan_requested,
    ROUND(AVG(credit_score), 0) as avg_credit_score,
    COUNT(DISTINCT CASE WHEN d.decision_status = 'approved' THEN 1 END) as approved_count,
    ROUND(COUNT(DISTINCT CASE WHEN d.decision_status = 'approved' THEN 1 END) * 100.0 / COUNT(*), 0) as approval_rate_percent
FROM loan_applications a
LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
GROUP BY income_bracket
ORDER BY annual_income;

-- ============================================================================
-- AGGREGATE ANALYSIS: LOAN TYPE ANALYSIS
-- ============================================================================

-- Loan type statistics
SELECT
    loan_type,
    COUNT(*) as count,
    ROUND(AVG(loan_amount), 0) as avg_loan_amount,
    ROUND(AVG(loan_term_months), 0) as avg_term_months,
    ROUND(AVG(annual_income), 0) as avg_applicant_income,
    COUNT(DISTINCT CASE WHEN d.decision_status = 'approved' THEN 1 END) as approved_count,
    COUNT(DISTINCT CASE WHEN d.decision_status = 'rejected' THEN 1 END) as rejected_count,
    ROUND(COUNT(DISTINCT CASE WHEN d.decision_status = 'approved' THEN 1 END) * 100.0 / COUNT(*), 0) as approval_rate_percent
FROM loan_applications a
LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
GROUP BY loan_type
ORDER BY count DESC;

-- ============================================================================
-- AUDIT TRAIL: COMPLETE HISTORY FOR APP-001
-- ============================================================================

SELECT
    audit_id,
    entity_type,
    action_type,
    user_name,
    user_role,
    action_reason,
    status,
    timestamp,
    agent_notes
FROM audit_logs
WHERE entity_id IN (
    SELECT application_id FROM loan_applications WHERE application_id = 'APP-001'
)
ORDER BY timestamp ASC;

-- ============================================================================
-- AUDIT TRAIL: DECISION HISTORY
-- ============================================================================

SELECT
    audit_id,
    entity_type,
    action_type,
    user_name,
    user_role,
    status,
    timestamp,
    agent_notes
FROM audit_logs
WHERE action_type IN ('approve', 'reject', 'assign')
ORDER BY timestamp DESC;

-- ============================================================================
-- DTI ANALYSIS: DEBT-TO-INCOME RATIO
-- ============================================================================

SELECT
    application_id,
    applicant_name,
    annual_income,
    existing_debt,
    ROUND((existing_debt * 12) / annual_income * 100, 2) as dti_ratio_percent,
    CASE
        WHEN (existing_debt * 12) / annual_income <= 0.36 THEN 'Excellent (≤36%)'
        WHEN (existing_debt * 12) / annual_income <= 0.43 THEN 'Good (≤43%)'
        WHEN (existing_debt * 12) / annual_income <= 0.50 THEN 'Fair (≤50%)'
        ELSE 'High (>50%)'
    END as dti_category,
    credit_score,
    d.decision_status,
    ROUND(d.risk_score, 2) as risk_score
FROM loan_applications a
LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
ORDER BY dti_ratio_percent DESC;

-- ============================================================================
-- RISK ANALYSIS: HIGH RISK APPLICATIONS
-- ============================================================================

SELECT
    a.application_id,
    a.applicant_name,
    a.credit_score,
    a.annual_income,
    a.loan_amount,
    ROUND(d.risk_score, 2) as risk_score,
    d.decision_status,
    d.requires_manual_review,
    ROUND(d.approval_probability * 100, 0) as approval_probability_percent
FROM loan_applications a
LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
WHERE d.risk_score > 0.50
ORDER BY d.risk_score DESC;

-- ============================================================================
-- EMPLOYMENT ANALYSIS: EMPLOYMENT STATUS BREAKDOWN
-- ============================================================================

SELECT
    employment_status,
    COUNT(*) as count,
    ROUND(AVG(annual_income), 0) as avg_income,
    ROUND(AVG(years_employed), 1) as avg_years_employed,
    COUNT(DISTINCT CASE WHEN d.decision_status = 'approved' THEN 1 END) as approved_count,
    ROUND(COUNT(DISTINCT CASE WHEN d.decision_status = 'approved' THEN 1 END) * 100.0 / COUNT(*), 0) as approval_rate_percent
FROM loan_applications a
LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
GROUP BY employment_status;

-- ============================================================================
-- COMPREHENSIVE APPLICATION REPORT
-- ============================================================================

SELECT
    a.application_id,
    a.applicant_name,
    a.applicant_email,
    a.loan_type,
    a.loan_amount,
    a.loan_term_months,
    a.annual_income,
    a.credit_score,
    a.employment_status,
    a.years_employed,
    a.existing_debt,
    ROUND((a.existing_debt * 12) / a.annual_income * 100, 2) as dti_ratio_percent,
    a.status as application_status,
    d.decision_id,
    d.decision_status,
    d.decision_reason,
    ROUND(d.risk_score, 2) as risk_score,
    ROUND(d.approval_probability * 100, 0) as approval_probability_percent,
    d.approved_amount,
    d.approved_term_months,
    ROUND(d.interest_rate, 2) as interest_rate,
    d.requires_manual_review,
    a.created_at,
    d.decision_made_at
FROM loan_applications a
LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
ORDER BY a.created_at DESC;

-- ============================================================================
-- FIND APPLICATION BY EMAIL
-- ============================================================================
-- Uncomment and modify the email address as needed
-- SELECT
--     a.application_id,
--     a.applicant_name,
--     a.loan_amount,
--     a.status,
--     d.decision_id,
--     d.decision_status,
--     a.created_at
-- FROM loan_applications a
-- LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
-- WHERE a.applicant_email = 'john.smith@example.com';

-- ============================================================================
-- FIND APPLICATION BY APPLICATION ID
-- ============================================================================
-- Uncomment and modify the application ID as needed
-- SELECT
--     a.*,
--     c.first_name,
--     c.last_name,
--     c.occupation,
--     c.credit_history_months,
--     d.decision_id,
--     d.decision_status,
--     d.decision_reason,
--     d.risk_score,
--     d.agent_analysis
-- FROM loan_applications a
-- LEFT JOIN customers c ON a.applicant_email = c.email
-- LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
-- WHERE a.application_id = 'APP-001';

-- ============================================================================
-- EXPORT DATA (For debugging/analysis)
-- ============================================================================

-- All applications with their decisions (can be exported to CSV)
SELECT
    a.application_id,
    a.applicant_name,
    a.applicant_email,
    a.loan_amount,
    a.annual_income,
    a.credit_score,
    a.status,
    d.decision_status,
    d.risk_score,
    d.approval_probability
FROM loan_applications a
LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
ORDER BY a.created_at DESC;

-- ============================================================================
-- CLEANUP (If needed - uncomment to use)
-- ============================================================================

-- Delete all test data (WARNING: This will delete everything!)
-- DELETE FROM audit_logs;
-- DELETE FROM loan_decisions;
-- DELETE FROM loan_applications;
-- DELETE FROM customers;
--
-- Reset auto-increment counters
-- ALTER TABLE customers AUTO_INCREMENT = 1;
-- ALTER TABLE loan_applications AUTO_INCREMENT = 1;
-- ALTER TABLE loan_decisions AUTO_INCREMENT = 1;
-- ALTER TABLE audit_logs AUTO_INCREMENT = 1;

-- ============================================================================
-- END OF TEST QUERIES
-- ============================================================================
