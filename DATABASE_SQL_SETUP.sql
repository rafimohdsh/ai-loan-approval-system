-- ============================================================================
-- AGENTIC LOAN APPROVAL SYSTEM - DATABASE SETUP SCRIPTS
-- ============================================================================
-- Copy and paste these scripts into MySQL Workbench to create all tables
-- and insert test data for comprehensive scenario testing
-- ============================================================================

-- ============================================================================
-- STEP 1: CREATE DATABASE
-- ============================================================================

CREATE DATABASE IF NOT EXISTS loan_approval_db;
USE loan_approval_db;

-- ============================================================================
-- STEP 2: CREATE TABLES
-- ============================================================================

-- Table: customers
CREATE TABLE IF NOT EXISTS customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATETIME NOT NULL,
    ssn VARCHAR(20) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'USA',
    employment_status VARCHAR(50) NOT NULL,
    occupation VARCHAR(100),
    employer_name VARCHAR(255),
    years_employed FLOAT,
    annual_income FLOAT NOT NULL,
    monthly_expenses FLOAT,
    credit_score INT,
    credit_history_months INT,
    total_debt FLOAT DEFAULT 0.0,
    total_assets FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_customer_id (customer_id),
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_ssn (ssn),
    INDEX idx_is_active (is_active),
    INDEX idx_customer_email_phone (email, phone),
    INDEX idx_customer_ssn_name (ssn, first_name, last_name)
);

-- Table: loan_applications
CREATE TABLE IF NOT EXISTS loan_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id VARCHAR(50) UNIQUE NOT NULL,
    applicant_name VARCHAR(255) NOT NULL,
    applicant_email VARCHAR(255) NOT NULL,
    applicant_phone VARCHAR(20) NOT NULL,
    loan_amount FLOAT NOT NULL,
    loan_type VARCHAR(50) NOT NULL,
    loan_term_months INT NOT NULL,
    annual_income FLOAT NOT NULL,
    employment_status VARCHAR(50) NOT NULL,
    years_employed FLOAT NOT NULL,
    credit_score INT,
    existing_debt FLOAT DEFAULT 0.0,
    status ENUM('pending', 'under_review', 'approved', 'rejected', 'withdrawn') DEFAULT 'pending' NOT NULL,
    agent_notes TEXT,
    approval_reason TEXT,
    rejection_reason TEXT,
    risk_score FLOAT,
    approval_probability FLOAT,
    processed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_application_id (application_id),
    INDEX idx_email (applicant_email),
    INDEX idx_status (status)
);

-- Table: loan_decisions
CREATE TABLE IF NOT EXISTS loan_decisions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    decision_id VARCHAR(50) UNIQUE NOT NULL,
    loan_application_id INT NOT NULL,
    decision_status ENUM('approved', 'rejected', 'conditional', 'pending') NOT NULL,
    decision_reason ENUM('excellent_credit', 'good_income_to_debt', 'strong_credit_history',
                        'stable_employment', 'low_risk_profile', 'low_credit_score',
                        'high_debt_to_income', 'insufficient_income', 'poor_employment_history',
                        'high_risk_profile'),
    risk_score FLOAT NOT NULL,
    approval_probability FLOAT NOT NULL,
    approved_amount FLOAT,
    approved_term_months INT,
    interest_rate FLOAT,
    agent_analysis TEXT,
    primary_reasons TEXT,
    secondary_factors TEXT,
    recommendation_confidence FLOAT,
    requires_manual_review BOOLEAN DEFAULT FALSE,
    decision_made_by VARCHAR(100),
    decision_made_at DATETIME,
    conditions_for_approval TEXT,
    next_review_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (loan_application_id) REFERENCES loan_applications(id),
    INDEX idx_decision_id (decision_id),
    INDEX idx_app_id (loan_application_id),
    INDEX idx_decision_status (decision_status),
    INDEX idx_risk_score (risk_score)
);

