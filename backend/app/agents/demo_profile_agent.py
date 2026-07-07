#!/usr/bin/env python3
"""
Demonstration script for Profile Agent.
Shows example usage and outputs.
"""

import json
from datetime import datetime
from profile_agent import analyze_applicant


def print_profile(profile_dict, title="Applicant Profile"):
    """Pretty print profile data."""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    print(f"{'=' * 80}\n")
    print(json.dumps(profile_dict, indent=2, default=str))
    print(f"\n{'=' * 80}\n")


def demo_low_risk():
    """Demonstrate low-risk applicant profile."""
    profile = analyze_applicant(
        application_id="APP-001-LOW-RISK",
        applicant_name="Sarah Johnson",
        applicant_email="sarah.johnson@example.com",
        applicant_phone="+1-555-0001",
        annual_income=150000,
        employment_status="Permanent Full-time",
        years_employed=8,
        loan_amount=60000,
        loan_type="Personal",
        loan_term_months=60,
        credit_score=780,
        existing_debt=300,
        estimated_interest_rate=4.5,
    )

    print_profile(profile.model_dump(), "DEMO 1: LOW-RISK APPLICANT")
    print(f"Risk Level: {profile.risk_level}")
    print(f"Risk Score: {profile.risk_score}")
    print(f"Recommendation: APPROVE ✓")


def demo_medium_risk():
    """Demonstrate medium-risk applicant profile."""
    profile = analyze_applicant(
        application_id="APP-002-MED-RISK",
        applicant_name="Michael Chen",
        applicant_email="mchen@example.com",
        applicant_phone="+1-555-0002",
        annual_income=85000,
        employment_status="Permanent Full-time",
        years_employed=3,
        loan_amount=45000,
        loan_type="Auto",
        loan_term_months=72,
        credit_score=680,
        existing_debt=800,
        estimated_interest_rate=6.0,
    )

    print_profile(profile.model_dump(), "DEMO 2: MEDIUM-RISK APPLICANT")
    print(f"Risk Level: {profile.risk_level}")
    print(f"Risk Score: {profile.risk_score}")
    print(f"Risk Factors: {', '.join(profile.risk_factors)}")
    print(f"Recommendation: REVIEW CAREFULLY ⚠")


def demo_high_risk():
    """Demonstrate high-risk applicant profile."""
    profile = analyze_applicant(
        application_id="APP-003-HIGH-RISK",
        applicant_name="Robert Martinez",
        applicant_email="rmartinez@example.com",
        applicant_phone="+1-555-0003",
        annual_income=45000,
        employment_status="Part-time Contract",
        years_employed=0.8,
        loan_amount=85000,
        loan_type="Home",
        loan_term_months=360,
        credit_score=580,
        existing_debt=2000,
        estimated_interest_rate=8.5,
    )

    print_profile(profile.model_dump(), "DEMO 3: HIGH-RISK APPLICANT")
    print(f"Risk Level: {profile.risk_level}")
    print(f"Risk Score: {profile.risk_score}")
    print(f"Risk Factors: {', '.join(profile.risk_factors)}")
    print(f"Recommendation: REJECT ✗")


def demo_no_credit():
    """Demonstrate applicant with no credit history."""
    profile = analyze_applicant(
        application_id="APP-004-NO-CREDIT",
        applicant_name="Emma Thompson",
        applicant_email="emma.thompson@example.com",
        applicant_phone="+1-555-0004",
        annual_income=95000,
        employment_status="Permanent Full-time",
        years_employed=2,
        loan_amount=35000,
        loan_type="Personal",
        loan_term_months=48,
        credit_score=None,  # No credit history
        existing_debt=0,
        estimated_interest_rate=7.0,
    )

    print_profile(profile.model_dump(), "DEMO 4: NO CREDIT HISTORY")
    print(f"Risk Level: {profile.risk_level}")
    print(f"Risk Score: {profile.risk_score}")
    print(f"Risk Factors: {', '.join(profile.risk_factors)}")
    print(f"Recommendation: REQUEST CREDIT ESTABLISHMENT PLAN")


