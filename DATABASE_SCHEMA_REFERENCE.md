# 🏦 RS Bank Loan Approval System - Database Schema Reference

**Version**: 1.0  
**Date**: July 5, 2026  
**Status**: ✅ Production Ready

---

## 📊 Database Overview

- **Database Name**: `rsbank_loan`
- **Total Tables**: 6
- **Total Columns**: 45+
- **Indexes**: 15+
- **Foreign Keys**: 4

---

## 🗂️ Tables & Schema

### 1. **loan_applications** - Main Loan Applications Table

**Purpose**: Store all loan application submissions

```sql
CREATE TABLE loan_applications (
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
    INDEX idx_application_date (application_date)
);
```

**Columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Auto-increment primary key | 1, 2, 3... |
| application_id | VARCHAR(50) | Unique application identifier | LN000001 |
| applicant_name | VARCHAR(100) | Full name of applicant | Rajesh Kumar |
| applicant_age | INT | Age of applicant | 38 |
| annual_income | DECIMAL(15,2) | Annual gross income | 2000000.00 |
| employment_type | VARCHAR(50) | Type of employment | employed, self-employed |
| employment_years | INT | Years in current employment | 12 |
| credit_score | INT | CIBIL/Credit score | 795 |
| location | VARCHAR(100) | City/Location | Mumbai, Bangalore |
| loan_amount | DECIMAL(15,2) | Requested loan amount | 5000000.00 |
| tenure_months | INT | Loan tenure in months | 60 |
| loan_purpose | VARCHAR(50) | Purpose of loan | home, auto, education |
| application_date | TIMESTAMP | When application was submitted | 2026-07-05 10:30:45 |
| status | VARCHAR(50) | Current status | pending, approved, rejected, manual_review |
| updated_date | TIMESTAMP | Last update timestamp | 2026-07-05 10:30:45 |

**Indexes**:
- `idx_app_id` - For quick lookup by application_id
- `idx_status` - For filtering by status
- `idx_application_date` - For date range queries

