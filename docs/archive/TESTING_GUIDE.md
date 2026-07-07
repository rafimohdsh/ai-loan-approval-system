# Testing Guide - Agentic Loan Approval System

## Quick Start

```bash
# Navigate to project directory
cd /home/ubuntu/agentic-loan-approval-system

# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Expected Output: 89 passing tests, 76% coverage
```

---

## Test Files Overview

### 1. test_orchestration_service.py
**Focus:** Agent workflows, LangGraph execution, multi-agent orchestration

```bash
# Run orchestration tests only
pytest tests/test_orchestration_service.py -v

# Run specific test class
pytest tests/test_orchestration_service.py::TestOrchestrationService -v

# Run specific test
pytest tests/test_orchestration_service.py::TestOrchestrationService::test_process_loan_application_creates_decision -v
```

**What's Tested:**
- ✅ Loan application processing
- ✅ Multi-agent decision making
- ✅ Workflow graph execution
- ✅ Error handling and recovery
- ✅ Audit trail generation

**17 Tests:**
- Core workflow: 7 tests
- Graph execution: 7 tests
- Error handling: 3 tests

---

### 2. test_database_operations.py
**Focus:** CRUD operations, data integrity, constraints, queries

```bash
# Run database tests only
pytest tests/test_database_operations.py -v

# Show database queries
pytest tests/test_database_operations.py -v -s

# Test specific class
pytest tests/test_database_operations.py::TestLoanApplicationDatabase -v
```

**What's Tested:**
- ✅ Create/Read/Update/Delete operations
- ✅ Unique constraints (IDs)
- ✅ Pagination and filtering
- ✅ Foreign key relationships
- ✅ Decision creation logic
- ✅ Status transitions

**18 Tests:**
- LoanApplication CRUD: 10 tests
- LoanDecision operations: 8 tests

---

### 3. test_edge_cases_and_errors.py
**Focus:** Boundary conditions, calculations, data validation, error scenarios

```bash
# Run edge case tests only
pytest tests/test_edge_cases_and_errors.py -v

# Run specific category
pytest tests/test_edge_cases_and_errors.py::TestBoundaryConditions -v
pytest tests/test_edge_cases_and_errors.py::TestDTICalculations -v
pytest tests/test_edge_cases_and_errors.py::TestCreditRiskAssessment -v

# Test string handling
pytest tests/test_edge_cases_and_errors.py::TestStringEdgeCases -v
```

**What's Tested:**
- ✅ Boundary values (credit scores, DTI ratios)
- ✅ String validation (length, characters)
- ✅ Calculation accuracy
- ✅ Risk assessment algorithms
- ✅ Employment scenarios
- ✅ Credit evaluation edge cases

**35 Tests:**
- Boundary conditions: 9 tests
- String edge cases: 3 tests
- DTI calculations: 5 tests
- Credit risk: 5 tests
- Risk factors: 6 tests
- Risk levels: 4 tests
- Applicant profile: 3 tests

---

### 4. test_integration.py
**Focus:** End-to-end workflows, multiple scenarios, performance

```bash
# Run integration tests only
pytest tests/test_integration.py -v

# Run specific workflow
pytest tests/test_integration.py::TestEndToEndLoanApprovalFlow -v

# Run error recovery tests
pytest tests/test_integration.py::TestErrorRecovery -v

# Run performance tests
pytest tests/test_integration.py::TestPerformanceEdgeCases -v
```

**What's Tested:**
- ✅ Complete approval flows
- ✅ Complete rejection flows
- ✅ Manual review scenarios
- ✅ Multiple applications
- ✅ Status transitions
- ✅ Audit trail generation
- ✅ Different loan types
- ✅ Employment status variations

**19 Tests:**
- End-to-end workflows: 12 tests
- Error recovery: 1 test
- Performance: 2 tests

---

## Running Tests with Different Options

### Basic Execution
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with extra verbose (show print statements)
pytest tests/ -v -s

# Run and stop on first failure
pytest tests/ -x

# Run with local variable display
pytest tests/ -l
```

### Coverage Analysis
```bash
# Generate coverage report
pytest tests/ --cov=backend/app --cov-report=term-missing

# HTML coverage report (opens in browser)
pytest tests/ --cov=backend/app --cov-report=html
open htmlcov/index.html

# Coverage report by module
pytest tests/ --cov=backend/app --cov-report=term-missing | grep -E "^backend"
```

### Filtering Tests
```bash
# Run tests matching a pattern
pytest tests/ -k "orchestration"
pytest tests/ -k "database"
pytest tests/ -k "edge_case"
pytest tests/ -k "integration"

# Run tests NOT matching pattern
pytest tests/ -k "not api"

# Run tests by class
pytest tests/ -k "TestOrchestrationService"

# Run tests by method
pytest tests/ -k "test_process_loan"
```

### Performance Testing
```bash
# Run tests with timing
pytest tests/ -v --durations=10

# Run single test with timing
pytest tests/test_orchestration_service.py::TestOrchestrationService::test_process_loan_application_creates_decision -v --durations=0

# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/ -n 4  # Run with 4 workers
```

### Debugging
```bash
# Drop into debugger on failure
pytest tests/ -x --pdb

# Drop into debugger at start of test
pytest tests/ --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb

# Show full traceback
pytest tests/ --tb=long

# Show no traceback
pytest tests/ --tb=no

# Show line numbers
pytest tests/ -l
```

---

## Common Test Commands

### Run All Tests with Coverage
```bash
pytest tests/ --cov=backend/app --cov-report=term-missing -v
```

### Quick Test of Core Functionality
```bash
pytest tests/test_orchestration_service.py tests/test_database_operations.py -v
```

### Test Specific Feature Area
```bash
# Agent orchestration
pytest tests/test_orchestration_service.py -v

