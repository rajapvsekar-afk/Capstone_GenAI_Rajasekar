# 📊 RS Bank Loan Approval System - Database Tables Summary

**Quick Reference Guide**  
**Version**: 1.0 | **Date**: July 5, 2026 | **Status**: ✅ Production Ready

---

## 🗂️ Table Structure at a Glance

### **TABLE 1: loan_applications**
**Purpose**: Store all loan application submissions

| Field | Type | Purpose |
|-------|------|---------|
| id | INT AUTO_INCREMENT | Unique row identifier |
| application_id | VARCHAR(50) UNIQUE | Unique application number (e.g., LN000001) |
| applicant_name | VARCHAR(100) | Full name of applicant |
| applicant_age | INT | Age of applicant |
| annual_income | DECIMAL(15,2) | Annual gross income |
| employment_type | VARCHAR(50) | employed, self-employed, retired |
| employment_years | INT | Years in current employment |
| credit_score | INT | CIBIL credit score (300-900) |
| location | VARCHAR(100) | City/Location |
| loan_amount | DECIMAL(15,2) | Requested loan amount |
| tenure_months | INT | Loan tenure in months |
| loan_purpose | VARCHAR(50) | home, auto, education, personal |
| application_date | TIMESTAMP | When application was submitted |
| status | VARCHAR(50) | pending, approved, rejected, manual_review |
| updated_date | TIMESTAMP | Last update time |

**Indexes**: `idx_app_id`, `idx_status`, `idx_application_date`

**Example Data**:
```
application_id: LN000001
applicant_name: Rajesh Kumar
annual_income: 2000000.00
loan_amount: 5000000.00
status: approved
```

---

### **TABLE 2: applicants**
**Purpose**: Detailed applicant profiles and KYC verification

| Field | Type | Purpose |
|-------|------|---------|
| id | INT AUTO_INCREMENT | Unique row identifier |
| applicant_id | VARCHAR(50) UNIQUE | Unique applicant ID (e.g., APP001) |
| name | VARCHAR(100) | Applicant name |
| age | INT | Age |
| annual_income | DECIMAL(15,2) | Annual income |
| employment_type | VARCHAR(50) | Type of employment |
| employment_years | INT | Years employed |
| credit_score | INT | Credit score |
| existing_liabilities | DECIMAL(15,2) | Current debts |
| total_assets | DECIMAL(15,2) | Total assets |
| location | VARCHAR(100) | City |
| kyc_verified | BOOLEAN | KYC verification status (TRUE/FALSE) |
| kyc_verified_date | TIMESTAMP | When KYC was verified |
| kyc_documents | TEXT | JSON list of documents |
| payment_defaults | INT | Number of payment defaults |
| bankruptcy_history | BOOLEAN | Has bankruptcy history |
| created_date | TIMESTAMP | Profile creation date |

**Indexes**: `idx_applicant_id`, `idx_kyc`, `idx_credit_score`

**Example Data**:
```
applicant_id: APP001
name: Rajesh Kumar
kyc_verified: TRUE
payment_defaults: 0
bankruptcy_history: FALSE
```

---

### **TABLE 3: credit_history**
**Purpose**: Track historical credit inquiry records

| Field | Type | Purpose |
|-------|------|---------|
| id | INT AUTO_INCREMENT | Unique row identifier |
| applicant_id | VARCHAR(50) | Link to applicants table |
| credit_score | INT | Credit score at inquiry |
| inquiry_type | VARCHAR(50) | hard, soft |
| record_date | TIMESTAMP | Date of inquiry |

**Indexes**: `idx_applicant_id`, `idx_record_date`  
**Foreign Key**: `applicant_id` → `applicants.applicant_id`

**Example Data**:
```
applicant_id: APP001
credit_score: 795
record_date: 2026-07-05 10:30:45
```

---

### **TABLE 4: evaluations**
**Purpose**: Store AI evaluation results and final decisions

| Field | Type | Purpose |
|-------|------|---------|
| id | INT AUTO_INCREMENT | Unique row identifier |
| evaluation_id | VARCHAR(50) UNIQUE | Unique evaluation ID (e.g., EVAL000001) |
| application_id | VARCHAR(50) | Link to loan_applications |
| decision | VARCHAR(50) | approved, rejected, manual_review |
| final_score | DECIMAL(5,2) | Composite score (0-100) |
| risk_level | VARCHAR(50) | LOW, MEDIUM, HIGH, CRITICAL |
| agent_results | LONGTEXT | JSON with all 4 agent scores |
| explanation | LONGTEXT | JSON explanation of decision |
| evaluation_date | TIMESTAMP | Evaluation timestamp |

