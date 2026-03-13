
from fastapi import APIRouter, Depends
from core.rbac import RoleChecker

router = APIRouter()

admin_only = RoleChecker(["admin"])
admin_manager = RoleChecker(["admin", "manager"])
string_ck = RoleChecker(["string"])



@router.get("/admin")
def admin_data(user = Depends(admin_only)):

    return {"message": "Admin access granted"}


@router.get("/dashboard")
def dashboard(user = Depends(admin_manager)):

    return {"message": "Admin or Manager allowed"}


@router.get("/itmes")
def items(user = Depends(string_ck)):
    return {"message":"Only strings are allowed"}