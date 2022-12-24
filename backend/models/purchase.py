import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, ARRAY, JSON
from sqlalchemy.orm import relationship
from backend.database.setup import Base


class Purchases(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    invoice_number = Column(String, nullable=False, unique=True)
    date_of_purchase = Column(DateTime, default=datetime.datetime.utcnow)
    product_qty = Column(JSON, nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    excise_duty = Column(Integer, nullable=True)
    cash_discount = Column(Integer, nullable=True)
    p_discount = Column(Integer, nullable=True)
    extra_discount = Column(Integer, nullable=True)
    vat = Column(Integer, nullable=True)
    cash_payment = Column(Integer, nullable=True)
    balance_amount = Column(Integer, nullable=True)
    extra_info = Column(JSON, nullable=True)