from sqlalchemy.ext.asyncio  import AsyncSession
from app.models.payment import Payment
from app.models.plans import Plan
from app.models.subscription import Subscription
from sqlalchemy import select
from app.repositories.payment_repo import PaymentRepo
from datetime import datetime,timedelta
from fastapi import HTTPException

class PaymentService:

    @staticmethod
    async def create_payment(db:AsyncSession,user_id:int,sub_id:int,idemp_key:str):
        
        result= await db.execute(
            select(Subscription).where(Subscription.id==sub_id,Subscription.user_id==user_id)
        )
        subscription=result.scalar_one_or_none()

        if subscription is None:
            raise ValueError("Subscription  not found")

        if subscription.status !="PENDING":
            raise ValueError("Subscription is not pending")

        existing_payment=await PaymentRepo.get_payment_by_idempotency_key(db,idemp_key=idemp_key)
        if existing_payment:
            return existing_payment

        payment=Payment(user_id=user_id,subscription_id=subscription.id,
                        amount=subscription.amount,status="PENDING",
                        provider="demo",provider_transaction_id=f"pending-{idemp_key}",idempotency_key=idemp_key)
        return await PaymentRepo.create_payment(db,payment)


    @staticmethod
    async def mark_payment_success(db: AsyncSession, user_id: int, payment_id: int):
        try:
                payment = await PaymentRepo.get_payment_by_id(db, payment_id)

                if payment is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Payment not found"
                    )

                if payment.user_id != user_id:
                    raise HTTPException(
                        status_code=403,
                        detail="Payment does not belong to user"
                    )

                if payment.status != "PENDING":
                    raise HTTPException(
                        status_code=400,
                        detail="Payment is not pending"
                    )

                result = await db.execute(
                    select(Subscription).where(
                        Subscription.id == payment.subscription_id,Subscription.user_id==user_id
                    )
                )
                subscription = result.scalar_one_or_none()

                if subscription is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Subscription not found"
                    )

                result = await db.execute(
                    select(Plan).where(
                        Plan.id == subscription.plan_id
                    )
                )
                plan = result.scalar_one_or_none()

                if plan is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Plan not found"
                    )

                now = datetime.utcnow()

                payment.status = "SUCCESS"
                subscription.status = "ACTIVE"
                subscription.started_at = now

                if plan.billing_interval == "monthly":
                    subscription.expires_at = now + timedelta(days=30)

                elif plan.billing_interval == "yearly":
                    subscription.expires_at = now + timedelta(days=365)

                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Unsupported billing interval"
                    )

                await db.commit()

                await db.refresh(payment)
                await db.refresh(subscription)

                return payment
        except HTTPException:
                        await db.rollback()
                        raise
        except Exception:
                        await db.rollback()
                        raise

    @staticmethod
    async def mark_payment_failed(
            db: AsyncSession,
            user_id: int,
            payment_id: int
        ):
            try:
                payment = await PaymentRepo.get_payment_by_id(db, payment_id)

                if payment is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Payment not found"
                    )

                if payment.user_id != user_id:
                    raise HTTPException(
                        status_code=403,
                        detail="Payment does not belong to user"
                    )

                if payment.status != "PENDING":
                    raise HTTPException(
                        status_code=400,
                        detail="Payment is not pending"
                    )

                payment.status = "FAILED"

                await db.commit()
                await db.refresh(payment)

                return payment
            except HTTPException:
                await db.rollback()
                raise
            except Exception:
                await db.rollback()
                raise
        
    @staticmethod
    async def get_user_payments(
        db: AsyncSession,
        user_id: int
    ):
        return await PaymentRepo.get_user_payments(
            db=db,
            user_id=user_id
        )