**Sample Query**:
```sql
SELECT * FROM loan_applications 
WHERE status = 'approved' AND application_date >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

---

### 2. **applicants** - Applicant Profiles Table

**Purpose**: Store detailed applicant information and KYC verification status

```sql
CREATE TABLE applicants (
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
    kyc_verified_date TIMESTAMP,
    kyc_documents TEXT,
    payment_defaults INT DEFAULT 0,
    bankruptcy_history BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_kyc (kyc_verified),
    INDEX idx_credit_score (credit_score)
);
```

**Columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Primary key | 1, 2, 3... |
| applicant_id | VARCHAR(50) | Unique applicant ID | APP001 |
| name | VARCHAR(100) | Applicant name | Rajesh Kumar |
| age | INT | Age | 38 |
| annual_income | DECIMAL(15,2) | Annual income | 2000000.00 |
| employment_type | VARCHAR(50) | Job type | employed, self-employed |
| employment_years | INT | Years employed | 12 |
| credit_score | INT | Credit score | 795 |
| existing_liabilities | DECIMAL(15,2) | Current debts | 500000.00 |
| total_assets | DECIMAL(15,2) | Total assets | 1500000.00 |
| location | VARCHAR(100) | City | Mumbai |
| kyc_verified | BOOLEAN | KYC status | TRUE/FALSE |
| kyc_verified_date | TIMESTAMP | When KYC verified | 2026-07-01 14:20:00 |
| kyc_documents | TEXT | JSON list of documents | ["aadhar", "pan", "passport"] |
| payment_defaults | INT | Number of defaults | 0, 1, 2... |
| bankruptcy_history | BOOLEAN | Bankruptcy flag | FALSE |
| created_date | TIMESTAMP | Profile creation date | 2026-07-01 10:00:00 |

**Indexes**:
- `idx_applicant_id` - Primary lookup
- `idx_kyc` - For KYC status queries
- `idx_credit_score` - For credit-based filtering

**Sample Query**:
```sql
SELECT * FROM applicants 
WHERE kyc_verified = TRUE AND credit_score >= 750 AND payment_defaults = 0;
```

---

### 3. **credit_history** - Credit Records Table

**Purpose**: Maintain historical credit inquiry records

```sql
CREATE TABLE credit_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) NOT NULL,
    credit_score INT NOT NULL,
    inquiry_type VARCHAR(50),
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_record_date (record_date),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);
```

**Columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Primary key | 1, 2, 3... |
| applicant_id | VARCHAR(50) | Applicant reference | APP001 |
| credit_score | INT | Credit score at inquiry | 795 |
| inquiry_type | VARCHAR(50) | Type of inquiry | hard, soft |
| record_date | TIMESTAMP | Date of inquiry | 2026-07-05 10:30:45 |

**Foreign Key**:
- `applicant_id` → `applicants.applicant_id`

**Indexes**:
- `idx_applicant_id` - Link to applicant
- `idx_record_date` - Time-based queries

**Sample Query**:
```sql
SELECT * FROM credit_history 
WHERE applicant_id = 'APP001' 
ORDER BY record_date DESC LIMIT 5;
```

---

### 4. **evaluations** - Loan Evaluation Results Table

**Purpose**: Store evaluation results and decisions

```sql
CREATE TABLE evaluations (
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
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
);
```

**Columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Primary key | 1, 2, 3... |
| evaluation_id | VARCHAR(50) | Unique evaluation ID | EVAL000001 |
| application_id | VARCHAR(50) | Linked application | LN000001 |
| decision | VARCHAR(50) | Final decision | approved, rejected, manual_review |
| final_score | DECIMAL(5,2) | Composite score (0-100) | 87.6 |
| risk_level | VARCHAR(50) | Risk assessment | LOW, MEDIUM, HIGH, CRITICAL |
| agent_results | LONGTEXT | JSON of all agent scores | {"document": 93, "credit": 90...} |
| explanation | LONGTEXT | Decision explanation | JSON explanation |
| evaluation_date | TIMESTAMP | Evaluation timestamp | 2026-07-05 10:30:45 |

**Foreign Key**:
- `application_id` → `loan_applications.application_id`

**Indexes**:
- `idx_eval_id` - Primary lookup
- `idx_app_id` - Link to application
- `idx_decision` - Decision-based filtering
- `idx_evaluation_date` - Date range queries

**Sample Query**:
```sql
SELECT 
    e.evaluation_id,
    e.application_id,
    e.decision,
    e.final_score,
    la.applicant_name
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
WHERE e.decision = 'approved' AND e.final_score >= 80
ORDER BY e.evaluation_date DESC;
```

---

### 5. **audit_logs** - Audit Trail Table

**Purpose**: Complete audit trail of all operations

```sql
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluation_id VARCHAR(50),
    agent_name VARCHAR(100),
    action VARCHAR(100),
    details LONGTEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_eval_id (evaluation_id),
    INDEX idx_agent_name (agent_name),
    INDEX idx_timestamp (timestamp),
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id)
);
```

**Columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Primary key | 1, 2, 3... |
| evaluation_id | VARCHAR(50) | Evaluation reference | EVAL000001 |
| agent_name | VARCHAR(100) | Agent that performed action | Document Verification Agent |
| action | VARCHAR(100) | Action performed | analyzed, evaluated, flagged |
| details | LONGTEXT | JSON details | {"score": 93, "status": "completed"} |
| timestamp | TIMESTAMP | When action occurred | 2026-07-05 10:30:45 |

**Foreign Key**:
- `evaluation_id` → `evaluations.evaluation_id`

**Indexes**:
- `idx_eval_id` - Evaluation lookup
- `idx_agent_name` - Agent-based filtering
- `idx_timestamp` - Time range queries

**Sample Query**:
```sql
SELECT * FROM audit_logs 
WHERE evaluation_id = 'EVAL000001' 
ORDER BY timestamp ASC;
```

---

### 6. **aml_screening** - AML/KYC Compliance Table

**Purpose**: Track AML screening and compliance verification

```sql
CREATE TABLE aml_screening (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) UNIQUE NOT NULL,
    aml_screened BOOLEAN DEFAULT FALSE,
    aml_status VARCHAR(50),
    flagged BOOLEAN DEFAULT FALSE,
    aml_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_flagged (flagged),
    INDEX idx_aml_date (aml_date),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);
```

**Columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Primary key | 1, 2, 3... |
| applicant_id | VARCHAR(50) | Applicant reference | APP001 |
| aml_screened | BOOLEAN | Has been screened | TRUE/FALSE |
| aml_status | VARCHAR(50) | Screening status | approved, pending, flagged |
| flagged | BOOLEAN | Is flagged for review | TRUE/FALSE |
| aml_date | TIMESTAMP | Screening date | 2026-07-05 10:30:45 |

**Foreign Key**:
- `applicant_id` → `applicants.applicant_id`

**Indexes**:
- `idx_applicant_id` - Primary lookup
- `idx_flagged` - High-risk screening
- `idx_aml_date` - Compliance date tracking

**Sample Query**:
```sql
SELECT * FROM aml_screening 
WHERE flagged = TRUE AND aml_screened = TRUE;
```

---

## 🔗 Relationships Diagram

```
┌─────────────────────────┐
│  loan_applications      │
│  (PK: id)               │
│  (UQ: application_id)   │
└────────┬────────────────┘
         │
         │ application_id
         ├──────────────────┬─────────────────┐
         │                  │                 │
         ▼                  ▼                 ▼
    ┌────────────┐   ┌────────────┐   ┌────────────┐
    │applicants  │   │evaluations │   │audit_logs  │
    │(PK: id)    │   │(PK: id)    │   │(PK: id)    │
    │(UQ: appID) │   │(UQ: evalID)│   │            │
    └────┬───────┘   └──┬────┬────┘   └────────────┘
         │              │    │
         │ appID        │    │ evalID
         │            evalID  │
         ├─────────┐         │
         │         │         │
         ▼         ▼         ▼
    ┌────────────────────────────────┐
    │  credit_history                │
    │  (PK: id)                      │
    │  (FK: applicant_id)            │
    └────────────────────────────────┘

    ┌────────────────────────────────┐
    │  aml_screening                 │
    │  (PK: id)                      │
    │  (UQ, FK: applicant_id)        │
    └────────────────────────────────┘
```

---

## 📋 Complete Foreign Key Relationships

```
applicants.applicant_id ─────────┐
                                 ├─→ credit_history.applicant_id
                                 ├─→ aml_screening.applicant_id
loan_applications.application_id ─────────┐
                                          ├─→ evaluations.application_id
evaluations.evaluation_id ─────────────→ audit_logs.evaluation_id
```

---

## 🔍 Useful SQL Queries

### 1. **All Applications with Latest Evaluation**
```sql
SELECT 
    la.application_id,
    la.applicant_name,
    la.loan_amount,
    e.decision,
    e.final_score,
    e.evaluation_date
FROM loan_applications la
LEFT JOIN evaluations e ON la.application_id = e.application_id
ORDER BY la.application_date DESC;
```

### 2. **Approval Statistics by Decision**
```sql
SELECT 
    decision,
    COUNT(*) as count,
    AVG(final_score) as avg_score,
    MIN(final_score) as min_score,
    MAX(final_score) as max_score
FROM evaluations
GROUP BY decision;
```

### 3. **High-Risk Applications Requiring Review**
```sql
SELECT 
    e.evaluation_id,
    la.applicant_name,
    e.final_score,
    e.risk_level,
    e.decision
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
WHERE e.risk_level IN ('HIGH', 'CRITICAL') 
ORDER BY e.final_score ASC;
```

### 4. **KYC and AML Status Report**
```sql
SELECT 
    a.applicant_id,
    a.name,
    a.kyc_verified,
    a.kyc_verified_date,
    am.aml_screened,
    am.flagged,
    am.aml_status
FROM applicants a
LEFT JOIN aml_screening am ON a.applicant_id = am.applicant_id
WHERE a.kyc_verified = FALSE OR am.flagged = TRUE;
```

### 5. **Credit History Trend for Applicant**
```sql
SELECT 
    record_date,
    credit_score,
    DATEDIFF(CURDATE(), DATE(record_date)) as days_ago
