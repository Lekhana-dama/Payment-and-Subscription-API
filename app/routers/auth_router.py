from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.services.auth_service import AuthService
from app.schemes.user_model import UserCreate

router=APIRouter(prefix="/auth",tags=["Auth"])

@router.post("/register")
async def register(user_data:UserCreate,db:AsyncSession=Depends(get_db)):
    try:
        user=await AuthService.register(db=db,username=user_data.username,email=user_data.email,password=user_data.password)
        return {
            "message":"User registered sucessfully",
            "user_id":user.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        access_token = await AuthService.login(
            db=db,
            email=form_data.username,
            password=form_data.password
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )