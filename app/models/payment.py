from app.database import Base
from sqlalchemy import String,Integer,ForeignKey,Numeric,DateTime,Column,Float,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

class Payment(Base):

    __tablename__="payments"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    subscription_id=Column(Integer,ForeignKey("subscriptions.id"),nullable=False,index=True)
    amount=Column(Numeric(10,2),nullable=False)
    status=Column(String,nullable=False,default="PENDING")
    provider=Column(String,nullable=False)
    provider_transaction_id=Column(String,nullable=False,unique=True,index=True)
    idempotency_key=Column(String,nullable=False,unique=True,index=True)
    created_at=Column(DateTime,default=datetime.utcnow)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    subscription=relationship("Subscription",back_populates="payments")
    user=relationship("User",back_populates="payments")
    invoice=relationship("Invoice",back_populates="payment")