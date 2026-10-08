from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.invoice_repo import InvoiceRepo
from app.database import get_db
from app.services.invoice_service import InvoiceService
from app.schemes.invoice_model import InvoiceCreate, InvoiceResponse
from app.dependencies.dependencies import get_current_user
from fastapi import HTTPException

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
)

@router.post("/",response_model=InvoiceResponse)
async def create_invoice(invoice_data:InvoiceCreate,db:AsyncSession=Depends(get_db),current_user=Depends(get_current_user)):
    return await InvoiceService.create_invoice(db=db,user_id=current_user.id,payment_id=invoice_data.payment_id)

@router.get("/{invoice_id}",response_model=InvoiceResponse)
async def get_invoice(invoice_id:int,db:AsyncSession=Depends(get_db),current_user=Depends(get_current_user)):
    invoice=await InvoiceRepo.get_invoice_by_id(db,invoice_id)
    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )
    if invoice.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Invoice does not belong to user"
        )

    return invoice

