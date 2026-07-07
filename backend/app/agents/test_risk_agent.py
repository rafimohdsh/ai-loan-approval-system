"""Minimal test scenario for Risk Agent."""

from ..agents.risk_agent import 

def test_risk_agent():
    """Test risk calculation with sample applicant."""
    profile = calculate_risk(
        total_monthly_debt=2000,
        monthly_income=8000,
        loan_amount=100000,
        annual_income=96000,
        credit_score=720,
    )

    # Verify structure
    assert profile.dti_metrics.dti_ratio == 0.25
    assert profile.dti_metrics.status == "Acceptable"
    assert profile.credit_risk.risk_level == RiskLevel.LOW
    assert profile.loan_risk.risk_level == RiskLevel.MEDIUM
    assert profile.overall_risk_level == RiskLevel.LOW

    print("✓ Risk agent test passed")
    print(f"  DTI: {profile.dti_metrics.dti_percentage}%")
    print(f"  Credit Risk: {profile.credit_risk.risk_level}")
    print(f"  Loan Risk: {profile.loan_risk.risk_level}")
    print(f"  Overall Risk: {profile.overall_risk_level} ({profile.overall_risk_score})")


if __name__ == "__main__":
    test_risk_agent()