def demo_edge_case():
    """Demonstrate edge case with extreme parameters."""
    profile = analyze_applicant(
        application_id="APP-005-EDGE",
        applicant_name="Alex Kumar",
        applicant_email="alex.kumar@example.com",
        applicant_phone="+1-555-0005",
        annual_income=35000,
        employment_status="Self-employed",
        years_employed=0.5,
        loan_amount=150000,
        loan_type="Home",
        loan_term_months=360,
        credit_score=560,
        existing_debt=3500,
        estimated_interest_rate=10.0,
    )

    print_profile(profile.model_dump(), "DEMO 5: EDGE CASE (EXTREME RISK)")
    print(f"Risk Level: {profile.risk_level}")
    print(f"Risk Score: {profile.risk_score}")
    print(f"Risk Factors: {', '.join(profile.risk_factors)}")
    print(f"Recommendation: REJECT - MULTIPLE SEVERE RISK FACTORS ✗✗")


def comparison_table():
    """Create comparison table of all demos."""
    print("\n" + "=" * 100)
    print(f"{'COMPARISON TABLE':^100}")
    print("=" * 100)

    profiles = [
        ("Low Risk", "APP-001-LOW-RISK", "Sarah Johnson", 150000, 780, 60000, "Permanent Full-time", 8),
        ("Medium Risk", "APP-002-MED-RISK", "Michael Chen", 85000, 680, 45000, "Permanent Full-time", 3),
        ("High Risk", "APP-003-HIGH-RISK", "Robert Martinez", 45000, 580, 85000, "Part-time Contract", 0.8),
        ("No Credit", "APP-004-NO-CREDIT", "Emma Thompson", 95000, None, 35000, "Permanent Full-time", 2),
        ("Extreme Risk", "APP-005-EDGE", "Alex Kumar", 35000, 560, 150000, "Self-employed", 0.5),
    ]

    # Generate profiles and collect data
    results = []
    for label, app_id, name, income, credit, loan, emp_status, years in profiles:
        profile = analyze_applicant(
            application_id=app_id,
            applicant_name=name,
            applicant_email=f"{name.lower().replace(' ', '.')}@example.com",
            applicant_phone="+1-555-0000",
            annual_income=income,
            employment_status=emp_status,
            years_employed=years,
            loan_amount=loan,
            loan_type="Personal",
            loan_term_months=60,
            credit_score=credit,
        )
        results.append({
            "Category": label,
            "Name": name,
            "Income": f"${income:,}",
            "Credit": str(credit) if credit else "N/A",
            "Loan": f"${loan:,}",
            "DTI": f"{profile.credit_profile.debt_to_income_ratio:.1%}",
            "Risk Level": profile.risk_level,
            "Risk Score": f"{profile.risk_score:.1f}",
        })

    # Print table header
    header_format = "{:<15} {:<20} {:<15} {:<12} {:<15} {:<10} {:<15} {:<12}"
    print(header_format.format(
        "Category", "Name", "Income", "Credit", "Loan", "DTI", "Risk Level", "Risk Score"
    ))
    print("-" * 100)

    # Print rows
    for result in results:
        print(header_format.format(
            result["Category"],
            result["Name"],
            result["Income"],
            result["Credit"],
            result["Loan"],
            result["DTI"],
            result["Risk Level"],
            result["Risk Score"]
        ))

    print("=" * 100 + "\n")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + f"{'PROFILE AGENT - DEMONSTRATION':^78}" + "║")
    print("║" + f"{'Structured Applicant Analysis System':^78}" + "║")
    print("╚" + "=" * 78 + "╝")

    demo_low_risk()
    demo_medium_risk()
    demo_high_risk()
    demo_no_credit()
    demo_edge_case()

    comparison_table()

    print("\nKey Features Demonstrated:")
    print("  ✓ Comprehensive applicant profiling")
    print("  ✓ Multi-factor risk assessment")
    print("  ✓ Structured JSON output (Pydantic models)")
    print("  ✓ Handling of edge cases (no credit, extreme parameters)")
    print("  ✓ Clear risk factors and recommendations")
    print("  ✓ Employment stability scoring")
    print("  ✓ Debt-to-income analysis")
    print("\nAll profiles are fully JSON-serializable and ready for API integration.")


if __name__ == "__main__":
    main()
