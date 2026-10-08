from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional

class SubscriptionCreate(BaseModel):
    plan_id:int

class SubscriptionResponse(BaseModel):
    id:int
    plan_id:int
    amount:Decimal
    status:str
    started_at:Optional[datetime]=None
    expires_at:Optional[datetime]=None

    