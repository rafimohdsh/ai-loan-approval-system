"""Risk Agent - Calculates DTI, credit risk, and loan risk. Returns structured JSON."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DTIMetrics(BaseModel):
    """Debt-to-Income ratio metrics."""
    total_monthly_debt: float = Field(..., description="Total monthly debt obligations")
    monthly_income: float = Field(..., description="Gross monthly income")
    dti_ratio: float = Field(..., description="DTI ratio (0.0-1.0)")
    dti_percentage: float = Field(..., description="DTI as percentage")
    status: str = Field(..., description="DTI status: Acceptable, Warning, or Critical")


class CreditRiskAssessment(BaseModel):
    """Credit risk evaluation."""
    credit_score: Optional[int] = Field(None, description="Credit score (300-850)")
    risk_level: RiskLevel = Field(..., description="Risk level based on credit score")
    risk_score: float = Field(..., description="Credit risk score (0-100)")
    description: str = Field(..., description="Risk description")


class LoanRiskAssessment(BaseModel):
    """Loan-specific risk evaluation."""
    loan_amount: float = Field(..., description="Loan amount in dollars")
    annual_income: float = Field(..., description="Annual income in dollars")
    income_to_loan_ratio: float = Field(..., description="Income-to-loan ratio")
    risk_level: RiskLevel = Field(..., description="Loan risk level")
    risk_score: float = Field(..., description="Loan risk score (0-100)")
    description: str = Field(..., description="Risk description")


class RiskProfile(BaseModel):
    """Complete risk assessment."""
    dti_metrics: DTIMetrics = Field(..., description="DTI analysis")
    credit_risk: CreditRiskAssessment = Field(..., description="Credit risk assessment")
    loan_risk: LoanRiskAssessment = Field(..., description="Loan risk assessment")
    overall_risk_score: float = Field(..., description="Weighted overall risk (0-100)")
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")


def calculate_dti(total_monthly_debt: float, monthly_income: float) -> DTIMetrics:
    """
    Calculate debt-to-income ratio.

    Args:
        total_monthly_debt: Total monthly debt obligations
        monthly_income: Gross monthly income

    Returns:
        DTIMetrics with ratio and status
    """
    if monthly_income == 0:
        dti_ratio = 1.0
    else:
        dti_ratio = total_monthly_debt / monthly_income

    dti_percentage = dti_ratio * 100

    if dti_ratio <= 0.36:
        status = "Acceptable"
    elif dti_ratio <= 0.50:
        status = "Warning"
    else:
        status = "Critical"

    return DTIMetrics(
        total_monthly_debt=total_monthly_debt,
        monthly_income=monthly_income,
        dti_ratio=round(dti_ratio, 3),
        dti_percentage=round(dti_percentage, 1),
        status=status,
    )


def assess_credit_risk(credit_score: Optional[int]) -> CreditRiskAssessment:
    """
    Assess credit risk based on credit score.

    Args:
        credit_score: Credit score (300-850) or None

    Returns:
        CreditRiskAssessment with risk level and score
    """
    if credit_score is None:
        return CreditRiskAssessment(
            credit_score=None,
            risk_level=RiskLevel.HIGH,
            risk_score=60.0,
            description="No credit history available",
        )

    if credit_score >= 750:
        risk_level = RiskLevel.LOW
        risk_score = 10.0
        description = "Excellent credit - very low risk"
    elif credit_score >= 700:
        risk_level = RiskLevel.LOW
        risk_score = 20.0
        description = "Good credit - low risk"
    elif credit_score >= 650:
        risk_level = RiskLevel.MEDIUM
        risk_score = 40.0
        description = "Fair credit - moderate risk"
    elif credit_score >= 600:
        risk_level = RiskLevel.HIGH
        risk_score = 65.0
        description = "Poor credit - high risk"
    else:
        risk_level = RiskLevel.VERY_HIGH
        risk_score = 85.0
        description = "Very poor credit - very high risk"

    return CreditRiskAssessment(
        credit_score=credit_score,
        risk_level=risk_level,
        risk_score=risk_score,
        description=description,
    )


def assess_loan_risk(loan_amount: float, annual_income: float) -> LoanRiskAssessment:
    """
    Assess loan-specific risk based on income-to-loan ratio.

    Args:
        loan_amount: Requested loan amount in dollars
        annual_income: Annual income in dollars

    Returns:
        LoanRiskAssessment with risk level and score
    """
    if annual_income == 0:
        income_to_loan_ratio = 0.0
    else:
        income_to_loan_ratio = annual_income / loan_amount

    if income_to_loan_ratio >= 5.0:
        risk_level = RiskLevel.LOW
        risk_score = 10.0
        description = "Loan amount well within income limits"
    elif income_to_loan_ratio >= 3.0:
        risk_level = RiskLevel.LOW
        risk_score = 25.0
        description = "Loan amount acceptable relative to income"
    elif income_to_loan_ratio >= 1.5:
        risk_level = RiskLevel.MEDIUM
        risk_score = 45.0
        description = "Loan amount is significant relative to income"
    elif income_to_loan_ratio >= 1.0:
        risk_level = RiskLevel.HIGH
        risk_score = 65.0
        description = "Loan amount approaches annual income"
    else:
        risk_level = RiskLevel.VERY_HIGH
        risk_score = 85.0
        description = "Loan exceeds annual income"

    return LoanRiskAssessment(
        loan_amount=loan_amount,
        annual_income=annual_income,
        income_to_loan_ratio=round(income_to_loan_ratio, 2),
        risk_level=risk_level,
        risk_score=risk_score,
        description=description,
    )


def calculate_risk(
    total_monthly_debt: float,
    monthly_income: float,
    loan_amount: float,
    annual_income: float,
    credit_score: Optional[int] = None,
) -> RiskProfile:
    """
    Calculate comprehensive risk profile.

    Args:
        total_monthly_debt: Total monthly debt obligations
        monthly_income: Gross monthly income
        loan_amount: Requested loan amount
        annual_income: Annual income
        credit_score: Credit score (optional)

    Returns:
        RiskProfile with all risk assessments
    """
    dti = calculate_dti(total_monthly_debt, monthly_income)
    credit_risk = assess_credit_risk(credit_score)
    loan_risk = assess_loan_risk(loan_amount, annual_income)

    # Calculate weighted overall risk
    dti_score = _dti_to_risk_score(dti.dti_ratio)
    overall_risk_score = (dti_score * 0.40) + (credit_risk.risk_score * 0.35) + (loan_risk.risk_score * 0.25)
    overall_risk_score = round(overall_risk_score, 1)

    if overall_risk_score < 30:
        overall_risk_level = RiskLevel.LOW
    elif overall_risk_score < 50:
        overall_risk_level = RiskLevel.MEDIUM
    elif overall_risk_score < 75:
        overall_risk_level = RiskLevel.HIGH
    else:
        overall_risk_level = RiskLevel.VERY_HIGH

    return RiskProfile(
        dti_metrics=dti,
        credit_risk=credit_risk,
        loan_risk=loan_risk,
        overall_risk_score=overall_risk_score,
        overall_risk_level=overall_risk_level,
    )


def _dti_to_risk_score(dti_ratio: float) -> float:
    """Convert DTI ratio to risk score (0-100)."""
    if dti_ratio <= 0.36:
        return 15.0
    elif dti_ratio <= 0.50:
        return 40.0
    elif dti_ratio <= 0.60:
        return 65.0
    else:
        return 90.0
