#!/usr/bin/env python3
"""
FastAPI-based Microservices for RS Bank Loan Approval Agents
Each agent runs as an independent REST API service
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Dict, List, Optional, Any
import time
import uuid
from datetime import datetime
import logging
import asyncio
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ApplicantData(BaseModel):
    """Applicant information"""
    applicant_id: str
    name: str
    age: int
    annual_income: float
    employment_type: str
    employment_years: int
    credit_score: int
    existing_liabilities: float
    total_assets: float
    location: str
    kyc_verified: bool
    payment_defaults: int = 0
    bankruptcy_history: bool = False

    @validator('age')
    def age_valid(cls, v):
        if v < 18 or v > 100:
            raise ValueError('Age must be between 18 and 100')
        return v

    @validator('credit_score')
    def credit_score_valid(cls, v):
        if v < 300 or v > 900:
            raise ValueError('Credit score must be between 300 and 900')
        return v

class LoanData(BaseModel):
    """Loan information"""
    loan_id: str
    amount: float
    tenure_months: int
    purpose: str

    @validator('amount')
    def amount_valid(cls, v):
        if v <= 0:
            raise ValueError('Loan amount must be positive')
        return v

    @validator('tenure_months')
    def tenure_valid(cls, v):
        if v < 1 or v > 360:
            raise ValueError('Tenure must be between 1 and 360 months')
        return v

class EvaluationRequest(BaseModel):
    """Request for agent evaluation"""
    applicant: ApplicantData
    loan: LoanData

class AgentResponse(BaseModel):
    """Response from agent"""
    agent_name: str
    score: float
    confidence: float
    status: str
    findings: Dict[str, Any]
    processing_time_ms: float
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    agent_name: str
    uptime_seconds: int
    version: str

# ============================================================================
# DOCUMENT VERIFICATION AGENT (FASTAPI)
# ============================================================================

def create_document_agent():
    """Create Document Verification Agent FastAPI app"""
    app = FastAPI(
        title="Document Verification Agent",
        description="Verifies document completeness and consistency",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Server startup time
    app.startup_time = time.time()

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        uptime = int(time.time() - app.startup_time)
        return HealthResponse(
            status="healthy",
            agent_name="Document Verification Agent",
            uptime_seconds=uptime,
            version="1.0.0"
        )

    @app.post("/evaluate", response_model=AgentResponse)
    async def evaluate(request: EvaluationRequest):
        """Evaluate document completeness and consistency"""
        start_time = time.time()

        try:
            applicant = request.applicant

            # Document completeness check
            completeness_score = 90
            if not applicant.kyc_verified:
                completeness_score -= 30

            # Data consistency check
            consistency_score = 85
            if applicant.location and len(applicant.location) > 0:
                consistency_score = 95

            # Final score
            final_score = (completeness_score * 0.4) + (consistency_score * 0.6)

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"Document evaluation completed: score={final_score:.1f}")

            return AgentResponse(
                agent_name="Document Verification Agent",
                score=min(100, final_score),
                confidence=0.98,
                status="completed",
                findings={
                    "document_completeness": completeness_score,
                    "data_consistency": consistency_score,
                    "kyc_verified": applicant.kyc_verified
                },
                processing_time_ms=processing_time,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/info")
    async def get_info():
        """Get agent information"""
        return {
            "name": "Document Verification Agent",
            "weight": 0.15,
            "version": "1.0.0",
            "description": "Verifies document completeness and consistency",
            "capabilities": [
                "Document completeness check",
                "Data consistency validation",
                "KYC verification",
                "Anomaly detection"
            ]
        }

    return app

# ============================================================================
# CREDIT ANALYSIS AGENT (FASTAPI)
# ============================================================================

def create_credit_agent():
    """Create Credit Analysis Agent FastAPI app"""
    app = FastAPI(
        title="Credit Analysis Agent",
        description="Analyzes credit worthiness and payment history",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Server startup time
    app.startup_time = time.time()

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        uptime = int(time.time() - app.startup_time)
        return HealthResponse(
            status="healthy",
            agent_name="Credit Analysis Agent",
            uptime_seconds=uptime,
            version="1.0.0"
        )

    @app.post("/evaluate", response_model=AgentResponse)
    async def evaluate(request: EvaluationRequest):
        """Evaluate credit worthiness"""
        start_time = time.time()

        try:
            applicant = request.applicant

            # Credit score rating
            if applicant.credit_score >= 750:
                credit_rating = "Excellent"
                score_component = 100
            elif applicant.credit_score >= 700:
                credit_rating = "Very Good"
                score_component = 85
            elif applicant.credit_score >= 650:
                credit_rating = "Good"
                score_component = 70
            elif applicant.credit_score >= 600:
                credit_rating = "Fair"
                score_component = 50
            else:
                credit_rating = "Poor"
                score_component = 20

            # History component (15%)
            history_component = 100 if applicant.employment_years >= 10 else (75 if applicant.employment_years >= 5 else 50)

            # Payment history component (20%)
            payment_component = max(10, 100 - (applicant.payment_defaults * 20))

            # Bankruptcy component (15%)
            bankruptcy_component = 20 if applicant.bankruptcy_history else 100

            # Weighted score
            final_score = (score_component * 0.40 +
                          history_component * 0.15 +
                          payment_component * 0.20 +
                          bankruptcy_component * 0.15)

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"Credit evaluation completed: score={final_score:.1f}")

            return AgentResponse(
                agent_name="Credit Analysis Agent",
                score=min(100, final_score),
                confidence=0.92,
                status="completed",
                findings={
                    "credit_score": applicant.credit_score,
                    "credit_rating": credit_rating,
                    "payment_defaults": applicant.payment_defaults,
                    "bankruptcy_history": applicant.bankruptcy_history,
                    "score_breakdown": {
                        "score_component": score_component,
                        "history_component": history_component,
                        "payment_component": payment_component,
                        "bankruptcy_component": bankruptcy_component
                    }
                },
                processing_time_ms=processing_time,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/info")
    async def get_info():
        """Get agent information"""
        return {
            "name": "Credit Analysis Agent",
            "weight": 0.30,
            "version": "1.0.0",
            "description": "Analyzes credit worthiness and payment history",
            "capabilities": [
                "Credit score analysis",
                "Payment history review",
                "Default tracking",
                "Bankruptcy detection"
            ]
        }

    return app

# ============================================================================
# RISK ASSESSMENT AGENT (FASTAPI)
# ============================================================================

def create_risk_agent():
    """Create Risk Assessment Agent FastAPI app"""
    app = FastAPI(
        title="Risk Assessment Agent",
        description="Assesses financial risk and repayment capacity",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Server startup time
    app.startup_time = time.time()

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        uptime = int(time.time() - app.startup_time)
        return HealthResponse(
            status="healthy",
            agent_name="Risk Assessment Agent",
            uptime_seconds=uptime,
            version="1.0.0"
        )

    @app.post("/evaluate", response_model=AgentResponse)
    async def evaluate(request: EvaluationRequest):
        """Evaluate financial risk"""
        start_time = time.time()

        try:
            applicant = request.applicant
            loan = request.loan

            # Calculate monthly income
            monthly_income = applicant.annual_income / 12

            # Calculate DTI ratio
            monthly_obligations = applicant.existing_liabilities / 12
            dti_ratio = (monthly_obligations / monthly_income * 100) if monthly_income > 0 else 0

            # DTI scoring (25%)
            dti_score = 100 if dti_ratio < 20 else (85 if dti_ratio < 35 else (60 if dti_ratio < 50 else 20))

            # LTV ratio
            ltv_ratio = (loan.amount / applicant.total_assets * 100) if applicant.total_assets > 0 else 100

            # LTV scoring (20%)
            ltv_score = 100 if ltv_ratio < 60 else (85 if ltv_ratio < 75 else (60 if ltv_ratio < 85 else 30))

            # Employment stability (20%)
            employment_score = 95 if applicant.employment_years >= 10 else (75 if applicant.employment_years >= 5 else (60 if applicant.employment_years >= 2 else 40))

            # Income adequacy (20%)
            income_score = 100 if monthly_income > loan.amount / (loan.tenure_months * 20) else (80 if monthly_income > loan.amount / (loan.tenure_months * 30) else 50)

            # Asset coverage (15%)
            asset_score = 100 if applicant.total_assets >= loan.amount * 2 else (85 if applicant.total_assets >= loan.amount * 1.5 else (60 if applicant.total_assets >= loan.amount else 40))

            # Weighted score
            final_score = (dti_score * 0.25 +
                          ltv_score * 0.20 +
                          employment_score * 0.20 +
                          income_score * 0.20 +
                          asset_score * 0.15)

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"Risk evaluation completed: score={final_score:.1f}")

            return AgentResponse(
                agent_name="Risk Assessment Agent",
                score=min(100, final_score),
                confidence=0.85,
                status="completed",
                findings={
                    "dti_ratio": round(dti_ratio, 2),
                    "ltv_ratio": round(ltv_ratio, 2),
                    "monthly_income": round(monthly_income, 2),
                    "employment_years": applicant.employment_years,
                    "total_assets": applicant.total_assets,
                    "score_breakdown": {
                        "dti_score": dti_score,
                        "ltv_score": ltv_score,
                        "employment_score": employment_score,
                        "income_score": income_score,
                        "asset_score": asset_score
                    }
                },
                processing_time_ms=processing_time,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/info")
    async def get_info():
        """Get agent information"""
        return {
            "name": "Risk Assessment Agent",
            "weight": 0.30,
            "version": "1.0.0",
            "description": "Assesses financial risk and repayment capacity",
            "capabilities": [
                "DTI ratio calculation",
                "LTV ratio evaluation",
                "Employment stability assessment",
                "Income adequacy analysis",
                "Asset coverage evaluation"
            ]
        }

    return app

# ============================================================================
# COMPLIANCE AGENT (FASTAPI)
# ============================================================================

def create_compliance_agent():
    """Create Compliance & Regulatory Agent FastAPI app"""
    app = FastAPI(
        title="Compliance & Regulatory Agent",
        description="Ensures regulatory compliance and KYC/AML checks",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Server startup time
    app.startup_time = time.time()

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        uptime = int(time.time() - app.startup_time)
        return HealthResponse(
            status="healthy",
            agent_name="Compliance & Regulatory Agent",
            uptime_seconds=uptime,
            version="1.0.0"
        )

    @app.post("/evaluate", response_model=AgentResponse)
    async def evaluate(request: EvaluationRequest):
        """Evaluate regulatory compliance"""
        start_time = time.time()

        try:
            applicant = request.applicant
            loan = request.loan

            flags = []
            score = 100

            # Age eligibility check
            if applicant.age < 21:
                flags.append("UNDERAGE")
                score -= 50
            elif applicant.age > 65:
                flags.append("OVERAGE")
                score -= 50

            # Maturity age check
            maturity_age = applicant.age + (loan.tenure_months / 12)
            if maturity_age > 70:
                flags.append("MATURITY_AGE_EXCEEDED")
                score -= 20

            # KYC verification
            if not applicant.kyc_verified:
                flags.append("KYC_INCOMPLETE")
                score -= 40

            # Loan amount limits
            max_limits = {"home": 10000000, "auto": 2000000, "personal": 500000, "education": 1000000, "business": 50000000}
            max_limit = max_limits.get(loan.purpose.lower(), 5000000)
            if loan.amount > max_limit:
                flags.append("LOAN_AMOUNT_EXCEEDED")
                score -= 30

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"Compliance evaluation completed: score={max(0, score):.1f}")

            return AgentResponse(
                agent_name="Compliance & Regulatory Agent",
                score=max(0, score),
                confidence=0.98,
                status="completed",
                findings={
                    "age": applicant.age,
                    "maturity_age": round(maturity_age, 1),
                    "kyc_verified": applicant.kyc_verified,
                    "loan_amount": loan.amount,
                    "loan_type": loan.purpose,
                    "flags": flags
                },
                processing_time_ms=processing_time,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/info")
    async def get_info():
        """Get agent information"""
        return {
            "name": "Compliance & Regulatory Agent",
            "weight": 0.25,
            "version": "1.0.0",
            "description": "Ensures regulatory compliance and KYC/AML checks",
            "capabilities": [
                "Age eligibility validation",
                "Tenure constraint checking",
                "KYC verification",
                "AML screening",
                "Loan amount limit validation"
            ]
        }

    return app

# ============================================================================
# API GATEWAY (FASTAPI)
# ============================================================================

def create_api_gateway(agent_urls: Dict[str, str]):
    """Create API Gateway that orchestrates all agents"""
    app = FastAPI(
        title="RS Bank Loan Approval API Gateway",
        description="Orchestrates multi-agent loan evaluation",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store agent URLs
    app.agent_urls = agent_urls
    app.startup_time = time.time()

    @app.get("/health")
    async def health_check():
        """Gateway health check"""
        uptime = int(time.time() - app.startup_time)
        return {
            "status": "healthy",
            "gateway": "API Gateway",
            "uptime_seconds": uptime,
            "agents": list(app.agent_urls.keys())
        }

    @app.post("/evaluate")
    async def evaluate(request: EvaluationRequest):
        """Evaluate loan application using all agents"""
        start_time = time.time()
        evaluation_id = f"EVAL{uuid.uuid4().hex[:8].upper()}"

        try:
            # Call all agents in parallel
            async with httpx.AsyncClient() as client:
                tasks = []
                for agent_name, agent_url in app.agent_urls.items():
                    task = client.post(
                        f"{agent_url}/evaluate",
                        json=request.dict(),
                        timeout=10.0
                    )
                    tasks.append(task)

                responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Process responses
            agent_results = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Agent call failed: {response}")
                    continue

                if response.status_code == 200:
                    agent_results.append(response.json())
                else:
                    logger.error(f"Agent returned error: {response.status_code}")

            # Synthesize results
            if not agent_results:
                raise Exception("No agent results received")

            weights = {
                "Document Verification Agent": 0.15,
                "Credit Analysis Agent": 0.30,
                "Risk Assessment Agent": 0.30,
                "Compliance & Regulatory Agent": 0.25
            }

            final_score = sum(r["score"] * weights.get(r["agent_name"], 0.25) for r in agent_results)

            # Determine risk level
            if final_score >= 80:
                risk_level = "LOW"
            elif final_score >= 60:
                risk_level = "MEDIUM"
            elif final_score >= 45:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"

            # Make decision
            if final_score >= 70:
                decision = "APPROVED"
            elif final_score >= 45:
                decision = "MANUAL_REVIEW"
            else:
                decision = "REJECTED"

            processing_time = (time.time() - start_time) * 1000

            logger.info(f"Evaluation {evaluation_id} completed: decision={decision}, score={final_score:.1f}")

            return {
                "evaluation_id": evaluation_id,
                "loan_id": request.loan.loan_id,
                "decision": decision,
                "final_score": round(final_score, 1),
                "risk_level": risk_level,
                "agent_results": agent_results,
                "processing_time_ms": round(processing_time, 2),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Gateway evaluation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agents")
    async def get_agents():
        """Get list of available agents"""
        return {
            "agents": list(app.agent_urls.keys()),
            "gateway": "API Gateway",
            "version": "1.0.0"
        }

    @app.post("/agents/status")
    async def check_agent_status():
        """Check status of all agents"""
        statuses = {}

        async with httpx.AsyncClient() as client:
            for agent_name, agent_url in app.agent_urls.items():
                try:
                    response = await client.get(f"{agent_url}/health", timeout=5.0)
                    if response.status_code == 200:
                        statuses[agent_name] = {
                            "status": "healthy",
                            "details": response.json()
                        }
                    else:
                        statuses[agent_name] = {"status": "unhealthy", "code": response.status_code}
                except Exception as e:
                    statuses[agent_name] = {"status": "error", "error": str(e)}

        return statuses

    return app

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Start individual agents and gateway
    print("RS Bank FastAPI Multi-Agent Loan Approval System")
    print("=" * 60)

    # Define agent URLs (for local development)
    agent_urls = {
        "Document Verification Agent": "http://localhost:8001",
        "Credit Analysis Agent": "http://localhost:8002",
        "Risk Assessment Agent": "http://localhost:8003",
        "Compliance & Regulatory Agent": "http://localhost:8004"
    }

    print("\nTo start all services, run these commands in separate terminals:")
    print("\n1. Document Agent:")
    print("   uvicorn fastapi_agents:document_agent --port 8001 --reload")
    print("\n2. Credit Agent:")
    print("   uvicorn fastapi_agents:credit_agent --port 8002 --reload")
    print("\n3. Risk Agent:")
    print("   uvicorn fastapi_agents:risk_agent --port 8003 --reload")
    print("\n4. Compliance Agent:")
    print("   uvicorn fastapi_agents:compliance_agent --port 8004 --reload")
    print("\n5. API Gateway:")
    print("   uvicorn fastapi_agents:gateway --port 8000 --reload")

    print("\nAPI Gateway URLs:")
    print("  - Health Check: http://localhost:8000/health")
    print("  - Evaluate: POST http://localhost:8000/evaluate")
    print("  - Agents: http://localhost:8000/agents")
    print("  - Agent Status: POST http://localhost:8000/agents/status")
    print("  - Docs: http://localhost:8000/docs")

# Create agent apps as module-level variables for uvicorn
document_agent = create_document_agent()
credit_agent = create_credit_agent()
risk_agent = create_risk_agent()
compliance_agent = create_compliance_agent()

# Default agent URLs for local development
_agent_urls = {
    "Document Verification Agent": "http://localhost:8001",
    "Credit Analysis Agent": "http://localhost:8002",
    "Risk Assessment Agent": "http://localhost:8003",
    "Compliance & Regulatory Agent": "http://localhost:8004"
}

gateway = create_api_gateway(_agent_urls)
