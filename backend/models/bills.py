import datetime
from sqlalchemy import Column, Integer, ForeignKey, Sequence, JSON, DateTime, Float
from sqlalchemy.orm import relationship
from backend.database.setup import Base
from backend.models.accounts import Accounts

class Bills(Base):
    __tablename__ = 'bills'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    sale_year = Column(Integer, nullable=False)
    sale_month = Column(Integer, nullable=False)
    sale_day = Column(Integer, nullable=False)
    product_qty = Column(JSON, nullable=False, default={})
    discount_amount = Column(Float)
    discount_percentage = Column(Float)
    vat = Column(Float)
    tax = Column(Float)
    paid_amount = Column(Float)
    extra_info = Column(JSON, nullable=True)

    accounts = relationship("Accounts", cascade="delete, merge, save-update")