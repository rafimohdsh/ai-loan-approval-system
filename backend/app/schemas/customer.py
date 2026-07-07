from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    date_of_birth: datetime
    ssn: str = Field(..., min_length=9, max_length=20)
    address: str
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    zip_code: str = Field(..., min_length=1, max_length=20)
    country: str = "USA"
    employment_status: str = Field(..., min_length=1, max_length=50)
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    years_employed: Optional[float] = None
    annual_income: float = Field(..., gt=0)
    monthly_expenses: Optional[float] = None
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    credit_history_months: Optional[int] = None
    total_debt: float = 0.0
    total_assets: float = 0.0
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    customer_id: str = Field(..., min_length=1, max_length=50)


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    employment_status: Optional[str] = None
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    years_employed: Optional[float] = None
    annual_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    credit_score: Optional[int] = None
    credit_history_months: Optional[int] = None
    total_debt: Optional[float] = None
    total_assets: Optional[float] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    customer_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    total: int
    count: int
    customers: list[CustomerResponse]
