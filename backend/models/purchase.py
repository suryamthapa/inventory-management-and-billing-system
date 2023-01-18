import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, ARRAY, JSON, Float
from sqlalchemy.orm import relationship
from backend.database.setup import Base


class Purchases(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    invoice_number = Column(String, nullable=False, unique=True)
    purchase_year = Column(Integer, nullable=False)
    purchase_month = Column(Integer, nullable=False)
    purchase_day = Column(Integer, nullable=False)
    product_qty = Column(JSON, nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    excise_duty = Column(Float, nullable=True)
    cash_discount = Column(Float, nullable=True)
    p_discount = Column(Float, nullable=True)
    extra_discount = Column(Float, nullable=True)
    vat = Column(Float, nullable=True)
    cash_payment = Column(Float, nullable=True)
    balance_amount = Column(Float, nullable=True)
    extra_info = Column(JSON, nullable=True)