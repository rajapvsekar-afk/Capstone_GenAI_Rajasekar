# FastMCP MySQL Integration Setup Guide

**Version**: 1.0  
**Date**: July 3, 2026  
**Status**: ✅ Ready to Deploy

---

## 🗄️ Overview

The FastMCP MySQL server provides persistent data storage for the RS Bank Loan Approval System with the following features:

✅ **12 MCP Tools** for data management  
✅ **Automatic Database Initialization**  
✅ **6 Core Tables** with proper relationships  
✅ **Complete Audit Logging**  
✅ **KYC & AML Screening Integration**  
✅ **Production-Ready Error Handling**  

---

## 📋 Prerequisites

### Install MySQL Server
```bash
# Ubuntu/Debian
sudo apt-get install mysql-server mysql-client

# macOS (using Homebrew)
brew install mysql

# Or use Docker
docker run --name rsbank-mysql -e MYSQL_ROOT_PASSWORD=rsbank123 -p 3306:3306 -d mysql:8.0
```

### Install Python MySQL Connector
```bash
pip3 install mysql-connector-python
```

---

## 🚀 Quick Start

### Step 1: Create Database
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE rsbank_loan;
CREATE USER 'rsbank_user'@'localhost' IDENTIFIED BY 'rsbank_pass';
GRANT ALL PRIVILEGES ON rsbank_loan.* TO 'rsbank_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 2: Initialize MCP Server
```bash
python3 mcp_mysql_server.py
```

**Expected Output:**
```
✅ MCP MySQL Server initialized successfully!

Available tools:
  - save_application
  - get_application
  - get_applicant_profile
  - get_credit_history
  - save_evaluation
  - get_evaluation
  - get_all_evaluations
  - update_application_status
  - get_statistics
  - save_audit_log
  - verify_kyc
  - check_aml_screening
```

### Step 3: Verify Connection
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT VERSION();"

# Check database created
mysql -u root -p -e "USE rsbank_loan; SHOW TABLES;"
```

---

## 📊 Database Schema

### 1. **loan_applications** - Main loan applications
```sql
CREATE TABLE loan_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id VARCHAR(50) UNIQUE,
    applicant_name VARCHAR(100),
    applicant_age INT,
    annual_income DECIMAL(15,2),
    employment_type VARCHAR(50),
    employment_years INT,
    credit_score INT,
    location VARCHAR(100),
    loan_amount DECIMAL(15,2),
    tenure_months INT,
    loan_purpose VARCHAR(50),
    application_date TIMESTAMP,
    status VARCHAR(50),
    updated_date TIMESTAMP,
    INDEX idx_app_id (application_id),
    INDEX idx_status (status)
);
```

### 2. **applicants** - Applicant profiles
```sql
CREATE TABLE applicants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    age INT,
    annual_income DECIMAL(15,2),
    employment_type VARCHAR(50),
    employment_years INT,
    credit_score INT,
    existing_liabilities DECIMAL(15,2),
    total_assets DECIMAL(15,2),
    location VARCHAR(100),
    kyc_verified BOOLEAN,
    kyc_verified_date TIMESTAMP,
    kyc_documents TEXT,
    payment_defaults INT,
    bankruptcy_history BOOLEAN,
    created_date TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_kyc (kyc_verified)
);
```

### 3. **credit_history** - Credit records
```sql
CREATE TABLE credit_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50),
    credit_score INT,
    inquiry_type VARCHAR(50),
    record_date TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);
```

### 4. **evaluations** - Loan evaluation results
```sql
CREATE TABLE evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluation_id VARCHAR(50) UNIQUE,
    application_id VARCHAR(50),
    decision VARCHAR(50),
    final_score DECIMAL(5,2),
    risk_level VARCHAR(50),
    agent_results LONGTEXT,
    explanation LONGTEXT,
    evaluation_date TIMESTAMP,
    INDEX idx_eval_id (evaluation_id),
    INDEX idx_app_id (application_id),
    INDEX idx_decision (decision),
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
);
```

### 5. **audit_logs** - Audit trail
```sql
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluation_id VARCHAR(50),
    agent_name VARCHAR(100),
    action VARCHAR(100),
    details LONGTEXT,
    timestamp TIMESTAMP,
    INDEX idx_eval_id (evaluation_id),
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id)
);
```

### 6. **aml_screening** - AML/KYC compliance
```sql
CREATE TABLE aml_screening (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) UNIQUE,
    aml_screened BOOLEAN,
    aml_status VARCHAR(50),
    flagged BOOLEAN,
    aml_date TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);
