"""
RS Bank Multi-Agent Agentic AI Loan Platform
Main entry point with demo scenarios and analytics
"""

import asyncio
import json
from datetime import datetime

from core.models import (
    ApplicantProfile, LoanApplication, LoanType
)
from core.event_bus import event_bus
from data.dataset_generator import DatasetGenerator
from services.orchestrator import LoanOrchestrator, AgentRegistry
from core.explainability import explainability_engine


async def print_evaluation_report(evaluation):
    """Print detailed evaluation report."""
    print("\n" + "=" * 100)
    print("                           LOAN EVALUATION REPORT")
    print("=" * 100)

    print(f"\n📋 Application Details")
    print(f"   Evaluation ID: {evaluation.evaluation_id}")
    print(f"   Application ID: {evaluation.application_id}")
    print(f"   Timestamp: {evaluation.evaluation_timestamp.isoformat()}")
    print(f"   Processing Time: {evaluation.total_processing_time_ms:.2f}ms")

    # Decision Banner
    decision_display = {
        "approved": "✅ APPROVED",
        "rejected": "❌ REJECTED",
        "requires_manual_review": "⚠️  REQUIRES MANUAL REVIEW"
    }

    print(f"\n🎯 Decision")
    print(f"   Status: {decision_display[evaluation.decision.value]}")
    print(f"   Overall Score: {evaluation.overall_score:.1f}/100")
    print(f"   Risk Level: {evaluation.risk_level.value.upper()}")

    # Agent Scores
    print(f"\n📊 Agent Analysis")
    print(f"   {'Agent Name':<35} {'Score':<10} {'Confidence':<12} {'Status':<12}")
    print(f"   {'-'*68}")
    for agent_name, result in evaluation.agent_results.items():
        confidence_pct = result.confidence * 100
        print(f"   {agent_name:<35} {result.score:>6.1f}/100 {confidence_pct:>10.0f}% {result.status.value:<12}")

    # Decision Details
    if evaluation.decision.value == "approved":
        print(f"\n✅ Approval Details")
        print(f"   Approved Amount: Rs. {evaluation.approved_amount:,.2f}")
        print(f"   Interest Rate: {evaluation.interest_rate:.2f}% p.a.")

        emi = orchestrator.calculate_emi(
            evaluation.approved_amount,
            evaluation.interest_rate,
            12  # Assuming 12 months for calculation
        )
        print(f"   Estimated Monthly EMI: Rs. {emi:,.2f}")

        if evaluation.conditions:
            print(f"\n   Conditions:")
            for i, cond in enumerate(evaluation.conditions, 1):
                print(f"   {i}. {cond}")

    elif evaluation.decision.value == "rejected":
        print(f"\n❌ Rejection Reasons")
        for i, reason in enumerate(evaluation.rejection_reasons[:5], 1):
            print(f"   {i}. {reason}")

    elif evaluation.decision.value == "requires_manual_review":
        print(f"\n⚠️  Manual Review Required")
        for reason in evaluation.manual_review_reasons[:5]:
            print(f"   • {reason}")

    # Key Findings
    print(f"\n📌 Key Findings")
    for agent_name, result in evaluation.agent_results.items():
        if result.findings:
            print(f"\n   {agent_name}:")
            for finding in result.findings[:2]:
                print(f"   → {finding}")

    # Decision Explanation
    print(f"\n💡 Decision Explanation")
    print(f"   {evaluation.decision_explanation}")

    print("\n" + "=" * 100)


