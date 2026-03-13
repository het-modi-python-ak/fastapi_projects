from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate,LoginResponse
from database.database import get_db
from models.user import User
from typing import Annotated
from core.security import hash_password, verify_password, create_access_token
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
router = APIRouter()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    db_user = User(
        username=user.username,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created"}


@router.post("/login",response_model=LoginResponse)
def login(data: Annotated[OAuth2PasswordRequestForm,Depends()], db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})

    return {
        "access_token": token
    }