from app.models.subscription import Subscription
from app.repositories.subscription_repo import SubscriptionRepo
from app.schemes.subscription_model import SubscriptionCreate,SubscriptionResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.services.subscription_service import SubscriptionService
from fastapi import APIRouter,Depends
from app.dependencies.dependencies import get_current_user
from app.models.user import User
from  typing import List
from fastapi import HTTPException

router=APIRouter(prefix="/subscriptions",tags=["Subscriptions"])

@router.post("",response_model=SubscriptionResponse)
async def create_subscription(subscription_data:SubscriptionCreate,db:AsyncSession=Depends(get_db),current_user:User=Depends(get_current_user)):
    return await SubscriptionService.create_subscription(db,current_user.id,subscription_data)

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscription = await SubscriptionRepo.get_subscription_by_id(
        db=db,
        subscription_id=subscription_id
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    if subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Subscription does not belong to user"
        )

    return subscription