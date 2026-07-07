"""Decision Agent - Uses AWS Bedrock Claude to make loan decisions. Returns APPROVED/REJECTED/MANUAL_REVIEW."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import boto3
import logging
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from botocore.exceptions import ClientError, BotoCoreError
import socket

logger = logging.getLogger(__name__)


class DecisionType(str, Enum):
    """Loan decision types."""
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class LoanDecision(BaseModel):
    """Loan decision output."""
    decision: DecisionType = Field(..., description="Final decision")
    confidence: float = Field(..., description="Confidence level (0.0-1.0)")
    reasoning: str = Field(..., description="Explanation for decision")
    conditions: Optional[str] = Field(None, description="Conditions if approved")


def get_bedrock_client(timeout: int = 30):
    """Get AWS Bedrock client with timeout configuration."""
    
    config = boto3.session.Config(
        connect_timeout=timeout,
        read_timeout=timeout,
        retries={'max_attempts': 0}
    )
    return boto3.client("bedrock-runtime", region_name="us-east-1", config=config)


def _parse_decision_response(content: str) -> dict:
    """Parse JSON decision response from Claude.

    Args:
        content: Response text from Claude

    Returns:
        Parsed decision dictionary

    Raises:
        ValueError: If JSON cannot be parsed
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        raise ValueError("Could not parse decision response - no valid JSON found")


def _should_retry(exception: Exception) -> bool:
    """Determine if exception should trigger retry.

    Args:
        exception: Exception to evaluate

    Returns:
        True if should retry, False otherwise
    """
    if isinstance(exception, (ClientError, BotoCoreError)):
        return True
    if isinstance(exception, socket.timeout):
        return True
    if isinstance(exception, TimeoutError):
        return True
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ClientError, BotoCoreError, TimeoutError, socket.timeout)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def _call_bedrock_with_retry(
    client,
    prompt: str,
    timeout: int = 30,
) -> str:
    """Call Bedrock Claude with automatic retry logic.

    Args:
        client: Bedrock runtime client
        prompt: Decision prompt
        timeout: Request timeout in seconds

    Returns:
        Response text from Claude

    Raises:
        Exception: After max retries exhausted
    """
    try:
        response = client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-06-01",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]
    except (ClientError, BotoCoreError) as e:
        logger.warning(f"Bedrock API error (will retry): {str(e)}")
        raise
    except socket.timeout as e:
        logger.warning(f"Bedrock timeout (will retry): {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling Bedrock: {str(e)}")
        raise


def make_decision(
    applicant_name: str,
    annual_income: float,
    credit_score: Optional[int],
    dti_ratio: float,
    loan_amount: float,
    employment_years: float,
    employment_status: str,
    existing_debt: float,
    use_fallback: bool = True,
) -> LoanDecision:
    """
    Use Bedrock Claude to make loan decision with retry and fallback.

    Args:
        applicant_name: Applicant name
        annual_income: Annual income
        credit_score: Credit score
        dti_ratio: Debt-to-income ratio
        loan_amount: Loan amount requested
        employment_years: Years employed
        employment_status: Employment status
        existing_debt: Existing monthly debt
        use_fallback: Use fallback logic if Bedrock fails

    Returns:
        LoanDecision with decision, confidence, reasoning
    """
    prompt = f"""You are a loan officer. Make a decision on this loan application.

Applicant: {applicant_name}
Annual Income: ${annual_income:,.0f}
Monthly Income: ${annual_income/12:,.0f}
Credit Score: {credit_score if credit_score else 'Not available'}
DTI Ratio: {dti_ratio:.1%}
Loan Amount: ${loan_amount:,.0f}
Employment: {employment_years} years, {employment_status}
Existing Monthly Debt: ${existing_debt:,.0f}

Respond ONLY in this JSON format (no markdown, just raw JSON):
{{
  "decision": "approved" or "rejected" or "manual_review",
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation",
  "conditions": "conditions if approved, or null"
}}

Make decision based on:
1. Credit score (if available)
2. DTI ratio (ideal ≤36%, acceptable ≤43%)
3. Income-to-loan ratio
4. Employment stability
5. Overall risk profile

Use manual_review if borderline or missing critical info."""

    try:
        client = get_bedrock_client(timeout=30)
        content = _call_bedrock_with_retry(client, prompt, timeout=30)
        logger.info(f"Successfully received decision from Bedrock for {applicant_name}")
    except Exception as e:
        logger.error(f"Failed to get decision from Bedrock after retries: {str(e)}")
        if use_fallback:
            logger.info(f"Using fallback decision logic for {applicant_name}")
            return make_decision_fallback(
                applicant_name,
                annual_income,
                credit_score,
                dti_ratio,
                loan_amount,
                employment_years,
                employment_status,
                existing_debt,
            )
        else:
            raise

    try:
        decision_data = _parse_decision_response(content)
    except ValueError as e:
        logger.error(f"Failed to parse decision response: {str(e)}")
        if use_fallback:
            logger.info(f"Using fallback decision logic due to parse error")
            return make_decision_fallback(
                applicant_name,
                annual_income,
                credit_score,
                dti_ratio,
                loan_amount,
                employment_years,
                employment_status,
                existing_debt,
            )
        else:
            raise

    decision_str = decision_data.get("decision", "manual_review").lower()
    if decision_str == "approved":
        decision = DecisionType.APPROVED
    elif decision_str == "rejected":
        decision = DecisionType.REJECTED
    else:
        decision = DecisionType.MANUAL_REVIEW

    return LoanDecision(
        decision=decision,
        confidence=float(decision_data.get("confidence", 0.5)),
        reasoning=decision_data.get("reasoning", "Bedrock decision"),
        conditions=decision_data.get("conditions"),
    )


