from passlib.context import CryptContext
from jose import JWTError,jwt
from datetime import datetime,timedelta
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException
import hashlib
from cryptography.fernet import Fernet

load_dotenv()


SECRET_KEY =os.getenv("JWT_SECRET")
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120



pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def prehash_password(password:str)->str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password:str)->str:
    prehashed=prehash_password(password)
    return pwd_context.hash(prehashed)

def verify_password(password:str, hashed_pass:str) -> bool:
    prehashed=prehash_password(password)
    return pwd_context.verify(prehashed,hashed_pass)


def create_access_token(data: dict):
    to_encode=data.copy()
    expire=datetime.utcnow() +timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401,detail="Invalid token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401,detail="Invalid Token")
    

fernet =Fernet(os.environ["DB_SECRET_KEY"])

import hashlib

def hash_uri(uri: str) -> str:
    return hashlib.sha256(uri.encode()).hexdigest()

def encrypt(text:str)->str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(text:str)->str:
    return fernet.decrypt(text.encode()).decode()

