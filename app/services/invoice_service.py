from app.models.invoice import Invoice
from app.repositories.invoice_repo import InvoiceRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime
from app.repositories.payment_repo import PaymentRepo

class InvoiceService:
    @staticmethod
    async def create_invoice(db:AsyncSession,user_id:int,payment_id:int):
        payment=await PaymentRepo.get_payment_by_id(db,payment_id)
        if payment is None:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )

        if payment.user_id !=user_id:
            raise HTTPException(
                status_code=403,
                detail="Invoice can only be created for successful payment"
            )

        existing_invoice=await InvoiceRepo.get_invoice_by_payment_id(db,payment_id)
        if existing_invoice:
            return existing_invoice
        invoice_number = f"INV-{payment.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        invoice=Invoice(user_id=payment.user_id,
                        subscription_id=payment.subscription_id,
                        payment_id=payment.id,
                        invoice_number=invoice_number,
                        amount=payment.amount,
                        status="PAID",
                        issued_at=datetime.utcnow(),
                        paid_at=datetime.utcnow()
                        )
        return await InvoiceRepo.create_invoice(db,invoice)
        