async def process_sample_applications(orchestrator, num_samples=3):
    """Process sample loan applications."""
    print("\n" + "=" * 100)
    print("                    PROCESSING SAMPLE APPLICATIONS")
    print("=" * 100)

    samples = [
        # Strong applicant - APPROVED
        {
            "name": "Rajesh Kumar",
            "age": 38,
            "annual_income": 2_000_000,
            "employment_status": "employed",
            "employment_years": 12,
            "employer_name": "TCS",
            "job_title": "Senior Manager",
            "monthly_expenses": 50_000,
            "credit_score": 795,
            "credit_history_years": 15,
            "existing_loans": 0,
            "existing_loan_amount": 0,
            "credit_card_utilization": 20,
            "payment_defaults": 0,
            "bankruptcies": 0,
            "savings_balance": 3_000_000,
            "property_owned": True,
            "property_value": 10_000_000,
            "other_assets": 500_000,
            "dependents": 2,
            "education_level": "MBA",
            "residential_status": "owned",
            "years_at_address": 10,
            "documents_submitted": ["id_proof", "address_proof", "income_proof", "bank_statements"],
            "loan_type": LoanType.HOME,
            "loan_amount": 5_000_000,
            "term_months": 240,
            "purpose": "Home Purchase",
        },
        # Weak applicant - REJECTED
        {
            "name": "Amit Sharma",
            "age": 26,
            "annual_income": 350_000,
            "employment_status": "employed",
            "employment_years": 0.8,
            "employer_name": "StartupXYZ",
            "job_title": "Junior Developer",
            "monthly_expenses": 22_000,
            "credit_score": 580,
            "credit_history_years": 1,
            "existing_loans": 3,
            "existing_loan_amount": 300_000,
            "credit_card_utilization": 92,
            "payment_defaults": 4,
            "bankruptcies": 0,
            "savings_balance": 25_000,
            "property_owned": False,
            "property_value": 0,
            "other_assets": 0,
            "dependents": 1,
            "education_level": "B.Tech",
            "residential_status": "rented",
            "years_at_address": 1,
            "documents_submitted": ["id_proof", "address_proof"],
            "loan_type": LoanType.PERSONAL,
            "loan_amount": 600_000,
            "term_months": 36,
            "purpose": "Debt Consolidation",
        },
        # Borderline applicant - MANUAL REVIEW
        {
            "name": "Priya Patel",
            "age": 42,
            "annual_income": 1_000_000,
            "employment_status": "self_employed",
            "employment_years": 6,
            "employer_name": "Patel Consulting",
            "job_title": "Founder",
            "monthly_expenses": 40_000,
            "credit_score": 685,
            "credit_history_years": 9,
            "existing_loans": 1,
            "existing_loan_amount": 250_000,
            "credit_card_utilization": 48,
            "payment_defaults": 1,
            "bankruptcies": 1,
            "savings_balance": 600_000,
            "property_owned": True,
            "property_value": 4_000_000,
            "other_assets": 300_000,
            "dependents": 2,
            "education_level": "CA",
            "residential_status": "owned",
            "years_at_address": 7,
            "documents_submitted": ["id_proof", "address_proof", "income_proof", "bank_statements", "business_registration"],
            "loan_type": LoanType.BUSINESS,
            "loan_amount": 2_000_000,
            "term_months": 60,
            "purpose": "Business Expansion",
        },
    ]

    evaluations = []

    for i, sample_data in enumerate(samples[:num_samples], 1):
        print(f"\n[Application {i}/{num_samples}] Processing {sample_data['name']}...")

        # Create applicant profile
        applicant = ApplicantProfile(
            applicant_id=f"APP{i:06d}",
            name=sample_data["name"],
            age=sample_data["age"],
            annual_income=sample_data["annual_income"],
            employment_status=sample_data["employment_status"],
            employment_years=sample_data["employment_years"],
            employer_name=sample_data["employer_name"],
            job_title=sample_data["job_title"],
            monthly_expenses=sample_data["monthly_expenses"],
            credit_score=sample_data["credit_score"],
            credit_history_years=sample_data["credit_history_years"],
            existing_loans=sample_data["existing_loans"],
            existing_loan_amount=sample_data["existing_loan_amount"],
            credit_card_utilization=sample_data["credit_card_utilization"],
            payment_defaults=sample_data["payment_defaults"],
            bankruptcies=sample_data["bankruptcies"],
            savings_balance=sample_data["savings_balance"],
            property_owned=sample_data["property_owned"],
            property_value=sample_data["property_value"],
            other_assets=sample_data["other_assets"],
            dependents=sample_data["dependents"],
            education_level=sample_data["education_level"],
            residential_status=sample_data["residential_status"],
            years_at_address=sample_data["years_at_address"],
            documents_submitted=sample_data["documents_submitted"],
        )

        # Create loan application
        loan_app = LoanApplication(
            application_id=f"LN{i:06d}",
            applicant=applicant,
            loan_type=sample_data["loan_type"],
            requested_amount=sample_data["loan_amount"],
            term_months=sample_data["term_months"],
            purpose=sample_data["purpose"],
            collateral_offered=(sample_data["loan_type"] in [LoanType.HOME, LoanType.AUTO]),
            collateral_value=sample_data["property_value"] if sample_data["property_owned"] else 0,
        )

        # Evaluate
        evaluation = await orchestrator.evaluate(loan_app)
        evaluations.append(evaluation)

        await print_evaluation_report(evaluation)

    return evaluations


async def print_batch_summary(evaluations):
    """Print batch processing summary."""
    print("\n" + "=" * 100)
    print("                        BATCH PROCESSING SUMMARY")
    print("=" * 100)

    approved = sum(1 for e in evaluations if e.decision.value == "approved")
    rejected = sum(1 for e in evaluations if e.decision.value == "rejected")
    manual = sum(1 for e in evaluations if e.decision.value == "requires_manual_review")

    print(f"\n📊 Processing Results")
    print(f"   Total Applications: {len(evaluations)}")
    print(f"   ✅ Approved: {approved} ({approved/len(evaluations)*100:.1f}%)")
    print(f"   ❌ Rejected: {rejected} ({rejected/len(evaluations)*100:.1f}%)")
    print(f"   ⚠️  Manual Review: {manual} ({manual/len(evaluations)*100:.1f}%)")

    # Score distribution
    scores = [e.overall_score for e in evaluations]
    print(f"\n📈 Score Distribution")
    print(f"   Min: {min(scores):.1f} | Max: {max(scores):.1f}")
    print(f"   Average: {sum(scores)/len(scores):.1f}")
    print(f"   Median: {sorted(scores)[len(scores)//2]:.1f}")

    # Risk distribution
    risk_counts = {}
    for e in evaluations:
        risk = e.risk_level.value
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    print(f"\n⚠️  Risk Distribution")
    for risk_level in ["low", "medium", "high", "critical"]:
        count = risk_counts.get(risk_level, 0)
        if count > 0:
            print(f"   {risk_level.capitalize()}: {count} ({count/len(evaluations)*100:.1f}%)")

    # Timing
    total_time = sum(e.total_processing_time_ms for e in evaluations)
    avg_time = total_time / len(evaluations)

    print(f"\n⏱️  Performance Metrics")
    print(f"   Total Processing Time: {total_time:.2f}ms")
    print(f"   Average Time per Application: {avg_time:.2f}ms")

    print("\n" + "=" * 100)


