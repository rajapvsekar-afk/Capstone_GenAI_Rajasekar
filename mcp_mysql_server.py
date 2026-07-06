#!/usr/bin/env python3
"""
FastMCP MySQL Server for RS Bank Loan Approval System
Connects to MySQL database for persistent data storage
"""

import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE CONNECTION MANAGER
# ============================================================================

class MySQLConnectionManager:
    """Manages MySQL database connections"""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self) -> bool:
        """Establish MySQL connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True
            )
            logger.info(f"Connected to MySQL at {self.host}:{self.port}/{self.database}")
            return True
        except Error as e:
            logger.error(f"Database connection error: {e}")
            return False

    def disconnect(self):
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Disconnected from MySQL")

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Query execution error: {e}")
            return []

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows > 0
        except Error as e:
            logger.error(f"Update execution error: {e}")
            return False

# ============================================================================
# MCP TOOLS
# ============================================================================

class LoanApprovalMCPServer:
    """FastMCP Server for Loan Approval with MySQL backend"""

    def __init__(self, db_manager: MySQLConnectionManager):
        self.db = db_manager
        self.tools = {
            "save_application": self.save_application,
            "get_application": self.get_application,
            "get_applicant_profile": self.get_applicant_profile,
            "get_credit_history": self.get_credit_history,
            "save_evaluation": self.save_evaluation,
            "get_evaluation": self.get_evaluation,
            "get_all_evaluations": self.get_all_evaluations,
            "update_application_status": self.update_application_status,
            "get_statistics": self.get_statistics,
            "save_audit_log": self.save_audit_log,
            "verify_kyc": self.verify_kyc,
            "check_aml_screening": self.check_aml_screening,
        }

    # =====================================================================
    # APPLICATION MANAGEMENT
    # =====================================================================

    def save_application(self, application_id: str, applicant_name: str,
                        applicant_age: int, annual_income: float,
                        employment_type: str, employment_years: int,
                        credit_score: int, location: str,
                        loan_amount: float, tenure_months: int,
                        loan_purpose: str) -> Dict[str, Any]:
        """Save loan application to database"""
        try:
            query = """
            INSERT INTO loan_applications
            (application_id, applicant_name, applicant_age, annual_income,
             employment_type, employment_years, credit_score, location,
             loan_amount, tenure_months, loan_purpose, application_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (application_id, applicant_name, applicant_age, annual_income,
                     employment_type, employment_years, credit_score, location,
                     loan_amount, tenure_months, loan_purpose,
                     datetime.now().isoformat(), "submitted")

            success = self.db.execute_update(query, params)
            return {
                "status": "success" if success else "failed",
                "application_id": application_id,
                "message": "Application saved successfully" if success else "Failed to save application"
            }
        except Exception as e:
            logger.error(f"Error saving application: {e}")
            return {"status": "error", "message": str(e)}

    def get_application(self, application_id: str) -> Dict[str, Any]:
        """Retrieve application from database"""
        try:
            query = "SELECT * FROM loan_applications WHERE application_id = %s"
            results = self.db.execute_query(query, (application_id,))

            if results:
                return {
                    "status": "found",
                    "data": results[0]
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Application {application_id} not found"
                }
        except Exception as e:
            logger.error(f"Error retrieving application: {e}")
            return {"status": "error", "message": str(e)}

    def update_application_status(self, application_id: str, status: str) -> Dict[str, Any]:
        """Update application status"""
        try:
            query = """
            UPDATE loan_applications
            SET status = %s, updated_date = %s
            WHERE application_id = %s
            """
            params = (status, datetime.now().isoformat(), application_id)

            success = self.db.execute_update(query, params)
            return {
                "status": "success" if success else "failed",
                "message": f"Status updated to {status}" if success else "Failed to update status"
            }
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return {"status": "error", "message": str(e)}

    # =====================================================================
    # APPLICANT PROFILE
    # =====================================================================

    def get_applicant_profile(self, applicant_id: str) -> Dict[str, Any]:
        """Retrieve applicant profile"""
        try:
            query = "SELECT * FROM applicants WHERE applicant_id = %s"
            results = self.db.execute_query(query, (applicant_id,))

            if results:
                return {
                    "status": "found",
                    "profile": results[0]
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Applicant {applicant_id} not found"
                }
        except Exception as e:
            logger.error(f"Error retrieving profile: {e}")
            return {"status": "error", "message": str(e)}

    # =====================================================================
    # CREDIT HISTORY
    # =====================================================================

    def get_credit_history(self, applicant_id: str) -> Dict[str, Any]:
        """Retrieve credit history"""
        try:
            query = """
            SELECT * FROM credit_history
            WHERE applicant_id = %s
            ORDER BY record_date DESC
            LIMIT 12
            """
            results = self.db.execute_query(query, (applicant_id,))

            return {
                "status": "success",
                "applicant_id": applicant_id,
                "records": results,
                "record_count": len(results)
            }
        except Exception as e:
            logger.error(f"Error retrieving credit history: {e}")
            return {"status": "error", "message": str(e)}

    # =====================================================================
    # EVALUATION MANAGEMENT
    # =====================================================================

    def save_evaluation(self, evaluation_id: str, application_id: str,
                       decision: str, final_score: float, risk_level: str,
                       agent_results: str, explanation: str) -> Dict[str, Any]:
        """Save evaluation result"""
        try:
            query = """
            INSERT INTO evaluations
            (evaluation_id, application_id, decision, final_score, risk_level,
             agent_results, explanation, evaluation_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (evaluation_id, application_id, decision, final_score,
                     risk_level, agent_results, explanation, datetime.now().isoformat())

            success = self.db.execute_update(query, params)
            return {
                "status": "success" if success else "failed",
                "evaluation_id": evaluation_id,
                "message": "Evaluation saved successfully" if success else "Failed to save evaluation"
            }
        except Exception as e:
            logger.error(f"Error saving evaluation: {e}")
            return {"status": "error", "message": str(e)}

    def get_evaluation(self, evaluation_id: str) -> Dict[str, Any]:
        """Retrieve evaluation result"""
        try:
            query = "SELECT * FROM evaluations WHERE evaluation_id = %s"
            results = self.db.execute_query(query, (evaluation_id,))

            if results:
                return {
                    "status": "found",
                    "evaluation": results[0]
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Evaluation {evaluation_id} not found"
                }
        except Exception as e:
            logger.error(f"Error retrieving evaluation: {e}")
            return {"status": "error", "message": str(e)}

    def get_all_evaluations(self, application_id: str) -> Dict[str, Any]:
        """Get all evaluations for an application"""
        try:
            query = """
            SELECT * FROM evaluations
            WHERE application_id = %s
            ORDER BY evaluation_date DESC
            """
            results = self.db.execute_query(query, (application_id,))

            return {
                "status": "success",
                "application_id": application_id,
                "evaluations": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Error retrieving evaluations: {e}")
            return {"status": "error", "message": str(e)}

    # =====================================================================
    # AUDIT LOGGING
    # =====================================================================

    def save_audit_log(self, evaluation_id: str, agent_name: str,
                       action: str, details: str) -> Dict[str, Any]:
        """Save audit log entry"""
        try:
            query = """
            INSERT INTO audit_logs
            (evaluation_id, agent_name, action, details, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (evaluation_id, agent_name, action, details, datetime.now().isoformat())

            success = self.db.execute_update(query, params)
            return {
                "status": "success" if success else "failed",
                "message": "Audit log saved" if success else "Failed to save audit log"
            }
        except Exception as e:
            logger.error(f"Error saving audit log: {e}")
            return {"status": "error", "message": str(e)}

    # =====================================================================
    # COMPLIANCE & SCREENING
    # =====================================================================

    def verify_kyc(self, applicant_id: str) -> Dict[str, Any]:
        """Verify KYC status"""
        try:
            query = """
            SELECT kyc_verified, kyc_verified_date, kyc_documents
            FROM applicants WHERE applicant_id = %s
            """
            results = self.db.execute_query(query, (applicant_id,))

            if results:
                return {
                    "status": "success",
                    "kyc_verified": results[0].get("kyc_verified", False),
                    "verified_date": results[0].get("kyc_verified_date"),
                    "documents": results[0].get("kyc_documents", "")
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"KYC record for {applicant_id} not found"
                }
        except Exception as e:
            logger.error(f"Error verifying KYC: {e}")
            return {"status": "error", "message": str(e)}

    def check_aml_screening(self, applicant_id: str) -> Dict[str, Any]:
        """Check AML screening status"""
        try:
            query = """
            SELECT aml_screened, aml_status, aml_date, flagged
            FROM aml_screening WHERE applicant_id = %s
            """
            results = self.db.execute_query(query, (applicant_id,))

            if results:
                return {
                    "status": "success",
                    "aml_screened": results[0].get("aml_screened", False),
                    "aml_status": results[0].get("aml_status", "pending"),
                    "flagged": results[0].get("flagged", False),
                    "screening_date": results[0].get("aml_date")
                }
            else:
                return {
                    "status": "not_screened",
                    "message": f"AML screening not found for {applicant_id}"
                }
        except Exception as e:
            logger.error(f"Error checking AML screening: {e}")
            return {"status": "error", "message": str(e)}

    # =====================================================================
    # STATISTICS & ANALYTICS
    # =====================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            stats = {}

            # Total applications
            query = "SELECT COUNT(*) as count FROM loan_applications"
            result = self.db.execute_query(query)
            stats["total_applications"] = result[0]["count"] if result else 0

            # Approved count
            query = "SELECT COUNT(*) as count FROM evaluations WHERE decision = 'approved'"
            result = self.db.execute_query(query)
            stats["approved_count"] = result[0]["count"] if result else 0

            # Rejected count
            query = "SELECT COUNT(*) as count FROM evaluations WHERE decision = 'rejected'"
            result = self.db.execute_query(query)
            stats["rejected_count"] = result[0]["count"] if result else 0

            # Manual review count
            query = "SELECT COUNT(*) as count FROM evaluations WHERE decision = 'manual_review'"
            result = self.db.execute_query(query)
            stats["manual_review_count"] = result[0]["count"] if result else 0

            # Average score
            query = "SELECT AVG(final_score) as avg_score FROM evaluations"
            result = self.db.execute_query(query)
            stats["average_score"] = float(result[0]["avg_score"]) if result and result[0]["avg_score"] else 0

            # Approval rate
            total = stats["total_applications"]
            if total > 0:
                stats["approval_rate"] = (stats["approved_count"] / total) * 100
            else:
                stats["approval_rate"] = 0

            return {
                "status": "success",
                "statistics": stats
            }
        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}")
            return {"status": "error", "message": str(e)}

    # =====================================================================
    # TOOL EXECUTION
    # =====================================================================

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name"""
        if tool_name not in self.tools:
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' not found"
            }

        try:
            tool_func = self.tools[tool_name]
            return tool_func(**params)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

class DatabaseInitializer:
    """Initialize MySQL database schema"""

    def __init__(self, db_manager: MySQLConnectionManager):
        self.db = db_manager

    def initialize(self) -> bool:
        """Initialize database tables"""
        try:
            # Create loan_applications table
            self._create_applications_table()

            # Create applicants table
            self._create_applicants_table()

            # Create credit_history table
            self._create_credit_history_table()

            # Create evaluations table
            self._create_evaluations_table()

            # Create audit_logs table
            self._create_audit_logs_table()

            # Create aml_screening table
            self._create_aml_screening_table()

            logger.info("Database initialization completed")
            return True
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            return False

    def _create_applications_table(self):
        """Create loan_applications table"""
        query = """
        CREATE TABLE IF NOT EXISTS loan_applications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            application_id VARCHAR(50) UNIQUE NOT NULL,
            applicant_name VARCHAR(100) NOT NULL,
            applicant_age INT NOT NULL,
            annual_income DECIMAL(15, 2) NOT NULL,
            employment_type VARCHAR(50),
            employment_years INT,
            credit_score INT,
            location VARCHAR(100),
            loan_amount DECIMAL(15, 2) NOT NULL,
            tenure_months INT NOT NULL,
            loan_purpose VARCHAR(50),
            application_date TIMESTAMP,
            status VARCHAR(50) DEFAULT 'submitted',
            updated_date TIMESTAMP,
            INDEX idx_app_id (application_id),
            INDEX idx_status (status)
        )
        """
        self.db.execute_update(query)
        logger.info("Created loan_applications table")

    def _create_applicants_table(self):
        """Create applicants table"""
        query = """
        CREATE TABLE IF NOT EXISTS applicants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            applicant_id VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            age INT,
            annual_income DECIMAL(15, 2),
            employment_type VARCHAR(50),
            employment_years INT,
            credit_score INT,
            existing_liabilities DECIMAL(15, 2),
            total_assets DECIMAL(15, 2),
            location VARCHAR(100),
            kyc_verified BOOLEAN DEFAULT FALSE,
            kyc_verified_date TIMESTAMP,
            kyc_documents TEXT,
            payment_defaults INT DEFAULT 0,
            bankruptcy_history BOOLEAN DEFAULT FALSE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_applicant_id (applicant_id),
            INDEX idx_kyc (kyc_verified)
        )
        """
        self.db.execute_update(query)
        logger.info("Created applicants table")

    def _create_credit_history_table(self):
        """Create credit_history table"""
        query = """
        CREATE TABLE IF NOT EXISTS credit_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            applicant_id VARCHAR(50) NOT NULL,
            credit_score INT,
            inquiry_type VARCHAR(50),
            record_date TIMESTAMP,
            INDEX idx_applicant_id (applicant_id),
            FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
        )
        """
        self.db.execute_update(query)
        logger.info("Created credit_history table")

    def _create_evaluations_table(self):
        """Create evaluations table"""
        query = """
        CREATE TABLE IF NOT EXISTS evaluations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            evaluation_id VARCHAR(50) UNIQUE NOT NULL,
            application_id VARCHAR(50) NOT NULL,
            decision VARCHAR(50),
            final_score DECIMAL(5, 2),
            risk_level VARCHAR(50),
            agent_results LONGTEXT,
            explanation LONGTEXT,
            evaluation_date TIMESTAMP,
            INDEX idx_eval_id (evaluation_id),
            INDEX idx_app_id (application_id),
            INDEX idx_decision (decision),
            FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        )
        """
        self.db.execute_update(query)
        logger.info("Created evaluations table")

    def _create_audit_logs_table(self):
        """Create audit_logs table"""
        query = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            evaluation_id VARCHAR(50) NOT NULL,
            agent_name VARCHAR(100),
            action VARCHAR(100),
            details LONGTEXT,
            timestamp TIMESTAMP,
            INDEX idx_eval_id (evaluation_id),
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id)
        )
        """
        self.db.execute_update(query)
        logger.info("Created audit_logs table")

    def _create_aml_screening_table(self):
        """Create aml_screening table"""
        query = """
        CREATE TABLE IF NOT EXISTS aml_screening (
            id INT AUTO_INCREMENT PRIMARY KEY,
            applicant_id VARCHAR(50) UNIQUE NOT NULL,
            aml_screened BOOLEAN DEFAULT FALSE,
            aml_status VARCHAR(50),
            flagged BOOLEAN DEFAULT FALSE,
            aml_date TIMESTAMP,
            INDEX idx_applicant_id (applicant_id),
            FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
        )
        """
        self.db.execute_update(query)
        logger.info("Created aml_screening table")

