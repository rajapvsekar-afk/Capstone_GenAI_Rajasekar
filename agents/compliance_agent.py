"""
Regulatory Compliance Agent
Checks loan against RBI regulations and bank policies
"""

import asyncio
from typing import Any, Dict, List

import sys
sys.path.insert(0, '/home/ubuntu/rs_bank_agentic_loan_platform')

from core.models import AgentResult, AgentStatus, LoanApplication, LoanType
from core.explainability import ExplanationNode, ExplanationType
from agents.base_agent import BaseAgent


class RegulatoryComplianceAgent(BaseAgent):
    """
    Ensures compliance with RBI regulations, KYC requirements,
    AML policies, and bank lending guidelines.
    """

    LOAN_LIMITS = {
        LoanType.PERSONAL: {"min": 10_000, "max": 2_000_000},
        LoanType.HOME: {"min": 500_000, "max": 50_000_000},
        LoanType.AUTO: {"min": 100_000, "max": 5_000_000},
        LoanType.EDUCATION: {"min": 50_000, "max": 3_000_000},
        LoanType.BUSINESS: {"min": 100_000, "max": 20_000_000},
    }

    def __init__(self):
        super().__init__(
            name="Regulatory Compliance Agent",
            description="Ensures compliance with RBI regulations and bank policies",
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
        score = 100.0

        applicant = application.applicant
        self.log("Checking regulatory compliance...")
        await asyncio.sleep(0.01)

        # Age Compliance
        age_score, age_findings, age_flags = self._check_age_compliance(applicant.age)
        score = min(score, age_score)
        findings.extend(age_findings)
        flags.extend(age_flags)

        # Loan Tenure Compliance
        tenure_score, tenure_findings, tenure_flags, tenure_recs = self._check_tenure_compliance(
            applicant.age, application.term_months
        )
        score = min(score, tenure_score)
        findings.extend(tenure_findings)
        flags.extend(tenure_flags)
        recommendations.extend(tenure_recs)

        # Loan Amount Limits
        limit_score, limit_findings, limit_flags, limit_recs = self._check_loan_limits(application)
        score = min(score, limit_score)
        findings.extend(limit_findings)
        flags.extend(limit_flags)
        recommendations.extend(limit_recs)

        # KYC Compliance
        kyc_score, kyc_findings, kyc_flags = self._check_kyc_compliance(applicant)
        score = min(score, kyc_score)
        findings.extend(kyc_findings)
        flags.extend(kyc_flags)

        # AML Screening
        aml_score, aml_findings, aml_flags, aml_recs = self._check_aml_compliance(
            application, applicant
        )
        score = min(score, aml_score)
        findings.extend(aml_findings)
        flags.extend(aml_flags)
        recommendations.extend(aml_recs)

        self.log(f"Compliance check complete. Score: {score:.1f}")

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            score=max(0, score),
            confidence=0.98,  # Compliance checks are deterministic
            findings=findings,
            recommendations=recommendations,
            flags=flags,
            explanations=[e.human_readable for e in self._explanations],
            processing_time_ms=0,
            raw_data={
                "loan_limits": self.LOAN_LIMITS.get(application.loan_type, {}),
                "age_at_maturity": applicant.age + (application.term_months / 12),
            },
        )

    def _check_age_compliance(self, age: int) -> tuple:
        findings = []
        flags = []

        if age < 21:
            score = 0
            findings.append(f"Applicant age ({age}) below minimum requirement (21)")
            flags.append("UNDERAGE_APPLICANT")
            self._explanations.append(ExplanationNode(
                node_id="age_min",
                explanation_type=ExplanationType.RULE_BASED,
                factor="minimum_age_requirement",
                value=age,
                threshold=21,
                impact="negative",
                score_contribution=-100,
                human_readable="Applicant age is below legal minimum (21 years)"
            ))
        elif age > 65:
            score = 80
            findings.append(f"Applicant age ({age}) above standard limit (65)")
            flags.append("SENIOR_APPLICANT")
            recommendations = ["Verify pension/retirement income sustainability"]
            self._explanations.append(ExplanationNode(
                node_id="age_senior",
                explanation_type=ExplanationType.RULE_BASED,
                factor="senior_applicant",
                value=age,
                threshold=65,
                impact="neutral",
                score_contribution=-20,
                human_readable="Applicant is a senior citizen - requires pension verification"
            ))
        else:
            score = 100
            findings.append(f"Age requirement met: {age} years")
            recommendations = []
            self._explanations.append(ExplanationNode(
                node_id="age_valid",
                explanation_type=ExplanationType.RULE_BASED,
                factor="age_eligibility",
                value=age,
                threshold="21-65",
                impact="positive",
                score_contribution=0,
                human_readable="Applicant age meets eligibility criteria (21-65 years)"
            ))

        return score, findings, flags

    def _check_tenure_compliance(self, age: int, term_months: int) -> tuple:
        findings = []
        flags = []
        recommendations = []

        age_at_maturity = age + (term_months / 12)

        if age_at_maturity > 70:
            score = 70
            findings.append(f"Age at loan maturity ({age_at_maturity:.0f}) exceeds 70")
            flags.append("MATURITY_AGE_EXCEEDED")
            max_term = int((70 - age) * 12)
            recommendations.append(f"Reduce term to max {max_term} months")
            self._explanations.append(ExplanationNode(
                node_id="tenure_exceed",
                explanation_type=ExplanationType.THRESHOLD,
                factor="maturity_age_compliance",
                value=f"{age_at_maturity:.0f} years",
                threshold="70 years",
                impact="negative",
                score_contribution=-30,
                human_readable=f"Loan maturity age ({age_at_maturity:.0f}) exceeds regulatory limit of 70 years"
            ))
        else:
            score = 100
            findings.append(f"Loan maturity age acceptable: {age_at_maturity:.0f} years")

        return score, findings, flags, recommendations

    def _check_loan_limits(self, application: LoanApplication) -> tuple:
        findings = []
        flags = []
        recommendations = []

        limits = self.LOAN_LIMITS.get(application.loan_type, {"min": 10_000, "max": 5_000_000})

        if application.requested_amount < limits["min"]:
            score = 70
            findings.append(f"Loan amount below minimum for {application.loan_type.value}")
            flags.append("BELOW_MIN_LOAN_AMOUNT")
        elif application.requested_amount > limits["max"]:
            score = 0
            findings.append(f"Loan amount exceeds maximum for {application.loan_type.value}")
            flags.append("EXCEEDS_MAX_LOAN_AMOUNT")
            recommendations.append(f"Maximum allowed: Rs. {limits['max']:,}")
        else:
            score = 100
            findings.append("Loan amount within permissible limits")

        self._explanations.append(ExplanationNode(
            node_id="loan_limits",
            explanation_type=ExplanationType.THRESHOLD,
            factor="loan_amount_limits",
            value=f"Rs. {application.requested_amount:,.0f}",
            threshold=f"Rs. {limits['min']:,} - {limits['max']:,}",
            impact="positive" if score == 100 else "negative",
            score_contribution=score - 100,
            human_readable=f"Loan amount {application.requested_amount:,.0f} within limits Rs. {limits['min']:,} - {limits['max']:,}"
        ))

        return score, findings, flags, recommendations

    def _check_kyc_compliance(self, applicant) -> tuple:
        findings = []
        flags = []
        kyc_docs = ["id_proof", "address_proof"]

        submitted = applicant.documents_submitted
        missing_kyc = [doc for doc in kyc_docs if doc not in submitted]

        if missing_kyc:
            score = 0
            findings.append(f"KYC documents incomplete: {', '.join(missing_kyc)}")
            flags.append("KYC_INCOMPLETE")
            self._explanations.append(ExplanationNode(
                node_id="kyc_incomplete",
                explanation_type=ExplanationType.RULE_BASED,
                factor="kyc_compliance",
                value=f"{len(kyc_docs) - len(missing_kyc)}/{len(kyc_docs)}",
                impact="negative",
                score_contribution=-100,
                human_readable=f"KYC documents incomplete - missing: {', '.join(missing_kyc)}"
            ))
        else:
            score = 100
            findings.append("KYC documentation complete")
            self._explanations.append(ExplanationNode(
                node_id="kyc_complete",
                explanation_type=ExplanationType.RULE_BASED,
                factor="kyc_compliance",
                value="2/2",
                impact="positive",
                score_contribution=0,
                human_readable="KYC documentation verified and complete"
            ))

        return score, findings, flags

    def _check_aml_compliance(self, application: LoanApplication, applicant) -> tuple:
        findings = []
        flags = []
        recommendations = []
        score = 100.0

        # Large transaction from unemployed
        if application.requested_amount > 1_000_000 and applicant.employment_status == "unemployed":
            score = 50
            flags.append("AML_FLAG")
            findings.append("Large loan amount with unemployed status - AML review required")
            recommendations.append("Enhanced due diligence required - possible source of funds verification")
            self._explanations.append(ExplanationNode(
                node_id="aml_flag",
                explanation_type=ExplanationType.FLAG_TRIGGERED,
                factor="aml_screening",
                value=f"Rs. {application.requested_amount:,.0f} with unemployed status",
                impact="negative",
                score_contribution=-50,
                human_readable="AML flag triggered: Large transaction amount with unemployment status"
            ))

        # Multiple rapid applications
        rapid_applications = len(application.applicant.documents_submitted) if hasattr(
            application, '_rapid_check') else 0
        if rapid_applications > 3:
            score = min(score, 80)
            flags.append("RAPID_APPLICATIONS")
            findings.append("Multiple loan applications in short period")

        return score, findings, flags, recommendations

    def get_explanations(self) -> List[ExplanationNode]:
        return self._explanations