**Indexes**: `idx_eval_id`, `idx_app_id`, `idx_decision`, `idx_evaluation_date`  
**Foreign Key**: `application_id` → `loan_applications.application_id`

**Example Data**:
```
evaluation_id: EVAL000001
application_id: LN000001
decision: approved
final_score: 87.6
risk_level: LOW
agent_results: {
  "Document Verification Agent": 93,
  "Credit Analysis Agent": 90,
  "Risk Assessment Agent": 85,
  "Compliance & Regulatory Agent": 80
}
```

---

### **TABLE 5: audit_logs**
**Purpose**: Complete audit trail of all operations (compliance)

| Field | Type | Purpose |
|-------|------|---------|
| id | INT AUTO_INCREMENT | Unique row identifier |
| evaluation_id | VARCHAR(50) | Link to evaluations |
| agent_name | VARCHAR(100) | Which agent performed action |
| action | VARCHAR(100) | Action performed |
| details | LONGTEXT | JSON details |
| timestamp | TIMESTAMP | When action occurred |

**Indexes**: `idx_eval_id`, `idx_agent_name`, `idx_timestamp`  
**Foreign Key**: `evaluation_id` → `evaluations.evaluation_id`

**Example Data**:
```
evaluation_id: EVAL000001
agent_name: Document Verification Agent
action: evaluated
timestamp: 2026-07-05 10:30:45
details: {
  "completeness": 90,
  "consistency": 95,
  "score": 93
}
```

---

### **TABLE 6: aml_screening**
**Purpose**: AML/KYC compliance tracking

| Field | Type | Purpose |
|-------|------|---------|
| id | INT AUTO_INCREMENT | Unique row identifier |
| applicant_id | VARCHAR(50) UNIQUE | Link to applicants |
| aml_screened | BOOLEAN | Has been screened (TRUE/FALSE) |
| aml_status | VARCHAR(50) | approved, pending, flagged |
| flagged | BOOLEAN | Is flagged for review |
| aml_date | TIMESTAMP | Screening date |

**Indexes**: `idx_applicant_id`, `idx_flagged`, `idx_aml_date`  
**Foreign Key**: `applicant_id` → `applicants.applicant_id`

**Example Data**:
```
applicant_id: APP001
aml_screened: TRUE
aml_status: approved
flagged: FALSE
```

---

## 🔗 Entity Relationship Diagram

```
                    ┌──────────────────────────────────┐
                    │  loan_applications               │
                    │  ────────────────────────        │
                    │  id (PK)                         │
                    │  application_id (UNIQUE)         │
                    │  applicant_name                  │
                    │  loan_amount                     │
                    │  status                          │
                    └──────────┬───────────────────────┘
                               │
                        application_id
                               │
                    ┌──────────┴─────────────────┐
                    │                           │
                    ▼                           ▼
        ┌──────────────────────┐    ┌──────────────────────┐
        │  evaluations         │    │  REFERENCES          │
        │  ────────────────    │    │  loan_applications   │
        │  id (PK)             │    └──────────────────────┘
        │  evaluation_id (UQ)  │
        │  decision            │
        │  final_score         │
        │  agent_results       │
        └──────────┬───────────┘
                   │
            evaluation_id
                   │
        ┌──────────▼────────────────┐
        │  audit_logs              │
        │  ────────────────────    │
        │  id (PK)                 │
        │  evaluation_id (FK)      │
        │  agent_name              │
        │  action                  │
        └──────────────────────────┘

┌──────────────────────────────────┐
│  applicants                      │
│  ─────────────────────────────   │
│  id (PK)                         │
│  applicant_id (UNIQUE)           │
│  name                            │
│  kyc_verified                    │
│  payment_defaults                │
│  bankruptcy_history              │
└──────────┬────────────┬──────────┘
           │            │
           │     applicant_id
           │            │
  applicant_id    ┌─────┴──────────────┐
           │      │                    │
           ▼      ▼                    ▼
    ┌────────────────┐      ┌──────────────────────┐
    │credit_history  │      │aml_screening         │
    │────────────    │      │─────────────────     │
    │id (PK)         │      │id (PK)               │
    │applicant_id    │      │applicant_id (UQ)     │
    │credit_score    │      │aml_screened          │
    │record_date     │      │flagged               │
    └────────────────┘      └──────────────────────┘
```

---

## 📋 Decision Workflow

```
loan_applications (NEW)
    ↓
    └─→ Saved with status: "pending"
        ↓
        └─→ 4 AI Agents Evaluate
            ├─ Document Verification Agent → Score
            ├─ Credit Analysis Agent → Score
            ├─ Risk Assessment Agent → Score
            └─ Compliance & Regulatory Agent → Score
            ↓
            └─→ Scores Synthesized
                └─→ evaluations (NEW)
                    ├─ evaluation_id: EVAL000001
                    ├─ final_score: 87.6
                    ├─ decision: approved/rejected/manual_review
                    └─ audit_logs (ENTRIES)
                        ├─ agent_name: Document Agent
                        ├─ action: evaluated
                        └─ details: {...}
                ↓
                └─→ loan_applications (UPDATED)
                    └─ status: approved/rejected/manual_review
```

