from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import ALG
from app.config import SERECT_KEY
from app.database import get_db
from app.models.user import User

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token:str=Depends(oauth2_scheme),db:AsyncSession=Depends(get_db)):
    credentials_exception=HTTPException(
                status_code=401,detail="could not validate credentials")

    try:
        payload=jwt.decode(token,SERECT_KEY,algorithms=[ALG])
        user_id=payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result=await db.execute(select(User).where(User.id==int(user_id)))
    user=result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user