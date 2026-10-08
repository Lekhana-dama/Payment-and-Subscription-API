from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.repositories.payment_repo import PaymentRepo

class InvoiceRepo:
    @staticmethod
    async def create_invoice(db:AsyncSession,invoice:Invoice):
        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)
        return invoice

    @staticmethod
    async def get_invoice_by_id(db:AsyncSession,invoice_id:int):
        result=await db.execute(select(Invoice).where(Invoice.id==invoice_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_invoice_by_payment_id(db:AsyncSession,payment_id:int):
        result=await db.execute(
            select(Invoice).where(Invoice.payment_id==payment_id)

        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_invoices(db:AsyncSession,user_id:int):
        result=await db.execute(
            select(Invoice).where(Invoice.user_id==user_id).order_by(Invoice.created_at.desc())
        )
        return result.scalars().all()

            