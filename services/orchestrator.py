"""
Loan Orchestrator Service
Coordinates multi-agent workflow and decision synthesis
"""

import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional

import sys
sys.path.insert(0, '/home/ubuntu/rs_bank_agentic_loan_platform')

from core.models import (
    LoanApplication, LoanDecision, LoanEvaluation, AgentResult, RiskLevel, AuditEntry
)
from core.event_bus import Event, EventType, event_bus
from core.explainability import explainability_engine, audit_logger
from agents.base_agent import BaseAgent
from agents.document_agent import DocumentVerificationAgent
from agents.credit_agent import CreditAnalysisAgent
from agents.risk_agent import RiskAssessmentAgent
from agents.compliance_agent import RegulatoryComplianceAgent


class AgentRegistry:
    """Registry for all available agents."""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        agents = [
            DocumentVerificationAgent(),
            CreditAnalysisAgent(),
            RiskAssessmentAgent(),
            RegulatoryComplianceAgent(),
        ]

        for agent in agents:
            self.agents[agent.name] = agent
            print(f"  ✓ Registered: {agent.name} (v{agent.version})")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        return self.agents.get(name)

    def get_all_agents(self) -> List[BaseAgent]:
        return list(self.agents.values())

    def health_check(self) -> Dict[str, dict]:
        return {name: agent.health_check() for name, agent in self.agents.items()}


