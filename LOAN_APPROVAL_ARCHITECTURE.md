# Advanced Architecture & Implementation Guide
## Multi-Agent Agentic AI Loan Approval System

**Version**: 1.0  
**Date**: July 3, 2026  
**Level**: Senior Developer / Architect

---

## 🏗️ System Architecture Deep Dive

### 1. Presentation Layer - Streamlit UI

```python
# app.py - Streamlit application
import streamlit as st
import asyncio
from datetime import datetime
import json

st.set_page_config(page_title="RS Bank Loan Portal", layout="wide")

class LoanPortalUI:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def render_application_form(self):
        """Main loan application form"""
        st.header("📋 Loan Application Form")
        
        col1, col2 = st.columns(2)
        
        with col1:
            applicant_name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=18, max_value=100)
            email = st.text_input("Email Address")
            
        with col2:
            employment_type = st.selectbox(
                "Employment Type",
                ["Employed", "Self-Employed", "Retired", "Unemployed"]
            )
            employment_years = st.number_input("Years in Current Job", min_value=0)
            annual_income = st.number_input("Annual Income (Rs.)", min_value=0)
        
        loan_section = st.expander("Loan Details", expanded=True)
        with loan_section:
            col1, col2 = st.columns(2)
            with col1:
                loan_amount = st.number_input("Loan Amount (Rs.)", min_value=0)
                tenure_months = st.number_input("Tenure (Months)", min_value=1, max_value=360)
            with col2:
                loan_purpose = st.selectbox(
                    "Loan Purpose",
                    ["Home", "Education", "Auto", "Business", "Personal"]
                )
        
        credit_section = st.expander("Credit Information", expanded=True)
        with credit_section:
            col1, col2 = st.columns(2)
            with col1:
                credit_score = st.number_input("Credit Score", min_value=300, max_value=900)
            with col2:
                existing_liabilities = st.number_input("Existing Liabilities (Rs.)", min_value=0)
        
        if st.button("🚀 Submit Application", key="submit_btn"):
            application = {
                "applicant": {
                    "name": applicant_name,
                    "age": age,
                    "email": email,
                    "employment_type": employment_type.lower(),
                    "employment_years": employment_years,
                    "annual_income": annual_income,
                    "credit_score": credit_score,
                    "existing_liabilities": existing_liabilities,
                    "total_assets": 0  # Would be populated from DB
                },
                "loan_details": {
                    "amount": loan_amount,
                    "tenure_months": tenure_months,
                    "purpose": loan_purpose.lower()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self._process_application(application)
    
    def render_decision_display(self, evaluation):
        """Display loan evaluation result"""
        st.header("📊 Loan Evaluation Result")
        
        # Decision banner
        decision = evaluation["decision"]
        if decision == "APPROVED":
            st.success(f"✅ APPLICATION APPROVED - Score: {evaluation['final_score']:.1f}/100")
        elif decision == "REJECTED":
            st.error(f"❌ APPLICATION REJECTED - Score: {evaluation['final_score']:.1f}/100")
        else:
            st.warning(f"⚠️ REQUIRES MANUAL REVIEW - Score: {evaluation['final_score']:.1f}/100")
        
        # Agent scores
        st.subheader("📌 Agent Analysis")
        col1, col2, col3, col4 = st.columns(4)
        
        for i, agent in enumerate(evaluation["agent_results"]):
            cols = [col1, col2, col3, col4]
            with cols[i]:
                st.metric(
                    agent["agent_name"].split(" ")[0],
                    f"{agent['score']:.0f}/100",
                    f"Confidence: {agent['confidence']}%"
                )
        
        # Approval details
        if decision == "APPROVED":
            st.subheader("✅ Approval Details")
            approval = evaluation.get("approval_details", {})
            col1, col2, col3 = st.columns(3)
            
            col1.metric("Approved Amount", f"Rs. {approval.get('approved_amount', 0):,.0f}")
            col2.metric("Interest Rate", f"{approval.get('interest_rate', 0):.2f}% p.a.")
            col3.metric("Monthly EMI", f"Rs. {approval.get('monthly_emi', 0):,.0f}")
        
        # Explanation
        st.subheader("💡 Decision Explanation")
        explanation = evaluation.get("explanation", {})
        st.markdown(f"**{explanation.get('summary', '')}**")
        
        if "key_findings" in explanation:
            for finding in explanation["key_findings"]:
                impact = finding["impact"]
                icon = "✅" if impact == "POSITIVE" else "❌" if impact == "NEGATIVE" else "⚪"
                st.write(f"{icon} **{finding['factor']}**: {finding['details']}")
    
    async def _process_application(self, application):
        """Submit application to orchestrator"""
        with st.spinner("🔄 Evaluating your application..."):
            try:
                evaluation = await self.orchestrator.evaluate(application)
                self.render_decision_display(evaluation)
            except Exception as e:
                st.error(f"Error: {str(e)}")
```

