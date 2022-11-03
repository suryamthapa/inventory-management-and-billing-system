import datetime
from enum import unique
from sqlalchemy import Column, Integer, DateTime, String, Enum
from sqlalchemy.orm import relationship
from backend.database.setup import Base
from backend.models.bills import Bills

class Customers(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    full_name = Column(String)
    company = Column(String, unique=True)
    company_pan_no = Column(String)
    phone_number = Column(String, unique=True)
    telephone = Column(String, unique=True)
    email = Column(String, unique=True)
    address = Column(String, nullable=False)

    bills = relationship("Bills")