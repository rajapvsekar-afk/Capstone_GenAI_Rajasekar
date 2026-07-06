"""
Core Domain Models for RS Bank Loan Platform
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class LoanDecision(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"


class LoanType(Enum):
    PERSONAL = "personal"
    HOME = "home"
    AUTO = "auto"
    EDUCATION = "education"
    BUSINESS = "business"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ApplicantProfile:
    applicant_id: str
    name: str
    age: int
    annual_income: float
    employment_status: str
    employment_years: float
    employer_name: str
    job_title: str
    monthly_expenses: float
    credit_score: int
    credit_history_years: int
    existing_loans: int
    existing_loan_amount: float
    credit_card_utilization: float
    payment_defaults: int
    bankruptcies: int
    savings_balance: float
    property_owned: bool
    property_value: float
    other_assets: float
    dependents: int
    education_level: str
    residential_status: str
    years_at_address: int
    documents_submitted: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "applicant_id": self.applicant_id,
            "name": self.name,
            "age": self.age,
            "annual_income": self.annual_income,
            "employment_status": self.employment_status,
            "employment_years": self.employment_years,
            "credit_score": self.credit_score,
            "credit_history_years": self.credit_history_years,
            "existing_loans": self.existing_loans,
            "payment_defaults": self.payment_defaults,
            "bankruptcies": self.bankruptcies,
            "documents_submitted": self.documents_submitted,
        }


@dataclass
class LoanApplication:
    application_id: str
    applicant: ApplicantProfile
    loan_type: LoanType
    requested_amount: float
    term_months: int
    purpose: str
    collateral_offered: bool
    collateral_value: float
    co_applicant: Optional[ApplicantProfile] = None
    submission_date: datetime = field(default_factory=datetime.now)
    status: str = "submitted"

    def to_dict(self) -> dict:
        return {
            "application_id": self.application_id,
            "applicant": self.applicant.to_dict(),
            "loan_type": self.loan_type.value,
            "requested_amount": self.requested_amount,
            "term_months": self.term_months,
            "purpose": self.purpose,
            "collateral_offered": self.collateral_offered,
            "collateral_value": self.collateral_value,
            "submission_date": self.submission_date.isoformat(),
        }


@dataclass
class AgentResult:
    agent_id: str
    agent_name: str
    status: AgentStatus
    score: float
    confidence: float
    findings: list
    recommendations: list
    flags: list
    explanations: list
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "score": self.score,
            "confidence": self.confidence,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "flags": self.flags,
            "explanations": self.explanations,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LoanEvaluation:
    evaluation_id: str
    application_id: str
    decision: LoanDecision
    overall_score: float
    risk_level: RiskLevel
    agent_results: dict
    approved_amount: Optional[float]
    interest_rate: Optional[float]
    conditions: list
    rejection_reasons: list
    manual_review_reasons: list
    decision_explanation: str
    audit_trail: list
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    total_processing_time_ms: float = 0

    def to_dict(self) -> dict:
        return {
            "evaluation_id": self.evaluation_id,
            "application_id": self.application_id,
            "decision": self.decision.value,
            "overall_score": self.overall_score,
            "risk_level": self.risk_level.value,
            "agent_results": {k: v.to_dict() for k, v in self.agent_results.items()},
            "approved_amount": self.approved_amount,
            "interest_rate": self.interest_rate,
            "conditions": self.conditions,
            "rejection_reasons": self.rejection_reasons,
            "manual_review_reasons": self.manual_review_reasons,
            "decision_explanation": self.decision_explanation,
            "audit_trail": self.audit_trail,
            "evaluation_timestamp": self.evaluation_timestamp.isoformat(),
            "total_processing_time_ms": self.total_processing_time_ms,
        }


@dataclass
class AuditEntry:
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    timestamp: datetime = field(default_factory=datetime.now)
    agent_name: str = ""
    action: str = ""
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    explanation: str = ""
    duration_ms: float = 0

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "action": self.action,
            "explanation": self.explanation,
            "duration_ms": self.duration_ms,
        }
