-- ============================================================================
-- RS BANK LOAN APPROVAL SYSTEM - SQL QUERIES REFERENCE
-- Version: 1.0 | Date: July 5, 2026 | Status: Production Ready
-- ============================================================================

-- ============================================================================
-- SCHEMA CREATION (Run these to set up the database)
-- ============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS rsbank_loan;
USE rsbank_loan;

-- 1. Loan Applications Table
CREATE TABLE IF NOT EXISTS loan_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id VARCHAR(50) UNIQUE NOT NULL,
    applicant_name VARCHAR(100) NOT NULL,
    applicant_age INT NOT NULL,
    annual_income DECIMAL(15,2) NOT NULL,
    employment_type VARCHAR(50),
    employment_years INT,
    credit_score INT,
    location VARCHAR(100),
    loan_amount DECIMAL(15,2) NOT NULL,
    tenure_months INT NOT NULL,
    loan_purpose VARCHAR(50),
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_app_id (application_id),
    INDEX idx_status (status),
    INDEX idx_application_date (application_date),
    INDEX idx_applicant_name (applicant_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Applicants Table
CREATE TABLE IF NOT EXISTS applicants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    annual_income DECIMAL(15,2) NOT NULL,
    employment_type VARCHAR(50),
    employment_years INT,
    credit_score INT,
    existing_liabilities DECIMAL(15,2),
    total_assets DECIMAL(15,2),
    location VARCHAR(100),
    kyc_verified BOOLEAN DEFAULT FALSE,
    kyc_verified_date TIMESTAMP NULL,
    kyc_documents TEXT,
    payment_defaults INT DEFAULT 0,
    bankruptcy_history BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_kyc (kyc_verified),
    INDEX idx_credit_score (credit_score),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Credit History Table
CREATE TABLE IF NOT EXISTS credit_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) NOT NULL,
    credit_score INT NOT NULL,
    inquiry_type VARCHAR(50),
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_record_date (record_date),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Evaluations Table
CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluation_id VARCHAR(50) UNIQUE NOT NULL,
    application_id VARCHAR(50) NOT NULL,
    decision VARCHAR(50) NOT NULL,
    final_score DECIMAL(5,2),
    risk_level VARCHAR(50),
    agent_results LONGTEXT,
    explanation LONGTEXT,
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_eval_id (evaluation_id),
    INDEX idx_app_id (application_id),
    INDEX idx_decision (decision),
    INDEX idx_evaluation_date (evaluation_date),
    INDEX idx_risk_level (risk_level),
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluation_id VARCHAR(50),
    agent_name VARCHAR(100),
    action VARCHAR(100),
    details LONGTEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_eval_id (evaluation_id),
    INDEX idx_agent_name (agent_name),
    INDEX idx_timestamp (timestamp),
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. AML Screening Table
CREATE TABLE IF NOT EXISTS aml_screening (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) UNIQUE NOT NULL,
    aml_screened BOOLEAN DEFAULT FALSE,
    aml_status VARCHAR(50),
    flagged BOOLEAN DEFAULT FALSE,
    aml_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_flagged (flagged),
    INDEX idx_aml_date (aml_date),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ANALYSIS & REPORTING QUERIES
-- ============================================================================

-- 1. GET ALL APPLICATIONS WITH LATEST EVALUATION
SELECT
    la.application_id,
    la.applicant_name,
    la.applicant_age,
    la.annual_income,
    la.loan_amount,
    la.application_date,
    e.evaluation_id,
    e.decision,
    e.final_score,
    e.risk_level,
    e.evaluation_date
FROM loan_applications la
LEFT JOIN evaluations e ON la.application_id = e.application_id
ORDER BY la.application_date DESC;

-- 2. APPROVAL STATISTICS BY DECISION
SELECT
    e.decision,
    COUNT(*) as count,
    ROUND(AVG(e.final_score), 2) as avg_score,
    MIN(e.final_score) as min_score,
    MAX(e.final_score) as max_score,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM evaluations), 2) as percentage
