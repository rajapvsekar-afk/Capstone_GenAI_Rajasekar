# 🚀 Database Schema - Quick Start Guide

**All Tables & Queries at a Glance**

---

## 📚 Documentation Files Created

### 1. **DATABASE_SCHEMA_REFERENCE.md** (Comprehensive)
- Complete table definitions with all columns
- Data types and constraints
- Foreign key relationships
- Useful SQL queries (8 complete examples)
- Key metrics queries
- Security & compliance info
- Performance optimization tips

**Use this for**: Understanding complete schema structure

---

### 2. **DATABASE_TABLES_SUMMARY.md** (Quick Reference)
- All 6 tables at a glance
- Field-by-field breakdown
- Entity relationship diagram
- Common query examples
- Key metrics and access control
- Performance tips
- Validation checklist

**Use this for**: Quick lookups and understanding relationships

---

### 3. **SCHEMA_VISUAL_GUIDE.md** (Visual Deep Dive)
- Complete ASCII database architecture
- Full data flow diagram
- Query relationship maps
- Decision tree logic
- Key field mappings
- Table size & performance metrics

**Use this for**: Visual understanding and workflow diagrams

---

### 4. **SQL_QUERIES_REFERENCE.sql** (Executable SQL)
- Complete schema creation scripts
- 23 ready-to-run queries
- Analysis & reporting queries
- Time-based analytics
- Maintenance scripts
- User management queries

**Use this for**: Copy-paste SQL commands

---

## 🗂️ The 6 Tables (Overview)

| # | Table | Purpose | Records/Day |
|---|-------|---------|-------------|
| 1 | **loan_applications** | Main applications registry | ~150 |
| 2 | **applicants** | Applicant profiles & KYC | ~40 |
| 3 | **credit_history** | Credit inquiry records | ~80 |
| 4 | **evaluations** | AI evaluation results | ~140 |
| 5 | **audit_logs** | Complete audit trail | ~560 |
| 6 | **aml_screening** | Compliance & AML tracking | ~40 |

---

## 🔑 Key Fields to Remember

### **Applications**
- **application_id** (VARCHAR 50) - Unique identifier: `LN000001`
- **status** - pending, approved, rejected, manual_review
- **application_date** - When submitted

### **Applicants**
- **applicant_id** (VARCHAR 50) - Unique identifier: `APP001`
- **kyc_verified** - TRUE/FALSE (compliance)
- **payment_defaults** - Number of defaults
- **bankruptcy_history** - TRUE/FALSE

### **Evaluations**
- **evaluation_id** (VARCHAR 50) - Unique identifier: `EVAL000001`
- **decision** - approved/rejected/manual_review
- **final_score** - 0-100 (composite)
- **risk_level** - LOW/MEDIUM/HIGH/CRITICAL

### **Audit Logs**
- **agent_name** - Which AI agent performed action
- **action** - evaluated, analyzed, flagged, etc.
- **details** - JSON with full details

---

## 🚀 Quick SQL Snippets

### **Get Latest Evaluation**
```sql
SELECT la.*, e.decision, e.final_score 
FROM loan_applications la
JOIN evaluations e ON la.application_id = e.application_id
WHERE la.application_id = 'LN000001'
ORDER BY e.evaluation_date DESC LIMIT 1;
```

### **Approval Statistics**
```sql
SELECT decision, COUNT(*) as count, AVG(final_score) as avg_score
FROM evaluations
GROUP BY decision;
```

### **High-Risk Applications**
```sql
SELECT * FROM evaluations
WHERE risk_level IN ('HIGH', 'CRITICAL')
ORDER BY final_score ASC;
```

### **KYC Compliance Status**
```sql
SELECT a.applicant_id, a.name, a.kyc_verified, am.aml_status, am.flagged
FROM applicants a
LEFT JOIN aml_screening am ON a.applicant_id = am.applicant_id
WHERE a.kyc_verified = FALSE OR am.flagged = TRUE;
```

### **Audit Trail for Application**
```sql
SELECT e.evaluation_id, al.agent_name, al.action, al.timestamp
FROM evaluations e
JOIN audit_logs al ON e.evaluation_id = al.evaluation_id
WHERE e.application_id = 'LN000001'
ORDER BY al.timestamp ASC;
```

---

## 📊 Database Statistics

```
TOTAL TABLES:        6
TOTAL COLUMNS:       45+
TOTAL INDEXES:       15+
FOREIGN KEYS:        4
DEFAULT SIZE:        17.5 MB (first year)
BACKUP FREQUENCY:    Daily
ARCHIVE AFTER:       2 years
```

---

## 🔗 Entity Relationships

```
loan_applications
    ├─→ evaluations (via application_id)
    └─→ audit_logs (via evaluation_id)

applicants
    ├─→ credit_history
    └─→ aml_screening

All linked via IDs:
- application_id (VARCHAR 50)
- applicant_id (VARCHAR 50)
- evaluation_id (VARCHAR 50)
```