# ============================================================================
# MAIN SERVER
# ============================================================================

def create_server(host: str = "localhost", user: str = "root",
                 password: str = "password", database: str = "rsbank_loan"):
    """Create and initialize MCP server"""
    # Create connection manager
    db_manager = MySQLConnectionManager(host, user, password, database)

    # Connect to database
    if not db_manager.connect():
        logger.error("Failed to connect to database")
        return None

    # Initialize database
    initializer = DatabaseInitializer(db_manager)
    if not initializer.initialize():
        logger.error("Failed to initialize database")
        db_manager.disconnect()
        return None

    # Create MCP server
    mcp_server = LoanApprovalMCPServer(db_manager)
    logger.info("MCP Server created successfully")

    return mcp_server

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Create server with default MySQL connection
    server = create_server(
        host="localhost",
        user="root",
        password="rsbank123",
        database="rsbank_loan"
    )

    if server:
        print("\n✅ MCP MySQL Server initialized successfully!")
        print(f"\nAvailable tools:")
        for tool in server.get_available_tools():
            print(f"  - {tool}")

        # Example: Save an application
        result = server.execute_tool("save_application", {
            "application_id": "LN000001",
            "applicant_name": "Test User",
            "applicant_age": 35,
            "annual_income": 1500000,
            "employment_type": "employed",
            "employment_years": 5,
            "credit_score": 750,
            "location": "Mumbai",
            "loan_amount": 3000000,
            "tenure_months": 60,
            "loan_purpose": "home"
        })
        print(f"\nSave Application Result: {json.dumps(result, indent=2)}")

        # Example: Get statistics
        result = server.execute_tool("get_statistics", {})
        print(f"\nStatistics: {json.dumps(result, indent=2)}")

        # Disconnect
        server.db.disconnect()
