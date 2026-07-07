-- ============================================================================
-- AGENTIC LOAN APPROVAL SYSTEM - COMPLETE DATABASE SETUP
-- Copy and paste everything into MySQL Workbench and execute
-- ============================================================================

USE mysql;
CREATE DATABASE IF NOT EXISTS loan_approval_db;
USE loan_approval_db;

-- ============================================================================
-- CREATE TABLES
-- ============================================================================

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
    INDEX idx_ssn (ssn)
);

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
    INDEX idx_decision_status (decision_status)
);

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
    INDEX idx_entity_id (entity_id),
    INDEX idx_action_type (action_type),
    INDEX idx_timestamp (timestamp)
);

-- ============================================================================
-- INSERT TEST DATA - SCENARIO 1: APPROVED (High Credit, Good Income)
-- ============================================================================
INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, occupation, employer_name, years_employed, annual_income, monthly_expenses, credit_score, credit_history_months, total_debt, total_assets, notes)
VALUES ('CUST-001', 'John', 'Smith', 'john.smith@example.com', '+1-555-0101', '1985-03-15', '123-45-6789', '123 Main St', 'San Francisco', 'CA', '94105', 'Employed', 'Software Engineer', 'Tech Corp', 8, 150000, 3500, 750, 120, 12000, 350000, 'Excellent profile');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone, loan_amount, loan_type, loan_term_months, annual_income, employment_status, years_employed, credit_score, existing_debt, status)
VALUES ('APP-001', 'John Smith', 'john.smith@example.com', '+1-555-0101', 50000, 'Personal', 60, 150000, 'Employed', 8, 750, 5000, 'pending');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, decision_reason, risk_score, approval_probability, approved_amount, approved_term_months, interest_rate, recommendation_confidence, requires_manual_review, decision_made_by, conditions_for_approval)
VALUES ('DEC-001', 1, 'approved', 'excellent_credit', 0.15, 0.95, 50000, 60, 5.2, 0.95, FALSE, 'Agent_Profile', 'Standard terms');

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name, action_reason, status, timestamp)
VALUES ('AUD-001', 'loan_application', 'APP-001', 'create', 'system', 'API', 'Application submitted', 'success', CURRENT_TIMESTAMP);

-- ============================================================================
-- INSERT TEST DATA - SCENARIO 2: REJECTED (Low Credit, High Debt)
-- ============================================================================
INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, occupation, employer_name, years_employed, annual_income, monthly_expenses, credit_score, credit_history_months, total_debt, total_assets, notes)
VALUES ('CUST-002', 'Jane', 'Doe', 'jane.doe@example.com', '+1-555-0102', '1990-07-22', '234-56-7890', '456 Oak Ave', 'Phoenix', 'AZ', '85001', 'Employed', 'Retail Manager', 'Store Inc', 2, 35000, 2800, 550, 36, 22000, 5000, 'Low credit');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone, loan_amount, loan_type, loan_term_months, annual_income, employment_status, years_employed, credit_score, existing_debt, status)
VALUES ('APP-002', 'Jane Doe', 'jane.doe@example.com', '+1-555-0102', 45000, 'Personal', 48, 35000, 'Employed', 2, 550, 18000, 'pending');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, decision_reason, risk_score, approval_probability, recommendation_confidence, requires_manual_review, decision_made_by)
VALUES ('DEC-002', 2, 'rejected', 'high_debt_to_income', 0.78, 0.05, 0.92, FALSE, 'Agent_Risk');

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name, action_reason, status, timestamp)
VALUES ('AUD-002', 'loan_application', 'APP-002', 'create', 'system', 'API', 'Application submitted', 'success', CURRENT_TIMESTAMP);

-- ============================================================================
-- INSERT TEST DATA - SCENARIO 3: MANUAL REVIEW (New Employment)
-- ============================================================================
INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, occupation, employer_name, years_employed, annual_income, monthly_expenses, credit_score, credit_history_months, total_debt, total_assets, notes)
VALUES ('CUST-003', 'Michael', 'Johnson', 'michael.johnson@example.com', '+1-555-0103', '1992-11-08', '345-67-8901', '789 Pine Rd', 'Denver', 'CO', '80202', 'Employed', 'Systems Admin', 'IT Services LLC', 1.5, 85000, 2200, 650, 48, 8500, 25000, 'New employer');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone, loan_amount, loan_type, loan_term_months, annual_income, employment_status, years_employed, credit_score, existing_debt, status)
VALUES ('APP-003', 'Michael Johnson', 'michael.johnson@example.com', '+1-555-0103', 60000, 'Home', 180, 85000, 'Employed', 1.5, 650, 8000, 'pending');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, risk_score, approval_probability, recommendation_confidence, requires_manual_review, decision_made_by, agent_analysis)
VALUES ('DEC-003', 3, 'pending', 0.45, 0.55, 0.70, TRUE, 'Agent_Decision', 'New employment needs verification');

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name, action_reason, status, timestamp)
VALUES ('AUD-003', 'loan_application', 'APP-003', 'create', 'system', 'API', 'Application submitted', 'success', CURRENT_TIMESTAMP);