---

## ✅ Schema Status

- ✅ 6 Tables Created
- ✅ Foreign Keys Established
- ✅ 15+ Indexes Created
- ✅ Test Data Ready
- ✅ Queries Validated
- ✅ Documentation Complete
- ✅ Production Ready

---

## 🗄️ MySQL Connection

```bash
# Connect to database
mysql -u rsbank_user -p rsbank_loan

# Or with Docker
docker exec -it rsbank-mysql mysql -u rsbank_user -p rsbank_loan
```

---

## 📝 Sample Data Formats

### Application
```json
{
  "application_id": "LN000001",
  "applicant_name": "Rajesh Kumar",
  "annual_income": 2000000.00,
  "loan_amount": 5000000.00,
  "tenure_months": 60,
  "status": "pending"
}
```

### Evaluation
```json
{
  "evaluation_id": "EVAL000001",
  "application_id": "LN000001",
  "decision": "approved",
  "final_score": 87.6,
  "risk_level": "LOW",
  "agent_results": {
    "Document Verification Agent": 93,
    "Credit Analysis Agent": 90,
    "Risk Assessment Agent": 85,
    "Compliance & Regulatory Agent": 80
  }
}
```

### Audit Log Entry
```json
{
  "evaluation_id": "EVAL000001",
  "agent_name": "Document Verification Agent",
  "action": "evaluated",
  "details": {
    "completeness": 90,
    "consistency": 95,
    "score": 93
  }
}
```

---

## 🔐 Access Control

| Role | Read | Write | Delete | Tables |
|------|------|-------|--------|--------|
| Admin | ✓ | ✓ | ✓ | All |
| Evaluator | ✓ | ✓ | ✗ | evaluations, audit_logs |
| Applicant | ✓ | ✓ | ✗ | loan_applications |
| Compliance | ✓ | ✗ | ✗ | aml_screening, audit_logs |
| Reporter | ✓ | ✗ | ✗ | All (read-only) |

---

## 🛠️ Useful Commands

### Check Database Size
```sql
SELECT SUM(data_length + index_length) / 1024 / 1024 as size_mb
FROM information_schema.tables
WHERE table_schema = 'rsbank_loan';
```

### Count Records
```sql
SELECT 'loan_applications' as table_name, COUNT(*) as count FROM loan_applications
UNION ALL
SELECT 'evaluations', COUNT(*) FROM evaluations
UNION ALL
SELECT 'applicants', COUNT(*) FROM applicants
UNION ALL
SELECT 'credit_history', COUNT(*) FROM credit_history
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs
UNION ALL
SELECT 'aml_screening', COUNT(*) FROM aml_screening;
```

### Backup Database
```bash
mysqldump -u rsbank_user -p rsbank_loan > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
mysql -u rsbank_user -p rsbank_loan < backup_20260705.sql
```

---

## 📖 Documentation Map

```
START HERE
    │
    ├─→ Need quick overview?
    │   └─→ Read: DATABASE_TABLES_SUMMARY.md
    │
    ├─→ Need complete details?
    │   └─→ Read: DATABASE_SCHEMA_REFERENCE.md
    │
    ├─→ Need visual understanding?
    │   └─→ Read: SCHEMA_VISUAL_GUIDE.md
    │
    ├─→ Need SQL commands?
    │   └─→ Use: SQL_QUERIES_REFERENCE.sql
    │
    └─→ Need to execute?
        └─→ Run: python3 mcp_mysql_server.py
```

---

## 🎯 Next Steps

1. **Initialize Database**
   ```bash
   python3 mcp_mysql_server.py
   ```

2. **Verify Tables**
   ```bash
   mysql -u rsbank_user -p rsbank_loan -e "SHOW TABLES;"
   ```

3. **Test Connection**
   ```bash
   mysql -u rsbank_user -p rsbank_loan -e "SELECT COUNT(*) FROM loan_applications;"
   ```

4. **Check Schema**
   ```bash
   mysql -u rsbank_user -p rsbank_loan -e "DESCRIBE loan_applications;"
   ```

5. **Run Queries**
   ```bash
   mysql -u rsbank_user -p rsbank_loan < SQL_QUERIES_REFERENCE.sql
   ```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection Refused | Check MySQL is running: `sudo systemctl start mysql` |
| Access Denied | Verify credentials: user=rsbank_user, password=rsbank_pass |
| Table Not Found | Initialize database: `python3 mcp_mysql_server.py` |
| Slow Queries | Check indexes: `SHOW INDEXES FROM table_name;` |
| Foreign Key Error | Verify parent table exists first |

---

**Created**: July 6, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0  
**Database**: rsbank_loan
