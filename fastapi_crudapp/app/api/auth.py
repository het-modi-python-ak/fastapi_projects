from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from jose import jwt,JWTError
from passlib.context import CryptContext

from auth.database import init_db, get_user, create_user 
from dotenv import load_dotenv
import os
from middleware.logging import LoggingMiddleware


load_dotenv()




SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_DAYS  = 7



router = APIRouter(tags=["auth"])


# router.add_middleware(LoggingMiddleware)

@router.on_event("startup")
def on_startup():
    init_db()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   #hasing password
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)
    
class UserPublic(BaseModel):
    username: str
   

class Token(BaseModel):
    access_token: str
    refresh_token:str   #added refresh token
    token_type: str = "bearer"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_toke(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


#refresh token

def create_refresh_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp":expire,"type":"refresh"})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)





def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise cred_exc
    except JWTError:
        raise cred_exc
    
    user = get_user(username)
    if not user:
        raise cred_exc
    return UserPublic(username=user["username"])

# route
@router.get("/user")
def fun1():
    return {"message": "hello"}



@router.post("/register", status_code=201, summary="create a new user")
def register_user(body: UserCreate):
    hashed = hash_password(body.password)
    create_user(body.username, hashed)
    return {"message": "user registered successfully"}



@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_toke({"sub": user["username"]})
    refresh_token = create_refresh_token({"sub":user["username"]})
    return {"access_token": access_token,"refresh_token":refresh_token, "token_type": "bearer"}




#refresh endpoint

@router.post("/refresh")
def refresh_token(refresh_token:str):
    cred_excep = HTTPException(status_code=401,detail="Invalid refresh token")

    try :
        payload = jwt.decode(refresh_token,SECRET_KEY,algorithms=[ALGORITHM])
        if payload.get("type")!= "refresh":
            raise cred_excep
        username = payload.get("sub")
        if username is None:
            raise cred_excep
    except JWTError:
        raise cred_excep
    
    new_access_token = create_access_toke({"sub":username})
    return { "acess_token":new_access_token,"token_type":"bearer"}




@router.get("/me", response_model=UserPublic, summary="get my profile")
def read_me(current_user: UserPublic = Depends(get_current_user)):
    return current_user