-- Table: audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    audit_id VARCHAR(50) UNIQUE NOT NULL,
    entity_type ENUM('customer', 'loan_application', 'loan_decision', 'audit_log', 'system') NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    action_type ENUM('create', 'update', 'delete', 'view', 'approve', 'reject', 'assign', 'comment', 'export', 'system_action') NOT NULL,
    user_id VARCHAR(100),
    user_role VARCHAR(50),
    user_name VARCHAR(255),
    old_values TEXT,
    new_values TEXT,
    changes_description TEXT,
    action_reason TEXT,
    agent_notes TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    extra_context TEXT,
    related_audit_log_id INT,
    FOREIGN KEY (related_audit_log_id) REFERENCES audit_logs(id),
    INDEX idx_audit_id (audit_id),
    INDEX idx_entity_type (entity_type),
    INDEX idx_entity_id (entity_id),
    INDEX idx_action_type (action_type),
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_audit_entity (entity_type, entity_id),
    INDEX idx_audit_user_timestamp (user_id, timestamp),
    INDEX idx_audit_action_timestamp (action_type, timestamp)
);

-- ============================================================================
-- STEP 3: INSERT TEST DATA - SCENARIO 1: APPROVED APPLICATION
-- ============================================================================
-- This scenario: High credit score, good income, low debt, stable employment
-- Expected Result: APPROVED

INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn,
                       address, city, state, zip_code, employment_status, occupation, employer_name,
                       years_employed, annual_income, monthly_expenses, credit_score,
                       credit_history_months, total_debt, total_assets, notes)
VALUES
('CUST-001', 'John', 'Smith', 'john.smith@example.com', '+1-555-0101', '1985-03-15', '123-45-6789',
 '123 Main St', 'San Francisco', 'CA', '94105', 'Employed', 'Senior Software Engineer', 'Tech Corp',
 8, 150000, 3500, 750, 120, 12000, 350000, 'Excellent credit profile. High earner.');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone,
                              loan_amount, loan_type, loan_term_months, annual_income, employment_status,
                              years_employed, credit_score, existing_debt, status)
VALUES
('APP-001', 'John Smith', 'john.smith@example.com', '+1-555-0101',
 50000, 'Personal', 60, 150000, 'Employed', 8, 750, 5000, 'pending');

-- ============================================================================
-- STEP 4: INSERT TEST DATA - SCENARIO 2: REJECTED APPLICATION
-- ============================================================================
-- This scenario: Low credit score, insufficient income, high debt
-- Expected Result: REJECTED

INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn,
                       address, city, state, zip_code, employment_status, occupation, employer_name,
                       years_employed, annual_income, monthly_expenses, credit_score,
                       credit_history_months, total_debt, total_assets, notes)
VALUES
('CUST-002', 'Jane', 'Doe', 'jane.doe@example.com', '+1-555-0102', '1990-07-22', '234-56-7890',
 '456 Oak Ave', 'Phoenix', 'AZ', '85001', 'Employed', 'Retail Manager', 'Store Inc',
 2, 35000, 2800, 550, 36, 22000, 5000, 'Low credit score. High debt-to-income ratio.');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone,
                              loan_amount, loan_type, loan_term_months, annual_income, employment_status,
                              years_employed, credit_score, existing_debt, status)
VALUES
('APP-002', 'Jane Doe', 'jane.doe@example.com', '+1-555-0102',
 45000, 'Personal', 48, 35000, 'Employed', 2, 550, 18000, 'pending');

-- ============================================================================
-- STEP 5: INSERT TEST DATA - SCENARIO 3: MANUAL REVIEW APPLICATION
-- ============================================================================
-- This scenario: Borderline credit, new employment, decent income
-- Expected Result: MANUAL_REVIEW

INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn,
                       address, city, state, zip_code, employment_status, occupation, employer_name,
                       years_employed, annual_income, monthly_expenses, credit_score,
                       credit_history_months, total_debt, total_assets, notes)
VALUES
('CUST-003', 'Michael', 'Johnson', 'michael.johnson@example.com', '+1-555-0103', '1992-11-08', '345-67-8901',
 '789 Pine Rd', 'Denver', 'CO', '80202', 'Employed', 'Systems Administrator', 'IT Services LLC',
 1.5, 85000, 2200, 650, 48, 8500, 25000, 'New to current employer. Fair credit score.');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone,
                              loan_amount, loan_type, loan_term_months, annual_income, employment_status,
                              years_employed, credit_score, existing_debt, status)
VALUES
('APP-003', 'Michael Johnson', 'michael.johnson@example.com', '+1-555-0103',
 60000, 'Home', 180, 85000, 'Employed', 1.5, 650, 8000, 'pending');

-- ============================================================================
-- STEP 6: INSERT TEST DATA - SCENARIO 4: HIGH INCOME, EXCELLENT CREDIT
-- ============================================================================
-- This scenario: Highest income bracket, excellent credit, large loan
-- Expected Result: APPROVED with high confidence

INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn,
                       address, city, state, zip_code, employment_status, occupation, employer_name,
                       years_employed, annual_income, monthly_expenses, credit_score,
                       credit_history_months, total_debt, total_assets, notes)
VALUES
('CUST-004', 'Sarah', 'Williams', 'sarah.williams@example.com', '+1-555-0104', '1988-01-25', '456-78-9012',
 '321 Elm St', 'New York', 'NY', '10001', 'Employed', 'Chief Financial Officer', 'Fortune 500 Corp',
 12, 250000, 5000, 800, 180, 15000, 750000, 'Excellent financial profile. Executive position.');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone,
                              loan_amount, loan_type, loan_term_months, annual_income, employment_status,
                              years_employed, credit_score, existing_debt, status)
VALUES
('APP-004', 'Sarah Williams', 'sarah.williams@example.com', '+1-555-0104',
 200000, 'Home', 360, 250000, 'Employed', 12, 800, 8000, 'pending');

-- ============================================================================
-- STEP 7: INSERT TEST DATA - SCENARIO 5: SELF-EMPLOYED, AVERAGE PROFILE
-- ============================================================================
-- This scenario: Self-employed, moderate income, moderate credit
-- Expected Result: May require manual review or conditional approval

INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn,
                       address, city, state, zip_code, employment_status, occupation, employer_name,
                       years_employed, annual_income, monthly_expenses, credit_score,
                       credit_history_months, total_debt, total_assets, notes)
VALUES
('CUST-005', 'David', 'Brown', 'david.brown@example.com', '+1-555-0105', '1987-05-12', '567-89-0123',
 '654 Birch Lane', 'Austin', 'TX', '78701', 'Self-employed', 'Consultant', 'DB Consulting',
 5, 95000, 3000, 680, 84, 11000, 120000, 'Self-employed consultant. Stable business income.');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone,
                              loan_amount, loan_type, loan_term_months, annual_income, employment_status,
                              years_employed, credit_score, existing_debt, status)
VALUES
('APP-005', 'David Brown', 'david.brown@example.com', '+1-555-0105',
 75000, 'Auto', 72, 95000, 'Self-employed', 5, 680, 9000, 'pending');

-- ============================================================================
-- STEP 8: INSERT TEST DATA - SCENARIO 6: NO CREDIT HISTORY
-- ============================================================================
-- This scenario: No credit score, good income, new applicant
-- Expected Result: MANUAL_REVIEW (no credit data)

INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn,
                       address, city, state, zip_code, employment_status, occupation, employer_name,
                       years_employed, annual_income, monthly_expenses, credit_score,
                       credit_history_months, total_debt, total_assets, notes)
VALUES
('CUST-006', 'Emily', 'Garcia', 'emily.garcia@example.com', '+1-555-0106', '1995-09-30', '678-90-1234',
 '987 Spruce Way', 'Portland', 'OR', '97201', 'Employed', 'Junior Developer', 'StartUp Inc',
 1.2, 65000, 1800, NULL, NULL, 2000, 15000, 'Recent graduate. No credit history. Stable employment.');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone,
                              loan_amount, loan_type, loan_term_months, annual_income, employment_status,
                              years_employed, credit_score, existing_debt, status)
VALUES
('APP-006', 'Emily Garcia', 'emily.garcia@example.com', '+1-555-0106',
 30000, 'Personal', 48, 65000, 'Employed', 1.2, NULL, 1500, 'pending');

-- ============================================================================
-- STEP 9: INSERT LOAN DECISIONS - FOR APPROVED APPLICATIONS
-- ============================================================================

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, decision_reason,
                           risk_score, approval_probability, approved_amount, approved_term_months,
                           interest_rate, recommendation_confidence, requires_manual_review,
                           decision_made_by, conditions_for_approval)
VALUES
('DEC-001', (SELECT id FROM loan_applications WHERE application_id='APP-001'),
 'approved', 'excellent_credit', 0.15, 0.95, 50000, 60, 5.2, 0.95, FALSE, 'Agent_Profile',
 'Standard loan terms apply');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, decision_reason,
                           risk_score, approval_probability, approved_amount, approved_term_months,
                           interest_rate, recommendation_confidence, requires_manual_review,
                           decision_made_by, conditions_for_approval)