# Database operations
pytest tests/test_database_operations.py -v

# Business logic edge cases
pytest tests/test_edge_cases_and_errors.py -v

# End-to-end workflows
pytest tests/test_integration.py -v
```

### Debug a Failing Test
```bash
# First: run the test to see error
pytest tests/test_orchestration_service.py::TestOrchestrationService::test_process_loan_application_creates_decision -v

# Then: run with more detail
pytest tests/test_orchestration_service.py::TestOrchestrationService::test_process_loan_application_creates_decision -v -s --tb=long

# Finally: run with debugger
pytest tests/test_orchestration_service.py::TestOrchestrationService::test_process_loan_application_creates_decision --pdb
```

---

## Understanding Test Output

### Successful Test Run
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1
collected 89 items

tests/test_orchestration_service.py::TestOrchestrationService::test_process_loan_application_creates_decision PASSED [  5%]
tests/test_orchestration_service.py::TestOrchestrationService::test_process_loan_application_updates_application_status PASSED [ 11%]
...
================================ 89 passed in 40.96s =================================
```

### Test Failure Example
```
FAILED tests/test_database_operations.py::TestLoanApplicationDatabase::test_set_approval_decision - pydantic_core._pydantic_core.ValidationError: 1 validation error for LoanApprovalDecision
application_id
  Field required [type=missing, ...]
```

**Fix:** Provide required `application_id` field in test data

### Coverage Report Example
```
Name                                          Stmts   Miss  Cover   Missing
------------------------------------------------------------------------------------
backend/app/services/orchestration_service    46      0    100%
backend/app/agents/profile_agent              138     3    98%     126, 176, 179
backend/app/models/loan_application           35      0    100%
...
TOTAL                                          1418    342   76%
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest tests/ --cov=backend/app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

source venv/bin/activate
pytest tests/ -q --tb=short

if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
```

---

## Test Data

### Sample Good Applicant
```python
{
    "applicant_name": "John Doe",
    "applicant_email": "john@example.com",
    "applicant_phone": "+1-555-1234",
    "location": "San Francisco, CA",
    "loan_amount": 50000.0,
    "loan_type": "Personal",
    "loan_term_months": 60,
    "annual_income": 150000.0,
    "employment_status": "Employed Full-time",
    "years_employed": 5.0,
    "credit_score": 750,
    "existing_debt": 300.0,
}
# Expected Result: APPROVED (20% risk, 95% probability)
```

### Sample High-Risk Applicant
```python
{
    "applicant_name": "Jane Smith",
    "applicant_email": "jane@example.com",
    "applicant_phone": "+1-555-5678",
    "location": "New York, NY",
    "loan_amount": 100000.0,
    "loan_type": "Personal",
    "loan_term_months": 120,
    "annual_income": 40000.0,
    "employment_status": "Self-employed",
    "years_employed": 0.5,
    "credit_score": 550,
    "existing_debt": 5000.0,
}
# Expected Result: REJECTED (85% risk, 5% probability)
```

### Sample Marginal Applicant
```python
{
    "applicant_name": "Bob Johnson",
    "applicant_email": "bob@example.com",
    "applicant_phone": "+1-555-9999",
    "location": "Denver, CO",
    "loan_amount": 50000.0,
    "loan_type": "Personal",
    "loan_term_months": 60,
    "annual_income": 80000.0,
    "employment_status": "Employed",
    "years_employed": 0.8,
    "credit_score": None,
    "existing_debt": 2000.0,
}
# Expected Result: UNDER_REVIEW (60% risk, 50% probability)
```

---

## Troubleshooting

### Common Issues

**Issue: Import errors**
```bash
# Solution: Ensure you're in the virtual environment
source venv/bin/activate

# Or verify PYTHONPATH
export PYTHONPATH=/home/ubuntu/agentic-loan-approval-system:$PYTHONPATH
```

**Issue: Database is locked**
```bash
# Solution: Tests use in-memory SQLite, but clear pytest cache
rm -rf .pytest_cache
pytest tests/
```

**Issue: Tests too slow**
```bash
# Solution: Check if running with -s flag (captures output)
pytest tests/ -v  # Fast
pytest tests/ -v -s  # Slower (due to output capturing)

# Or run in parallel
pip install pytest-xdist
pytest tests/ -n 4
```

**Issue: Mock not working**
```bash
# Solution: Ensure you're patching the right import path
# Patch where it's used, not where it's defined
@patch('backend.app.services.orchestration_service.create_loan_approval_graph')
def test_something(self, mock_graph):
    ...
```

---

## Performance Benchmarks

```
Total Execution Time: ~40 seconds
Average Test Time: ~450ms
Slowest Tests (Workflow execution):
  - test_graph_execution_with_valid_state: ~2000ms
  - test_complete_approved_workflow: ~1500ms
  - test_complete_rejected_workflow: ~1400ms

Fastest Tests (Utility functions):
  - test_credit_risk_threshold_scores: ~5ms
  - test_dti_calculations: ~10ms
  - test_loan_amount_minimal: ~20ms
```

---

## Next Steps

1. **Run full test suite**
   ```bash
   pytest tests/ --cov=backend/app -v
   ```

2. **Check coverage gaps**
   ```bash
   pytest tests/ --cov=backend/app --cov-report=html
   ```

3. **Add more tests for low coverage areas**
   - API endpoints (57%)
   - Database connections (63%)
   - External services (0%)

4. **Set up continuous testing**
   - GitHub Actions
   - Pre-commit hooks
   - CI/CD pipeline

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/faq/testing.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-events/)

---

**Last Updated:** July 3, 2026  
**Test Suite Version:** 1.0  
**Status:** Production Ready ✅
