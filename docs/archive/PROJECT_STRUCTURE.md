# Agentic Loan Approval System - Project Structure

## Overview
This project implements an intelligent loan approval system using agentic AI, with FastAPI backend, Streamlit frontend, LangGraph orchestration, and AWS Bedrock Claude Haiku for decision-making.

## Directory Structure

```
agentic-loan-approval-system/
│
├── backend/                           # FastAPI backend application
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # FastAPI application entry point
│       ├── agents/                    # LangGraph agent workflows
│       │   ├── __init__.py
│       │   ├── workflows/             # LangGraph state machines
│       │   │   ├── __init__.py
│       │   │   └── loan_approval_graph.py  # Main workflow definition
│       │   ├── tools/                 # Agent tools and utilities
│       │   │   ├── __init__.py
│       │   │   └── analysis_tools.py  # Financial analysis utilities
│       │   └── prompts/               # System prompts for agents
│       │       ├── __init__.py
│       │       └── system_prompts.py  # Agent system prompts
│       ├── api/                       # API layer
│       │   ├── __init__.py
│       │   └── endpoints/             # Route definitions
│       │       ├── __init__.py
│       │       └── loans.py           # Loan endpoints
│       ├── database/                  # Database configuration
│       │   ├── __init__.py
│       │   └── connection.py          # SQLAlchemy connection setup
│       ├── models/                    # SQLAlchemy ORM models
│       │   ├── __init__.py
│       │   ├── base.py                # Base model with mixins
│       │   └── loan_application.py    # Loan application model
│       ├── schemas/                   # Pydantic validation schemas
│       │   ├── __init__.py
│       │   └── loan.py                # Loan schemas
│       └── services/                  # Business logic layer
│           ├── __init__.py
│           └── loan_service.py        # Loan operations service
│
├── frontend/                          # Streamlit frontend application
│   ├── __init__.py
│   ├── main.py                        # Main Streamlit app
│   ├── pages/                         # Multi-page app pages
│   │   ├── __init__.py
│   │   ├── dashboard.py               # Dashboard page
│   │   └── submit_application.py      # Application submission
│   ├── components/                    # Reusable Streamlit components
│   │   ├── __init__.py
│   │   └── loan_form.py               # Loan application form
│   ├── utils/                         # Frontend utilities
│   │   ├── __init__.py
│   │   └── api_client.py              # API client wrapper
│   └── assets/                        # Static files
│       ├── images/
│       └── styles/
│
├── mcp/                               # FastMCP server
│   ├── __init__.py
│   ├── server.py                      # MCP server implementation
│   └── tools/                         # MCP tools
│       ├── __init__.py
│       └── loan_tools.py              # Loan analysis tools
│
├── config/                            # Configuration management
│   ├── __init__.py
│   └── settings.py                    # Application settings
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_loan_service.py          # Service layer tests
│   └── test_analysis_tools.py        # Tool function tests
│
├── logs/                              # Application logs (runtime)
│   └── .gitkeep
│
├── root configuration files
│   ├── README.md                      # Project documentation
│   ├── PROJECT_STRUCTURE.md           # This file
│   ├── requirements.txt               # Python dependencies
│   ├── pytest.ini                     # Pytest configuration
│   ├── .env.example                   # Environment variables template
│   └── .gitignore                     # Git ignore rules
```

## Module Descriptions

### Backend (`backend/app/`)

#### `main.py`
- FastAPI application factory
- CORS middleware configuration
- Route registration
- Database table creation

#### `agents/workflows/`
- **loan_approval_graph.py**: Defines LangGraph workflow with multiple agent nodes:
  - analyze_loan: Financial analysis
  - evaluate_credit: Credit assessment
  - compliance_check: Regulatory checks
  - final_decision: Approval decision

#### `agents/tools/`
- **analysis_tools.py**: Helper functions for financial calculations
  - `calculate_debt_to_income_ratio()`
  - `calculate_income_to_loan_ratio()`
  - `calculate_monthly_payment()`
  - `assess_employment_stability()`
  - `interpret_credit_score()`

#### `agents/prompts/`
- **system_prompts.py**: System prompts for different agent roles:
  - LOAN_ANALYZER_PROMPT
  - CREDIT_EVALUATOR_PROMPT
  - APPROVAL_DECISION_PROMPT
  - COMPLIANCE_CHECKER_PROMPT

