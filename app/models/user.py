from app.database import Base
from sqlalchemy import String,Integer,DateTime,Column
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    
        __tablename__="users"
        id=Column(Integer,primary_key=True,index=True)
        username=Column(String,nullable=False)
        email=Column(String,unique=True,nullable=False)
        password_hash=Column(String,nullable=False)
        role=Column(String,nullable=False,default="user")
        created_at=Column(DateTime,default=datetime.utcnow)
        updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
        subscriptions=relationship("Subscription",back_populates="user")
        invoices=relationship("Invoice",back_populates="user")
        payments=relationship("Payment",back_populates="user")