async def generate_and_analyze_dataset(orchestrator, num_samples=10):
    """Generate dataset and analyze subset."""
    print("\n" + "=" * 100)
    print("                    DATASET GENERATION & ANALYSIS")
    print("=" * 100)

    generator = DatasetGenerator(seed=42)
    print("\n🔄 Generating dataset...")
    records = generator.generate_records(1000)
    print(f"✓ Generated {len(records)} records")

    print("\n📊 Dataset Statistics")
    generator.print_statistics()

    print(f"\n🔄 Processing {num_samples} sample applications from dataset...")
    evaluations = []

    for i, record in enumerate(records[:num_samples], 1):
        applicant = ApplicantProfile(
            applicant_id=record["applicant_id"],
            name=f"Applicant {i}",
            age=record["age"],
            annual_income=record["annual_income"],
            employment_status=record["employment_type"],
            employment_years=record["employment_years"],
            employer_name="Company",
            job_title="Employee",
            monthly_expenses=record["monthly_expenses"],
            credit_score=record["credit_score"],
            credit_history_years=random.randint(2, 15) if record["credit_score"] >= 650 else random.randint(1, 5),
            existing_loans=1 if record["existing_liabilities"] > 0 else 0,
            existing_loan_amount=record["existing_liabilities"],
            credit_card_utilization=random.randint(10, 95),
            payment_defaults=0 if record["credit_score"] >= 700 else random.randint(0, 3),
            bankruptcies=0 if record["credit_score"] >= 650 else random.randint(0, 1),
            savings_balance=record["annual_income"] * random.uniform(0.5, 2),
            property_owned=random.choice([True, False]),
            property_value=record["loan_amount"] * 2 if random.random() > 0.5 else 0,
            other_assets=record["annual_income"] * random.uniform(0, 0.5),
            dependents=random.randint(0, 3),
            education_level=random.choice(["B.Tech", "MBA", "Graduate", "High School"]),
            residential_status=random.choice(["owned", "rented", "family"]),
            years_at_address=random.randint(1, 10),
            documents_submitted=["id_proof", "address_proof", "income_proof"] if random.random() > 0.3 else ["id_proof"],
        )

        loan_app = LoanApplication(
            application_id=record["applicant_id"],
            applicant=applicant,
            loan_type=random.choice(list(LoanType)),
            requested_amount=record["loan_amount"],
            term_months=record["tenure_months"],
            purpose=record["loan_purpose"],
            collateral_offered=random.choice([True, False]),
            collateral_value=record["loan_amount"] * random.uniform(1.2, 2),
        )

        try:
            evaluation = await orchestrator.evaluate(loan_app)
            evaluations.append(evaluation)
            print(f"  ✓ {i}. {record['applicant_id']} - {evaluation.decision.value.upper()}")
        except Exception as e:
            print(f"  ✗ {i}. {record['applicant_id']} - Error: {str(e)[:50]}")

    return evaluations


async def main():
    """Main entry point."""
    print("\n" + "=" * 100)
    print("              RS BANK MULTI-AGENT AGENTIC AI LOAN PLATFORM")
    print("                   Production-Ready Microservices Architecture")
    print("=" * 100)

    # Initialize
    print("\n🚀 Initializing system...")
    registry = AgentRegistry()
    global orchestrator
    orchestrator = LoanOrchestrator(registry)

    # Health check
    print("\n🏥 System Health Check")
    health = registry.health_check()
    for agent_name, status in health.items():
        print(f"   ✓ {agent_name}: {status['status']}")

    # Process sample applications
    print("\n" + "=" * 100)
    evaluations = await process_sample_applications(orchestrator, num_samples=3)

    # Batch summary
    await print_batch_summary(evaluations)

    # Generate and analyze dataset
    print("\n" + "=" * 100)
    dataset_evaluations = await generate_and_analyze_dataset(orchestrator, num_samples=10)
    await print_batch_summary(dataset_evaluations)

    print("\n✅ Platform execution complete!")


import random

if __name__ == "__main__":
    asyncio.run(main())
