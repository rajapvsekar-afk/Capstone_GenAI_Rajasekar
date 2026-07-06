"""
Document Verification Agent
Validates document completeness and data consistency
"""

import asyncio
from typing import Any, Dict, List

import sys
sys.path.insert(0, '/home/ubuntu/rs_bank_agentic_loan_platform')

from core.models import AgentResult, AgentStatus, LoanApplication, LoanType
from core.explainability import ExplanationNode, ExplanationType, explainability_engine
from agents.base_agent import BaseAgent


class DocumentVerificationAgent(BaseAgent):
    """
    Validates applicant documents and data completeness.
    Checks for anomalies and inconsistencies in submitted data.
    """

    REQUIRED_DOCUMENTS = {
        LoanType.PERSONAL: ["id_proof", "address_proof", "income_proof", "bank_statements"],
        LoanType.HOME: ["id_proof", "address_proof", "income_proof", "bank_statements",
                        "property_documents", "sale_agreement"],
        LoanType.AUTO: ["id_proof", "address_proof", "income_proof", "bank_statements",
                        "vehicle_quotation"],
        LoanType.EDUCATION: ["id_proof", "address_proof", "income_proof", "admission_letter",
                             "fee_structure"],
        LoanType.BUSINESS: ["id_proof", "address_proof", "income_proof", "bank_statements",
                            "business_registration", "financial_statements", "business_plan"],
    }

    def __init__(self):
        super().__init__(
            name="Document Verification Agent",
            description="Validates completeness and authenticity of submitted documents",
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

        self.log("Starting document verification...")
        await asyncio.sleep(0.01)  # Simulate I/O

        # Check document completeness
        doc_score, doc_findings, doc_flags, doc_recs = self._check_documents(application)
        score = min(score, doc_score)
        findings.extend(doc_findings)
        flags.extend(doc_flags)
        recommendations.extend(doc_recs)

        # Validate data consistency
        data_score, data_findings, data_flags, data_recs = self._validate_data(application)
        score = min(score, data_score)
        findings.extend(data_findings)
        flags.extend(data_flags)
        recommendations.extend(data_recs)

        # Check for anomalies
        anomaly_score, anomaly_findings, anomaly_flags = self._detect_anomalies(application)
        score = min(score, anomaly_score)
        findings.extend(anomaly_findings)
        flags.extend(anomaly_flags)

        self.log(f"Verification complete. Score: {score:.1f}")

        status = AgentStatus.COMPLETED
        if score < 50:
            status = AgentStatus.COMPLETED  # Still completed, but low score

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.name,
            status=status,
            score=max(0, score),
            confidence=0.95 if not flags else 0.80,
            findings=findings,
            recommendations=recommendations,
            flags=flags,
            explanations=[e.human_readable for e in self._explanations],
            processing_time_ms=0,
            raw_data={
                "documents_required": len(self.REQUIRED_DOCUMENTS.get(application.loan_type, [])),
                "documents_submitted": len(application.applicant.documents_submitted),
            },
        )

    def _check_documents(self, application: LoanApplication) -> tuple:
        findings = []
        flags = []
        recommendations = []
        score = 100.0

        required = self.REQUIRED_DOCUMENTS.get(application.loan_type, [])
        submitted = application.applicant.documents_submitted
        missing = [doc for doc in required if doc not in submitted]

        if missing:
            penalty = len(missing) * 15
            score -= penalty
            findings.append(f"Missing documents: {', '.join(missing)}")
            flags.append("INCOMPLETE_DOCUMENTATION")
            recommendations.append(f"Request missing documents: {', '.join(missing)}")

            self._explanations.append(ExplanationNode(
                node_id="doc_missing",
                explanation_type=ExplanationType.RULE_BASED,
                factor="document_completeness",
                value=f"{len(submitted)}/{len(required)}",
                impact="negative",
                weight=0.15,
                score_contribution=-penalty,
                human_readable=f"Missing {len(missing)} required documents: {', '.join(missing)}"
            ))
        else:
            findings.append(f"All {len(required)} required documents submitted")
            self._explanations.append(ExplanationNode(
                node_id="doc_complete",
                explanation_type=ExplanationType.RULE_BASED,
                factor="document_completeness",
                value=f"{len(required)}/{len(required)}",
                impact="positive",
                weight=0.15,
                score_contribution=0,
                human_readable=f"All required documents ({len(required)}) have been submitted"
            ))

        return score, findings, flags, recommendations

    def _validate_data(self, application: LoanApplication) -> tuple:
        findings = []
        flags = []
        recommendations = []
        score = 100.0
        applicant = application.applicant

        # Income validation
        if applicant.annual_income <= 0:
            score -= 30
            flags.append("INVALID_INCOME_DATA")
            findings.append("Income data is invalid or missing")
            self._explanations.append(ExplanationNode(
                node_id="income_invalid",
                explanation_type=ExplanationType.RULE_BASED,
                factor="income_validation",
                value=applicant.annual_income,
                impact="negative",
                score_contribution=-30,
                human_readable="Income data is invalid (zero or negative)"
            ))

        # Age validation
        if applicant.age < 18 or applicant.age > 100:
            score -= 25
            flags.append("INVALID_AGE_DATA")
            findings.append(f"Age value appears invalid: {applicant.age}")
        else:
            findings.append(f"Age verified: {applicant.age} years")

        # Credit score range
        if applicant.credit_score < 300 or applicant.credit_score > 900:
            score -= 20
            flags.append("SUSPICIOUS_CREDIT_SCORE")
            findings.append(f"Credit score outside normal range: {applicant.credit_score}")

        return score, findings, flags, recommendations

    def _detect_anomalies(self, application: LoanApplication) -> tuple:
        findings = []
        flags = []
        score = 100.0
        applicant = application.applicant

        # Income-employment mismatch
        if applicant.employment_status == "unemployed" and applicant.annual_income > 500000:
            score -= 15
            flags.append("INCOME_EMPLOYMENT_MISMATCH")
            findings.append("High income reported despite unemployed status - verification required")
            self._explanations.append(ExplanationNode(
                node_id="income_emp_mismatch",
                explanation_type=ExplanationType.FLAG_TRIGGERED,
                factor="income_employment_consistency",
                value=f"Unemployed with Rs.{applicant.annual_income:,.0f} income",
                impact="negative",
                score_contribution=-15,
                human_readable="Income-employment mismatch detected: high income with unemployed status"
            ))

        # Address duration anomaly
        if applicant.years_at_address > applicant.age - 18:
            score -= 10
            flags.append("ADDRESS_DURATION_ANOMALY")
            findings.append("Years at address exceeds possible duration")

        # Loan amount vs income sanity check
        if application.requested_amount > applicant.annual_income * 10:
            findings.append("Loan amount is more than 10x annual income - high risk")
            flags.append("HIGH_LOAN_TO_INCOME")

        return score, findings, flags

    def get_explanations(self) -> List[ExplanationNode]:
        return self._explanations
