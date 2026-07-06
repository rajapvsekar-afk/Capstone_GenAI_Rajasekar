#!/usr/bin/env python3
"""
LangGraph + LangChain Orchestration Engine for RS Bank Loan Approval
Advanced multi-agent workflow orchestration with state management
"""

from typing import TypedDict, Any, Annotated, Sequence, Optional
from enum import Enum
import time
import json
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.types import Send

# LangChain imports (for agent wrapper if needed)
from langchain.tools import BaseTool, tool
from langchain_core.pydantic_v1 import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class AgentName(Enum):
    """Agent names in the system"""
    DOCUMENT = "Document Verification Agent"
    CREDIT = "Credit Analysis Agent"
    RISK = "Risk Assessment Agent"
    COMPLIANCE = "Compliance & Regulatory Agent"

class DecisionStatus(Enum):
    """Loan decision status"""
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"
    PENDING = "pending"

@dataclass
class ApplicantInfo:
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

@dataclass
class LoanInfo:
    """Loan request information"""
    loan_id: str
    amount: float
    tenure_months: int
    purpose: str

@dataclass
class AgentResult:
    """Result from an individual agent"""
    agent_name: str
    score: float
    confidence: float
    status: str
    findings: dict
    processing_time_ms: float
    timestamp: str

class OrchestratorState(TypedDict):
    """State for the orchestration workflow"""
    # Input
    applicant: dict
    loan: dict

    # Processing
    agent_results: Sequence[AgentResult]
    intermediate_scores: dict

    # Output
    final_score: float
    decision: str
    risk_level: str
    approval_details: Optional[dict]
    rejection_reasons: list
    manual_review_reasons: list
    explanation: dict
    audit_trail: list

    # Metadata
    evaluation_id: str
    start_time: float
    processing_times: dict

# ============================================================================
# ORCHESTRATION LOGIC
# ============================================================================

