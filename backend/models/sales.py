import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from backend.database.setup import Base

class Sales(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    bill_id = Column(Integer, ForeignKey('bills.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    selling_price = Column(Integer)
    discount_amount = Column(Integer)
    discount_percentage = Column(Integer)
    vat = Column(Integer)
    tax = Column(Integer)



