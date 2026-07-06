"""
Explainability Engine for Auditable AI Decisions
Provides human-readable explanations and audit trails
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import json


class ExplanationType(Enum):
    RULE_BASED = "rule_based"
    THRESHOLD = "threshold"
    WEIGHTED_SCORE = "weighted_score"
    FLAG_TRIGGERED = "flag_triggered"
    POLICY_VIOLATION = "policy_violation"
    AGGREGATION = "aggregation"


@dataclass
class ExplanationNode:
    node_id: str
    explanation_type: ExplanationType
    factor: str
    value: Any
    threshold: Optional[Any] = None
    impact: str = ""  # positive, negative, neutral
    weight: float = 0.0
    score_contribution: float = 0.0
    human_readable: str = ""
    children: List["ExplanationNode"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "type": self.explanation_type.value,
            "factor": self.factor,
            "value": self.value,
            "threshold": self.threshold,
            "impact": self.impact,
            "weight": self.weight,
            "score_contribution": self.score_contribution,
            "explanation": self.human_readable,
            "sub_factors": [c.to_dict() for c in self.children],
        }


class ExplainabilityEngine:
    """
    Generates human-readable explanations for loan decisions.
    Supports regulatory compliance and customer transparency requirements.
    """

    def __init__(self):
        self.explanation_templates = {
            "credit_score_high": "Credit score of {value} exceeds the excellent threshold of {threshold}, contributing +{contribution:.1f} points",
            "credit_score_good": "Credit score of {value} meets the good threshold of {threshold}, contributing +{contribution:.1f} points",
            "credit_score_fair": "Credit score of {value} is below preferred level of {threshold}, contributing +{contribution:.1f} points",
            "credit_score_low": "Credit score of {value} is below minimum threshold of {threshold}, negatively impacting approval chances",
            "dti_good": "Debt-to-income ratio of {value:.1f}% is within acceptable limit of {threshold}%",
            "dti_high": "Debt-to-income ratio of {value:.1f}% exceeds recommended limit of {threshold}%",
            "employment_stable": "Employment tenure of {value} years demonstrates stability",
            "employment_short": "Employment tenure of {value} years is below preferred {threshold} years",
            "document_complete": "All required documents ({value}) have been submitted",
            "document_missing": "Missing required documents: {value}",
            "age_eligible": "Applicant age of {value} meets eligibility criteria (21-65 years)",
            "age_ineligible": "Applicant age of {value} does not meet eligibility criteria",
            "bankruptcy_flag": "Bankruptcy history detected - requires manual review per policy",
            "aml_flag": "Anti-money laundering check flagged - enhanced due diligence required",
            "income_adequate": "Annual income of Rs. {value:,.0f} provides {ratio:.1f}x coverage of loan amount",
            "income_inadequate": "Annual income of Rs. {value:,.0f} provides only {ratio:.2f}x coverage of loan amount",
        }

    def create_explanation(
        self,
        template_key: str,
        factor: str,
        value: Any,
        threshold: Any = None,
        impact: str = "neutral",
        weight: float = 0.0,
        contribution: float = 0.0,
        **kwargs
    ) -> ExplanationNode:
        template = self.explanation_templates.get(template_key, "{factor}: {value}")

        format_args = {
            "value": value,
            "threshold": threshold,
            "contribution": contribution,
            **kwargs
        }

        try:
            human_readable = template.format(**format_args)
        except (KeyError, ValueError):
            human_readable = f"{factor}: {value}"

        return ExplanationNode(
            node_id=f"exp_{factor}_{id(value)}",
            explanation_type=ExplanationType.THRESHOLD if threshold else ExplanationType.RULE_BASED,
            factor=factor,
            value=value,
            threshold=threshold,
            impact=impact,
            weight=weight,
            score_contribution=contribution,
            human_readable=human_readable,
        )

    def aggregate_explanations(
        self,
        explanations: List[ExplanationNode],
        decision: str,
        final_score: float
    ) -> dict:
        positive_factors = [e for e in explanations if e.impact == "positive"]
        negative_factors = [e for e in explanations if e.impact == "negative"]
        neutral_factors = [e for e in explanations if e.impact == "neutral"]

        summary = self._generate_summary(decision, final_score, positive_factors, negative_factors)

        return {
            "decision": decision,
            "final_score": final_score,
            "summary": summary,
            "positive_factors": [e.to_dict() for e in positive_factors],
            "negative_factors": [e.to_dict() for e in negative_factors],
            "neutral_factors": [e.to_dict() for e in neutral_factors],
            "total_factors_evaluated": len(explanations),
        }

    def _generate_summary(
        self,
        decision: str,
        score: float,
        positive: List[ExplanationNode],
        negative: List[ExplanationNode]
    ) -> str:
        if decision == "approved":
            top_positive = sorted(positive, key=lambda x: x.score_contribution, reverse=True)[:3]
            factors = ", ".join([e.factor for e in top_positive])
            return f"Application APPROVED with score {score:.1f}/100. Key positive factors: {factors}."

        elif decision == "rejected":
            top_negative = sorted(negative, key=lambda x: abs(x.score_contribution), reverse=True)[:3]
            factors = ", ".join([e.factor for e in top_negative])
            return f"Application REJECTED with score {score:.1f}/100. Primary concerns: {factors}."

        else:
            flags = [e.factor for e in negative if "flag" in e.factor.lower()]
            if flags:
                return f"Application requires MANUAL REVIEW due to: {', '.join(flags)}. Score: {score:.1f}/100."
            return f"Application requires MANUAL REVIEW. Borderline score: {score:.1f}/100."

    def generate_customer_explanation(self, evaluation: dict) -> str:
        """Generate customer-friendly explanation for adverse action notices."""
        decision = evaluation.get("decision", "")

        if decision == "approved":
            return self._approved_explanation(evaluation)
        elif decision == "rejected":
            return self._rejected_explanation(evaluation)
        else:
            return self._review_explanation(evaluation)

    def _approved_explanation(self, evaluation: dict) -> str:
        amount = evaluation.get("approved_amount", 0)
        rate = evaluation.get("interest_rate", 0)
        conditions = evaluation.get("conditions", [])

        text = f"""
