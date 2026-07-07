# Database Connection Layer - Quick Start

## 30-Second Setup

### 1. Configure .env
```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/loan_approval_db
DEBUG=False
```

### 2. Initialize Database
```python
from backend.app.database.manager import initialize_database

initialize_database()
```

### 3. Use in FastAPI
```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db

app = FastAPI()

@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items
```

## Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **Engine** | `connection.py` | Connection pooling (pool_size=10) |
| **SessionLocal** | `connection.py` | Session factory |
| **Base** | `engine.py` | ORM base for models |
| **get_db()** | `connection.py` | FastAPI dependency |
| **DatabaseManager** | `manager.py` | Lifecycle management |
| **Diagnostics** | `diagnostics.py` | Health checks |

## Import Paths

```python
# Connection & Session
from backend.app.database import engine, SessionLocal, get_db, get_db_sync

# Base (ORM)
from backend.app.database import Base

# Tables & Schema
from backend.app.database import create_tables, drop_tables, verify_database_schema

# Manager
from backend.app.database.manager import (
    initialize_database,
    shutdown_database,
    is_database_healthy,
    session_context
)

# Diagnostics
from backend.app.database.diagnostics import DatabaseDiagnostics
```

## Common Usage Patterns

### FastAPI Dependency (Recommended)
```python
@app.get("/customers")
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()
```

### Context Manager
```python
from backend.app.database.manager import session_context

with session_context() as db:
    customer = db.query(Customer).first()
```

### Direct Session
```python
from backend.app.database import SessionLocal

db = SessionLocal()
try:
    customer = db.query(Customer).first()
finally:
    db.close()
```

### Async Session
```python
from backend.app.database.manager import db_manager

async with db_manager.async_session() as db:
    customer = db.query(Customer).first()
```

## Initialization in FastAPI

```python
from fastapi import FastAPI
from backend.app.database.manager import initialize_database, shutdown_database

app = FastAPI()

@app.on_event("startup")
def startup():
    initialize_database()

@app.on_event("shutdown")
def shutdown():
    shutdown_database()
```

## Health Checks

```python
# Test connection
from backend.app.database.diagnostics import DatabaseDiagnostics
if DatabaseDiagnostics.test_connection():
    print("✓ Connected")

# Full health check
health = DatabaseDiagnostics.health_check()
print(health["status"])

# Print report
DatabaseDiagnostics.print_health_report()
```

## Database Manager Usage

```python
from backend.app.database.manager import db_manager

# Initialize
db_manager.initialize()

# Check health
db_manager.health_check()

# Get diagnostics
db_manager.get_diagnostics()

# Shutdown
db_manager.shutdown()
```

## CLI Commands

```bash
# Test connection
python -m backend.app.database.cli test-connection

# Initialize
python -m backend.app.database.cli init

# Health check
python -m backend.app.database.cli status

# Verify schema
python -m backend.app.database.cli verify

# Get statistics
python -m backend.app.database.cli stats
```

## Connection Pool Configuration

Default settings (in `connection.py`):
- **pool_size:** 10 connections
- **max_overflow:** 20 additional connections
- **pool_pre_ping:** True (tests connections)
- **pool_recycle:** 3600 seconds (1 hour)

Adjust in `connection.py` for your needs:
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,      # More connections for high traffic
    max_overflow=40,   # More overflow connections
    pool_recycle=1800, # Recycle every 30 minutes
)
```

## Error Handling

```python
from sqlalchemy.exc import SQLAlchemyError, OperationalError

try:
    db = SessionLocal()
    result = db.query(User).all()
    db.commit()
except OperationalError:
    logger.error("Connection failed")
except SQLAlchemyError as e:
    db.rollback()
    logger.error(f"Database error: {e}")
finally:
    db.close()
```

## Model Usage (No Changes Needed)

All models already use the Base from the connection layer:

```python
from backend.app.database import Base

# Models automatically use this Base:
# - Customer (customers table)
# - LoanApplication (loan_applications table)
# - LoanDecision (loan_decisions table)
# - AuditLog (audit_logs table)
```

## Files Reference

- **connection.py** - Engine, SessionLocal, get_db
- **engine.py** - Base, create_tables, verify_database_schema
- **manager.py** - DatabaseManager, lifecycle
- **diagnostics.py** - Health checks, diagnostics
- **cli.py** - Command-line interface

## Environment Setup

```env
# .env file
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/loan_approval_db
DEBUG=False
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Troubleshooting

**Connection Refused:**
```bash
# Test MySQL is running
mysql -u user -p -h localhost

# Check DATABASE_URL format
# Should be: mysql+pymysql://user:pass@host:port/db
```

**Too Many Connections:**
```python
# Check pool status
from backend.app.database.diagnostics import DatabaseDiagnostics
status = DatabaseDiagnostics.get_connection_pool_status()
print(status)  # Check 'checked_in_connections'
```

**Lost Connection:**
```python
# pool_pre_ping is enabled by default
# It automatically tests connections before use
```

## Next Steps

1. ✅ Update .env with DATABASE_URL
2. ✅ Call `initialize_database()` in FastAPI startup
3. ✅ Use `get_db` in route handlers
4. ✅ Run `python -m backend.app.database.cli status` to verify

---

**Quick Links:**
- Full Guide: [CONNECTIONS_SETUP_GUIDE.md](CONNECTIONS_SETUP_GUIDE.md)
- Database Guide: [DATABASE_GUIDE.md](DATABASE_GUIDE.md)
- Examples: [backend/app/database/example_usage.py](backend/app/database/example_usage.py)

**Version:** 1.0.0 | **Status:** ✅ Production Ready