---

## 🔍 Common Query Examples

### **Get Latest Evaluation for an Application**
```sql
SELECT la.*, e.*
FROM loan_applications la
JOIN evaluations e ON la.application_id = e.application_id
WHERE la.application_id = 'LN000001'
ORDER BY e.evaluation_date DESC
LIMIT 1;
```

### **Get All Approved Applications This Week**
```sql
SELECT la.*, e.final_score, e.evaluation_date
FROM loan_applications la
JOIN evaluations e ON la.application_id = e.application_id
WHERE e.decision = 'approved'
  AND e.evaluation_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY e.evaluation_date DESC;
```

### **Get Applications Requiring Manual Review**
```sql
SELECT la.*, e.final_score, e.agent_results, e.explanation
FROM loan_applications la
JOIN evaluations e ON la.application_id = e.application_id
WHERE e.decision = 'manual_review'
ORDER BY e.evaluation_date DESC;
```

### **Get KYC Non-Compliant Applicants**
```sql
SELECT a.*, am.aml_status, am.flagged
FROM applicants a
LEFT JOIN aml_screening am ON a.applicant_id = am.applicant_id
WHERE a.kyc_verified = FALSE
   OR am.flagged = TRUE
ORDER BY a.applicant_id;
```

### **Approval Statistics**
```sql
SELECT
    e.decision,
    COUNT(*) as count,
    AVG(e.final_score) as avg_score
FROM evaluations e
GROUP BY e.decision;
```

---

## 📊 Key Metrics

| Metric | Query |
|--------|-------|
| Total Applications | `SELECT COUNT(*) FROM loan_applications;` |
| Approved Count | `SELECT COUNT(*) FROM evaluations WHERE decision = 'approved';` |
| Rejection Rate | `SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM evaluations) FROM evaluations WHERE decision = 'rejected';` |
| Avg Approval Score | `SELECT AVG(final_score) FROM evaluations WHERE decision = 'approved';` |
| KYC Compliant | `SELECT COUNT(*) FROM applicants WHERE kyc_verified = TRUE;` |
| AML Flagged | `SELECT COUNT(*) FROM aml_screening WHERE flagged = TRUE;` |

---

## 🗄️ Data Types Reference

| Type | Size | Example |
|------|------|---------|
| INT | 4 bytes | 2000000 |
| DECIMAL(15,2) | 8 bytes | 2000000.00 |
| VARCHAR(50) | Variable | LN000001 |
| VARCHAR(100) | Variable | Rajesh Kumar |
| BOOLEAN | 1 byte | TRUE/FALSE |
| TIMESTAMP | 4 bytes | 2026-07-05 10:30:45 |
| TEXT | Variable | {"key": "value"} |
| LONGTEXT | Variable | Large JSON objects |

---

## 🔐 Access Control

### **Table Access by Role**

| Role | Tables | Operations |
|------|--------|-----------|
| **Admin** | All | SELECT, INSERT, UPDATE, DELETE |
| **Application User** | loan_applications, applicants | SELECT, INSERT |
| **Evaluator** | evaluations, audit_logs | SELECT, INSERT, UPDATE |
| **Compliance** | aml_screening, audit_logs | SELECT |
| **Reporting** | All | SELECT (Read-Only) |

---

## 📈 Performance Tips

1. **Index Usage**
   - Queries by `application_id` - Use `idx_app_id`
   - Queries by `status` - Use `idx_status`
   - Date ranges - Use `idx_evaluation_date`

2. **Query Optimization**
   - Use `EXPLAIN` before complex queries
   - Join on indexed columns
   - Limit result sets

3. **Scaling**
   - Implement connection pooling
   - Archive old audit logs
   - Regular index maintenance

---

## ✅ Validation Checklist

- [ ] All 6 tables created
- [ ] Foreign keys established
- [ ] Indexes created
- [ ] Test data inserted
- [ ] Queries tested
- [ ] Permissions configured
- [ ] Backups scheduled
- [ ] Monitoring enabled

---

## 📞 Quick Support

| Issue | Solution |
|-------|----------|
| Table not found | Run `SHOW TABLES;` to verify creation |
| Foreign key error | Check referenced table exists |
| Slow query | Add indexes or use EXPLAIN |
| Data not found | Verify application_id format |
| Permission denied | Check user role and grants |

---

**Created**: July 5, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0  
**Database**: rsbank_loan
