from app.models.subscription import Subscription
from app.repositories.subscription_repo import SubscriptionRepo
from app.schemes.subscription_model import SubscriptionCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.plans import Plan

class SubscriptionService:
    @staticmethod
    async def create_subscription(db:AsyncSession,user_id:int,subscription_data:SubscriptionCreate):
        existing_subscription=await SubscriptionRepo.get_active_subscription(db,user_id)
        if existing_subscription:
            raise ValueError("User already has an active subscription")
        result=await db.execute(select(Plan).where(Plan.id==subscription_data.plan_id,Plan.is_active==True))
        plan=result.scalar_one_or_none()
        if plan is None:
            raise ValueError("Plan not found or inactive")
        subscription=Subscription(user_id=user_id,plan_id=plan.id,amount=plan.price)
        return await SubscriptionRepo.create_subscription(db,subscription)

   