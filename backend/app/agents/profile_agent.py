"""Profile Agent - Analyzes applicant information and returns structured JSON."""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..agents.tools.analysis_tools import (
    calculate_debt_to_income_ratio,
    calculate_income_to_loan_ratio,
    calculate_monthly_payment,
    assess_employment_stability,
    interpret_credit_score,
)
from .tool_registry import get_tool_registry
from .mcp_tools import MCPToolError

logger = logging.getLogger(__name__)


class IncomeProfile(BaseModel):
    """Applicant's income and employment profile."""
    annual_income: float = Field(..., description="Annual income in dollars")
    monthly_income: float = Field(..., description="Monthly income in dollars")
    employment_status: str = Field(..., description="Employment status (e.g., Employed, Self-employed, etc.)")
    years_employed: float = Field(..., description="Years at current employment")
    employment_stability_score: float = Field(..., description="Stability score 0-100")
    employment_category: str = Field(..., description="Category of employment (permanent, contract, etc.)")


class CreditProfile(BaseModel):
    """Applicant's credit and debt profile."""
    credit_score: Optional[int] = Field(None, description="Credit score (300-850)")
    credit_risk_level: Optional[str] = Field(None, description="Risk level based on credit score")
    credit_risk_description: Optional[str] = Field(None, description="Description of credit risk")
    existing_debt: float = Field(..., description="Total existing monthly debt obligations")
    total_monthly_debt_obligation: float = Field(..., description="Total monthly debt (existing + new loan)")
    debt_to_income_ratio: float = Field(..., description="Debt-to-income ratio")
    debt_to_income_status: str = Field(..., description="Status (Acceptable, Warning, High Risk)")


class LoanProfile(BaseModel):
    """Applicant's requested loan details and analysis."""
    loan_amount: float = Field(..., description="Requested loan amount in dollars")
    loan_type: str = Field(..., description="Type of loan (Personal, Home, Auto, etc.)")
    loan_term_months: int = Field(..., description="Loan term in months")
    estimated_interest_rate: float = Field(5.0, description="Estimated annual interest rate (%)")
    estimated_monthly_payment: float = Field(..., description="Estimated monthly payment")
    income_to_loan_ratio: float = Field(..., description="Annual income to loan amount ratio")
    income_to_loan_status: str = Field(..., description="Status (Acceptable, Warning, High Risk)")


class PersonalProfile(BaseModel):
    """Applicant's personal information."""
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    application_id: str = Field(..., description="Unique application identifier")


class ApplicantProfile(BaseModel):
    """Complete structured profile of loan applicant."""
    personal_info: PersonalProfile = Field(..., description="Personal information")
    income_profile: IncomeProfile = Field(..., description="Income and employment profile")
    credit_profile: CreditProfile = Field(..., description="Credit and debt profile")
    loan_profile: LoanProfile = Field(..., description="Requested loan details and analysis")

    risk_score: float = Field(..., description="Overall risk score 0-100 (100 is highest risk)")
    risk_level: str = Field(..., description="Overall risk level (Low, Medium, High, Very High)")
    risk_factors: List[str] = Field(default_factory=list, description="List of identified risk factors")

    profile_summary: str = Field(..., description="Executive summary of the profile")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Profile generation timestamp")


def calculate_risk_level(debt_to_income: float, credit_score: Optional[int], income_to_loan: float, employment_years: float) -> tuple[str, float]:
    """
    Calculate overall risk level and score.

    Returns:
        tuple: (risk_level, risk_score) where risk_score is 0-100
    """
    risk_score = 0.0

    # Credit score component (40% weight)
    if credit_score:
        if credit_score >= 750:
            risk_score += 0
        elif credit_score >= 700:
            risk_score += 10
        elif credit_score >= 650:
            risk_score += 25
        elif credit_score >= 600:
            risk_score += 40
        else:
            risk_score += 60
    else:
        risk_score += 30  # Unknown credit

    # Debt-to-income component (30% weight)
    if debt_to_income <= 0.36:
        risk_score += 0
    elif debt_to_income <= 0.43:
        risk_score += 15
    elif debt_to_income <= 0.50:
        risk_score += 30
    else:
        risk_score += 40

    # Income-to-loan component (20% weight)
    if income_to_loan >= 5:
        risk_score += 0
    elif income_to_loan >= 3:
        risk_score += 10
    elif income_to_loan >= 1:
        risk_score += 20
    else:
        risk_score += 30

    # Employment stability component (10% weight)
    if employment_years >= 5:
        risk_score += 0
    elif employment_years >= 2:
        risk_score += 5
    elif employment_years >= 1:
        risk_score += 10
    else:
        risk_score += 15

    # Normalize to 0-100
    risk_score = min(100, max(0, risk_score * 0.6))  # Scale down to 0-60 range, then adjust

    # Determine risk level
    if risk_score < 25:
        risk_level = "Low"
    elif risk_score < 50:
        risk_level = "Medium"
    elif risk_score < 75:
        risk_level = "High"
    else:
        risk_level = "Very High"

    return risk_level, risk_score


