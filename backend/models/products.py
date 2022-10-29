import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import relationship
from backend.database.setup import Base
from backend.models.sales import Sales


class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    product_name = Column(String, nullable=False, unique=True)
    cost_price = Column(Integer, nullable=False)
    marked_price = Column(Integer, nullable=False)
    unit = Column(String, nullable=False, default="pcs")
    stock = Column(Integer, nullable=False, default=0)

    bills = relationship("Sales")