FROM evaluations e
GROUP BY e.decision
ORDER BY COUNT(*) DESC;

-- 3. HIGH-RISK APPLICATIONS REQUIRING MANUAL REVIEW
SELECT
    e.evaluation_id,
    la.application_id,
    la.applicant_name,
    la.annual_income,
    la.loan_amount,
    a.credit_score,
    a.payment_defaults,
    a.bankruptcy_history,
    e.final_score,
    e.risk_level,
    e.decision,
    e.evaluation_date
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
JOIN applicants a ON la.applicant_id = a.applicant_id
WHERE e.risk_level IN ('HIGH', 'CRITICAL')
   OR e.decision = 'manual_review'
ORDER BY e.final_score ASC;

-- 4. KYC AND AML COMPLIANCE STATUS REPORT
SELECT
    a.applicant_id,
    a.name,
    a.age,
    a.kyc_verified,
    a.kyc_verified_date,
    am.aml_screened,
    am.aml_status,
    am.flagged,
    am.aml_date,
    CASE
        WHEN a.kyc_verified = FALSE THEN 'KYC PENDING'
        WHEN am.flagged = TRUE THEN 'AML FLAGGED'
        WHEN am.aml_screened = FALSE THEN 'AML PENDING'
        ELSE 'COMPLIANT'
    END as compliance_status
FROM applicants a
LEFT JOIN aml_screening am ON a.applicant_id = am.applicant_id
WHERE a.kyc_verified = FALSE
   OR am.flagged = TRUE
   OR am.aml_screened = FALSE
ORDER BY a.applicant_id;

-- 5. CREDIT HISTORY TREND FOR APPLICANT
SELECT
    applicant_id,
    record_date,
    credit_score,
    DATEDIFF(CURDATE(), DATE(record_date)) as days_ago,
    LAG(credit_score) OVER (PARTITION BY applicant_id ORDER BY record_date) as previous_score,
    credit_score - LAG(credit_score) OVER (PARTITION BY applicant_id ORDER BY record_date) as score_change
FROM credit_history
WHERE applicant_id = 'APP001'
ORDER BY record_date DESC
LIMIT 10;

-- 6. COMPLETE AUDIT TRAIL FOR APPLICATION
SELECT
    al.timestamp,
    al.agent_name,
    al.action,
    al.details,
    e.evaluation_id,
    la.application_id,
    e.decision
FROM audit_logs al
JOIN evaluations e ON al.evaluation_id = e.evaluation_id
JOIN loan_applications la ON e.application_id = la.application_id
WHERE e.application_id = 'LN000001'
ORDER BY al.timestamp ASC;

-- 7. APPLICATIONS IN MANUAL REVIEW
SELECT
    e.evaluation_id,
    la.application_id,
    la.applicant_name,
    la.annual_income,
    la.loan_amount,
    la.tenure_months,
    a.credit_score,
    a.payment_defaults,
    a.bankruptcy_history,
    e.final_score,
    e.risk_level,
    e.explanation,
    e.evaluation_date
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
JOIN applicants a ON la.applicant_id = a.applicant_id
WHERE e.decision = 'manual_review'
ORDER BY e.evaluation_date DESC;

-- 8. REJECTED APPLICATIONS - ROOT CAUSE ANALYSIS
SELECT
    e.evaluation_id,
    e.application_id,
    la.applicant_name,
    la.annual_income,
    la.credit_score as loan_app_score,
    ap.credit_score as applicant_score,
    ap.payment_defaults,
    ap.bankruptcy_history,
    e.final_score,
    e.agent_results,
    a.agent_name,
    a.action,
    a.details,
    e.evaluation_date
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
JOIN applicants ap ON la.applicant_id = ap.applicant_id
LEFT JOIN audit_logs a ON e.evaluation_id = a.evaluation_id
WHERE e.decision = 'rejected'
ORDER BY e.evaluation_date DESC;

