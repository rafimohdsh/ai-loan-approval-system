import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Application
    APP_NAME: str = "Agentic Loan Approval System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    # FastAPI
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:Tek%4012345@localhost:3306/loan_approval_db"
    )

    # AWS Bedrock
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0")

    # MCP
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", 8001))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")

    # Agent Configuration
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", 300))
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", 10))

    # Decision Timing Configuration (in seconds)
    DECISION_PENDING_DURATION: int = int(os.getenv("DECISION_PENDING_DURATION", 300))  # 5 minutes
    DECISION_REVIEW_DURATION: int = int(os.getenv("DECISION_REVIEW_DURATION", 600))    # 10 minutes (5 + 5)
    DECISION_FINAL_DURATION: int = int(os.getenv("DECISION_FINAL_DURATION", 600))      # 10 minutes total


settings = Settings()
