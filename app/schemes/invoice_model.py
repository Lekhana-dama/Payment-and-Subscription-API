from pydantic import BaseModel,ConfigDict
from decimal import Decimal
from datetime import datetime


class InvoiceCreate(BaseModel):
    payment_id:int

class InvoiceResponse(BaseModel):
    id:int
    user_id:int
    subscription_id:int
    payment_id:int
    invoice_number:str
    amount:Decimal
    status:str
    issued_at:datetime
    due_at:datetime|None
    paid_at:datetime|None

    model_config=ConfigDict(from_attributes=True)
