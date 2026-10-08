from pydantic import BaseModel,EmailStr
from datetime import datetime

class PaymentCreate(BaseModel):
    subscription_id:int
    idempotency_key:str

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    amount: float
    status: str
    provider: str
    provider_transaction_id: str
    created_at:datetime

    class Config:
        from_attributes = True