from app.schemes.subscription_model import SubscriptionCreate
from app.models.subscription import Subscription
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class SubscriptionRepo:

    @staticmethod
    async def create_subscription(db:AsyncSession,subscription:Subscription):
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        return subscription

    @staticmethod
    async def get_by_id(db:AsyncSession,id:int):
        result=await db.execute(
            select(Subscription).where(Subscription.id==id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db:AsyncSession,user_id:int):
        result=await db.execute(
            select(Subscription).where(Subscription.user_id==user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_active_subscription(db:AsyncSession,user_id:int):
        result=await db.execute(select(Subscription).where(
            Subscription.user_id==user_id,
            Subscription.status=="ACTIVE"
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_subscription_by_id(db:AsyncSession,subscription_id:int):
        result= await db.execute(select(Subscription).where(Subscription.id==subscription_id))
        return result.scalar_one_or_none()
