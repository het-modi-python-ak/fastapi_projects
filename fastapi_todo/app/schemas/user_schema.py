from pydantic import BaseModel
class UserCreate(BaseModel):
    username:str
    password:str
    role:str


class Login(BaseModel):
    username:str
    password:str


class LoginResponse(BaseModel):
    access_token:str