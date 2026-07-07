"""API endpoints for system settings."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import logging
import boto3

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])


class BedrockConfig(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str


@router.post("/bedrock-config")
def configure_bedrock(config: BedrockConfig):
    """Configure AWS Bedrock credentials."""
    try:
        # Set environment variables
        os.environ["AWS_ACCESS_KEY_ID"] = config.aws_access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = config.aws_secret_access_key
        os.environ["AWS_DEFAULT_REGION"] = config.aws_region

        logger.info(f"Bedrock configuration updated for region {config.aws_region}")
        return {
            "status": "success",
            "message": "Bedrock credentials configured successfully",
            "region": config.aws_region,
        }
    except Exception as e:
        logger.error(f"Error configuring Bedrock: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bedrock-test")
def test_bedrock_connection(config: BedrockConfig):
    """Test AWS Bedrock connection."""
    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=config.aws_region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
        )

        # Simple test call to list models
        response = client.list_foundation_models()

        logger.info(f"Bedrock connection test successful for region {config.aws_region}")
        return {
            "status": "success",
            "message": "Connection test passed",
            "region": config.aws_region,
            "models_available": len(response.get("modelSummaries", [])),
        }
    except Exception as e:
        logger.error(f"Bedrock connection test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")
