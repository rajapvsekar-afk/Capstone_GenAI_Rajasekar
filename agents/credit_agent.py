"""
Credit Analysis Agent
Evaluates credit history and creditworthiness
"""

import asyncio
from typing import Any, Dict, List

import sys
sys.path.insert(0, '/home/ubuntu/rs_bank_agentic_loan_platform')

from core.models import AgentResult, AgentStatus, LoanApplication
from core.explainability import ExplanationNode, ExplanationType, explainability_engine
from agents.base_agent import BaseAgent


class CreditAnalysisAgent(BaseAgent):
    """
    Analyzes credit history, payment behavior, and overall creditworthiness.
    Uses weighted scoring across multiple credit factors.
    """

    WEIGHTS = {
        "credit_score": 0.40,
        "credit_history": 0.15,
        "payment_history": 0.20,
        "bankruptcy": 0.15,
        "utilization": 0.10,
    }

    CREDIT_SCORE_TIERS = [
        (800, 40, "Excellent"),
        (750, 35, "Very Good"),
        (700, 28, "Good"),
        (650, 20, "Fair"),
        (600, 12, "Below Average"),
        (0, 5, "Poor"),
    ]

    def __init__(self):
        super().__init__(
            name="Credit Analysis Agent",
            description="Evaluates credit score, history, and creditworthiness",
            version="2.0.0"
        )
        self._explanations: List[ExplanationNode] = []

    async def analyze(
        self,
        application: LoanApplication,
        context: Dict[str, Any]
    ) -> AgentResult:
        self._explanations = []
        findings = []
        flags = []
        recommendations = []
        score = 0.0

        applicant = application.applicant
        self.log("Analyzing credit profile...")
        await asyncio.sleep(0.01)

        # Credit Score Analysis (40%)
        cs_score, cs_findings, cs_flags = self._analyze_credit_score(applicant.credit_score)
        score += cs_score
        findings.extend(cs_findings)
        flags.extend(cs_flags)

        # Credit History Length (15%)
        ch_score, ch_findings, ch_flags = self._analyze_credit_history(applicant.credit_history_years)
        score += ch_score
        findings.extend(ch_findings)
        flags.extend(ch_flags)

        # Payment History (20%)
        ph_score, ph_findings, ph_flags, ph_recs = self._analyze_payment_history(applicant.payment_defaults)
        score += ph_score
        findings.extend(ph_findings)
        flags.extend(ph_flags)
        recommendations.extend(ph_recs)

        # Bankruptcy Check (15%)
        bk_score, bk_findings, bk_flags, bk_recs = self._analyze_bankruptcy(applicant.bankruptcies)
        score += bk_score
        findings.extend(bk_findings)
        flags.extend(bk_flags)
        recommendations.extend(bk_recs)

        # Credit Utilization (10%)
        cu_score, cu_findings, cu_flags = self._analyze_utilization(applicant.credit_card_utilization)
        score += cu_score
        findings.extend(cu_findings)
        flags.extend(cu_flags)

        self.log(f"Credit analysis complete. Score: {score:.1f}")

        confidence = 0.90 if applicant.credit_score >= 650 else 0.75

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            score=score,
            confidence=confidence,
            findings=findings,
            recommendations=recommendations,
            flags=flags,
            explanations=[e.human_readable for e in self._explanations],
            processing_time_ms=0,
            raw_data={
                "credit_score": applicant.credit_score,
                "history_years": applicant.credit_history_years,
                "defaults": applicant.payment_defaults,
                "bankruptcies": applicant.bankruptcies,
                "utilization": applicant.credit_card_utilization,
            },
        )

    def _analyze_credit_score(self, credit_score: int) -> tuple:
        findings = []
        flags = []

        for threshold, points, tier in self.CREDIT_SCORE_TIERS:
            if credit_score >= threshold:
                score = points
                findings.append(f"{tier} credit score: {credit_score}")

                impact = "positive" if points >= 28 else "neutral" if points >= 20 else "negative"

                if points < 20:
                    flags.append("LOW_CREDIT_SCORE")
                if points < 12:
                    flags.append("VERY_LOW_CREDIT_SCORE")

                self._explanations.append(ExplanationNode(
                    node_id="credit_score",
                    explanation_type=ExplanationType.THRESHOLD,
                    factor="credit_score",
                    value=credit_score,
                    threshold=threshold,
                    impact=impact,
                    weight=self.WEIGHTS["credit_score"],
                    score_contribution=points,
                    human_readable=f"Credit score of {credit_score} ({tier}) contributes +{points} points"
                ))
                break

        return score, findings, flags

    def _analyze_credit_history(self, history_years: int) -> tuple:
        findings = []
        flags = []

        if history_years >= 10:
            score = 15
            findings.append(f"Established credit history: {history_years} years")
            impact = "positive"
        elif history_years >= 5:
            score = 12
            findings.append(f"Moderate credit history: {history_years} years")
            impact = "positive"
        elif history_years >= 2:
            score = 8
            findings.append(f"Limited credit history: {history_years} years")
            flags.append("LIMITED_CREDIT_HISTORY")
            impact = "neutral"
        else:
            score = 3
            findings.append(f"Very limited credit history: {history_years} years")
            flags.append("THIN_CREDIT_FILE")
            impact = "negative"

        self._explanations.append(ExplanationNode(
            node_id="credit_history",
            explanation_type=ExplanationType.THRESHOLD,
            factor="credit_history_length",
            value=history_years,
            threshold=5,
            impact=impact,
            weight=self.WEIGHTS["credit_history"],
            score_contribution=score,
            human_readable=f"Credit history of {history_years} years contributes +{score} points"
        ))

        return score, findings, flags

    def _analyze_payment_history(self, defaults: int) -> tuple:
        findings = []
        flags = []
        recommendations = []

        if defaults == 0:
            score = 20
            findings.append("No payment defaults on record")
            impact = "positive"
        elif defaults <= 2:
            score = 12
            findings.append(f"Minor payment issues: {defaults} defaults")
            flags.append("PAST_DEFAULTS")
            impact = "neutral"
        else:
            score = 3
            findings.append(f"Significant payment issues: {defaults} defaults")
            flags.append("MULTIPLE_DEFAULTS")
            recommendations.append("Requires additional scrutiny and possible guarantor")
            impact = "negative"

        self._explanations.append(ExplanationNode(
            node_id="payment_history",
            explanation_type=ExplanationType.THRESHOLD,
            factor="payment_defaults",
            value=defaults,
            threshold=0,
            impact=impact,
            weight=self.WEIGHTS["payment_history"],
            score_contribution=score,
            human_readable=f"Payment history with {defaults} defaults contributes +{score} points"
        ))

        return score, findings, flags, recommendations

    def _analyze_bankruptcy(self, bankruptcies: int) -> tuple:
        findings = []
        flags = []
        recommendations = []

        if bankruptcies == 0:
            score = 15
            findings.append("No bankruptcy filings")
            impact = "positive"
        else:
            score = 0
            findings.append(f"Bankruptcy filings: {bankruptcies}")
            flags.append("BANKRUPTCY_HISTORY")
            recommendations.append("Manual review required for bankruptcy history")
            impact = "negative"

        self._explanations.append(ExplanationNode(
            node_id="bankruptcy",
            explanation_type=ExplanationType.FLAG_TRIGGERED if bankruptcies > 0 else ExplanationType.RULE_BASED,
            factor="bankruptcy_history",
            value=bankruptcies,
            threshold=0,
            impact=impact,
            weight=self.WEIGHTS["bankruptcy"],
            score_contribution=score,
            human_readable=f"Bankruptcy check: {bankruptcies} filing(s) - contributes +{score} points"
        ))

        return score, findings, flags, recommendations

    def _analyze_utilization(self, utilization: float) -> tuple:
        findings = []
        flags = []

        if utilization <= 30:
            score = 10
            findings.append(f"Healthy credit utilization: {utilization}%")
            impact = "positive"
        elif utilization <= 50:
            score = 7
            findings.append(f"Moderate credit utilization: {utilization}%")
            impact = "neutral"
        elif utilization <= 75:
            score = 4
            findings.append(f"High credit utilization: {utilization}%")
            flags.append("HIGH_CREDIT_UTILIZATION")
            impact = "negative"
        else:
            score = 1
            findings.append(f"Very high credit utilization: {utilization}%")
            flags.append("MAXED_CREDIT_LINES")
            impact = "negative"

        self._explanations.append(ExplanationNode(
            node_id="utilization",
            explanation_type=ExplanationType.THRESHOLD,
            factor="credit_utilization",
            value=f"{utilization}%",
            threshold="30%",
            impact=impact,
            weight=self.WEIGHTS["utilization"],
            score_contribution=score,
            human_readable=f"Credit utilization of {utilization}% contributes +{score} points"
        ))

        return score, findings, flags

    def get_explanations(self) -> List[ExplanationNode]:
        return self._explanations