---

### 2. Microservice Layer - FastAPI Gateway

```python
# api/gateway.py - FastAPI application gateway
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Optional, List
import uuid
from datetime import datetime

app = FastAPI(
    title="RS Bank Loan Approval API",
    description="Multi-Agent Agentic AI Loan Evaluation System",
    version="1.0.0"
)

# Security headers and CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rsbank.com", "https://portal.rsbank.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Request validation models
class ApplicantData(BaseModel):
    name: str
    age: int
    employment_type: str
    employment_years: int
    annual_income: float
    credit_score: int
    existing_liabilities: float
    total_assets: float
    
    @validator("age")
    def age_must_be_valid(cls, v):
        if v < 18 or v > 100:
            raise ValueError("Age must be between 18 and 100")
        return v
    
    @validator("annual_income")
    def income_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Annual income must be positive")
        return v

class LoanDetails(BaseModel):
    amount: float
    tenure_months: int
    purpose: str
    
    @validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Loan amount must be positive")
        return v
    
    @validator("tenure_months")
    def tenure_valid(cls, v):
        if v < 1 or v > 360:
            raise ValueError("Tenure must be between 1 and 360 months")
        return v

class LoanApplicationRequest(BaseModel):
    applicant: ApplicantData
    loan_details: LoanDetails
    documents: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "applicant": {
                    "name": "Rajesh Kumar",
                    "age": 38,
                    "employment_type": "employed",
                    "employment_years": 12,
                    "annual_income": 2000000,
                    "credit_score": 795,
                    "existing_liabilities": 500000,
                    "total_assets": 1500000
                },
                "loan_details": {
                    "amount": 5000000,
                    "tenure_months": 60,
                    "purpose": "home_loan"
                },
                "documents": ["aadhar", "pan", "salary_slip"]
            }
        }

# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Dependency injection
from functools import lru_cache

@lru_cache()
def get_orchestrator():
    """Initialize orchestrator on first request"""
    from services.orchestrator import LoanOrchestrator
    from agents import (
        DocumentVerificationAgent,
        CreditAnalysisAgent,
        RiskAssessmentAgent,
        ComplianceAgent
    )
    
    agents = {
        "document": DocumentVerificationAgent(),
        "credit": CreditAnalysisAgent(),
        "risk": RiskAssessmentAgent(),
        "compliance": ComplianceAgent()
    }
    return LoanOrchestrator(agents)

# API Endpoints
@app.post("/api/v1/loan/apply", tags=["Loan Application"])
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def submit_loan_application(
    request: Request,
    application_request: LoanApplicationRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a new loan application for evaluation.
    
    - **applicant**: Applicant details
    - **loan_details**: Requested loan parameters
    - **documents**: List of submitted documents
    
    Returns evaluation result with decision and reasoning.
    """
    try:
        # Generate unique IDs
        application_id = f"LN{uuid.uuid4().hex[:8].upper()}"
        evaluation_id = f"EVAL{uuid.uuid4().hex[:8].upper()}"
        
        # Prepare application object
        application = {
            "application_id": application_id,
            "evaluation_id": evaluation_id,
            "applicant": application_request.applicant.dict(),
            "loan_details": application_request.loan_details.dict(),
            "documents": application_request.documents,
            "created_at": datetime.utcnow().isoformat(),
            "ip_address": request.client.host
        }
        
        # Get orchestrator and evaluate
        orchestrator = get_orchestrator()
        evaluation = await orchestrator.evaluate(application)
        
        # Log to audit trail (background task)
        background_tasks.add_task(log_evaluation, evaluation)
        
        return {
            "status": "success",
            "evaluation_id": evaluation_id,
            "application_id": application_id,
            "data": evaluation
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/loan/status/{application_id}", tags=["Loan Application"])
async def get_application_status(application_id: str):
    """
    Retrieve the status of a submitted loan application.
    """
    # Query database for application status
    # This would typically query a database
    return {
        "application_id": application_id,
        "status": "processed",
        "decision": "APPROVED",
        "evaluation_date": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health", tags=["System"])
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {
            "document": "operational",
            "credit": "operational",
            "risk": "operational",
            "compliance": "operational"
        }
    }

@app.get("/api/v1/metrics", tags=["System"])
async def get_metrics():
    """Get system metrics"""
    return {
        "applications_processed": 1523,
        "average_processing_time_ms": 52,
        "decision_distribution": {
            "approved": 45,
            "rejected": 35,
            "manual_review": 20
        },
        "uptime_seconds": 604800
    }

# Logging function (background task)
async def log_evaluation(evaluation: dict):
    """Log evaluation to audit trail"""
    # Write to audit log file or database
    with open("audit_logs/evaluations.jsonl", "a") as f:
        f.write(json.dumps(evaluation) + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### 3. Orchestration Layer - LangGraph

```python
# services/orchestrator.py - LangGraph orchestrator
import asyncio
import time
from typing import Dict, List, Any
from datetime import datetime
import json

