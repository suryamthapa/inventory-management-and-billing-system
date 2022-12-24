import datetime
from enum import unique
from sqlalchemy import Column, Integer, DateTime, String, Enum, JSON
from sqlalchemy.orm import relationship
from backend.database.setup import Base
from backend.models.purchase import Purchases


class Vendors(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    vat_number = Column(String, nullable=False)
    vendor_name = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    telephone = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True)
    extra_info = Column(JSON, nullable=True)

    purchase = relationship("Purchases")