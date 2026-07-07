# Database Connection Layer Setup Guide

## Overview

The database connection layer provides a complete, production-ready implementation using SQLAlchemy and MySQL with the following components:

- **SQLAlchemy Engine** - Connection pooling and management
- **SessionLocal** - Session factory for database operations
- **Base** - ORM base for all models (using existing model definitions)
- **Connection Utilities** - Diagnostics, health checks, lifecycle management

## Architecture

```
Application
    ↓
get_db() / get_db_sync() [Dependency Injection]
    ↓
SessionLocal [Session Factory]
    ↓
Engine [Connection Pool]
    ↓
MySQL Database
```

## Core Components

### 1. SQLAlchemy Engine (`engine` in connection.py)

```python
from backend.app.database import engine

# Configuration:
# - pool_size: 10 connections
# - max_overflow: 20 additional connections
# - pool_pre_ping: Tests connections before use
# - pool_recycle: Recycles connections after 3600 seconds
# - echo: SQL logging (enabled in DEBUG mode)
# - charset: utf8mb4 for full Unicode support
```

**Features:**
- Connection pooling for performance
- Automatic connection testing
- Connection recycling to prevent stale connections
- Debug SQL logging support

### 2. SessionLocal (Session Factory)

```python
from backend.app.database import SessionLocal

# Create a session
db = SessionLocal()

# Use it
user = db.query(User).first()

# Close it
db.close()
```

**Configuration:**
- `autocommit=False` - Manual transaction control
- `autoflush=False` - Explicit flush control
- `expire_on_commit=False` - Prevent expiration after commit

### 3. Base (ORM Base)

```python
from backend.app.database import Base

# All existing models use Base:
# - Customer (customers table)
# - LoanApplication (loan_applications table)
# - LoanDecision (loan_decisions table)
# - AuditLog (audit_logs table)
```

**Usage in models:**
```python
from backend.app.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    # ... field definitions
```

## Connection Methods

### FastAPI Dependency Injection

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db

app = FastAPI()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    # db is automatically provided and closed after request
    users = db.query(User).all()
    return users

@app.post("/users")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### Direct Session Creation

```python
from backend.app.database import SessionLocal

db = SessionLocal()
try:
    user = db.query(User).first()
    # ... do work
    db.commit()
finally:
    db.close()
```

### Context Manager (Recommended)

```python
from backend.app.database.manager import session_context

with session_context() as db:
    user = db.query(User).first()
    # Auto-commit on exit, auto-rollback on error
```

### Sync Session Getter

```python
from backend.app.database import get_db_sync

db = get_db_sync()
try:
    user = db.query(User).first()
finally:
    db.close()
```

## Initialization & Shutdown

### Automatic Initialization

```python
from backend.app.database.manager import initialize_database, shutdown_database
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
def startup():
    """Called when FastAPI app starts"""
    initialize_database()

@app.on_event("shutdown")
def shutdown():
    """Called when FastAPI app shuts down"""
    shutdown_database()
```

### Manual Initialization

```python
from backend.app.database import create_tables, verify_database_schema

# Create all tables
create_tables()

# Verify schema
if verify_database_schema():
    print("Schema is valid")
```

### CLI Initialization

```bash
# Test connection
python -m backend.app.database.cli test-connection

# Initialize database
python -m backend.app.database.cli init

# Verify schema
python -m backend.app.database.cli verify
```

## Configuration

### Environment Variables

```env
# .env file
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/loan_approval_db
DEBUG=False
LOG_LEVEL=INFO
```

**Components:**
- `mysql+pymysql://` - MySQL driver
- `user:password` - Database credentials
- `localhost:3306` - Database host and port
- `loan_approval_db` - Database name

### Connection Pool Settings

Located in `/backend/app/database/connection.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=Pool,
    pool_size=10,           # Initial pool size
    max_overflow=20,        # Additional connections when pool exhausted
    pool_pre_ping=True,     # Test connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=settings.DEBUG,    # Log SQL statements in debug mode
)
```

**Tuning Guide:**
- `pool_size=10` - Good for small to medium apps
- For high traffic: `pool_size=20, max_overflow=40`
- For low traffic: `pool_size=5, max_overflow=10`

## Health Checking & Diagnostics

### Quick Health Check

```python
from backend.app.database.diagnostics import DatabaseDiagnostics

# Test connection
if DatabaseDiagnostics.test_connection():
    print("✓ Database is accessible")

# Get health report
health = DatabaseDiagnostics.health_check()
print(health["status"])  # "healthy", "degraded", or "unhealthy"

# Print formatted report
DatabaseDiagnostics.print_health_report()
```

### Server Information

```python
from backend.app.database.diagnostics import DatabaseDiagnostics

info = DatabaseDiagnostics.get_server_info()
print(f"MySQL Version: {info['version']}")
print(f"Threads: {info['threads']}")
```

### Connection Pool Status

```python
from backend.app.database.diagnostics import DatabaseDiagnostics

status = DatabaseDiagnostics.get_connection_pool_status()
print(f"Pool size: {status['pool_size']}")
print(f"Active connections: {status['checked_in_connections']}")
print(f"Overflow connections: {status['overflow']}")
```

### Table Statistics

