#!/bin/bash

# Agentic Loan Approval System - Startup Script

echo "🏦 Agentic Loan Approval System"
echo "================================"
echo ""

# Check Python
echo "✓ Checking Python..."
python3 --version

# Check if requirements installed
echo "✓ Checking dependencies..."
pip list | grep -q streamlit && pip list | grep -q fastapi && echo "✓ Dependencies found" || echo "⚠ Installing dependencies..."

# Create environment variables if not exists
if [ ! -f .env ]; then
    echo "✓ Creating .env file..."
    cat > .env << EOF
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/loan_approval_db
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
API_BASE_URL=http://localhost:8000
EOF
    echo "✓ .env file created (update with your settings)"
fi

echo ""
echo "To run the system:"
echo ""
echo "Terminal 1 - Backend (FastAPI):"
echo "  cd backend && python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "Terminal 2 - Frontend (Streamlit):"
echo "  streamlit run frontend/app.py"
echo ""
echo "Then open: http://localhost:8501"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