def make_decision_fallback(
    applicant_name: str,
    annual_income: float,
    credit_score: Optional[int],
    dti_ratio: float,
    loan_amount: float,
    employment_years: float,
    employment_status: str,
    existing_debt: float,
) -> LoanDecision:
    """
    Fallback decision logic when Bedrock is unavailable.

    Returns APPROVED, REJECTED, or MANUAL_REVIEW based on rule-based engine.
    """
    logger.info(f"Using fallback decision logic for {applicant_name}")

    if credit_score is None:
        return LoanDecision(
            decision=DecisionType.MANUAL_REVIEW,
            confidence=0.6,
            reasoning="No credit history - requires manual review (fallback)",
            conditions=None,
        )

    if credit_score < 600:
        return LoanDecision(
            decision=DecisionType.REJECTED,
            confidence=0.95,
            reasoning="Credit score below acceptable threshold (fallback)",
            conditions=None,
        )

    if dti_ratio > 0.50:
        return LoanDecision(
            decision=DecisionType.REJECTED,
            confidence=0.9,
            reasoning="Debt-to-income ratio exceeds acceptable limit (fallback)",
            conditions=None,
        )

    income_to_loan = annual_income / loan_amount if loan_amount > 0 else 0
    if income_to_loan < 1.0:
        return LoanDecision(
            decision=DecisionType.REJECTED,
            confidence=0.85,
            reasoning="Loan amount exceeds annual income (fallback)",
            conditions=None,
        )

    if employment_years < 1:
        return LoanDecision(
            decision=DecisionType.MANUAL_REVIEW,
            confidence=0.7,
            reasoning="Employment tenure less than 1 year - requires review (fallback)",
            conditions=None,
        )

    if credit_score < 650 or dti_ratio > 0.43:
        return LoanDecision(
            decision=DecisionType.MANUAL_REVIEW,
            confidence=0.75,
            reasoning="Multiple risk factors - requires manual review (fallback)",
            conditions=None,
        )

    if credit_score >= 700 and dti_ratio <= 0.36 and income_to_loan >= 3.0:
        return LoanDecision(
            decision=DecisionType.APPROVED,
            confidence=0.95,
            reasoning="Strong financial profile (fallback)",
            conditions="Standard loan terms apply",
        )

    return LoanDecision(
        decision=DecisionType.APPROVED,
        confidence=0.80,
        reasoning="Application meets loan approval criteria (fallback)",
        conditions="Standard loan terms apply",
    )


def make_decision_mock(
    applicant_name: str,
    annual_income: float,
    credit_score: Optional[int],
    dti_ratio: float,
    loan_amount: float,
    employment_years: float,
    employment_status: str,
    existing_debt: float,
) -> LoanDecision:
    """
    Mock decision logic for testing (no Bedrock required).

    Returns APPROVED, REJECTED, or MANUAL_REVIEW based on simple rules.
    """
    return make_decision_fallback(
        applicant_name,
        annual_income,
        credit_score,
        dti_ratio,
        loan_amount,
        employment_years,
        employment_status,
        existing_debt,
    )