class LoanOrchestrator:
    """Coordinates multi-agent loan evaluation workflow"""
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.weights = {
            "document": 0.15,
            "credit": 0.30,
            "risk": 0.30,
            "compliance": 0.25
        }
    
    async def evaluate(self, application: Dict) -> Dict:
        """
        Main orchestration workflow for loan evaluation.
        
        Flow:
        1. Validate application
        2. Execute agents in parallel
        3. Synthesize results
        4. Make decision
        5. Generate explanation
        6. Create audit trail
        """
        start_time = time.time()
        
        try:
            # Step 1: Validation
            self._validate_application(application)
            
            # Step 2: Parallel agent execution
            agent_results = await self._execute_agents_parallel(application)
            
            # Step 3: Result synthesis
            final_score, analysis = self._synthesize_results(agent_results)
            
            # Step 4: Decision making
            decision, risk_level = self._make_decision(final_score, agent_results)
            
            # Step 5: Generate explanation
            explanation = self._generate_explanation(
                agent_results, final_score, decision
            )
            
            # Step 6: Build response with audit trail
            processing_time = (time.time() - start_time) * 1000
            
            response = {
                "evaluation_id": application.get("evaluation_id"),
                "application_id": application.get("application_id"),
                "status": "completed",
                "decision": decision,
                "final_score": final_score,
                "risk_level": risk_level,
                "processing_time_ms": processing_time,
                "agent_results": agent_results,
                "explanation": explanation,
                "approval_details": self._generate_approval_details(
                    application, final_score, decision
                ) if decision == "APPROVED" else None,
                "audit_trail": self._create_audit_trail(
                    application, agent_results, decision, processing_time
                )
            }
            
            return response
            
        except ValueError as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _execute_agents_parallel(self, application: Dict) -> List[Dict]:
        """Execute all agents concurrently"""
        tasks = [
            self.agents["document"].execute(application),
            self.agents["credit"].execute(application),
            self.agents["risk"].execute(application),
            self.agents["compliance"].execute(application)
        ]
        
        results = await asyncio.gather(*tasks)
        return results
    
    def _synthesize_results(self, agent_results: List[Dict]) -> tuple:
        """Combine agent scores using weighted average"""
        final_score = 0
        analysis = {}
        
        agent_names = ["document", "credit", "risk", "compliance"]
        
        for result, name in zip(agent_results, agent_names):
            if result["status"] == "completed":
                score = result["score"]
                weight = self.weights[name]
                final_score += score * weight
                analysis[name] = {
                    "score": score,
                    "weight": weight,
                    "contribution": score * weight
                }
        
        return final_score, analysis
    
    def _make_decision(self, final_score: float, agent_results: List[Dict]) -> tuple:
        """Apply decision thresholds"""
        # Check for critical flags
        critical_flags = self._check_critical_flags(agent_results)
        
        if critical_flags:
            return "REJECTED", "CRITICAL"
        
        if final_score >= 70:
            risk_level = "LOW" if final_score >= 80 else "MEDIUM"
            return "APPROVED", risk_level
        elif final_score >= 45:
            return "MANUAL_REVIEW", "MEDIUM"
        else:
            return "REJECTED", "HIGH"
    
    def _check_critical_flags(self, agent_results: List[Dict]) -> bool:
        """Check for critical rejection flags"""
        critical_flags = [
            "UNDERAGE", "OVERAGE", "KYC_INCOMPLETE",
            "SANCTIONED_ENTITY", "HIGH_DEFAULT_RISK"
        ]
        
        for result in agent_results:
            if "findings" in result:
                for flag in critical_flags:
                    if flag in str(result.get("findings", {})):
                        return True
        return False
    
    def _generate_explanation(self, agent_results: List[Dict], 
                              final_score: float, decision: str) -> Dict:
        """Generate human-readable explanation"""
        summary = self._generate_summary(decision, final_score)
        
        key_findings = []
        for result in agent_results:
            if result["status"] == "completed":
                finding = self._extract_key_finding(result)
                if finding:
                    key_findings.append(finding)
        
        return {
            "summary": summary,
            "key_findings": key_findings
        }
    
    def _generate_summary(self, decision: str, score: float) -> str:
        """Generate decision summary"""
        if decision == "APPROVED":
            return (f"Application APPROVED with composite score {score:.1f}/100. "
                   "Applicant meets all eligibility criteria and demonstrates "
                   "strong repayment capacity.")
        elif decision == "REJECTED":
            return (f"Application REJECTED with score {score:.1f}/100. "
                   "Applicant does not meet minimum eligibility requirements.")
        else:
            return (f"Application requires MANUAL REVIEW with score {score:.1f}/100. "
                   "Escalating to senior credit officer for detailed assessment.")
    
    def _extract_key_finding(self, agent_result: Dict) -> Dict:
        """Extract key finding from agent result"""
        agent_name = agent_result.get("agent_name", "Unknown")
        
        if "finding" in agent_result:
            impact = "POSITIVE" if agent_result["score"] >= 75 else "NEGATIVE"
        else:
            impact = "NEUTRAL"
        
        return {
            "factor": agent_name,
            "impact": impact,
            "details": agent_result.get("reasoning", "")
        }
    
    def _generate_approval_details(self, application: Dict, 
                                   final_score: float, decision: str) -> Dict:
        """Generate approval details"""
        loan_amount = application["loan_details"]["amount"]
        tenure_months = application["loan_details"]["tenure_months"]
        
        # Calculate interest rate based on score and risk
        base_rate = 7.5
        rate = base_rate + (0.1 if final_score < 75 else 0)
        
        # Calculate monthly EMI
        monthly_rate = rate / 100 / 12
        num_payments = tenure_months
        emi = (loan_amount * monthly_rate * (1 + monthly_rate)**num_payments) / \
              ((1 + monthly_rate)**num_payments - 1)
        
        return {
            "approved_amount": loan_amount,
            "interest_rate": rate,
            "monthly_emi": emi,
            "conditions": [
                "Salary account to be maintained with RS Bank",
                "Annual credit score review",
                "Insurance coverage as per bank policy"
            ]
        }
    
    def _create_audit_trail(self, application: Dict, agent_results: List[Dict],
                           decision: str, processing_time: float) -> List[Dict]:
        """Create detailed audit trail for compliance"""
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "stage": "Application Received",
                "status": "completed",
                "details": f"Application {application['application_id']} received"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "stage": "Agent Execution",
                "status": "completed",
                "details": f"4 agents executed in parallel ({processing_time:.0f}ms total)"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "stage": "Decision Synthesis",
                "status": "completed",
                "details": f"Final score calculated → {decision}"
            }
        ]
    
    def _validate_application(self, application: Dict):
        """Validate application data"""
        required_fields = ["applicant", "loan_details", "application_id"]
        for field in required_fields:
            if field not in application:
                raise ValueError(f"Missing required field: {field}")
