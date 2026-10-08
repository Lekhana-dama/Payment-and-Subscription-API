from app.database import Base
from sqlalchemy import String,Integer,Numeric,DateTime,Column,ForeignKey,Float,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
class Subscription(Base):
    __tablename__='subscriptions'

    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),index=True,nullable=False)
    plan_id=Column(Integer,ForeignKey("plans.id"),index=True,nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    started_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    plan=relationship("Plan",back_populates="subscriptions")
    payments=relationship("Payment",back_populates="subscription")
    user=relationship("User",back_populates="subscriptions")
    invoices=relationship("Invoice",back_populates="subscription")