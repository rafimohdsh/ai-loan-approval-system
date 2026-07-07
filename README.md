# Agentic Loan Approval System

An intelligent, multi-agent loan approval system leveraging LangGraph for workflow orchestration and AWS Bedrock Claude Haiku for decision-making.

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Orchestration**: LangGraph
- **MCP**: FastMCP
- **LLM**: AWS Bedrock Claude Haiku
- **Database**: MySQL with SQLAlchemy ORM
- **Testing**: pytest

## Project Structure

```
agentic-loan-approval-system/
├── backend/
│   └── app/
│       ├── agents/           # LangGraph agents & workflows
│       │   ├── workflows/    # Graph definitions and state management
│       │   ├── tools/        # Agent tools and utilities
│       │   └── prompts/      # Prompt templates for agents
│       ├── api/              # FastAPI endpoints
│       │   └── endpoints/    # Route definitions
│       ├── database/         # Database configuration & connections
│       ├── models/           # SQLAlchemy models
│       ├── schemas/          # Pydantic schemas for validation
│       └── services/         # Business logic services
├── frontend/
│   ├── pages/                # Streamlit pages
│   ├── components/           # Reusable Streamlit components
│   ├── utils/                # Frontend utilities
│   └── assets/               # Static files
│       ├── images/
│       └── styles/
├── mcp/
│   └── tools/                # FastMCP server tools
├── config/                   # Configuration files
├── tests/                    # Test suite
└── logs/                     # Application logs
```

## Setup & Installation

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- AWS credentials configured
- Poetry or pip for dependency management

### Environment Setup
```bash
cd agentic-loan-approval-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database Setup
```bash
# Configure MySQL connection in config/settings.py
# Run migrations (when available)
```

### AWS Configuration
```bash
# Set up AWS credentials for Bedrock access
aws configure
export AWS_REGION=us-east-1  # Adjust to your region
```

## Running the Application

### Backend (FastAPI)
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend (Streamlit)
```bash
cd frontend
streamlit run main.py
```

## Project Features

- **Loan Application Processing**: Multi-agent workflow for evaluating loan applications
- **Decision Agents**: Specialized agents for credit analysis, risk assessment, and approval logic
- **MCP Integration**: FastMCP server for secure agent-tool communication
- **Real-time Updates**: WebSocket support for live approval status
- **Database Persistence**: Loan application history and audit logs

## Development

### Adding New Agents
1. Create workflow definition in `backend/app/agents/workflows/`
2. Define tools in `backend/app/agents/tools/`
3. Add prompts in `backend/app/agents/prompts/`
4. Register in agent orchestrator

### Adding New Endpoints
1. Create route file in `backend/app/api/endpoints/`
2. Register route in main FastAPI app
3. Add corresponding Pydantic schema in `backend/app/schemas/`

### Testing
```bash
pytest tests/ -v
```

## Configuration

Key configuration files:
- `config/settings.py` - Application settings
- `config/database.py` - Database configuration
- `config/aws.py` - AWS Bedrock configuration

## License

MIT