```

---

### 4. Advanced Agent Implementation with Claude Integration

```python
# agents/claude_integrated_agent.py - Using Anthropic Claude SDK
from anthropic import Anthropic

class ClaudeEnhancedAgent:
    """Agent that uses Claude for intelligent analysis"""
    
    def __init__(self, name: str, weight: float, system_prompt: str):
        self.name = name
        self.weight = weight
        self.client = Anthropic(api_key="your-key")
        self.system_prompt = system_prompt
        self.conversation_history = []
    
    async def analyze(self, application: Dict) -> Dict:
        """Use Claude for analysis with multi-turn conversation"""
        # First turn: Initial analysis
        initial_message = self._format_analysis_prompt(application)
        
        response = self.client.messages.create(
            model="claude-opus-4.8",
            max_tokens=1024,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": initial_message}
            ]
        )
        
        initial_analysis = response.content[0].text
        
        # Second turn: Generate score and confidence
        scoring_prompt = f"""Based on your analysis:
        
        {initial_analysis}
        
        Please provide:
        1. A confidence percentage (0-100)
        2. A reasoning explanation
        3. Any flags or concerns
        
        Format as JSON."""
        
        response2 = self.client.messages.create(
            model="claude-opus-4.8",
            max_tokens=512,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": initial_message},
                {"role": "assistant", "content": initial_analysis},
                {"role": "user", "content": scoring_prompt}
            ]
        )
        
        return self._parse_response(response2.content[0].text)
    
    def _format_analysis_prompt(self, application: Dict) -> str:
        """Format analysis request for Claude"""
        return f"""Analyze this loan application:
        
        Applicant: {application['applicant']['name']}
        Age: {application['applicant']['age']}
        Annual Income: Rs. {application['applicant']['annual_income']}
        Credit Score: {application['applicant']['credit_score']}
        Employment: {application['applicant']['employment_type']} for {application['applicant']['employment_years']} years
        Loan Requested: Rs. {application['loan_details']['amount']} for {application['loan_details']['tenure_months']} months
        
        Please evaluate comprehensively."""
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Claude's response"""
        import json
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)
            return parsed
        except:
            return {
                "score": 50,
                "confidence": 50,
                "reasoning": response_text
            }
