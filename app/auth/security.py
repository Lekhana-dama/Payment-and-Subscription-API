from datetime import timedelta,datetime,timezone
from jose import jwt
from passlib.context import CryptContext
from app.config import SERECT_KEY


pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

ALG="HS256"

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data:dict,expires_delta:timedelta|None=None):
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.now(timezone.utc)+expires_delta

    else:
        expire=datetime.now(timezone.utc)+timedelta(minutes=30)

    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SERECT_KEY,algorithm=ALG)