```

---

## 🛠️ MCP Tools Reference

### 1. **save_application**
Save a new loan application
```python
server.execute_tool("save_application", {
    "application_id": "LN000001",
    "applicant_name": "Rajesh Kumar",
    "applicant_age": 38,
    "annual_income": 2000000,
    "employment_type": "employed",
    "employment_years": 12,
    "credit_score": 795,
    "location": "Mumbai",
    "loan_amount": 5000000,
    "tenure_months": 60,
    "loan_purpose": "home"
})
```

### 2. **get_application**
Retrieve application by ID
```python
server.execute_tool("get_application", {
    "application_id": "LN000001"
})
```

### 3. **get_applicant_profile**
Get applicant profile
```python
server.execute_tool("get_applicant_profile", {
    "applicant_id": "APP001"
})
```

### 4. **get_credit_history**
Retrieve credit history
```python
server.execute_tool("get_credit_history", {
    "applicant_id": "APP001"
})
```

### 5. **save_evaluation**
Save evaluation result
```python
server.execute_tool("save_evaluation", {
    "evaluation_id": "EVAL001",
    "application_id": "LN000001",
    "decision": "approved",
    "final_score": 87.6,
    "risk_level": "low",
    "agent_results": '{"doc": 93, "credit": 90}',
    "explanation": "Application approved..."
})
```

### 6. **get_evaluation**
Retrieve evaluation
```python
server.execute_tool("get_evaluation", {
    "evaluation_id": "EVAL001"
})
```

### 7. **get_all_evaluations**
Get all evaluations for an application
```python
server.execute_tool("get_all_evaluations", {
    "application_id": "LN000001"
})
```

### 8. **update_application_status**
Update application status
```python
server.execute_tool("update_application_status", {
    "application_id": "LN000001",
    "status": "approved"
})
```

### 9. **save_audit_log**
Save audit log entry
```python
server.execute_tool("save_audit_log", {
    "evaluation_id": "EVAL001",
    "agent_name": "Credit Analysis Agent",
    "action": "analyzed",
    "details": "Credit score analysis completed"
})
```

### 10. **verify_kyc**
Check KYC verification status
```python
server.execute_tool("verify_kyc", {
    "applicant_id": "APP001"
})
```

### 11. **check_aml_screening**
Check AML screening status
```python
server.execute_tool("check_aml_screening", {
    "applicant_id": "APP001"
})
```

### 12. **get_statistics**
Get system statistics
```python
server.execute_tool("get_statistics", {})
```

---

## 📝 Integration with Chatbot UI

### Connect MCP Server to Streamlit
```python
# In chatbot_ui.py
from mcp_mysql_server import create_server

@st.cache_resource
def get_mcp_server():
    """Initialize MCP server"""
    return create_server(
        host="localhost",
        user="rsbank_user",
        password="rsbank_pass",
        database="rsbank_loan"
    )

# Use in app
mcp_server = get_mcp_server()

# Save evaluation
mcp_server.execute_tool("save_evaluation", {
    "evaluation_id": result.evaluation_id,
    "application_id": result.loan_id,
    "decision": result.decision.value,
    "final_score": result.final_score,
    "risk_level": result.risk_level.value,
    "agent_results": json.dumps([r.findings for r in result.agent_results]),
    "explanation": json.dumps(result.explanation)
})
```

---

## 🔒 Security Best Practices

### 1. **Use Strong Passwords**
```bash
# Create secure user
CREATE USER 'rsbank_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';
```

### 2. **Restrict User Privileges**
```bash
# Grant only required privileges
GRANT SELECT, INSERT, UPDATE ON rsbank_loan.* TO 'rsbank_user'@'localhost';
```

### 3. **Enable SSL/TLS**
```bash
# Configure MySQL for SSL
[mysqld]
ssl-ca=/path/to/ca.pem
ssl-cert=/path/to/cert.pem
ssl-key=/path/to/key.pem
```

### 4. **Regular Backups**
```bash
# Backup database
mysqldump -u rsbank_user -p rsbank_loan > backup.sql

# Restore database
mysql -u rsbank_user -p rsbank_loan < backup.sql
```

### 5. **Audit Logging**
All operations are logged in the `audit_logs` table with timestamps

---

## 🧪 Testing

### Test 1: Connection
```bash
python3 -c "
from mcp_mysql_server import MySQLConnectionManager
db = MySQLConnectionManager('localhost', 'root', 'rsbank123', 'rsbank_loan')
if db.connect():
    print('✅ Database connection successful')
    db.disconnect()
else:
    print('❌ Connection failed')
