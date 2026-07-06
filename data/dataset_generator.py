"""
Loan Application Dataset Generator
Creates 1000 realistic loan application records for testing and analysis
"""

import csv
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os


class DatasetGenerator:
    """Generates realistic loan application datasets."""

    EMPLOYMENT_TYPES = ["employed", "self_employed", "retired", "unemployed"]

    LOCATIONS = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune",
        "Kolkata", "Jaipur", "Ahmedabad", "Surat", "Lucknow", "Chandigarh",
        "Indore", "Visakhapatnam", "Vadodara", "Ghaziabad", "Ludhiana",
        "Kanpur", "Kochi", "Coimbatore", "Noida", "Thane", "Nagpur",
        "Aurangabad", "Bhopal", "Pimpri-Chinchwad", "Patna", "Vadodara"
    ]

    LOAN_PURPOSES = [
        "Home Purchase", "Education", "Car Purchase", "Personal Expenses",
        "Business Expansion", "Medical Emergency", "Debt Consolidation",
        "Wedding", "Home Renovation", "Starting Business", "Property Investment"
    ]

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.records: List[Dict[str, Any]] = []

    def generate_applicant_id(self, index: int) -> str:
        return f"APP{index+1:06d}"

    def generate_age(self) -> int:
        return random.randint(21, 65)

    def generate_annual_income(self) -> float:
        # Income distribution: 40% low, 40% middle, 20% high
        tier = random.random()
        if tier < 0.40:
            return round(random.uniform(200_000, 600_000), 2)
        elif tier < 0.80:
            return round(random.uniform(600_000, 1_500_000), 2)
        else:
            return round(random.uniform(1_500_000, 5_000_000), 2)

    def generate_employment_type(self) -> str:
        weights = [0.70, 0.15, 0.10, 0.05]  # employed, self_employed, retired, unemployed
        return random.choices(self.EMPLOYMENT_TYPES, weights=weights)[0]

    def generate_credit_score(self) -> int:
        # Skewed distribution: most have good credit
        tier = random.random()
        if tier < 0.10:
            return random.randint(300, 550)  # Poor
        elif tier < 0.25:
            return random.randint(550, 650)  # Fair
        elif tier < 0.55:
            return random.randint(650, 750)  # Good
        elif tier < 0.85:
            return random.randint(750, 800)  # Very Good
        else:
            return random.randint(800, 900)  # Excellent

    def generate_loan_amount(self) -> float:
        tier = random.random()
        if tier < 0.30:
            return round(random.uniform(100_000, 500_000), 2)  # Small
        elif tier < 0.60:
            return round(random.uniform(500_000, 2_000_000), 2)  # Medium
        else:
            return round(random.uniform(2_000_000, 10_000_000), 2)  # Large

    def generate_tenure_months(self) -> int:
        return random.choice([12, 24, 36, 48, 60, 84, 120, 180, 240])

    def generate_existing_liabilities(self) -> float:
        # 60% have no existing liabilities, 40% have some
        if random.random() < 0.60:
            return 0.0
        else:
            return round(random.uniform(50_000, 2_000_000), 2)

    def generate_location(self) -> str:
        return random.choice(self.LOCATIONS)

    def generate_timestamp(self, days_back: int = 30) -> str:
        start_date = datetime.now() - timedelta(days=days_back)
        random_date = start_date + timedelta(
            days=random.randint(0, days_back),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        return random_date.isoformat()

    def generate_employment_years(self, employment_type: str) -> float:
        if employment_type == "employed":
            return round(random.uniform(0.5, 30), 1)
        elif employment_type == "self_employed":
            return round(random.uniform(0.5, 20), 1)
        elif employment_type == "retired":
            return round(random.uniform(0, 40), 1)
        else:  # unemployed
            return 0.0

    def generate_loan_purpose(self) -> str:
        return random.choice(self.LOAN_PURPOSES)

    def generate_monthly_expenses(self, annual_income: float) -> float:
        # Monthly expenses typically 30-50% of monthly income
        monthly_income = annual_income / 12
        expense_ratio = random.uniform(0.25, 0.50)
        return round(monthly_income * expense_ratio, 2)

    def generate_records(self, num_records: int = 1000) -> List[Dict[str, Any]]:
        """Generate synthetic loan application records."""
        self.records = []

        for i in range(num_records):
            age = self.generate_age()
            annual_income = self.generate_annual_income()
            employment_type = self.generate_employment_type()
            credit_score = self.generate_credit_score()
            loan_amount = self.generate_loan_amount()
            tenure_months = self.generate_tenure_months()
            existing_liabilities = self.generate_existing_liabilities()
            location = self.generate_location()
            timestamp = self.generate_timestamp()
            employment_years = self.generate_employment_years(employment_type)
            monthly_expenses = self.generate_monthly_expenses(annual_income)
            loan_purpose = self.generate_loan_purpose()

            record = {
                "applicant_id": self.generate_applicant_id(i),
                "age": age,
                "annual_income": annual_income,
                "employment_type": employment_type,
                "employment_years": employment_years,
                "credit_score": credit_score,
                "loan_amount": loan_amount,
                "tenure_months": tenure_months,
                "existing_liabilities": existing_liabilities,
                "location": location,
                "application_timestamp": timestamp,
                "loan_purpose": loan_purpose,
                "monthly_expenses": monthly_expenses,
                "monthly_income": round(annual_income / 12, 2),
                "dti_ratio": round((monthly_expenses / (annual_income / 12)) * 100, 2) if annual_income > 0 else 0,
            }
            self.records.append(record)

        return self.records

    def save_to_csv(self, filename: str):
        """Save records to CSV file."""
        if not self.records:
            print("No records to save. Generate records first.")
            return

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = self.records[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for record in self.records:
                writer.writerow(record)

        print(f"✓ Saved {len(self.records)} records to {filename}")

    def save_to_json(self, filename: str):
        """Save records to JSON file."""
        if not self.records:
            print("No records to save. Generate records first.")
            return

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w') as jsonfile:
            json.dump(self.records, jsonfile, indent=2)

        print(f"✓ Saved {len(self.records)} records to {filename}")

    def get_statistics(self) -> Dict[str, Any]:
        """Generate statistics about the dataset."""
        if not self.records:
            return {}

        ages = [r["age"] for r in self.records]
        incomes = [r["annual_income"] for r in self.records]
        credit_scores = [r["credit_score"] for r in self.records]
        loan_amounts = [r["loan_amount"] for r in self.records]
        liabilities = [r["existing_liabilities"] for r in self.records]

        employment_counts = {}
        for r in self.records:
            emp_type = r["employment_type"]
            employment_counts[emp_type] = employment_counts.get(emp_type, 0) + 1

        location_counts = {}
        for r in self.records:
            loc = r["location"]
            location_counts[loc] = location_counts.get(loc, 0) + 1

        stats = {
            "total_records": len(self.records),
            "age": {
                "min": min(ages),
                "max": max(ages),
                "mean": sum(ages) / len(ages),
                "median": sorted(ages)[len(ages) // 2],
            },
            "annual_income": {
                "min": min(incomes),
                "max": max(incomes),
                "mean": sum(incomes) / len(incomes),
                "median": sorted(incomes)[len(incomes) // 2],
            },
            "credit_score": {
                "min": min(credit_scores),
                "max": max(credit_scores),
                "mean": sum(credit_scores) / len(credit_scores),
                "median": sorted(credit_scores)[len(credit_scores) // 2],
            },
            "loan_amount": {
                "min": min(loan_amounts),
                "max": max(loan_amounts),
                "mean": sum(loan_amounts) / len(loan_amounts),
                "median": sorted(loan_amounts)[len(loan_amounts) // 2],
            },
            "existing_liabilities": {
                "min": min(liabilities),
                "max": max(liabilities),
                "mean": sum(liabilities) / len(liabilities),
                "median": sorted(liabilities)[len(liabilities) // 2],
            },
            "employment_distribution": employment_counts,
            "location_distribution": location_counts,
            "avg_dti_ratio": sum(r["dti_ratio"] for r in self.records) / len(self.records),
            "records_with_liabilities": sum(1 for r in self.records if r["existing_liabilities"] > 0),
            "records_with_good_credit": sum(1 for r in self.records if r["credit_score"] >= 700),
        }

        return stats

    def print_statistics(self):
        """Print dataset statistics."""
        stats = self.get_statistics()

        if not stats:
            print("No records to analyze.")
            return

        print("\n" + "=" * 80)
        print("                    LOAN APPLICATION DATASET STATISTICS")
        print("=" * 80)

        print(f"\n📊 Dataset Overview")
        print(f"   Total Records: {stats['total_records']:,}")
        print(f"   Records with Existing Liabilities: {stats['records_with_liabilities']:,}")
        print(f"   Records with Good Credit (≥700): {stats['records_with_good_credit']:,}")

        print(f"\n👤 Age Distribution")
        age = stats['age']
        print(f"   Min: {age['min']} years | Max: {age['max']} years")
        print(f"   Mean: {age['mean']:.1f} years | Median: {age['median']} years")

        print(f"\n💰 Annual Income Distribution")
        income = stats['annual_income']
        print(f"   Min: Rs. {income['min']:,.2f}")
        print(f"   Max: Rs. {income['max']:,.2f}")
        print(f"   Mean: Rs. {income['mean']:,.2f}")
        print(f"   Median: Rs. {income['median']:,.2f}")

        print(f"\n📈 Credit Score Distribution")
        cs = stats['credit_score']
        print(f"   Min: {cs['min']} | Max: {cs['max']}")
        print(f"   Mean: {cs['mean']:.1f} | Median: {cs['median']}")

        print(f"\n🏦 Loan Amount Distribution")
        loan = stats['loan_amount']
        print(f"   Min: Rs. {loan['min']:,.2f}")
        print(f"   Max: Rs. {loan['max']:,.2f}")
        print(f"   Mean: Rs. {loan['mean']:,.2f}")
        print(f"   Median: Rs. {loan['median']:,.2f}")

        print(f"\n💳 Existing Liabilities")
        liab = stats['existing_liabilities']
        print(f"   Min: Rs. {liab['min']:,.2f}")
        print(f"   Max: Rs. {liab['max']:,.2f}")
        print(f"   Mean: Rs. {liab['mean']:,.2f}")
        print(f"   Median: Rs. {liab['median']:,.2f}")

        print(f"\n💼 Employment Type Distribution")
        for emp_type, count in stats['employment_distribution'].items():
            percentage = (count / stats['total_records']) * 100
            print(f"   {emp_type.title()}: {count:,} ({percentage:.1f}%)")

        print(f"\n📍 Top 10 Locations")
        locations = sorted(stats['location_distribution'].items(), key=lambda x: x[1], reverse=True)[:10]
        for location, count in locations:
            percentage = (count / stats['total_records']) * 100
            print(f"   {location}: {count} ({percentage:.1f}%)")

        print(f"\n📊 Debt-to-Income Ratio")
        print(f"   Average DTI: {stats['avg_dti_ratio']:.1f}%")

        print("\n" + "=" * 80)

    def print_sample_records(self, num_samples: int = 5):
        """Print sample records from the dataset."""
        if not self.records:
            print("No records to display. Generate records first.")
            return

        samples = random.sample(self.records, min(num_samples, len(self.records)))

        print("\n" + "=" * 120)
        print("                                   SAMPLE LOAN APPLICATIONS")
        print("=" * 120)

        for i, record in enumerate(samples, 1):
            print(f"\n📋 Application #{i}")
            print(f"   Applicant ID: {record['applicant_id']}")
            print(f"   Age: {record['age']} years")
            print(f"   Annual Income: Rs. {record['annual_income']:,.2f}")
            print(f"   Monthly Income: Rs. {record['monthly_income']:,.2f}")
            print(f"   Employment: {record['employment_type'].title()} ({record['employment_years']} years)")
            print(f"   Credit Score: {record['credit_score']}")
            print(f"   Loan Amount: Rs. {record['loan_amount']:,.2f}")
            print(f"   Tenure: {record['tenure_months']} months")
            print(f"   Purpose: {record['loan_purpose']}")
            print(f"   Existing Liabilities: Rs. {record['existing_liabilities']:,.2f}")
            print(f"   Monthly Expenses: Rs. {record['monthly_expenses']:,.2f}")
            print(f"   DTI Ratio: {record['dti_ratio']:.2f}%")
            print(f"   Location: {record['location']}")
            print(f"   Submitted: {record['application_timestamp']}")

        print("\n" + "=" * 120)


def main():
    """Generate and save the dataset."""
    print("\n" + "=" * 80)
    print("           RS BANK LOAN APPLICATION DATASET GENERATOR")
    print("=" * 80)

    generator = DatasetGenerator(seed=42)

    print("\n🔄 Generating 1000 loan application records...")
    records = generator.generate_records(1000)
    print(f"✓ Generated {len(records)} records")

    # Save to CSV
    csv_path = "/home/ubuntu/rs_bank_agentic_loan_platform/data/loan_applications.csv"
    generator.save_to_csv(csv_path)

    # Save to JSON
    json_path = "/home/ubuntu/rs_bank_agentic_loan_platform/data/loan_applications.json"
    generator.save_to_json(json_path)

    # Print statistics
    generator.print_statistics()

    # Print sample records
    generator.print_sample_records(5)

    print("\n✅ Dataset generation complete!")
    print(f"   CSV: {csv_path}")
    print(f"   JSON: {json_path}")


if __name__ == "__main__":
    main()
