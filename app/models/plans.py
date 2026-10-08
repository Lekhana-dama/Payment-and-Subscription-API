from app.database import Base
from sqlalchemy import String,Integer,Numeric,DateTime,Column,Float,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
class Plan(Base):
    __tablename__='plans'
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    description=Column(String,nullable=False)
    price=Column(Numeric(10,2),nullable=False)
    billing_interval=Column(String,nullable=False)
    is_active=Column(Boolean,nullable=False,default=True)
    created_at=Column(DateTime,default=datetime.utcnow)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    subscriptions=relationship("Subscription",back_populates="plan")
    