VALUES
('DEC-004', (SELECT id FROM loan_applications WHERE application_id='APP-004'),
 'approved', 'low_risk_profile', 0.08, 0.98, 200000, 360, 4.5, 0.98, FALSE, 'Agent_Profile',
 'Approved at requested amount. Premium rate available.');

-- ============================================================================
-- STEP 10: INSERT LOAN DECISIONS - FOR REJECTED APPLICATIONS
-- ============================================================================

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, decision_reason,
                           risk_score, approval_probability, recommendation_confidence,
                           requires_manual_review, decision_made_by)
VALUES
('DEC-002', (SELECT id FROM loan_applications WHERE application_id='APP-002'),
 'rejected', 'high_debt_to_income', 0.78, 0.05, 0.92, FALSE, 'Agent_Risk',
 'High debt-to-income ratio. Credit score below threshold.');

-- ============================================================================
-- STEP 11: INSERT LOAN DECISIONS - FOR MANUAL REVIEW APPLICATIONS
-- ============================================================================

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status,
                           risk_score, approval_probability, recommendation_confidence,
                           requires_manual_review, decision_made_by, agent_analysis)
VALUES
('DEC-003', (SELECT id FROM loan_applications WHERE application_id='APP-003'),
 'pending', 0.45, 0.55, 0.70, TRUE, 'Agent_Decision',
 'Borderline profile: New employment (1.5 years) but stable income. Fair credit score (650). Recommend manual underwriter review for employment verification.');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status,
                           risk_score, approval_probability, recommendation_confidence,
                           requires_manual_review, decision_made_by, agent_analysis)
VALUES
('DEC-005', (SELECT id FROM loan_applications WHERE application_id='APP-005'),
 'pending', 0.42, 0.58, 0.68, TRUE, 'Agent_Decision',
 'Self-employed applicant requires additional verification. Business tax returns needed for 2 years. Income documentation required.');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status,
                           risk_score, approval_probability, recommendation_confidence,
                           requires_manual_review, decision_made_by, agent_analysis)
VALUES
('DEC-006', (SELECT id FROM loan_applications WHERE application_id='APP-006'),
 'pending', 0.50, 0.52, 0.60, TRUE, 'Agent_Decision',
 'No credit history available. Applicant has stable employment and decent income. Recommend manual review. Consider co-signer or require secured application.');

-- ============================================================================
-- STEP 12: INSERT AUDIT LOGS - APPLICATION CREATION
-- ============================================================================

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, timestamp)
VALUES
('AUD-001', 'loan_application', 'APP-001', 'create', 'system', 'API',
 'Loan application submitted via portal', 'success', CURRENT_TIMESTAMP);

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, timestamp)
VALUES
('AUD-002', 'loan_application', 'APP-002', 'create', 'system', 'API',
 'Loan application submitted via portal', 'success', CURRENT_TIMESTAMP);

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, timestamp)
VALUES
('AUD-003', 'loan_application', 'APP-003', 'create', 'system', 'API',
 'Loan application submitted via portal', 'success', CURRENT_TIMESTAMP);

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, timestamp)
VALUES
('AUD-004', 'loan_application', 'APP-004', 'create', 'system', 'API',
 'Loan application submitted via portal', 'success', CURRENT_TIMESTAMP);

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, timestamp)
VALUES
('AUD-005', 'loan_application', 'APP-005', 'create', 'system', 'API',
 'Loan application submitted via portal', 'success', CURRENT_TIMESTAMP);

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, timestamp)
VALUES
('AUD-006', 'loan_application', 'APP-006', 'create', 'system', 'API',
 'Loan application submitted via portal', 'success', CURRENT_TIMESTAMP);

-- ============================================================================
-- STEP 13: INSERT AUDIT LOGS - DECISIONS MADE
-- ============================================================================

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, agent_notes, timestamp)
VALUES
('AUD-007', 'loan_decision', 'DEC-001', 'approve', 'agent', 'Profile_Agent',
 'Application approved: High credit score, strong income, low risk', 'success',
 'Excellent financial profile. Approved for full requested amount.', CURRENT_TIMESTAMP);

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, agent_notes, timestamp)
VALUES
('AUD-008', 'loan_decision', 'DEC-002', 'reject', 'agent', 'Risk_Agent',
 'Application rejected: High debt-to-income, low credit score', 'success',
 'DTI ratio exceeds acceptable threshold. Credit score below minimum requirement.', CURRENT_TIMESTAMP);

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name,
                       action_reason, status, agent_notes, timestamp)
