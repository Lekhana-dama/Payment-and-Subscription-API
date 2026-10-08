from sqlalchemy.ext.asyncio  import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.services.payment_service import PaymentService
from fastapi import Depends,APIRouter
from app.dependencies.dependencies import get_current_user
from app.schemes.payment_model import PaymentCreate,PaymentResponse
from typing import List

router=APIRouter(prefix="/payments",tags=["Payments"])

@router.post("",response_model=PaymentResponse)
async def create_payment(payment_data:PaymentCreate,db:AsyncSession=Depends(get_db),current_user=Depends(get_current_user)):
    return await PaymentService.create_payment(db,current_user.id,payment_data.subscription_id,payment_data.idempotency_key)

@router.patch("/{payment_id}/success",response_model=PaymentResponse)
async def mark_payment_success(payment_id:int,db:AsyncSession=Depends(get_db),current_user=Depends(get_current_user)):
    return await PaymentService.mark_payment_success(db,current_user.id,payment_id)

@router.patch("/{payment_id}/failed", response_model=PaymentResponse)
async def mark_payment_failed(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await PaymentService.mark_payment_failed(
        db,
        current_user.id,
        payment_id
    )

@router.get("/",response_model=List[PaymentResponse])
async def get_payment_history(db:AsyncSession=Depends(get_db),current_user=Depends(get_current_user)):
    return await PaymentService.get_user_payments(db=db,user_id=current_user.id)