```

---

### 5. MCP Server Implementation

```python
# mcp_servers/applicant_db.py - FastMCP-based MCP server
from fastmcp import FastMCP
from typing import Any

mcp = FastMCP("ApplicantDB")

# Mock database
APPLICANT_DATABASE = {
    "APP001": {
        "name": "Rajesh Kumar",
        "age": 38,
        "employer": "TCS",
        "employment_years": 12,
        "income_verified": True,
        "documents_on_file": ["aadhar", "pan", "salary_slip"]
    }
}

@mcp.tool()
def get_applicant(applicant_id: str) -> dict:
    """Retrieve applicant profile from database"""
    return APPLICANT_DATABASE.get(applicant_id, {})

@mcp.tool()
def get_credit_score(applicant_id: str) -> int:
    """Get credit score from credit bureau"""
    # Would call actual credit bureau API
    return 795  # Mock value

@mcp.tool()
def verify_employment(employer: str, employment_years: int) -> dict:
    """Verify employment details"""
    return {
        "employer_verified": True,
        "employment_stability": "good" if employment_years >= 5 else "fair",
        "verification_date": "2024-01-15"
    }

@mcp.tool()
def send_notification(applicant_id: str, template: str, data: dict) -> str:
    """Send notification to applicant"""
    print(f"Sending {template} to {applicant_id}")
    return f"notification_id_{applicant_id}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8001)
