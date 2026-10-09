from fastapi import FastAPI
from app.models.user import User
from app.models.plans import Plan
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.database import Base
from app.routers.plan_router import router as plan_router
from app.routers.subscription_router import router as subscription_router
from app.routers.auth_router import router as auth_router
from app.routers.payment_router import router as payment_router
from app.routers.invoice_router import router as invoice_router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(title="Payment & Subscription API",description="Production-style Payment and Subscription Management API",
    version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan_router)
app.include_router(subscription_router)
app.include_router(auth_router)
app.include_router(payment_router)
app.include_router(invoice_router)




@app.get("/")
async def root():
    return {
        "message":"Payment api is running!!"
    }


