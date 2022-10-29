import datetime
from typing import Counter
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, JSON
from backend.database.setup import Base


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    key = Column(String, unique=True, nullable=False)
    value = Column(String)