Congratulations! Your loan application has been APPROVED.

Approved Amount: Rs. {amount:,.2f}
Interest Rate: {rate:.2f}% per annum

"""
        if conditions:
            text += "Conditions:\n"
            for cond in conditions:
                text += f"  • {cond}\n"

        return text

    def _rejected_explanation(self, evaluation: dict) -> str:
        reasons = evaluation.get("rejection_reasons", [])

        text = """
We regret to inform you that your loan application could not be approved at this time.

Principal factors affecting this decision:
"""
        for i, reason in enumerate(reasons[:5], 1):
            text += f"  {i}. {reason}\n"

        text += """
You may reapply after addressing these concerns or contact our branch for guidance.
"""
        return text

    def _review_explanation(self, evaluation: dict) -> str:
        return """
Your application requires additional review by our credit team.

A loan officer will contact you within 2-3 business days to discuss
your application and any additional documentation that may be required.

Reference Number: {}
""".format(evaluation.get("evaluation_id", "N/A"))


class AuditLogger:
    """
    Comprehensive audit logging for regulatory compliance.
    Captures all decision factors and reasoning.
    """

    def __init__(self):
        self.logs: List[dict] = []

    def log(
        self,
        correlation_id: str,
        agent_name: str,
        action: str,
        input_summary: dict,
        output_summary: dict,
        explanation: str,
        duration_ms: float
    ):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "correlation_id": correlation_id,
            "agent": agent_name,
            "action": action,
            "input": input_summary,
            "output": output_summary,
            "explanation": explanation,
            "duration_ms": duration_ms,
        }
        self.logs.append(entry)
        return entry

    def get_audit_trail(self, correlation_id: str) -> List[dict]:
        return [log for log in self.logs if log["correlation_id"] == correlation_id]

    def export_audit_report(self, correlation_id: str) -> str:
        trail = self.get_audit_trail(correlation_id)

        report = []
        report.append("=" * 70)
        report.append("           RS BANK LOAN DECISION AUDIT REPORT")
        report.append("=" * 70)
        report.append(f"Correlation ID: {correlation_id}")
        report.append(f"Report Generated: {datetime.now().isoformat()}")
        report.append("-" * 70)

        for entry in trail:
            report.append(f"\n[{entry['timestamp']}] {entry['agent']}")
            report.append(f"Action: {entry['action']}")
            report.append(f"Duration: {entry['duration_ms']:.2f}ms")
            report.append(f"Explanation: {entry['explanation']}")
            report.append("-" * 40)

        report.append("=" * 70)
        return "\n".join(report)


explainability_engine = ExplainabilityEngine()
audit_logger = AuditLogger()