def identify_risk_factors(
    debt_to_income: float,
    credit_score: Optional[int],
    income_to_loan: float,
    employment_years: float,
    employment_status: str,
    existing_debt: float,
) -> List[str]:
    """Identify and return list of risk factors."""
    factors = []

    if debt_to_income > 0.50:
        factors.append("High debt-to-income ratio (>50%)")
    elif debt_to_income > 0.43:
        factors.append("Elevated debt-to-income ratio (43-50%)")

    if credit_score and credit_score < 650:
        factors.append(f"Low credit score ({credit_score})")

    if credit_score is None:
        factors.append("No credit score available")

    if income_to_loan < 1:
        factors.append("Loan amount exceeds annual income")
    elif income_to_loan < 3:
        factors.append("Loan amount is high relative to income")

    if employment_years < 1:
        factors.append("Less than 1 year employment history")
    elif employment_years < 2:
        factors.append("Short employment history (<2 years)")

    if "contract" in employment_status.lower() or "part-time" in employment_status.lower():
        factors.append("Non-permanent employment status")

    if "self-employed" in employment_status.lower():
        factors.append("Self-employed (variable income risk)")

    if existing_debt > 0:
        factors.append("Existing debt obligations")

    return factors if factors else ["No significant risk factors identified"]


def analyze_applicant(
    application_id: str,
    applicant_name: str,
    applicant_email: str,
    applicant_phone: str,
    annual_income: float,
    employment_status: str,
    years_employed: float,
    loan_amount: float,
    loan_type: str,
    loan_term_months: int,
    credit_score: Optional[int] = None,
    existing_debt: float = 0.0,
    estimated_interest_rate: float = 5.0,
    use_mcp_tools: bool = False,
) -> ApplicantProfile:
    """
    Analyze applicant information and generate structured profile.

    Args:
        application_id: Unique application identifier
        applicant_name: Applicant's full name
        applicant_email: Applicant's email
        applicant_phone: Applicant's phone number
        annual_income: Annual income in dollars
        employment_status: Employment status
        years_employed: Years at current employment
        loan_amount: Requested loan amount
        loan_type: Type of loan
        loan_term_months: Loan term in months
        credit_score: Credit score (optional)
        existing_debt: Total existing monthly debt
        estimated_interest_rate: Estimated annual interest rate
        use_mcp_tools: Whether to use MCP tools (if available)

    Returns:
        ApplicantProfile: Structured profile with all analyses
    """
    registry = get_tool_registry() if use_mcp_tools else None

    # Calculate derived values
    monthly_income = annual_income / 12

    try:
        if registry:
            employment_info = registry.invoke_tool("assess_employment", years_employed=years_employed, employment_status=employment_status)
        else:
            employment_info = assess_employment_stability(years_employed, employment_status)
    except (MCPToolError, ValueError) as e:
        logger.warning(f"Failed to assess employment via MCP, using local tool: {e}")
        employment_info = assess_employment_stability(years_employed, employment_status)

    # Calculate loan metrics with optional MCP
    try:
        if registry:
            monthly_payment = registry.invoke_tool("calculate_payment", loan_amount=loan_amount, annual_rate=estimated_interest_rate, months=loan_term_months)
            debt_to_income = registry.invoke_tool("calculate_dti", monthly_debt=existing_debt + monthly_payment, monthly_income=monthly_income)
            income_to_loan = registry.invoke_tool("calculate_itl", annual_income=annual_income, loan_amount=loan_amount)
        else:
            monthly_payment = calculate_monthly_payment(loan_amount, estimated_interest_rate, loan_term_months)
            debt_to_income = calculate_debt_to_income_ratio(existing_debt + monthly_payment, monthly_income)
            income_to_loan = calculate_income_to_loan_ratio(annual_income, loan_amount)
    except (MCPToolError, ValueError) as e:
        logger.warning(f"Failed to calculate metrics via MCP, using local tools: {e}")
        monthly_payment = calculate_monthly_payment(loan_amount, estimated_interest_rate, loan_term_months)
        total_monthly_debt = existing_debt + monthly_payment
        debt_to_income = calculate_debt_to_income_ratio(total_monthly_debt, monthly_income)
        income_to_loan = calculate_income_to_loan_ratio(annual_income, loan_amount)

    total_monthly_debt = existing_debt + monthly_payment

    # Credit profile
    try:
        if registry and credit_score:
            credit_assessment = registry.invoke_tool("interpret_credit", credit_score=credit_score)
        else:
            credit_assessment = interpret_credit_score(credit_score) if credit_score else {}
    except (MCPToolError, ValueError) as e:
        logger.warning(f"Failed to interpret credit score via MCP, using local tool: {e}")
        credit_assessment = interpret_credit_score(credit_score) if credit_score else {}

    # Determine debt-to-income status
    if debt_to_income <= 0.36:
        dti_status = "Acceptable"
    elif debt_to_income <= 0.50:
        dti_status = "Warning"
    else:
        dti_status = "High Risk"

    # Determine income-to-loan status
    if income_to_loan >= 5:
        itl_status = "Acceptable"
    elif income_to_loan >= 1:
        itl_status = "Warning"
    else:
        itl_status = "High Risk"

    # Calculate overall risk
    risk_level, risk_score = calculate_risk_level(
        debt_to_income, credit_score, income_to_loan, years_employed
    )

    # Identify risk factors
    risk_factors = identify_risk_factors(
        debt_to_income, credit_score, income_to_loan, years_employed, employment_status, existing_debt
    )

    # Build profile
    profile = ApplicantProfile(
        personal_info=PersonalProfile(
            name=applicant_name,
            email=applicant_email,
            phone=applicant_phone,
            application_id=application_id,
        ),
        income_profile=IncomeProfile(
            annual_income=annual_income,
            monthly_income=monthly_income,
            employment_status=employment_status,
            years_employed=years_employed,
            employment_stability_score=employment_info["stability_score"],
            employment_category=employment_info["status_category"],
        ),
        credit_profile=CreditProfile(
            credit_score=credit_score,
            credit_risk_level=credit_assessment.get("risk_level"),
            credit_risk_description=credit_assessment.get("description"),
            existing_debt=existing_debt,
            total_monthly_debt_obligation=total_monthly_debt,
            debt_to_income_ratio=round(debt_to_income, 3),
            debt_to_income_status=dti_status,
        ),
        loan_profile=LoanProfile(
            loan_amount=loan_amount,
            loan_type=loan_type,
            loan_term_months=loan_term_months,
            estimated_interest_rate=estimated_interest_rate,
            estimated_monthly_payment=round(monthly_payment, 2),
            income_to_loan_ratio=round(income_to_loan, 2),
            income_to_loan_status=itl_status,
        ),
        risk_score=round(risk_score, 1),
        risk_level=risk_level,
        risk_factors=risk_factors,
        profile_summary=_generate_summary(
            applicant_name, annual_income, credit_score, debt_to_income, income_to_loan, risk_level
        ),
    )

    return profile


def _generate_summary(
    name: str,
    annual_income: float,
    credit_score: Optional[int],
    debt_to_income: float,
    income_to_loan: float,
    risk_level: str,
) -> str:
    """Generate executive summary of the profile."""
    credit_info = f"credit score of {credit_score}" if credit_score else "no available credit history"

    return (
        f"{name} is applying for a loan with an annual income of ${annual_income:,.0f} and {credit_info}. "
        f"With a debt-to-income ratio of {debt_to_income:.1%} and income-to-loan ratio of {income_to_loan:.2f}x, "
        f"the applicant presents an overall {risk_level.lower()} risk profile."
    )
