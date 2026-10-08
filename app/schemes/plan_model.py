from pydantic import BaseModel,ConfigDict
from decimal import Decimal

class PlanCreate(BaseModel):
    name:str
    description:str
    price:Decimal
    billing_interval:str
    is_active:bool=True

class PlanResponse(BaseModel):
    id:int
    name:str
    description:str
    price:Decimal
    billing_interval:str
    is_active:bool

model_config=ConfigDict(from_attributes=True)