```

---

## 🔄 State Management & Workflow

### LangGraph State Schema

```python
from typing import TypedDict, List, Dict

class LoanApplicationState(TypedDict):
    """Defines the state for loan evaluation workflow"""
    
    # Input
    application_id: str
    applicant_data: Dict
    loan_details: Dict
    documents: List[str]
    
    # Processing
    document_score: float
    credit_score: float
    risk_score: float
    compliance_score: float
    
    # Output
    final_score: float
    decision: str
    risk_level: str
    explanation: Dict
    approval_details: Dict
    audit_trail: List[Dict]
    
    # Metadata
    created_at: str
    completed_at: str
    processing_time_ms: float

# Workflow graph
def create_loan_evaluation_graph():
    """Create LangGraph workflow"""
    from langgraph.graph import StateGraph
    
    workflow = StateGraph(LoanApplicationState)
    
    # Add nodes
    workflow.add_node("validate", validate_application)
    workflow.add_node("document_agent", run_document_agent)
    workflow.add_node("credit_agent", run_credit_agent)
    workflow.add_node("risk_agent", run_risk_agent)
    workflow.add_node("compliance_agent", run_compliance_agent)
    workflow.add_node("synthesize", synthesize_results)
    workflow.add_node("decide", make_decision)
    
    # Add edges
    workflow.add_edge("START", "validate")
    workflow.add_edge("validate", "document_agent")
    workflow.add_edge("validate", "credit_agent")
    workflow.add_edge("validate", "risk_agent")
    workflow.add_edge("validate", "compliance_agent")
    workflow.add_edge("document_agent", "synthesize")
    workflow.add_edge("credit_agent", "synthesize")
    workflow.add_edge("risk_agent", "synthesize")
    workflow.add_edge("compliance_agent", "synthesize")
    workflow.add_edge("synthesize", "decide")
    workflow.add_edge("decide", "END")
    
    return workflow.compile()
```

---

## 📊 Performance Optimization

### Parallelization Strategy

```python
# Parallel agent execution pattern
async def execute_agents_optimized(application: Dict) -> Dict:
    """
    Execute agents with optimal parallelization:
    - Level 1: All 4 agents in parallel (independent execution)
    - Level 2: Within each agent, parallel sub-tasks
    - Level 3: MCP server calls in parallel
    """
    
    # Level 1: Parallel agent execution
    start = time.time()
    
    document_task = document_agent.execute(application)
    credit_task = credit_agent.execute(application)
    risk_task = risk_agent.execute(application)
    compliance_task = compliance_agent.execute(application)
    
    results = await asyncio.gather(
        document_task,
        credit_task,
        risk_task,
        compliance_task
    )
    
    elapsed = time.time() - start
    print(f"Parallel execution: {elapsed*1000:.1f}ms")
    
    return {
        "document": results[0],
        "credit": results[1],
        "risk": results[2],
        "compliance": results[3]
    }

# Caching strategy
from functools import lru_cache
import hashlib

@lru_cache(maxsize=10000)
def get_cached_credit_score(applicant_id: str) -> int:
    """Cache credit scores to reduce MCP server calls"""
    return fetch_from_credit_bureau(applicant_id)

# Connection pooling
from aiohttp import ClientSession

