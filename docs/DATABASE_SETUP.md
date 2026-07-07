# Database Setup Guide

## MySQL Installation

### macOS (Homebrew)
```bash
brew install mysql
brew services start mysql
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

### Windows
Download and install from: https://dev.mysql.com/downloads/mysql/

## Database Creation

### Option 1: Using Command Line

```bash
# Connect to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE loan_approval_db;
CREATE USER 'loan_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON loan_approval_db.* TO 'loan_user'@'localhost';
FLUSH PRIVILEGES;

# Verify
SHOW DATABASES;
EXIT;
```

### Option 2: Using Docker

```bash
# Run MySQL container
docker run --name loan-mysql \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_DATABASE=loan_approval_db \
  -e MYSQL_USER=loan_user \
  -e MYSQL_PASSWORD=secure_password \
  -p 3306:3306 \
  -d mysql:8.0

# Verify container is running
docker ps | grep loan-mysql
```

## Configuration

Update `.env` file with database connection:

```env
# For local MySQL
DATABASE_URL=mysql+pymysql://loan_user:secure_password@localhost:3306/loan_approval_db

# For Docker MySQL
DATABASE_URL=mysql+pymysql://loan_user:secure_password@127.0.0.1:3306/loan_approval_db
```

## Table Creation

Tables are automatically created when the FastAPI app starts (via `Base.metadata.create_all()`).

To manually create tables:

```python
from backend.app.database import engine
from backend.app.models import Base

# Create all tables
Base.metadata.create_all(bind=engine)
```

Or run:
```bash
cd backend
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

## Database Schema

### LoanApplication Table

```sql
CREATE TABLE IF NOT EXISTS loan_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_id VARCHAR(50) UNIQUE NOT NULL,
    applicant_name VARCHAR(255) NOT NULL,
    applicant_email VARCHAR(255) NOT NULL,
    applicant_phone VARCHAR(20) NOT NULL,
    
    loan_amount FLOAT NOT NULL,
    loan_type VARCHAR(50) NOT NULL,
    loan_term_months INT NOT NULL,
    
    annual_income FLOAT NOT NULL,
    employment_status VARCHAR(50) NOT NULL,
    years_employed FLOAT NOT NULL,
    
    credit_score INT,
    existing_debt FLOAT DEFAULT 0.0,
    
    status ENUM('pending', 'under_review', 'approved', 'rejected', 'withdrawn') 
        DEFAULT 'pending' NOT NULL,
    
    agent_notes TEXT,
    approval_reason TEXT,
    rejection_reason TEXT,
    
    risk_score FLOAT,
    approval_probability FLOAT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    processed_at DATETIME,
    
    INDEX idx_application_id (application_id),
    INDEX idx_email (applicant_email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

## Verification

### Check Connection
```bash
python
```

```python
from backend.app.database import SessionLocal
db = SessionLocal()
print("Database connection successful!")
db.close()
```

### Check Tables
```bash
mysql -u loan_user -p loan_approval_db

SHOW TABLES;
DESCRIBE loan_applications;
```

## Backup & Restore

### Backup
```bash
mysqldump -u loan_user -p loan_approval_db > backup_loan_db.sql
```

### Restore
```bash
mysql -u loan_user -p loan_approval_db < backup_loan_db.sql
```

## Troubleshooting

### Connection Refused
```
Error: Connection refused
Solution: 
- Ensure MySQL is running: mysql.server start (macOS) or sudo service mysql start (Linux)
- Check port 3306 is accessible: telnet localhost 3306
```

### Access Denied
```
Error: Access denied for user 'loan_user'@'localhost'
Solution:
- Verify credentials in .env
- Recreate user: mysql -u root -p < user_setup.sql
```

### Database Doesn't Exist
```
Error: Unknown database 'loan_approval_db'
Solution:
- Create database: mysql -u root -p -e "CREATE DATABASE loan_approval_db;"
- Verify: mysql -u root -p -e "SHOW DATABASES;"
```

## Performance Optimization

### Add Indexes (if not using SQLAlchemy auto-create)
```sql
CREATE INDEX idx_status ON loan_applications(status);
CREATE INDEX idx_application_id ON loan_applications(application_id);
CREATE INDEX idx_email ON loan_applications(applicant_email);
```

### Monitor Connections
```sql
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads%';
```

## Docker Management

### Stop Container
```bash
docker stop loan-mysql
```

### Start Container
```bash
docker start loan-mysql
```

### Remove Container
```bash
docker rm loan-mysql
```

### View Logs
```bash
docker logs loan-mysql
```

## Next Steps

Once database is set up, run the FastAPI application:
```bash
cd backend
uvicorn app.main:app --reload
```

Tables will be created automatically on first run!
