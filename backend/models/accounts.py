import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Enum, Float
from backend.database.setup import Base
from . import AccountType

class Accounts(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    transaction_date = Column(DateTime, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('bills.id'), nullable=True)
    type = Column(Enum(AccountType), nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)