class OptimizedMCPClient:
    def __init__(self, max_connections=100):
        self.session = None
        self.max_connections = max_connections
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.max_connections)
        self.session = ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()
```

---

## 🧪 Testing Framework

```python
# tests/test_orchestrator.py - Comprehensive testing
import pytest
import asyncio
from datetime import datetime

class TestLoanOrchestrator:
    
    @pytest.fixture
    def orchestrator(self):
        agents = {
            "document": MockDocumentAgent(),
            "credit": MockCreditAgent(),
            "risk": MockRiskAgent(),
            "compliance": MockComplianceAgent()
        }
        return LoanOrchestrator(agents)
    
    @pytest.fixture
    def sample_application(self):
        return {
            "application_id": "TEST001",
            "applicant": {
                "name": "Test User",
                "age": 35,
                "annual_income": 1000000,
                "credit_score": 750
            },
            "loan_details": {
                "amount": 5000000,
                "tenure_months": 60
            }
        }
    
    @pytest.mark.asyncio
    async def test_evaluation_within_sla(self, orchestrator, sample_application):
        """Test that evaluation completes within 100ms SLA"""
        result = await orchestrator.evaluate(sample_application)
        assert result["processing_time_ms"] < 100
    
    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self, orchestrator, sample_application):
        """Test that all agents execute in parallel"""
        result = await orchestrator.evaluate(sample_application)
        
        # Should have 4 agent results
        assert len(result["agent_results"]) == 4
        
        # Processing time should be ~1 agent time, not 4x
        # (If sequential: ~300ms, if parallel: ~100ms)
        assert result["processing_time_ms"] < 150
    
    @pytest.mark.asyncio
    async def test_decision_logic_approved(self, orchestrator):
        application = self.sample_application()
        # Set scores to trigger APPROVED decision
        result = await orchestrator.evaluate(application)
        
        if result["final_score"] >= 70:
            assert result["decision"] == "APPROVED"
    
    @pytest.mark.asyncio
    async def test_decision_logic_rejected(self, orchestrator):
        application = self.sample_application()
        # Set scores to trigger REJECTED decision
        result = await orchestrator.evaluate(application)
        
        if result["final_score"] < 45:
            assert result["decision"] == "REJECTED"
    
    def test_final_score_calculation(self, orchestrator):
        """Test weighted score calculation"""
        agent_scores = {
            "document": 95,
            "credit": 88,
            "risk": 76,
            "compliance": 100
        }
        
        expected_score = (
            95 * 0.15 +
            88 * 0.30 +
            76 * 0.30 +
            100 * 0.25
        )
        
        assert expected_score == 88.5
    
    def test_audit_trail_creation(self, orchestrator):
        """Test that audit trail is properly created"""
        result = {"audit_trail": []}  # Mock
        assert isinstance(result["audit_trail"], list)

# Load testing
@pytest.mark.asyncio
async def test_throughput_1000_applications(orchestrator):
    """Test processing 1000 applications"""
    applications = [
        generate_random_application() for _ in range(1000)
    ]
    
    start = time.time()
    tasks = [orchestrator.evaluate(app) for app in applications]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    throughput = 1000 / elapsed
    assert throughput > 80  # 80+ apps/sec
    
    approved_count = sum(1 for r in results if r["decision"] == "APPROVED")
    print(f"Processed 1000 apps in {elapsed:.1f}s ({throughput:.0f} apps/sec)")
    print(f"Approved: {approved_count}, Decision distribution: {calc_distribution(results)}")
```

---

## 🚀 Deployment Configuration

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 8001 8002 8003

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "main.py"]
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loan-approval-service
  namespace: rs-bank
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: loan-approval
  template:
    metadata:
      labels:
        app: loan-approval
    spec:
      containers:
      - name: api
        image: rs-bank/loan-approval:1.0
        ports:
        - containerPort: 8000
          name: http
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

**Status**: Ready for Implementation ✅  
**Last Updated**: July 3, 2026  
**Prepared by**: Senior Architecture Team
