"""Minimal test for Decision Agent."""

from ..agents.decision_agent import 

def test_decision_agent():
    """Test decision scenarios."""
    # Scenario 1: Strong applicant - APPROVED
    decision = make_decision_mock(
        applicant_name="John Smith",
        annual_income=120000,
        credit_score=750,
        dti_ratio=0.25,
        loan_amount=50000,
        employment_years=7,
        employment_status="Permanent Full-time",
        existing_debt=500,
    )
    assert decision.decision == DecisionType.APPROVED
    print(f"✓ Strong applicant: {decision.decision}")

    # Scenario 2: Poor credit - REJECTED
    decision = make_decision_mock(
        applicant_name="Jane Doe",
        annual_income=45000,
        credit_score=580,
        dti_ratio=0.65,
        loan_amount=85000,
        employment_years=0.5,
        employment_status="Part-time",
        existing_debt=2000,
    )
    assert decision.decision == DecisionType.REJECTED
    print(f"✓ Poor credit: {decision.decision}")

    # Scenario 3: Borderline - MANUAL_REVIEW
    decision = make_decision_mock(
        applicant_name="Bob Wilson",
        annual_income=85000,
        credit_score=None,
        dti_ratio=0.42,
        loan_amount=45000,
        employment_years=2.5,
        employment_status="Permanent Full-time",
        existing_debt=1200,
    )
    assert decision.decision == DecisionType.MANUAL_REVIEW
    print(f"✓ No credit history: {decision.decision}")

    print("\n✓ All decision scenarios passed")


if __name__ == "__main__":
    test_decision_agent()
