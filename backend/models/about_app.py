import datetime
from sqlalchemy import Column, DateTime, String, Integer, Boolean, JSON
from backend.database.setup import Base


class AboutApp(Base):
    __tablename__ = 'about_app'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    app_version = Column(String)
    unique_machine_code = Column(String)
    trial_begin_on = Column(DateTime)
    trial_completed = Column(Boolean)
    extra_info = Column(JSON, nullable=True)