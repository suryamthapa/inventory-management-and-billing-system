import datetime
from sqlalchemy import Column, Integer, DateTime, String, Enum, Boolean
from backend.database.setup import Base
from . import LisenceStatus


class Lisences(Base):
    __tablename__ = 'lisences'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    lisence_key = Column(String, unique=True)
    activated_on = Column(DateTime)
    duration = Column(Integer) # years
    status = Column(Enum(LisenceStatus), default=LisenceStatus.active)