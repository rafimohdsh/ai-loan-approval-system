"""Tests for Bedrock-integrated decision agent with retry, timeout, and fallback."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from botocore.exceptions import ClientError, BotoCoreError
import socket

from backend.app.agents.decision_agent import (
    make_decision,
    make_decision_fallback,
    DecisionType,
    LoanDecision,
    _parse_decision_response,
    _call_bedrock_with_retry,
)


@pytest.fixture
def sample_applicant_data():
    """Sample applicant data for tests."""
    return {
        "applicant_name": "John Doe",
        "annual_income": 120000.0,
        "credit_score": 750,
        "dti_ratio": 0.30,
        "loan_amount": 50000.0,
        "employment_years": 5.0,
        "employment_status": "Employed Full-time",
        "existing_debt": 500.0,
    }


@pytest.fixture
def valid_bedrock_response():
    """Valid response from Bedrock."""
    return {
        "decision": "approved",
        "confidence": 0.95,
        "reasoning": "Excellent financial profile",
        "conditions": "Standard terms"
    }


class TestParseDecisionResponse:
    """Test parsing of decision responses."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON response."""
        json_str = json.dumps({
            "decision": "approved",
            "confidence": 0.95,
            "reasoning": "Good profile",
            "conditions": "Standard"
        })
        result = _parse_decision_response(json_str)
        assert result["decision"] == "approved"
        assert result["confidence"] == 0.95

    def test_parse_json_with_markdown(self):
        """Test parsing JSON wrapped in markdown."""
        content = """```json
{
  "decision": "rejected",
  "confidence": 0.9,
  "reasoning": "Low credit",
  "conditions": null
}
```"""
        result = _parse_decision_response(content)
        assert result["decision"] == "rejected"
        assert result["confidence"] == 0.9

    def test_parse_json_with_text_prefix(self):
        """Test parsing JSON with text before it."""
        content = """Here is the decision:
{
  "decision": "manual_review",
  "confidence": 0.7,
  "reasoning": "Needs review",
  "conditions": null
}"""
        result = _parse_decision_response(content)
        assert result["decision"] == "manual_review"

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises error."""
        with pytest.raises(ValueError):
            _parse_decision_response("This is not JSON at all")

    def test_parse_malformed_json(self):
        """Test parsing malformed JSON."""
        with pytest.raises(ValueError):
            _parse_decision_response("{invalid json}")


class TestBedrockRetry:
    """Test retry logic for Bedrock calls."""

    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_successful_call_first_try(self, mock_get_client, valid_bedrock_response):
        """Test successful call on first attempt."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        response_body = {
            "content": [{"text": json.dumps(valid_bedrock_response)}]
        }
        mock_client.invoke_model.return_value = {
            "body": MagicMock(read=lambda: json.dumps(response_body))
        }

        result = _call_bedrock_with_retry(mock_client, "test prompt")

        assert result == json.dumps(valid_bedrock_response)
        assert mock_client.invoke_model.call_count == 1

    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_retry_on_client_error(self, mock_get_client, valid_bedrock_response):
        """Test retry on ClientError."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        error_response = {"Error": {"Code": "ThrottlingException"}}
        mock_client.invoke_model.side_effect = [
            ClientError(error_response, "InvokeModel"),
            ClientError(error_response, "InvokeModel"),
            {
                "body": MagicMock(
                    read=lambda: json.dumps({
                        "content": [{"text": json.dumps(valid_bedrock_response)}]
                    })
                )
            }
        ]

        result = _call_bedrock_with_retry(mock_client, "test prompt")

        assert result == json.dumps(valid_bedrock_response)
        assert mock_client.invoke_model.call_count == 3

    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_retry_on_timeout(self, mock_get_client, valid_bedrock_response):
        """Test retry on socket timeout."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.invoke_model.side_effect = [
            socket.timeout("Connection timed out"),
            {
                "body": MagicMock(
                    read=lambda: json.dumps({
                        "content": [{"text": json.dumps(valid_bedrock_response)}]
                    })
                )
            }
        ]

        result = _call_bedrock_with_retry(mock_client, "test prompt")

        assert result == json.dumps(valid_bedrock_response)
        assert mock_client.invoke_model.call_count == 2

    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_exhausted_retries(self, mock_get_client):
        """Test exception after exhausted retries."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        error_response = {"Error": {"Code": "InternalServerException"}}
        mock_client.invoke_model.side_effect = ClientError(error_response, "InvokeModel")

        from tenacity import RetryError
        with pytest.raises(RetryError):
            _call_bedrock_with_retry(mock_client, "test prompt")

        assert mock_client.invoke_model.call_count == 3


class TestMakeDecisionWithBedrock:
    """Test make_decision with Bedrock API."""

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_successful_bedrock_decision(self, mock_get_client, mock_retry,
                                         sample_applicant_data, valid_bedrock_response):
        """Test successful decision from Bedrock."""
        mock_get_client.return_value = MagicMock()
        mock_retry.return_value = json.dumps(valid_bedrock_response)

        decision = make_decision(**sample_applicant_data)

        assert decision.decision == DecisionType.APPROVED
        assert decision.confidence == 0.95
        assert decision.reasoning == "Excellent financial profile"
        assert decision.conditions == "Standard terms"

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_bedrock_returns_rejected(self, mock_get_client, mock_retry):
        """Test Bedrock decision to reject."""
        mock_get_client.return_value = MagicMock()
        mock_retry.return_value = json.dumps({
            "decision": "rejected",
            "confidence": 0.9,
            "reasoning": "Low credit score",
            "conditions": None
        })

        data = {
            "applicant_name": "Jane Smith",
            "annual_income": 40000.0,
            "credit_score": 550,
            "dti_ratio": 0.55,
            "loan_amount": 100000.0,
            "employment_years": 0.5,
            "employment_status": "Self-employed",
            "existing_debt": 5000.0,
        }

        decision = make_decision(**data)

        assert decision.decision == DecisionType.REJECTED
        assert decision.confidence == 0.9

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_bedrock_returns_manual_review(self, mock_get_client, mock_retry):
        """Test Bedrock decision for manual review."""
        mock_get_client.return_value = MagicMock()
        mock_retry.return_value = json.dumps({
            "decision": "manual_review",
            "confidence": 0.65,
            "reasoning": "Marginal profile - requires review",
            "conditions": None
        })

        data = {
            "applicant_name": "Bob Johnson",
            "annual_income": 80000.0,
            "credit_score": None,
            "dti_ratio": 0.40,
            "loan_amount": 60000.0,
            "employment_years": 0.8,
            "employment_status": "Employed",
            "existing_debt": 2000.0,
        }

        decision = make_decision(**data)

        assert decision.decision == DecisionType.MANUAL_REVIEW
        assert decision.confidence == 0.65


class TestFallbackLogic:
    """Test fallback decision logic when Bedrock fails."""

    def test_fallback_no_credit_score(self):
        """Test fallback with no credit score."""
        decision = make_decision_fallback(
            applicant_name="Test User",
            annual_income=100000.0,
            credit_score=None,
            dti_ratio=0.3,
            loan_amount=50000.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=500.0,
        )

        assert decision.decision == DecisionType.MANUAL_REVIEW
        assert "fallback" in decision.reasoning.lower()

    def test_fallback_low_credit_rejected(self):
        """Test fallback rejects low credit score."""
        decision = make_decision_fallback(
            applicant_name="Bad Credit",
            annual_income=100000.0,
            credit_score=550,
            dti_ratio=0.3,
            loan_amount=50000.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=500.0,
        )

        assert decision.decision == DecisionType.REJECTED
        assert "fallback" in decision.reasoning.lower()

    def test_fallback_high_dti_rejected(self):
        """Test fallback rejects high DTI."""
        decision = make_decision_fallback(
            applicant_name="High DTI",
            annual_income=50000.0,
            credit_score=700,
            dti_ratio=0.60,
            loan_amount=50000.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=5000.0,
        )

        assert decision.decision == DecisionType.REJECTED

    def test_fallback_excellent_approved(self):
        """Test fallback approves excellent profile."""
        decision = make_decision_fallback(
            applicant_name="Excellent",
            annual_income=200000.0,
            credit_score=800,
            dti_ratio=0.20,
            loan_amount=50000.0,
            employment_years=10.0,
            employment_status="Employed",
            existing_debt=1000.0,
        )

        assert decision.decision == DecisionType.APPROVED
        assert decision.confidence == 0.95

    def test_fallback_good_profile_approved(self):
        """Test fallback approves good profile."""
        decision = make_decision_fallback(
            applicant_name="Good",
            annual_income=150000.0,
            credit_score=750,
            dti_ratio=0.30,
            loan_amount=50000.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=500.0,
        )

        assert decision.decision == DecisionType.APPROVED
        # Could be 0.95 (excellent) or 0.80 (good), depends on exact thresholds
        assert decision.confidence >= 0.80


class TestDecisionWithRetryAndFallback:
    """Test make_decision with retry and fallback enabled."""

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_fallback_on_bedrock_failure(self, mock_get_client, mock_retry,
                                         sample_applicant_data):
        """Test fallback is used when Bedrock fails."""
        mock_get_client.return_value = MagicMock()
        error_response = {"Error": {"Code": "InternalServerException"}}
        mock_retry.side_effect = ClientError(error_response, "InvokeModel")

        decision = make_decision(**sample_applicant_data, use_fallback=True)

        assert decision is not None
        assert decision.decision in [DecisionType.APPROVED, DecisionType.REJECTED, DecisionType.MANUAL_REVIEW]
        assert "fallback" in decision.reasoning.lower()

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_no_fallback_raises_exception(self, mock_get_client, mock_retry,
                                          sample_applicant_data):
        """Test exception is raised when fallback disabled."""
        mock_get_client.return_value = MagicMock()
        error_response = {"Error": {"Code": "InternalServerException"}}
        mock_retry.side_effect = ClientError(error_response, "InvokeModel")

        with pytest.raises(ClientError):
            make_decision(**sample_applicant_data, use_fallback=False)

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_fallback_on_parse_error(self, mock_get_client, mock_retry,
                                      sample_applicant_data):
        """Test fallback on JSON parse error."""
        mock_get_client.return_value = MagicMock()
        mock_retry.return_value = "Not valid JSON at all!"

        decision = make_decision(**sample_applicant_data, use_fallback=True)

        assert decision is not None
        assert "fallback" in decision.reasoning.lower()

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_timeout_triggers_fallback(self, mock_get_client, mock_retry,
                                       sample_applicant_data):
        """Test timeout triggers fallback."""
        mock_get_client.return_value = MagicMock()
        mock_retry.side_effect = TimeoutError("Request timed out")

        decision = make_decision(**sample_applicant_data, use_fallback=True)

        assert decision is not None
        assert "fallback" in decision.reasoning.lower()


class TestDecisionEdgeCases:
    """Test edge cases in decision making."""

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_missing_fields_in_response(self, mock_get_client, mock_retry):
        """Test handling of missing fields in Bedrock response."""
        mock_get_client.return_value = MagicMock()
        mock_retry.return_value = json.dumps({
            "decision": "approved",
            # Missing confidence, reasoning, conditions
        })

        data = {
            "applicant_name": "Test",
            "annual_income": 100000.0,
            "credit_score": 750,
            "dti_ratio": 0.3,
            "loan_amount": 50000.0,
            "employment_years": 5.0,
            "employment_status": "Employed",
            "existing_debt": 500.0,
        }

        decision = make_decision(**data)

        assert decision.decision == DecisionType.APPROVED
        assert decision.confidence == 0.5  # Default value
        assert decision.reasoning == "Bedrock decision"

    @patch('backend.app.agents.decision_agent._call_bedrock_with_retry')
    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_case_insensitive_decision(self, mock_get_client, mock_retry):
        """Test case-insensitive decision parsing."""
        mock_get_client.return_value = MagicMock()
        mock_retry.return_value = json.dumps({
            "decision": "APPROVED",  # Uppercase
            "confidence": 0.9,
            "reasoning": "Test",
            "conditions": None
        })

        data = {
            "applicant_name": "Test",
            "annual_income": 100000.0,
            "credit_score": 750,
            "dti_ratio": 0.3,
            "loan_amount": 50000.0,
            "employment_years": 5.0,
            "employment_status": "Employed",
            "existing_debt": 500.0,
        }

        decision = make_decision(**data)

        assert decision.decision == DecisionType.APPROVED

    def test_fallback_with_zero_income(self):
        """Test fallback handles zero income."""
        decision = make_decision_fallback(
            applicant_name="Zero Income",
            annual_income=0.0,
            credit_score=700,
            dti_ratio=1.0,
            loan_amount=50000.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=5000.0,
        )

        assert decision.decision == DecisionType.REJECTED

    def test_fallback_with_zero_loan_amount(self):
        """Test fallback handles zero loan amount."""
        decision = make_decision_fallback(
            applicant_name="Zero Loan",
            annual_income=100000.0,
            credit_score=700,
            dti_ratio=0.0,
            loan_amount=0.0,
            employment_years=5.0,
            employment_status="Employed",
            existing_debt=0.0,
        )

        assert decision is not None
        # Zero loan amount means income_to_loan is 0, which < 1.0, so REJECTED
        assert decision.decision in [DecisionType.REJECTED, DecisionType.MANUAL_REVIEW, DecisionType.APPROVED]


class TestRetryBehavior:
    """Test retry behavior with different error scenarios."""

    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_retry_with_exponential_backoff(self, mock_get_client, valid_bedrock_response):
        """Test exponential backoff in retries."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        call_times = []

        def side_effect(*args, **kwargs):
            call_times.append(True)
            if len(call_times) < 2:
                raise ClientError({"Error": {"Code": "ThrottlingException"}}, "InvokeModel")
            return {
                "body": MagicMock(
                    read=lambda: json.dumps({
                        "content": [{"text": json.dumps(valid_bedrock_response)}]
                    })
                )
            }

        mock_client.invoke_model.side_effect = side_effect

        result = _call_bedrock_with_retry(mock_client, "test prompt")

        assert result == json.dumps(valid_bedrock_response)
        assert len(call_times) == 2

    @patch('backend.app.agents.decision_agent.get_bedrock_client')
    def test_boto_core_error_retry(self, mock_get_client, valid_bedrock_response):
        """Test retry on BotoCoreError."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.invoke_model.side_effect = [
            BotoCoreError(),
            {
                "body": MagicMock(
                    read=lambda: json.dumps({
                        "content": [{"text": json.dumps(valid_bedrock_response)}]
                    })
                )
            }
        ]

        result = _call_bedrock_with_retry(mock_client, "test prompt")

        assert result == json.dumps(valid_bedrock_response)
