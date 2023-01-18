import datetime
from sqlalchemy import Column, Integer, DateTime, String, JSON, Float
from sqlalchemy.orm import relationship
from backend.database.setup import Base


class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    product_name = Column(String, nullable=False, unique=True)
    cost_price = Column(Float, nullable=True)
    unit = Column(String, nullable=False, default="pcs")
    stock = Column(Float, nullable=False, default=0)
    extra_info = Column(JSON, nullable=True)