def calculate_debt_to_income_ratio(monthly_debt: float, monthly_income: float) -> float:
    """Calculate debt-to-income ratio."""
    if monthly_income == 0:
        return float('inf')
    return monthly_debt / monthly_income


def calculate_income_to_loan_ratio(annual_income: float, loan_amount: float) -> float:
    """Calculate income-to-loan ratio."""
    if annual_income == 0:
        return float('inf')
    return annual_income / loan_amount


def calculate_monthly_payment(loan_amount: float, annual_rate: float, months: int) -> float:
    """Calculate estimated monthly payment using amortization formula."""
    if months == 0 or annual_rate == 0:
        return 0
    monthly_rate = annual_rate / 12 / 100
    if monthly_rate == 0:
        return loan_amount / months
    payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return payment


def assess_employment_stability(years_employed: float, employment_status: str) -> dict:
    """Assess employment stability based on tenure and status."""
    stability_score = 0

    if years_employed >= 5:
        stability_score = 90
    elif years_employed >= 2:
        stability_score = 70
    elif years_employed >= 1:
        stability_score = 50
    else:
        stability_score = 20

    employment_status_lower = employment_status.lower()
    if "permanent" in employment_status_lower or "full-time" in employment_status_lower:
        stability_score = min(100, stability_score + 20)
    elif "contract" in employment_status_lower or "part-time" in employment_status_lower:
        stability_score = max(0, stability_score - 20)
    elif "self-employed" in employment_status_lower:
        stability_score = max(0, stability_score - 10)

    return {
        "stability_score": stability_score,
        "status_category": employment_status_lower,
        "tenure_years": years_employed
    }


def interpret_credit_score(credit_score: int) -> dict:
    """Interpret credit score and provide risk assessment."""
    if credit_score >= 750:
        risk_level = "low"
        description = "Excellent credit - very low risk"
    elif credit_score >= 700:
        risk_level = "low"
        description = "Good credit - low risk"
    elif credit_score >= 650:
        risk_level = "medium"
        description = "Fair credit - moderate risk"
    elif credit_score >= 600:
        risk_level = "high"
        description = "Poor credit - higher risk"
    else:
        risk_level = "very_high"
        description = "Very poor credit - very high risk"

    return {
        "score": credit_score,
        "risk_level": risk_level,
        "description": description
    }