-- ============================================================================
-- INSERT TEST DATA - SCENARIO 4: APPROVED (Excellent Profile, Large Loan)
-- ============================================================================
INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, occupation, employer_name, years_employed, annual_income, monthly_expenses, credit_score, credit_history_months, total_debt, total_assets, notes)
VALUES ('CUST-004', 'Sarah', 'Williams', 'sarah.williams@example.com', '+1-555-0104', '1988-01-25', '456-78-9012', '321 Elm St', 'New York', 'NY', '10001', 'Employed', 'CFO', 'Fortune 500', 12, 250000, 5000, 800, 180, 15000, 750000, 'Excellent');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone, loan_amount, loan_type, loan_term_months, annual_income, employment_status, years_employed, credit_score, existing_debt, status)
VALUES ('APP-004', 'Sarah Williams', 'sarah.williams@example.com', '+1-555-0104', 200000, 'Home', 360, 250000, 'Employed', 12, 800, 8000, 'pending');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, decision_reason, risk_score, approval_probability, approved_amount, approved_term_months, interest_rate, recommendation_confidence, requires_manual_review, decision_made_by, conditions_for_approval)
VALUES ('DEC-004', 4, 'approved', 'low_risk_profile', 0.08, 0.98, 200000, 360, 4.5, 0.98, FALSE, 'Agent_Profile', 'Premium rate available');

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name, action_reason, status, timestamp)
VALUES ('AUD-004', 'loan_application', 'APP-004', 'create', 'system', 'API', 'Application submitted', 'success', CURRENT_TIMESTAMP);

-- ============================================================================
-- INSERT TEST DATA - SCENARIO 5: MANUAL REVIEW (Self-Employed)
-- ============================================================================
INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, occupation, employer_name, years_employed, annual_income, monthly_expenses, credit_score, credit_history_months, total_debt, total_assets, notes)
VALUES ('CUST-005', 'David', 'Brown', 'david.brown@example.com', '+1-555-0105', '1987-05-12', '567-89-0123', '654 Birch Lane', 'Austin', 'TX', '78701', 'Self-employed', 'Consultant', 'DB Consulting', 5, 95000, 3000, 680, 84, 11000, 120000, 'Self-employed');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone, loan_amount, loan_type, loan_term_months, annual_income, employment_status, years_employed, credit_score, existing_debt, status)
VALUES ('APP-005', 'David Brown', 'david.brown@example.com', '+1-555-0105', 75000, 'Auto', 72, 95000, 'Self-employed', 5, 680, 9000, 'pending');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, risk_score, approval_probability, recommendation_confidence, requires_manual_review, decision_made_by, agent_analysis)
VALUES ('DEC-005', 5, 'pending', 0.42, 0.58, 0.68, TRUE, 'Agent_Decision', 'Self-employed needs tax return verification');

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name, action_reason, status, timestamp)
VALUES ('AUD-005', 'loan_application', 'APP-005', 'create', 'system', 'API', 'Application submitted', 'success', CURRENT_TIMESTAMP);

-- ============================================================================
-- INSERT TEST DATA - SCENARIO 6: MANUAL REVIEW (No Credit History)
-- ============================================================================
INSERT INTO customers (customer_id, first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, occupation, employer_name, years_employed, annual_income, monthly_expenses, credit_score, credit_history_months, total_debt, total_assets, notes)
VALUES ('CUST-006', 'Emily', 'Garcia', 'emily.garcia@example.com', '+1-555-0106', '1995-09-30', '678-90-1234', '987 Spruce Way', 'Portland', 'OR', '97201', 'Employed', 'Junior Dev', 'StartUp Inc', 1.2, 65000, 1800, NULL, NULL, 2000, 15000, 'No credit history');

INSERT INTO loan_applications (application_id, applicant_name, applicant_email, applicant_phone, loan_amount, loan_type, loan_term_months, annual_income, employment_status, years_employed, credit_score, existing_debt, status)
VALUES ('APP-006', 'Emily Garcia', 'emily.garcia@example.com', '+1-555-0106', 30000, 'Personal', 48, 65000, 'Employed', 1.2, NULL, 1500, 'pending');

INSERT INTO loan_decisions (decision_id, loan_application_id, decision_status, risk_score, approval_probability, recommendation_confidence, requires_manual_review, decision_made_by, agent_analysis)
VALUES ('DEC-006', 6, 'pending', 0.50, 0.52, 0.60, TRUE, 'Agent_Decision', 'No credit history - consider co-signer');

INSERT INTO audit_logs (audit_id, entity_type, entity_id, action_type, user_role, user_name, action_reason, status, timestamp)
VALUES ('AUD-006', 'loan_application', 'APP-006', 'create', 'system', 'API', 'Application submitted', 'success', CURRENT_TIMESTAMP);

-- ============================================================================
-- VERIFICATION QUERIES (Run separately to verify data)
-- ============================================================================

-- 1. Count records
-- SELECT 'Customers' as table_name, COUNT(*) as count FROM customers
-- UNION ALL SELECT 'Loan Applications', COUNT(*) FROM loan_applications
-- UNION ALL SELECT 'Loan Decisions', COUNT(*) FROM loan_decisions
-- UNION ALL SELECT 'Audit Logs', COUNT(*) FROM audit_logs;

-- 2. All applications with decisions
-- SELECT a.application_id, a.applicant_name, a.credit_score, a.loan_amount,
--        d.decision_status, ROUND(d.risk_score, 2) as risk_score,
--        ROUND(d.approval_probability * 100, 0) as approval_prob_percent
-- FROM loan_applications a
-- LEFT JOIN loan_decisions d ON a.id = d.loan_application_id
-- ORDER BY a.created_at DESC;

-- 3. Decision summary
-- SELECT decision_status, COUNT(*) as count, ROUND(AVG(risk_score), 2) as avg_risk
-- FROM loan_decisions GROUP BY decision_status;

-- ============================================================================
-- END OF SETUP
-- ============================================================================
