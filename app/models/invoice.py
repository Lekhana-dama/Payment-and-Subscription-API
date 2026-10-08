from app.database import Base
from sqlalchemy import String, Integer, Numeric, DateTime, Column, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=False,
        index=True
    )

    payment_id = Column(
        Integer,
        ForeignKey("payments.id"),
        nullable=False,
        index=True
    )

    invoice_number = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="PENDING"
    )

    issued_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    due_at = Column(
        DateTime,
        nullable=True
    )

    paid_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    user = relationship(
    "User",
    back_populates="invoices"
    )

    subscription = relationship(
        "Subscription",
        back_populates="invoices"
    )

    payment = relationship(
        "Payment",
        back_populates="invoice"
    )