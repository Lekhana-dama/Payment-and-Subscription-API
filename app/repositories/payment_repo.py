from sqlalchemy.ext.asyncio  import AsyncSession
from app.models.payment import Payment
from sqlalchemy import select

class PaymentRepo:

    @staticmethod
    async def create_payment(db:AsyncSession,payment:Payment):
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def get_payment_by_id(db:AsyncSession,payment_id:int):
        result=await db.execute(
            select(Payment).where(Payment.id==payment_id)
        )
        return result.scalar_one_or_none()


    @staticmethod
    async def get_payment_by_idempotency_key(db:AsyncSession,idemp_key:str):
        result=await db.execute(
            select(Payment).where(Payment.idempotency_key==idemp_key)
        )
        return result.scalar_one_or_none()
    @staticmethod
    async def get_user_payments(
        db: AsyncSession,
        user_id: int
    ):
        result = await db.execute(
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        )

        return result.scalars().all()