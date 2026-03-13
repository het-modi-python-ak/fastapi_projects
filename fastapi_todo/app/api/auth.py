from fastapi import APIRouter
router = APIRouter()

@router.get("/register",tags=["auth"])
def register_user():
    return {"user registered successfully"}