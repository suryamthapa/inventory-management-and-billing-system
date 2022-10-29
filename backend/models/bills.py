from sqlalchemy import Column, Integer, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from backend.database.setup import Base
from backend.models.sales import Sales

class Bills(Base):
    __tablename__ = 'bills'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    paid_amount = Column(Integer)
    discount_amount = Column(Integer)
    discount_percentage = Column(Integer)
    vat = Column(Integer)
    tax = Column(Integer)

    sales = relationship("Sales")