from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from .base import Base, TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False, index=True)

    date_of_birth = Column(DateTime, nullable=False)
    ssn = Column(String(20), nullable=False, unique=True, index=True)

    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), default="USA")

    employment_status = Column(String(50), nullable=False)  # Employed, Self-employed, Unemployed, Retired
    occupation = Column(String(100), nullable=True)
    employer_name = Column(String(255), nullable=True)
    years_employed = Column(Float, nullable=True)

    annual_income = Column(Float, nullable=False)
    monthly_expenses = Column(Float, nullable=True)

    credit_score = Column(Integer, nullable=True)
    credit_history_months = Column(Integer, nullable=True)

    total_debt = Column(Float, default=0.0)
    total_assets = Column(Float, default=0.0)

    is_active = Column(Boolean, default=True, index=True)

    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_customer_email_phone', 'email', 'phone'),
        Index('idx_customer_ssn_name', 'ssn', 'first_name', 'last_name'),
    )

    def __repr__(self):
        return f"<Customer(id={self.id}, customer_id={self.customer_id}, email={self.email})>"