class LoanOrchestrator:
    """
    Orchestrates multi-agent loan evaluation workflow.
    Implements scalable microservices-based architecture.
    """

    AGENT_WEIGHTS = {
        "Document Verification Agent": 0.15,
        "Credit Analysis Agent": 0.30,
        "Risk Assessment Agent": 0.30,
        "Regulatory Compliance Agent": 0.25,
    }

    APPROVAL_THRESHOLD = 70
    REJECTION_THRESHOLD = 45

    MANUAL_REVIEW_FLAGS = {
        "BANKRUPTCY_HISTORY",
        "AML_FLAG",
        "MULTIPLE_DEFAULTS",
        "KYC_INCOMPLETE",
        "INCOME_EMPLOYMENT_MISMATCH",
        "UNDERAGE_APPLICANT",
        "EXCEEDS_MAX_LOAN_AMOUNT",
    }

    BASE_RATES = {
        "personal": 12.5,
        "home": 8.5,
        "auto": 9.5,
        "education": 7.0,
        "business": 11.0,
    }

    def __init__(self, agent_registry: AgentRegistry):
        self.registry = agent_registry
        self.processing_queue: List[LoanApplication] = []

    async def evaluate(self, application: LoanApplication) -> LoanEvaluation:
        """Execute full loan evaluation workflow."""
        correlation_id = str(uuid.uuid4())[:12]
        start_time = time.time()

        await self._publish_evaluation_started(correlation_id, application)

        try:
            # Phase 1: Parallel agent execution
            agent_results = await self._run_agents(application, correlation_id)

            # Phase 2: Decision synthesis
            decision, overall_score, risk_level, approved_amount, interest_rate = \
                await self._synthesize_decision(agent_results, application)

            # Phase 3: Generate explanations and audit trail
            explanations, conditions, rejection_reasons, manual_review_reasons, decision_explanation = \
                await self._generate_explanations(agent_results, decision, overall_score)

            # Create evaluation
            evaluation = LoanEvaluation(
                evaluation_id=str(uuid.uuid4())[:12],
                application_id=application.application_id,
                decision=decision,
                overall_score=overall_score,
                risk_level=risk_level,
                agent_results=agent_results,
                approved_amount=approved_amount,
                interest_rate=interest_rate,
                conditions=conditions,
                rejection_reasons=rejection_reasons,
                manual_review_reasons=manual_review_reasons,
                decision_explanation=decision_explanation,
                audit_trail=audit_logger.get_audit_trail(correlation_id),
                total_processing_time_ms=(time.time() - start_time) * 1000,
            )

            await self._publish_evaluation_completed(correlation_id, evaluation)

            return evaluation

        except Exception as e:
            print(f"  ✗ Orchestration failed: {str(e)}")
            await self._publish_evaluation_failed(correlation_id, str(e))
            raise

    async def _run_agents(
        self,
        application: LoanApplication,
        correlation_id: str
    ) -> Dict[str, AgentResult]:
        """Execute all agents in parallel."""
        agents = self.registry.get_all_agents()
        context = {}

        tasks = [
            agent.execute(application, context, correlation_id)
            for agent in agents
        ]

        results = await asyncio.gather(*tasks, return_exceptions=False)

        return {
            agent.name: result
            for agent, result in zip(agents, results)
        }

    async def _synthesize_decision(
        self,
        agent_results: Dict[str, AgentResult],
        application: LoanApplication
    ) -> tuple:
        """Synthesize final decision from agent results."""
        await asyncio.sleep(0.01)  # Simulate processing

        # Calculate weighted score
        weighted_score = 0.0
        total_weight = 0.0
        all_flags = set()

        for agent_name, result in agent_results.items():
            weight = self.AGENT_WEIGHTS.get(agent_name, 0.1)
            weighted_score += result.score * weight
            total_weight += weight
            all_flags.update(result.flags)

        final_score = weighted_score / total_weight if total_weight > 0 else 0

        # Determine risk level
        if final_score >= 80:
            risk_level = RiskLevel.LOW
        elif final_score >= 65:
            risk_level = RiskLevel.MEDIUM
        elif final_score >= 50:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        # Determine decision
        if all_flags.intersection({"UNDERAGE_APPLICANT", "EXCEEDS_MAX_LOAN_AMOUNT", "INVALID_INCOME_DATA", "KYC_INCOMPLETE"}):
            decision = LoanDecision.REJECTED
        elif all_flags.intersection(self.MANUAL_REVIEW_FLAGS):
            decision = LoanDecision.REQUIRES_MANUAL_REVIEW
        elif final_score >= self.APPROVAL_THRESHOLD:
            decision = LoanDecision.APPROVED
        elif final_score >= self.REJECTION_THRESHOLD:
            decision = LoanDecision.REQUIRES_MANUAL_REVIEW
        else:
            decision = LoanDecision.REJECTED

        # Calculate approved amount and interest rate
        approved_amount = None
        interest_rate = None

        if decision == LoanDecision.APPROVED:
            approved_amount = application.requested_amount
            base_rate = self.BASE_RATES.get(application.loan_type.value, 10.0)

            if final_score >= 85:
                rate_adjustment = -1.5
            elif final_score >= 70:
                rate_adjustment = -0.5
            elif final_score >= 55:
                rate_adjustment = 0.5
            else:
                rate_adjustment = 1.5

            interest_rate = max(3.0, base_rate + rate_adjustment)  # Minimum 3% rate

        return decision, final_score, risk_level, approved_amount, interest_rate

    async def _generate_explanations(
        self,
        agent_results: Dict[str, AgentResult],
        decision: LoanDecision,
        final_score: float
    ) -> tuple:
        """Generate explanations and conditions."""
        conditions = []
        rejection_reasons = []
        manual_review_reasons = []

        all_flags = set()
        all_explanations = []

        for result in agent_results.values():
            all_flags.update(result.flags)
            all_explanations.extend(result.explanations)

        # Generate conditions for approved loans
        if decision == LoanDecision.APPROVED:
            if "HIGH_DTI_RATIO" in all_flags:
                conditions.append("Salary account to be maintained with RS Bank")
                conditions.append("Quarterly income verification required")

            if "LOW_CREDIT_SCORE" in all_flags or "LIMITED_CREDIT_HISTORY" in all_flags:
                conditions.append("Post-dated cheques for first 12 EMIs required")
                conditions.append("Annual credit score review")

            if "SENIOR_APPLICANT" in all_flags:
                conditions.append("Pension/retirement income verification annually")

            if "SHORT_EMPLOYMENT_TENURE" in all_flags:
                conditions.append("3-month salary slips and offer letter required")

        # Generate rejection reasons
        elif decision == LoanDecision.REJECTED:
            for result in agent_results.values():
                if result.status.value == "failure" or result.score < 30:
                    rejection_reasons.extend(result.findings[:2])

        # Generate manual review reasons
        elif decision == LoanDecision.REQUIRES_MANUAL_REVIEW:
            for flag in all_flags:
                if flag in self.MANUAL_REVIEW_FLAGS:
                    for result in agent_results.values():
                        if flag in result.flags:
                            manual_review_reasons.append(f"{result.agent_name}: {flag}")
                            break

        # Generate decision explanation
        if decision == LoanDecision.APPROVED:
            decision_explanation = f"Application APPROVED with composite score {final_score:.1f}/100. " \
                                 f"Applicant meets all eligibility criteria and demonstrates strong repayment capacity."
        elif decision == LoanDecision.REJECTED:
            top_reasons = rejection_reasons[:3] if rejection_reasons else ["Score below threshold"]
            decision_explanation = f"Application REJECTED with score {final_score:.1f}/100. " \
                                 f"Primary concerns: {'; '.join(top_reasons[:2])}."
        else:
            reasons = manual_review_reasons[:2] if manual_review_reasons else ["Borderline score"]
            decision_explanation = f"Application requires MANUAL REVIEW due to: {', '.join(reasons)}. " \
                                 f"Credit committee assessment recommended."

        return all_explanations, conditions, rejection_reasons, manual_review_reasons, decision_explanation

    async def _publish_evaluation_started(self, correlation_id: str, application: LoanApplication):
        event = Event(
            event_type=EventType.EVALUATION_STARTED,
            source="Orchestrator",
            correlation_id=correlation_id,
            payload={
                "application_id": application.application_id,
                "applicant": application.applicant.name,
                "loan_type": application.loan_type.value,
                "amount": application.requested_amount,
            },
        )
        await event_bus.publish(event)

    async def _publish_evaluation_completed(self, correlation_id: str, evaluation: LoanEvaluation):
        event = Event(
            event_type=EventType.EVALUATION_COMPLETED,
            source="Orchestrator",
            correlation_id=correlation_id,
            payload={
                "evaluation_id": evaluation.evaluation_id,
                "decision": evaluation.decision.value,
                "score": evaluation.overall_score,
                "risk_level": evaluation.risk_level.value,
            },
        )
        await event_bus.publish(event)

    async def _publish_evaluation_failed(self, correlation_id: str, error: str):
        event = Event(
            event_type=EventType.EVALUATION_STARTED,
            source="Orchestrator",
            correlation_id=correlation_id,
            payload={"error": error},
        )
        await event_bus.publish(event)

    def calculate_emi(self, principal: float, annual_rate: float, term_months: int) -> float:
        """Calculate Equated Monthly Installment."""
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return principal / term_months
        emi = principal * (monthly_rate * (1 + monthly_rate) ** term_months) / \
              ((1 + monthly_rate) ** term_months - 1)
        return round(emi, 2)