#### `api/endpoints/`
- **loans.py**: RESTful endpoints for loan operations
  - POST `/loans/applications` - Create application
  - GET `/loans/applications/{id}` - Get application
  - PUT `/loans/applications/{id}` - Update application
  - POST `/loans/applications/{id}/process` - Trigger workflow
  - POST `/loans/applications/{id}/decision` - Submit decision
  - GET `/loans/applications` - List applications
  - GET `/loans/stats` - Get statistics

#### `database/`
- **connection.py**: SQLAlchemy engine, session, and dependency injection

#### `models/`
- **base.py**: Base model class with timestamp mixin
- **loan_application.py**: LoanApplication model with status enum

#### `schemas/`
- **loan.py**: Pydantic models for validation:
  - LoanApplicationCreate
  - LoanApplicationUpdate
  - LoanApplicationResponse
  - LoanApprovalDecision

#### `services/`
- **loan_service.py**: Business logic for loan operations
  - CRUD operations
  - Status management
  - Statistics queries

### Frontend (`frontend/`)

#### `main.py`
- Streamlit app configuration
- Navigation sidebar
- Page routing

#### `pages/`
- **dashboard.py**: Overview and metrics
- **submit_application.py**: Application submission interface

#### `components/`
- **loan_form.py**: Multi-column loan application form with all required fields

#### `utils/`
- **api_client.py**: HTTP client wrapper for backend API

### MCP (`mcp/`)

#### `server.py`
- FastMCP server implementation
- Tool registration and execution

#### `tools/loan_tools.py`
- Financial profile analysis
- Risk factor calculation
- Approval decision generation

### Configuration (`config/`)

#### `settings.py`
- Environment-based settings
- Database configuration
- AWS Bedrock configuration
- MCP server configuration

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Framework | FastAPI | REST API development |
| Frontend | Streamlit | Web UI for loan applications |
| Orchestration | LangGraph | Multi-agent workflow |
| LLM | AWS Bedrock Claude Haiku | Decision making |
| Database | MySQL + SQLAlchemy | Data persistence |
| MCP | FastMCP | Tool calling for agents |
| Testing | pytest | Unit and integration tests |

## Data Flow

1. **Application Submission**
   - User submits loan application via Streamlit frontend
   - Frontend calls FastAPI POST endpoint
   - LoanService creates database record

2. **Workflow Processing**
   - Loan application triggers LangGraph workflow
   - Multiple agents analyze different aspects:
     - Financial analysis
     - Credit evaluation
     - Compliance review
   - Each agent may use MCP tools for calculations

3. **Decision Making**
   - Final decision agent synthesizes all analysis
   - AWS Bedrock Claude Haiku makes approval decision
   - Decision stored in database

4. **Response Handling**
   - Decision returned to frontend
   - Status updated in database
   - User notified via Streamlit

## Database Schema

### LoanApplication Table
- `id`: Primary key
- `application_id`: Unique identifier
- `applicant_name`, `email`, `phone`: Applicant info
- `loan_amount`, `loan_type`, `loan_term_months`: Loan details
- `annual_income`, `employment_status`, `years_employed`: Employment info
- `credit_score`, `existing_debt`: Financial info
- `status`: Application status (PENDING, UNDER_REVIEW, APPROVED, REJECTED, WITHDRAWN)
- `agent_notes`, `approval_reason`, `rejection_reason`: Agent feedback
- `risk_score`, `approval_probability`: Decision metrics
- `created_at`, `updated_at`, `processed_at`: Timestamps

## Environment Variables

See `.env.example` for configuration:
- `DEBUG`: Enable debug mode
- `DATABASE_URL`: MySQL connection string
- `AWS_REGION`: AWS region for Bedrock
- `BEDROCK_MODEL_ID`: Claude model ID
- `API_HOST`, `API_PORT`: FastAPI settings
- `MCP_SERVER_HOST`, `MCP_SERVER_PORT`: MCP server settings

## Running the Application

### Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure with your settings
```

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
streamlit run main.py
```

### MCP Server
```bash
python mcp/server.py
```

### Tests
```bash
pytest -v
```

## Next Steps for Implementation

1. **Implement Agent Logic**
   - Populate workflow nodes with actual Bedrock calls
   - Integrate MCP tools

2. **Add Authentication**
   - API key or JWT authentication
   - Streamlit session management

3. **Implement Real-time Updates**
   - WebSocket support
   - Status polling

4. **Add Error Handling**
   - Comprehensive logging
   - Error recovery mechanisms

5. **Deployment Configuration**
   - Docker files
   - CI/CD pipelines
   - Cloud deployment scripts

6. **Frontend Enhancement**
   - Real-time dashboard
   - Application tracking
   - Agent analysis visualization