VALUES
('AUD-009', 'loan_decision', 'DEC-003', 'assign', 'agent', 'Decision_Agent',
 'Application flagged for manual review: Borderline profile', 'success',
 'Requires human underwriter review due to new employment.', CURRENT_TIMESTAMP);

-- ============================================================================
-- VERIFICATION QUERIES - Use these to verify data
-- ============================================================================

-- Count all records in each table
-- SELECT 'Customers' as table_name, COUNT(*) as record_count FROM customers
-- UNION ALL
-- SELECT 'Loan Applications', COUNT(*) FROM loan_applications
-- UNION ALL
-- SELECT 'Loan Decisions', COUNT(*) FROM loan_decisions
-- UNION ALL
-- SELECT 'Audit Logs', COUNT(*) FROM audit_logs;

-- ============================================================================
-- QUERY: All Pending Applications
-- ============================================================================
-- SELECT
--     app.application_id,
--     app.applicant_name,
--     app.applicant_email,
--     app.loan_amount,
--     app.annual_income,
--     app.credit_score,
--     app.status,
--     app.created_at
-- FROM loan_applications app
-- WHERE app.status = 'pending'
-- ORDER BY app.created_at DESC;

-- ============================================================================
-- QUERY: Application with Decision Details
-- ============================================================================
-- SELECT
--     app.application_id,
--     app.applicant_name,
--     app.loan_amount,
--     app.credit_score,
--     app.annual_income,
--     dec.decision_id,
--     dec.decision_status,
--     dec.decision_reason,
--     ROUND(dec.risk_score, 2) as risk_score,
--     ROUND(dec.approval_probability * 100, 0) as approval_prob_percent,
--     app.status
-- FROM loan_applications app
-- LEFT JOIN loan_decisions dec ON app.id = dec.loan_application_id
-- ORDER BY app.created_at DESC;

-- ============================================================================
-- QUERY: Audit Trail for an Application
-- ============================================================================
-- SELECT
--     audit_id,
--     entity_type,
--     action_type,
--     user_name,
--     action_reason,
--     timestamp
-- FROM audit_logs
-- WHERE entity_id = 'APP-001'
-- ORDER BY timestamp ASC;

-- ============================================================================
-- QUERY: Decisions Summary
-- ============================================================================
-- SELECT
--     decision_status,
--     COUNT(*) as count,
--     ROUND(AVG(risk_score), 2) as avg_risk_score,
--     ROUND(AVG(approval_probability) * 100, 0) as avg_approval_prob_percent
-- FROM loan_decisions
-- GROUP BY decision_status;

-- ============================================================================
-- QUERY: High-Risk Applications (Risk Score > 0.7)
-- ============================================================================
-- SELECT
--     app.application_id,
--     app.applicant_name,
--     app.credit_score,
--     app.annual_income,
--     app.existing_debt,
--     dec.risk_score,
--     dec.decision_status
-- FROM loan_applications app
-- LEFT JOIN loan_decisions dec ON app.id = dec.loan_application_id
-- WHERE dec.risk_score > 0.7
-- ORDER BY dec.risk_score DESC;

-- ============================================================================
-- TESTING INSTRUCTIONS
-- ============================================================================
--
-- 1. RUN ALL STEPS 1-13 TO CREATE COMPLETE TEST ENVIRONMENT
--
-- 2. VERIFY DATA WAS INSERTED:
--    SELECT COUNT(*) FROM customers;                   -- Should return 6
--    SELECT COUNT(*) FROM loan_applications;          -- Should return 6
--    SELECT COUNT(*) FROM loan_decisions;             -- Should return 6
--    SELECT COUNT(*) FROM audit_logs;                 -- Should return 12+
--
-- 3. TEST SCENARIOS:
--    a) APP-001: Should be APPROVED (High credit, good income)
--    b) APP-002: Should be REJECTED (Low credit, high debt)
--    c) APP-003: Should be MANUAL_REVIEW (New employment)
--    d) APP-004: Should be APPROVED (Excellent profile)
--    e) APP-005: Should be MANUAL_REVIEW (Self-employed)
--    f) APP-006: Should be MANUAL_REVIEW (No credit history)
--
-- 4. RUN VERIFICATION QUERIES TO CONFIRM
--
-- ============================================================================