-- 9. APPROVED APPLICATIONS - SUCCESS FACTORS
SELECT
    e.evaluation_id,
    e.application_id,
    la.applicant_name,
    la.annual_income,
    la.loan_amount,
    a.credit_score,
    a.employment_years,
    a.total_assets,
    a.existing_liabilities,
    e.final_score,
    e.risk_level,
    ROUND((a.total_assets - a.existing_liabilities) / a.total_assets * 100, 2) as net_worth_percent,
    ROUND(a.existing_liabilities / (a.annual_income / 12) * 100, 2) as dti_ratio,
    e.evaluation_date
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
JOIN applicants a ON la.applicant_id = a.applicant_id
WHERE e.decision = 'approved' AND e.final_score >= 80
ORDER BY e.final_score DESC;

-- ============================================================================
-- KEY METRICS & DASHBOARDS
-- ============================================================================

-- 10. OVERALL STATISTICS
SELECT
    (SELECT COUNT(*) FROM loan_applications) as total_applications,
    (SELECT COUNT(*) FROM evaluations WHERE decision = 'approved') as approved_count,
    (SELECT COUNT(*) FROM evaluations WHERE decision = 'rejected') as rejected_count,
    (SELECT COUNT(*) FROM evaluations WHERE decision = 'manual_review') as manual_review_count,
    (SELECT COUNT(*) FROM applicants WHERE kyc_verified = TRUE) as kyc_verified_count,
    (SELECT COUNT(*) FROM aml_screening WHERE flagged = TRUE) as aml_flagged_count;

-- 11. AVERAGE LOAN AMOUNT BY DECISION
SELECT
    e.decision,
    COUNT(*) as application_count,
    ROUND(AVG(la.loan_amount), 2) as avg_loan_amount,
    ROUND(SUM(la.loan_amount), 2) as total_loan_amount,
    ROUND(AVG(e.final_score), 2) as avg_score
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
GROUP BY e.decision
ORDER BY application_count DESC;

-- 12. PERFORMANCE BY RISK LEVEL
SELECT
    e.risk_level,
    COUNT(*) as count,
    ROUND(AVG(e.final_score), 2) as avg_score,
    SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN e.decision = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
    SUM(CASE WHEN e.decision = 'manual_review' THEN 1 ELSE 0 END) as manual_review_count,
    ROUND(SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate
FROM evaluations e
GROUP BY e.risk_level
ORDER BY FIELD(e.risk_level, 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

-- 13. APPLICANTS WITH PAYMENT DEFAULTS
SELECT
    a.applicant_id,
    a.name,
    a.age,
    a.credit_score,
    a.payment_defaults,
    a.bankruptcy_history,
    COUNT(e.evaluation_id) as evaluation_count,
    SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN e.decision = 'rejected' THEN 1 ELSE 0 END) as rejected_count
FROM applicants a
LEFT JOIN loan_applications la ON a.applicant_id = la.applicant_id
LEFT JOIN evaluations e ON la.application_id = e.application_id
WHERE a.payment_defaults > 0 OR a.bankruptcy_history = TRUE
GROUP BY a.applicant_id, a.name, a.age, a.credit_score, a.payment_defaults, a.bankruptcy_history
ORDER BY a.payment_defaults DESC, a.bankruptcy_history DESC;

-- 14. INCOME DISTRIBUTION BY DECISION
SELECT
    e.decision,
    COUNT(*) as count,
    ROUND(MIN(la.annual_income), 2) as min_income,
    ROUND(AVG(la.annual_income), 2) as avg_income,
    ROUND(MAX(la.annual_income), 2) as max_income,
    ROUND(STDDEV(la.annual_income), 2) as income_std_dev
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
GROUP BY e.decision
ORDER BY avg_income DESC;

-- 15. LOAN PURPOSE ANALYSIS
SELECT
    la.loan_purpose,
    COUNT(*) as count,
    ROUND(AVG(e.final_score), 2) as avg_score,
    SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) as approved_count,
    ROUND(SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate,
    ROUND(AVG(la.loan_amount), 2) as avg_loan_amount
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
GROUP BY la.loan_purpose
ORDER BY approval_rate DESC;

-- 16. EMPLOYMENT TYPE ANALYSIS
SELECT
    la.employment_type,
    COUNT(*) as count,
    ROUND(AVG(la.employment_years), 2) as avg_years,
    ROUND(AVG(la.credit_score), 2) as avg_credit_score,
    ROUND(AVG(e.final_score), 2) as avg_eval_score,
    SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) as approved_count,
    ROUND(SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as approval_rate
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
GROUP BY la.employment_type
ORDER BY approval_rate DESC;

-- ============================================================================
-- TIME-BASED ANALYTICS
-- ============================================================================

-- 17. APPLICATIONS BY DATE
SELECT
    DATE(la.application_date) as application_date,
    COUNT(*) as count,
    ROUND(AVG(e.final_score), 2) as avg_score,
    SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN e.decision = 'rejected' THEN 1 ELSE 0 END) as rejected