"
```

### Test 2: Table Creation
```bash
mysql -u root -p rsbank_loan -e "SHOW TABLES;"
```

Expected output:
```
+-----------------------------+
| Tables_in_rsbank_loan       |
+-----------------------------+
| loan_applications           |
| applicants                  |
| credit_history              |
| evaluations                 |
| audit_logs                  |
| aml_screening               |
+-----------------------------+
```

### Test 3: Save and Retrieve
```bash
python3 mcp_mysql_server.py  # Run the example
```

---

## 📊 Sample Data Queries

### Total Applications
```sql
SELECT COUNT(*) as total_applications FROM loan_applications;
```

### Approval Statistics
```sql
SELECT 
    decision,
    COUNT(*) as count,
    AVG(final_score) as avg_score
FROM evaluations
GROUP BY decision;
```

### High-Risk Applications
```sql
SELECT 
    la.application_id,
    la.applicant_name,
    e.final_score,
    e.risk_level
FROM loan_applications la
JOIN evaluations e ON la.application_id = e.application_id
WHERE e.risk_level IN ('HIGH', 'CRITICAL');
```

### KYC Verification Status
```sql
SELECT 
    applicant_id,
    kyc_verified,
    kyc_verified_date
FROM applicants
WHERE kyc_verified = FALSE;
```

### AML Flagged Applicants
```sql
SELECT 
    applicant_id,
    aml_status,
    aml_date
FROM aml_screening
WHERE flagged = TRUE;
```

---

## 🚀 Production Deployment

### Docker Compose Setup
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: rsbank_loan
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - rsbank

  mcp_server:
    build: .
    environment:
      DB_HOST: mysql
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_DATABASE: rsbank_loan
    ports:
      - "5000:5000"
    depends_on:
      - mysql
    networks:
      - rsbank

volumes:
  mysql_data:

networks:
  rsbank:
```

### Environment Variables (.env)
```bash
DB_ROOT_PASSWORD=YourSecurePassword123!
DB_USER=rsbank_user
DB_PASSWORD=UserSecurePassword456!
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=rsbank_loan
```

---

## 📈 Performance Optimization

### Add Indexes
```sql
-- For frequently queried fields
CREATE INDEX idx_applicant_age ON applicants(age);
CREATE INDEX idx_income_range ON applicants(annual_income);
CREATE INDEX idx_eval_date ON evaluations(evaluation_date);
CREATE INDEX idx_created_date ON loan_applications(application_date);
```

### Query Optimization
```python
# Use parameterized queries (already implemented)
query = "SELECT * FROM loan_applications WHERE application_id = %s"
results = self.db.execute_query(query, (application_id,))
```

### Connection Pooling
```python
# Implement connection pooling for high traffic
from mysql.connector import pooling

connection_pool = pooling.MySQLConnectionPool(
    pool_name="rsbank_pool",
    pool_size=5,
    host="localhost",
    user="rsbank_user",
    password="rsbank_pass",
    database="rsbank_loan"
)
```

---

## 🔧 Troubleshooting

### Issue: Connection Refused
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Start MySQL if stopped
sudo systemctl start mysql
```

### Issue: Access Denied
```bash
# Verify user and password
mysql -u rsbank_user -p -h localhost

# Reset user password if needed
mysql -u root -p
ALTER USER 'rsbank_user'@'localhost' IDENTIFIED BY 'NewPassword123!';
FLUSH PRIVILEGES;
```

### Issue: Database Not Found
```bash
# Create database if missing
mysql -u root -p -e "CREATE DATABASE rsbank_loan;"

# Initialize tables
python3 mcp_mysql_server.py
```

### Issue: Slow Queries
```sql
-- Enable query logging
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Check slow queries
SHOW VARIABLES LIKE 'slow_query%';
```

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review MySQL error logs: `/var/log/mysql/error.log`
3. Check MCP server logs for detailed errors
4. Verify database connectivity with test queries

---

## ✅ Checklist

- [ ] MySQL server installed and running
- [ ] Database `rsbank_loan` created
- [ ] Database user `rsbank_user` created with proper privileges
- [ ] Python MySQL connector installed (`pip3 install mysql-connector-python`)
- [ ] MCP server initialized successfully (`python3 mcp_mysql_server.py`)
- [ ] All 6 tables created with proper indexes
- [ ] Test connection successful
- [ ] Sample data saved and retrieved
- [ ] Audit logging working
- [ ] KYC verification checks working
- [ ] AML screening checks working
- [ ] Statistics queries returning correct results

---

## 🎉 You're Ready!

Once all checklist items are complete, your FastMCP MySQL server is ready for:
- ✅ Production loan approval processing
- ✅ Persistent data storage
- ✅ Complete audit trails
- ✅ Compliance reporting
- ✅ Analytics and statistics

---

**Created**: July 3, 2026  
**Status**: ✅ Ready for Production  
**Version**: 1.0  
**Prepared by**: Senior Development Team
