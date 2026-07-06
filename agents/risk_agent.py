"""
Risk Assessment Agent
Evaluates financial risk factors and loan viability
"""

import asyncio
from typing import Any, Dict, List

import sys
sys.path.insert(0, '/home/ubuntu/rs_bank_agentic_loan_platform')

from core.models import AgentResult, AgentStatus, LoanApplication, LoanType
from core.explainability import ExplanationNode, ExplanationType
from agents.base_agent import BaseAgent


class RiskAssessmentAgent(BaseAgent):
    """
    Evaluates risk through DTI ratio, LTV ratio, employment stability,
    income adequacy, and asset coverage analysis.
    """

    BASE_RATES = {
        LoanType.PERSONAL: 12.5,
        LoanType.HOME: 8.5,
        LoanType.AUTO: 9.5,
        LoanType.EDUCATION: 7.0,
        LoanType.BUSINESS: 11.0,
    }

    def __init__(self):
        super().__init__(
            name="Risk Assessment Agent",
            description="Calculates risk score based on financial and behavioral factors",
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
        self.log("Performing risk assessment...")
        await asyncio.sleep(0.01)

        # Debt-to-Income Ratio (25%)
        dti_score, dti_findings, dti_flags, dti_recs, dti_ratio = self._analyze_dti(
            applicant, application
        )
        score += dti_score
        findings.extend(dti_findings)
        flags.extend(dti_flags)
        recommendations.extend(dti_recs)

        # Loan-to-Value Ratio (20%)
        ltv_score, ltv_findings, ltv_flags = self._analyze_ltv(application)
        score += ltv_score
        findings.extend(ltv_findings)
        flags.extend(ltv_flags)

        # Employment Stability (20%)
        emp_score, emp_findings, emp_flags, emp_recs = self._analyze_employment(applicant)
        score += emp_score
        findings.extend(emp_findings)
        flags.extend(emp_flags)
        recommendations.extend(emp_recs)

        # Income Adequacy (20%)
        inc_score, inc_findings, inc_flags = self._analyze_income_adequacy(
            applicant, application
        )
        score += inc_score
        findings.extend(inc_findings)
        flags.extend(inc_flags)

        # Asset Coverage (15%)
        asset_score, asset_findings, asset_flags = self._analyze_assets(
            applicant, application
        )
        score += asset_score
        findings.extend(asset_findings)
        flags.extend(asset_flags)

        self.log(f"Risk assessment complete. Score: {score:.1f}")

        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            score=score,
            confidence=0.85,
            findings=findings,
            recommendations=recommendations,
            flags=flags,
            explanations=[e.human_readable for e in self._explanations],
            processing_time_ms=0,
            raw_data={
                "dti_ratio": dti_ratio,
                "estimated_emi": self._calculate_emi(
                    application.requested_amount,
                    self.BASE_RATES.get(application.loan_type, 10),
                    application.term_months
                ),
            },
        )

    def _analyze_dti(self, applicant, application) -> tuple:
        findings = []
        flags = []
        recommendations = []

        monthly_income = applicant.annual_income / 12
        estimated_emi = self._calculate_emi(
            application.requested_amount,
            self.BASE_RATES.get(application.loan_type, 10),
            application.term_months
        )

        existing_debt_monthly = applicant.existing_loan_amount / 12 if applicant.existing_loans > 0 else 0
        total_monthly_debt = applicant.monthly_expenses + estimated_emi + existing_debt_monthly
        dti_ratio = (total_monthly_debt / monthly_income * 100) if monthly_income > 0 else 100

        if dti_ratio <= 30:
            score = 25
            findings.append(f"Excellent DTI ratio: {dti_ratio:.1f}%")
            impact = "positive"
        elif dti_ratio <= 40:
            score = 20
            findings.append(f"Acceptable DTI ratio: {dti_ratio:.1f}%")
            impact = "positive"
        elif dti_ratio <= 50:
            score = 12
            findings.append(f"High DTI ratio: {dti_ratio:.1f}%")
            flags.append("HIGH_DTI_RATIO")
            impact = "negative"
        else:
            score = 5
            findings.append(f"Very high DTI ratio: {dti_ratio:.1f}%")
            flags.append("EXCESSIVE_DTI_RATIO")
            recommendations.append("Consider reducing loan amount or extending term")
            impact = "negative"

        self._explanations.append(ExplanationNode(
            node_id="dti_ratio",
            explanation_type=ExplanationType.THRESHOLD,
            factor="debt_to_income_ratio",
            value=f"{dti_ratio:.1f}%",
            threshold="40%",
            impact=impact,
            weight=0.25,
            score_contribution=score,
            human_readable=f"Debt-to-income ratio of {dti_ratio:.1f}% contributes +{score} points"
        ))

        return score, findings, flags, recommendations, dti_ratio

    def _analyze_ltv(self, application) -> tuple:
        findings = []
        flags = []

        if application.collateral_offered and application.collateral_value > 0:
            ltv_ratio = (application.requested_amount / application.collateral_value) * 100

            if ltv_ratio <= 60:
                score = 20
                findings.append(f"Conservative LTV ratio: {ltv_ratio:.1f}%")
                impact = "positive"
            elif ltv_ratio <= 80:
                score = 15
                findings.append(f"Standard LTV ratio: {ltv_ratio:.1f}%")
                impact = "positive"
            elif ltv_ratio <= 90:
                score = 10
                findings.append(f"High LTV ratio: {ltv_ratio:.1f}%")
                flags.append("HIGH_LTV_RATIO")
                impact = "neutral"
            else:
                score = 5
                findings.append(f"Very high LTV ratio: {ltv_ratio:.1f}%")
                flags.append("EXCESSIVE_LTV_RATIO")
                impact = "negative"

            self._explanations.append(ExplanationNode(
                node_id="ltv_ratio",
                explanation_type=ExplanationType.THRESHOLD,
                factor="loan_to_value_ratio",
                value=f"{ltv_ratio:.1f}%",
                threshold="80%",
                impact=impact,
                weight=0.20,
                score_contribution=score,
                human_readable=f"Loan-to-value ratio of {ltv_ratio:.1f}% contributes +{score} points"
            ))
        else:
            if application.loan_type in [LoanType.HOME, LoanType.AUTO]:
                score = 8
                flags.append("NO_COLLATERAL_FOR_SECURED_LOAN")
                findings.append("No collateral offered for secured loan type")
            else:
                score = 15
                findings.append("Unsecured loan - collateral not required")

        return score, findings, flags

    def _analyze_employment(self, applicant) -> tuple:
        findings = []
        flags = []
        recommendations = []

        emp_years = applicant.employment_years
        emp_status = applicant.employment_status

        if emp_status == "employed":
            if emp_years >= 5:
                score = 20
                findings.append(f"Stable employment: {emp_years} years")
                impact = "positive"
            elif emp_years >= 2:
                score = 15
                findings.append(f"Moderate employment tenure: {emp_years} years")
                impact = "positive"
            else:
                score = 10
                findings.append(f"Short employment tenure: {emp_years} years")
                flags.append("SHORT_EMPLOYMENT_TENURE")
                impact = "neutral"
        elif emp_status == "self_employed":
            if emp_years >= 3:
                score = 16
                findings.append(f"Established self-employment: {emp_years} years")
                impact = "positive"
            else:
                score = 8
                findings.append(f"New self-employment: {emp_years} years")
                flags.append("NEW_BUSINESS")
                impact = "neutral"
        elif emp_status == "retired":
            score = 12
            findings.append("Retired - income from pension/investments")
            flags.append("RETIRED_APPLICANT")
            impact = "neutral"
        else:
            score = 3
            findings.append("Currently unemployed")
            flags.append("UNEMPLOYED")
            recommendations.append("Requires guarantor or co-applicant")
            impact = "negative"

        self._explanations.append(ExplanationNode(
            node_id="employment",
            explanation_type=ExplanationType.RULE_BASED,
            factor="employment_stability",
            value=f"{emp_status} for {emp_years} years",
            impact=impact,
            weight=0.20,
            score_contribution=score,
            human_readable=f"Employment status ({emp_status}, {emp_years} years) contributes +{score} points"
        ))

        return score, findings, flags, recommendations

    def _analyze_income_adequacy(self, applicant, application) -> tuple:
        findings = []
        flags = []

        if application.requested_amount > 0:
            income_to_loan = applicant.annual_income / application.requested_amount
        else:
            income_to_loan = 0

        if income_to_loan >= 0.5:
            score = 20
            findings.append(f"Strong income adequacy: {income_to_loan:.2f}x annual income")
            impact = "positive"
        elif income_to_loan >= 0.3:
            score = 15
            findings.append(f"Adequate income ratio: {income_to_loan:.2f}x annual income")
            impact = "positive"
        elif income_to_loan >= 0.15:
            score = 10
            findings.append(f"Marginal income ratio: {income_to_loan:.2f}x annual income")
            flags.append("LOW_INCOME_RATIO")
            impact = "neutral"
        else:
            score = 5
            findings.append(f"Insufficient income ratio: {income_to_loan:.2f}x annual income")
            flags.append("INSUFFICIENT_INCOME")
            impact = "negative"

        self._explanations.append(ExplanationNode(
            node_id="income_adequacy",
            explanation_type=ExplanationType.THRESHOLD,
            factor="income_to_loan_ratio",
            value=f"{income_to_loan:.2f}x",
            threshold="0.3x",
            impact=impact,
            weight=0.20,
            score_contribution=score,
            human_readable=f"Income provides {income_to_loan:.2f}x coverage of loan amount, contributing +{score} points"
        ))

        return score, findings, flags

    def _analyze_assets(self, applicant, application) -> tuple:
        findings = []
        flags = []

        total_assets = applicant.savings_balance + applicant.property_value + applicant.other_assets

        if application.requested_amount > 0:
            asset_coverage = total_assets / application.requested_amount
        else:
            asset_coverage = 0

        if asset_coverage >= 2:
            score = 15
            findings.append(f"Excellent asset coverage: {asset_coverage:.2f}x loan amount")
            impact = "positive"
        elif asset_coverage >= 1:
            score = 12
            findings.append(f"Good asset coverage: {asset_coverage:.2f}x loan amount")
            impact = "positive"
        elif asset_coverage >= 0.5:
            score = 8
            findings.append(f"Partial asset coverage: {asset_coverage:.2f}x loan amount")
            impact = "neutral"
        else:
            score = 3
            findings.append(f"Limited asset coverage: {asset_coverage:.2f}x loan amount")
            flags.append("LOW_ASSET_COVERAGE")
            impact = "negative"

        self._explanations.append(ExplanationNode(
            node_id="asset_coverage",
            explanation_type=ExplanationType.THRESHOLD,
            factor="asset_coverage_ratio",
            value=f"{asset_coverage:.2f}x",
            threshold="1.0x",
            impact=impact,
            weight=0.15,
            score_contribution=score,
            human_readable=f"Total assets provide {asset_coverage:.2f}x coverage of loan, contributing +{score} points"
        ))

        return score, findings, flags

    def _calculate_emi(self, principal: float, annual_rate: float, term_months: int) -> float:
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return principal / term_months
        emi = principal * (monthly_rate * (1 + monthly_rate) ** term_months) / \
              ((1 + monthly_rate) ** term_months - 1)
        return emi

    def get_explanations(self) -> List[ExplanationNode]:
        return self._explanations