FROM loan_applications la
LEFT JOIN evaluations e ON la.application_id = e.application_id
GROUP BY DATE(la.application_date)
ORDER BY application_date DESC;

-- 18. EVALUATION TREND (LAST 30 DAYS)
SELECT
    DATE(e.evaluation_date) as evaluation_date,
    COUNT(*) as evaluations,
    ROUND(AVG(e.final_score), 2) as avg_score,
    SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN e.decision = 'rejected' THEN 1 ELSE 0 END) as rejected,
    SUM(CASE WHEN e.decision = 'manual_review' THEN 1 ELSE 0 END) as manual_review
FROM evaluations e
WHERE e.evaluation_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(e.evaluation_date)
ORDER BY evaluation_date DESC;

-- ============================================================================
-- MAINTENANCE & UTILITY QUERIES
-- ============================================================================

-- 19. DATABASE SIZE AND STATISTICS
SELECT
    TABLE_NAME,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as table_size_mb,
    TABLE_ROWS,
    ROUND((data_length / 1024 / 1024), 2) as data_size_mb,
    ROUND((index_length / 1024 / 1024), 2) as index_size_mb
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'rsbank_loan'
ORDER BY (data_length + index_length) DESC;

-- 20. CHECK FOR DUPLICATE APPLICATIONS
SELECT
    applicant_name,
    annual_income,
    credit_score,
    COUNT(*) as count
FROM loan_applications
GROUP BY applicant_name, annual_income, credit_score
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- 21. FIND MISSING EVALUATIONS
SELECT
    la.application_id,
    la.applicant_name,
    la.application_date
FROM loan_applications la
LEFT JOIN evaluations e ON la.application_id = e.application_id
WHERE e.evaluation_id IS NULL
ORDER BY la.application_date DESC;

-- 22. CLEANUP: DELETE OLD AUDIT LOGS (OLDER THAN 1 YEAR)
-- DELETE FROM audit_logs
-- WHERE timestamp < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- 23. BACKUP: EXPORT EVALUATIONS
-- SELECT * FROM evaluations
-- INTO OUTFILE '/tmp/evaluations_backup.csv'
-- FIELDS TERMINATED BY ','
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n';

-- ============================================================================
-- USER & PERMISSION MANAGEMENT
-- ============================================================================

-- 24. CREATE READ-ONLY USER
-- CREATE USER 'rsbank_readonly'@'localhost' IDENTIFIED BY 'readonly_pass';
-- GRANT SELECT ON rsbank_loan.* TO 'rsbank_readonly'@'localhost';
-- FLUSH PRIVILEGES;

-- 25. CREATE REPORTING USER
-- CREATE USER 'rsbank_reporting'@'localhost' IDENTIFIED BY 'reporting_pass';
-- GRANT SELECT, INSERT ON rsbank_loan.evaluations TO 'rsbank_reporting'@'localhost';
-- GRANT SELECT ON rsbank_loan.audit_logs TO 'rsbank_reporting'@'localhost';
-- FLUSH PRIVILEGES;

-- ============================================================================
-- END OF SQL QUERIES
-- ============================================================================