```python
from backend.app.database.diagnostics import DatabaseDiagnostics

stats = DatabaseDiagnostics.get_table_stats()
for table_name, table_stats in stats.items():
    print(f"{table_name}: {table_stats['row_count']} rows, {table_stats['size_mb']}MB")
```

### Full Diagnostic Report

```python
from backend.app.database.diagnostics import DatabaseDiagnostics

report = DatabaseDiagnostics.get_diagnostic_report()
# Contains: connection status, server info, pool status,
# database stats, table stats, and health check
```

## Database Manager

### Lifecycle Management

```python
from backend.app.database.manager import db_manager

# Initialize
db_manager.initialize()

# Health check
if db_manager.health_check():
    print("Healthy")

# Get diagnostics
diagnostics = db_manager.get_diagnostics()

# Shutdown
db_manager.shutdown()
```

### Using Manager in FastAPI

```python
from fastapi import FastAPI
from backend.app.database.manager import db_manager

app = FastAPI()

@app.on_event("startup")
async def startup():
    db_manager.initialize()

@app.on_event("shutdown")
async def shutdown():
    db_manager.shutdown()

@app.get("/health")
def health():
    return {"status": "healthy" if db_manager.health_check() else "unhealthy"}
```

## Error Handling

### Connection Errors

```python
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from backend.app.database import SessionLocal

try:
    db = SessionLocal()
    result = db.query(User).all()
except OperationalError:
    # Connection failed - database might be down
    logger.error("Database connection failed")
except SQLAlchemyError as e:
    # Other SQLAlchemy errors
    logger.error(f"Database error: {str(e)}")
finally:
    if db:
        db.close()
```

### Transaction Rollback

```python
from backend.app.database import SessionLocal

db = SessionLocal()
try:
    user = User(name="John")
    db.add(user)
    db.commit()
except Exception as e:
    db.rollback()  # Undo all changes
    logger.error(f"Transaction failed: {str(e)}")
finally:
    db.close()
```

## Common Patterns

### Create Operation

```python
from backend.app.database import get_db
from fastapi import Depends

@app.post("/customers")
def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(**customer_data.dict())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
```

### Read Operation

```python
@app.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
```

### Update Operation

```python
@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer_data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in customer_data.dict(exclude_unset=True).items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)
    return customer
```

### Delete Operation

```python
@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted"}
```

### List with Pagination

```python
@app.get("/customers")
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    total = db.query(Customer).count()
    return {"total": total, "customers": customers}
```

## Testing

### Test Database Connection

```bash
python -m backend.app.database.cli test-connection
```

### Check Health Status

```bash
python -m backend.app.database.cli status
```

### Get Database Statistics

```bash
python -m backend.app.database.cli stats
```

### Verify Schema

```bash
python -m backend.app.database.cli verify
```

## Performance Tips

1. **Use Connection Pooling** - Already configured (pool_size=10)
2. **Set pool_pre_ping=True** - Prevents "Lost connection" errors
3. **Use Pagination** - Always limit query results
4. **Create Indexes** - Already configured on all key fields
5. **Batch Operations** - Group inserts/updates when possible
6. **Monitor Pool Status** - Check connection pool health regularly

```python
# Example: Monitor pool health in production
from backend.app.database.diagnostics import DatabaseDiagnostics

pool_status = DatabaseDiagnostics.get_connection_pool_status()
if pool_status['checked_in_connections'] < 2:
    logger.warning("Low available connections in pool")
```

## Troubleshooting

### Connection Refused

```
Error: Failed to establish a connection to database
```

**Solutions:**
1. Verify MySQL server is running
2. Check DATABASE_URL in .env
3. Verify firewall allows connection
4. Test manually: `mysql -u user -p -h localhost`

### Too Many Connections

```
Error: SQLALCHEMY ERROR - Too many connections
```

**Solutions:**
1. Increase `max_overflow` setting
2. Check for connection leaks (db.close() not called)
3. Use context managers to auto-close
4. Reduce `pool_size` if testing with small DB

### Lost Connection

```
Error: MySQL Connection lost
```

**Solutions:**
1. Enable `pool_pre_ping=True` (already done)
2. Reduce `pool_recycle` timeout
3. Check MySQL `wait_timeout` setting

## File Locations

```
/backend/app/database/
├── connection.py      # SQLAlchemy engine, SessionLocal, get_db
├── engine.py          # Base, table creation, schema management
├── manager.py         # DatabaseManager, lifecycle management
├── diagnostics.py     # Health checks, diagnostics
├── base.py            # DB initialization utilities
└── __init__.py        # All exports
```

## Usage Summary

**FastAPI Integration:**
```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db

app = FastAPI()

@app.get("/data")
def get_data(db: Session = Depends(get_db)):
    # Use db for queries
    pass
```

**Direct Usage:**
```python
from backend.app.database import SessionLocal

db = SessionLocal()
try:
    # Your code here
    pass
finally:
    db.close()
```

**Context Manager:**
```python
from backend.app.database.manager import session_context

with session_context() as db:
    # Auto-closed and committed/rolled back
    pass
```

## Next Steps

1. ✅ Update .env with DATABASE_URL
2. ✅ Call `initialize_database()` on app startup
3. ✅ Use `get_db` in FastAPI routes
4. ✅ Check health with `db_manager.health_check()`
5. ✅ Monitor with diagnostics

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** 2024-07-02