class LoanApprovalOrchestrator:
    """Main orchestration engine using LangGraph"""

    def __init__(self):
        self.agent_weights = {
            AgentName.DOCUMENT.value: 0.15,
            AgentName.CREDIT.value: 0.30,
            AgentName.RISK.value: 0.30,
            AgentName.COMPLIANCE.value: 0.25,
        }
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(OrchestratorState)

        # Add nodes
        workflow.add_node("initialize", self._initialize)
        workflow.add_node("execute_agents", self._execute_agents)
        workflow.add_node("synthesize_scores", self._synthesize_scores)
        workflow.add_node("determine_risk_level", self._determine_risk_level)
        workflow.add_node("make_decision", self._make_decision)
        workflow.add_node("generate_explanation", self._generate_explanation)
        workflow.add_node("create_audit_trail", self._create_audit_trail)
        workflow.add_node("finalize", self._finalize)

        # Add edges
        workflow.add_edge("initialize", "execute_agents")
        workflow.add_edge("execute_agents", "synthesize_scores")
        workflow.add_edge("synthesize_scores", "determine_risk_level")
        workflow.add_edge("determine_risk_level", "make_decision")
        workflow.add_edge("make_decision", "generate_explanation")
        workflow.add_edge("generate_explanation", "create_audit_trail")
        workflow.add_edge("create_audit_trail", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def _initialize(self, state: OrchestratorState) -> OrchestratorState:
        """Initialize evaluation"""
        logger.info("Initializing evaluation...")

        state["evaluation_id"] = f"EVAL{int(time.time() * 1000) % 1000000:06d}"
        state["start_time"] = time.time()
        state["agent_results"] = []
        state["intermediate_scores"] = {}
        state["processing_times"] = {}
        state["audit_trail"] = [{
            "timestamp": datetime.now().isoformat(),
            "stage": "INITIALIZED",
            "status": "started",
            "details": f"Evaluation {state['evaluation_id']} initialized"
        }]

        return state

    def _execute_agents(self, state: OrchestratorState) -> OrchestratorState:
        """Execute all agents in parallel (simulated)"""
        logger.info("Executing agents...")

        applicant_data = state["applicant"]
        loan_data = state["loan"]

        # Execute agents (in production, these would call FastAPI endpoints)
        results = []

        # Document Agent
        doc_result = self._run_document_agent(applicant_data, loan_data)
        results.append(doc_result)

        # Credit Agent
        credit_result = self._run_credit_agent(applicant_data, loan_data)
        results.append(credit_result)

        # Risk Agent
        risk_result = self._run_risk_agent(applicant_data, loan_data)
        results.append(risk_result)

        # Compliance Agent
        compliance_result = self._run_compliance_agent(applicant_data, loan_data)
        results.append(compliance_result)

        state["agent_results"] = results

        # Add to audit trail
        state["audit_trail"].append({
            "timestamp": datetime.now().isoformat(),
            "stage": "AGENTS_EXECUTED",
            "status": "completed",
            "details": f"4 agents executed successfully",
            "agent_count": len(results),
            "total_time_ms": sum(r.processing_time_ms for r in results)
        })

        return state

    def _synthesize_scores(self, state: OrchestratorState) -> OrchestratorState:
        """Synthesize agent scores into final score"""
        logger.info("Synthesizing scores...")

        final_score = 0.0
        for result in state["agent_results"]:
            weight = self.agent_weights.get(result.agent_name, 0.25)
            contribution = result.score * weight
            final_score += contribution
            state["intermediate_scores"][result.agent_name] = {
                "score": result.score,
                "weight": weight,
                "contribution": contribution
            }

        state["final_score"] = final_score

        # Add to audit trail
        state["audit_trail"].append({
            "timestamp": datetime.now().isoformat(),
            "stage": "SCORES_SYNTHESIZED",
            "status": "completed",
            "final_score": final_score,
            "breakdown": state["intermediate_scores"]
        })

        logger.info(f"Final score: {final_score:.1f}/100")
        return state

    def _determine_risk_level(self, state: OrchestratorState) -> OrchestratorState:
        """Determine risk level from score"""
        logger.info("Determining risk level...")

        score = state["final_score"]

        if score >= 80:
            risk_level = "LOW"
        elif score >= 60:
            risk_level = "MEDIUM"
        elif score >= 45:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        state["risk_level"] = risk_level

        # Add to audit trail
        state["audit_trail"].append({
            "timestamp": datetime.now().isoformat(),
            "stage": "RISK_DETERMINED",
            "status": "completed",
            "score": score,
            "risk_level": risk_level
        })

        logger.info(f"Risk level: {risk_level}")
        return state

    def _make_decision(self, state: OrchestratorState) -> OrchestratorState:
        """Make final decision"""
        logger.info("Making decision...")

        score = state["final_score"]
        applicant = state["applicant"]

        # Check for critical flags
        critical_flags = self._check_critical_flags(state["agent_results"])
        escalation_flags = self._check_escalation_flags(state["agent_results"], applicant)

        if critical_flags:
            decision = DecisionStatus.REJECTED.value
            state["rejection_reasons"] = critical_flags
        elif escalation_flags:
            decision = DecisionStatus.MANUAL_REVIEW.value
            state["manual_review_reasons"] = escalation_flags
        elif score >= 70:
            decision = DecisionStatus.APPROVED.value
        elif score >= 45:
            decision = DecisionStatus.MANUAL_REVIEW.value
        else:
            decision = DecisionStatus.REJECTED.value

        state["decision"] = decision

        # Generate approval details if approved
        if decision == DecisionStatus.APPROVED.value:
            state["approval_details"] = self._generate_approval_details(
                state["applicant"],
                state["loan"],
                state["final_score"]
            )

        # Add to audit trail
        state["audit_trail"].append({
            "timestamp": datetime.now().isoformat(),
            "stage": "DECISION_MADE",
            "status": "completed",
            "decision": decision,
            "score": score,
            "critical_flags": critical_flags,
            "escalation_flags": escalation_flags
        })

        logger.info(f"Decision: {decision}")
        return state

    def _generate_explanation(self, state: OrchestratorState) -> OrchestratorState:
        """Generate human-readable explanation"""
        logger.info("Generating explanation...")

        decision_text = {
            DecisionStatus.APPROVED.value: "APPROVED",
            DecisionStatus.REJECTED.value: "REJECTED",
            DecisionStatus.MANUAL_REVIEW.value: "REQUIRES MANUAL REVIEW"
        }

        summary = f"Application {decision_text[state['decision']]} with composite score {state['final_score']:.1f}/100."

        key_findings = []
        for result in state["agent_results"]:
            impact = "POSITIVE" if result.score >= 75 else ("NEUTRAL" if result.score >= 60 else "NEGATIVE")
            key_findings.append({
                "agent": result.agent_name,
                "score": result.score,
                "impact": impact,
                "details": result.findings
            })

        state["explanation"] = {
            "summary": summary,
            "key_findings": key_findings,
            "decision_rationale": self._explain_decision(state)
        }

        # Add to audit trail
        state["audit_trail"].append({
            "timestamp": datetime.now().isoformat(),
            "stage": "EXPLANATION_GENERATED",
            "status": "completed",
            "summary": summary
        })

        return state

    def _create_audit_trail(self, state: OrchestratorState) -> OrchestratorState:
        """Create final audit trail entry"""
        logger.info("Creating audit trail...")

        total_time = time.time() - state["start_time"]

        state["audit_trail"].append({
            "timestamp": datetime.now().isoformat(),
            "stage": "COMPLETED",
            "status": "completed",
            "total_processing_time_ms": total_time * 1000,
            "agent_count": len(state["agent_results"]),
            "decision": state["decision"],
            "final_score": state["final_score"]
        })

        return state

    def _finalize(self, state: OrchestratorState) -> OrchestratorState:
        """Finalize the evaluation"""
        logger.info("Finalizing evaluation...")

        # All processing done
        return state

    # Helper methods
    def _check_critical_flags(self, agent_results) -> list:
        """Check for critical rejection flags"""
        critical_flags = []

        for result in agent_results:
            if "flags" in result.findings:
                flags = result.findings["flags"]
                for flag in flags:
                    if flag in ["UNDERAGE", "OVERAGE", "KYC_INCOMPLETE", "LOAN_AMOUNT_EXCEEDED"]:
                        critical_flags.append(flag)

        return critical_flags

    def _check_escalation_flags(self, agent_results, applicant) -> list:
        """Check for escalation flags requiring manual review"""
        escalation_flags = []

        # Bankruptcy flag
        if applicant.get("bankruptcy_history"):
            escalation_flags.append("BANKRUPTCY_RECENT")

        # Multiple defaults flag
        if applicant.get("payment_defaults", 0) >= 2:
            escalation_flags.append("MULTIPLE_DEFAULTS")

        return escalation_flags

    def _generate_approval_details(self, applicant, loan, score) -> dict:
        """Generate approval details"""
        base_rate = 7.5
        rate = base_rate + (0.5 if score < 75 else 0)

        monthly_rate = rate / 100 / 12
        num_payments = loan["tenure_months"]
        emi = (loan["amount"] * monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)

        return {
            "approved_amount": loan["amount"],
            "interest_rate": rate,
            "monthly_emi": emi,
            "conditions": [
                "Salary account to be maintained with RS Bank",
                "Annual credit score review",
                "Insurance coverage as per bank policy"
            ]
        }

    def _explain_decision(self, state) -> str:
        """Generate decision rationale"""
        decision = state["decision"]
        score = state["final_score"]

        if decision == DecisionStatus.APPROVED.value:
            return f"Applicant meets all eligibility criteria with strong score of {score:.1f}. All agents concur on approval."
        elif decision == DecisionStatus.REJECTED.value:
            reasons = state.get("rejection_reasons", [])
            return f"Application rejected due to: {', '.join(reasons)}. Score {score:.1f} below threshold."
        else:
            reasons = state.get("manual_review_reasons", [])
            return f"Manual review required due to: {', '.join(reasons)}. Score {score:.1f} in review range (45-70)."

    # Agent simulators (in production, these would call FastAPI endpoints)
    def _run_document_agent(self, applicant, loan) -> AgentResult:
        """Simulate document verification agent"""
        start = time.time()

        completeness = 90 if applicant.get("kyc_verified") else 60
        consistency = 95 if applicant.get("location") else 85
        score = (completeness * 0.4) + (consistency * 0.6)

        processing_time = (time.time() - start) * 1000

        return AgentResult(
            agent_name=AgentName.DOCUMENT.value,
            score=min(100, score),
            confidence=0.98,
            status="completed",
            findings={
                "completeness": completeness,
                "consistency": consistency,
                "kyc_verified": applicant.get("kyc_verified", False)
            },
            processing_time_ms=processing_time,
            timestamp=datetime.now().isoformat()
        )

    def _run_credit_agent(self, applicant, loan) -> AgentResult:
        """Simulate credit analysis agent"""
        start = time.time()

        credit_score = applicant.get("credit_score", 700)
        if credit_score >= 750:
            score_component = 100
        elif credit_score >= 700:
            score_component = 85
        elif credit_score >= 650:
            score_component = 70
        else:
            score_component = 50 if credit_score >= 600 else 20

        employment_years = applicant.get("employment_years", 0)
        history_component = 100 if employment_years >= 10 else (75 if employment_years >= 5 else 50)

        payment_defaults = applicant.get("payment_defaults", 0)
        payment_component = max(10, 100 - (payment_defaults * 20))

        bankruptcy_component = 20 if applicant.get("bankruptcy_history") else 100

        score = (score_component * 0.40 + history_component * 0.15 +
                payment_component * 0.20 + bankruptcy_component * 0.15)

        processing_time = (time.time() - start) * 1000

        return AgentResult(
            agent_name=AgentName.CREDIT.value,
            score=min(100, score),
            confidence=0.92,
            status="completed",
            findings={
                "credit_score": credit_score,
                "payment_defaults": payment_defaults,
                "bankruptcy_history": applicant.get("bankruptcy_history", False)
            },
            processing_time_ms=processing_time,
            timestamp=datetime.now().isoformat()
        )

    def _run_risk_agent(self, applicant, loan) -> AgentResult:
        """Simulate risk assessment agent"""
        start = time.time()

        monthly_income = applicant.get("annual_income", 0) / 12
        monthly_obligations = applicant.get("existing_liabilities", 0) / 12
        dti_ratio = (monthly_obligations / monthly_income * 100) if monthly_income > 0 else 0

        dti_score = 100 if dti_ratio < 20 else (85 if dti_ratio < 35 else (60 if dti_ratio < 50 else 20))

        ltv_ratio = (loan["amount"] / applicant.get("total_assets", 1) * 100) if applicant.get("total_assets", 0) > 0 else 100
        ltv_score = 100 if ltv_ratio < 60 else (85 if ltv_ratio < 75 else (60 if ltv_ratio < 85 else 30))

        employment_score = 95 if applicant.get("employment_years", 0) >= 10 else 75

        score = (dti_score * 0.25 + ltv_score * 0.20 + employment_score * 0.55)

        processing_time = (time.time() - start) * 1000

        return AgentResult(
            agent_name=AgentName.RISK.value,
            score=min(100, score),
            confidence=0.85,
            status="completed",
            findings={
                "dti_ratio": round(dti_ratio, 2),
                "ltv_ratio": round(ltv_ratio, 2),
                "employment_years": applicant.get("employment_years", 0)
            },
            processing_time_ms=processing_time,
            timestamp=datetime.now().isoformat()
        )

    def _run_compliance_agent(self, applicant, loan) -> AgentResult:
        """Simulate compliance agent"""
        start = time.time()

        flags = []
        score = 100

        age = applicant.get("age", 35)
        if age < 21:
            flags.append("UNDERAGE")
            score -= 50
        elif age > 65:
            flags.append("OVERAGE")
            score -= 50

        maturity_age = age + (loan["tenure_months"] / 12)
        if maturity_age > 70:
            flags.append("MATURITY_AGE_EXCEEDED")
            score -= 20

        if not applicant.get("kyc_verified"):
            flags.append("KYC_INCOMPLETE")
            score -= 40

        processing_time = (time.time() - start) * 1000

        return AgentResult(
            agent_name=AgentName.COMPLIANCE.value,
            score=max(0, score),
            confidence=0.98,
            status="completed",
            findings={
                "age": age,
                "maturity_age": round(maturity_age, 1),
                "kyc_verified": applicant.get("kyc_verified", False),
                "flags": flags
            },
            processing_time_ms=processing_time,
            timestamp=datetime.now().isoformat()
        )

    def run(self, applicant: dict, loan: dict) -> dict:
        """Execute the full orchestration workflow"""
        logger.info(f"Starting loan evaluation for {applicant.get('name')}...")

        initial_state = {
            "applicant": applicant,
            "loan": loan,
            "agent_results": [],
            "intermediate_scores": {},
            "final_score": 0.0,
            "decision": "",
            "risk_level": "",
            "approval_details": None,
            "rejection_reasons": [],
            "manual_review_reasons": [],
            "explanation": {},
            "audit_trail": [],
            "evaluation_id": "",
            "start_time": time.time(),
            "processing_times": {}
        }

        result = self.graph.invoke(initial_state)

        logger.info(f"Evaluation completed: {result['decision']} (Score: {result['final_score']:.1f})")

        # Convert AgentResult dataclass to dict for JSON serialization
        agent_results_dict = [
            {
                "agent_name": r.agent_name,
                "score": r.score,
                "confidence": r.confidence,
                "status": r.status,
                "findings": r.findings,
                "processing_time_ms": r.processing_time_ms,
                "timestamp": r.timestamp
            }
            for r in result["agent_results"]
        ]

        return {
            "evaluation_id": result["evaluation_id"],
            "decision": result["decision"],
            "final_score": result["final_score"],
            "risk_level": result["risk_level"],
            "agent_results": agent_results_dict,
            "intermediate_scores": result["intermediate_scores"],
            "approval_details": result["approval_details"],
            "rejection_reasons": result["rejection_reasons"],
            "manual_review_reasons": result["manual_review_reasons"],
            "explanation": result["explanation"],
            "audit_trail": result["audit_trail"]
        }

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Create orchestrator
    orchestrator = LoanApprovalOrchestrator()

    # Test application
    applicant = {
        "applicant_id": "APP001",
        "name": "Rajesh Kumar",
        "age": 38,
        "annual_income": 2000000,
        "employment_type": "employed",
        "employment_years": 12,
        "credit_score": 795,
        "existing_liabilities": 500000,
        "total_assets": 1500000,
        "location": "Mumbai",
        "kyc_verified": True
    }

    loan = {
        "loan_id": "LN000001",
        "amount": 5000000,
        "tenure_months": 60,
        "purpose": "home"
    }

    # Run evaluation
    result = orchestrator.run(applicant, loan)

    print("\n" + "="*70)
    print("LOAN EVALUATION RESULT")
    print("="*70)
    print(json.dumps(result, indent=2, default=str))