FROM credit_history
WHERE applicant_id = 'APP001'
ORDER BY record_date DESC
LIMIT 10;
```

### 6. **Audit Trail for Application**
```sql
SELECT 
    al.timestamp,
    al.agent_name,
    al.action,
    al.details
FROM audit_logs al
JOIN evaluations e ON al.evaluation_id = e.evaluation_id
WHERE e.application_id = 'LN000001'
ORDER BY al.timestamp ASC;
```

### 7. **Applications in Manual Review with Agent Details**
```sql
SELECT 
    la.application_id,
    la.applicant_name,
    la.annual_income,
    e.final_score,
    e.agent_results,
    e.explanation
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
WHERE e.decision = 'manual_review'
ORDER BY e.evaluation_date DESC;
```

### 8. **Rejected Applications Analysis**
```sql
SELECT 
    e.evaluation_id,
    la.applicant_name,
    e.final_score,
    ap.payment_defaults,
    ap.bankruptcy_history,
    a.agent_name,
    a.action,
    a.details
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
JOIN applicants ap ON la.applicant_id = ap.applicant_id
LEFT JOIN audit_logs a ON e.evaluation_id = a.evaluation_id
WHERE e.decision = 'rejected'
ORDER BY e.evaluation_date DESC;
```

---

## 📊 Key Metrics Queries

### **Total Applications by Status**
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
FROM loan_applications;
```

### **Average Loan Amount by Decision**
```sql
SELECT 
    e.decision,
    COUNT(*) as count,
    AVG(la.loan_amount) as avg_amount,
    SUM(la.loan_amount) as total_amount
FROM evaluations e
JOIN loan_applications la ON e.application_id = la.application_id
GROUP BY e.decision;
```

### **Performance by Risk Level**
```sql
SELECT 
    e.risk_level,
    COUNT(*) as count,
    AVG(e.final_score) as avg_score,
    SUM(CASE WHEN e.decision = 'approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN e.decision = 'rejected' THEN 1 ELSE 0 END) as rejected_count
FROM evaluations e
GROUP BY e.risk_level
ORDER BY FIELD(e.risk_level, 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
```

---

## 🗄️ Database Initialization

### **Create All Tables**
```bash
# Execute the schema initialization
python3 mcp_mysql_server.py

# Or manually
mysql -u rsbank_user -p rsbank_loan < schema.sql
```

### **Check Table Creation**
```sql
USE rsbank_loan;
SHOW TABLES;
DESCRIBE loan_applications;
DESCRIBE applicants;
DESCRIBE credit_history;
DESCRIBE evaluations;
DESCRIBE audit_logs;
DESCRIBE aml_screening;
```

---

## 🔐 Data Security & Compliance

- ✅ **Audit Trail** - All operations logged in `audit_logs`
- ✅ **KYC Verification** - Tracked in `applicants` table
- ✅ **AML Screening** - Complete in `aml_screening` table
- ✅ **Data Encryption** - Configure in production
- ✅ **Regular Backups** - Schedule daily backups
- ✅ **Access Control** - Use database user roles

---

## 📈 Performance Tips

1. **Index Strategy**
   - Query by `application_id`, `evaluation_id` frequently → use indexes
   - Date range queries → use `evaluation_date` index
   - Filter by decision → use `idx_decision` index

2. **Query Optimization**
   ```sql
   -- Use EXPLAIN to analyze
   EXPLAIN SELECT * FROM evaluations WHERE decision = 'approved';
   ```

3. **Connection Pooling**
   - Implement for high traffic
   - Min pool size: 5, Max pool size: 20

---

## ✅ Validation Checklist

- [ ] Database `rsbank_loan` created
- [ ] All 6 tables created
- [ ] Foreign keys established
- [ ] Indexes created
- [ ] Test data inserted
- [ ] Queries validated
- [ ] Backups configured
- [ ] Security policies enforced

---

## 📞 Support

For database issues:
1. Check MySQL logs: `/var/log/mysql/error.log`
2. Verify connections: `mysql -u rsbank_user -p rsbank_loan`
3. Review audit logs for issues

---

**Created**: July 5, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0
