from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.services.database import register_user, login_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    name: str
    student_class: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(req: RegisterRequest):
    """Registers a new student with name, class, email, and password."""
    if req.password != req.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="పాస్‌వర్డ్ మరియు కన్ఫర్మ్ పాస్‌వర్డ్ సరిపోలలేదు (Passwords do not match)."
        )

    res = register_user(
        name=req.name,
        student_class=req.student_class,
        email=req.email,
        password=req.password
    )

    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])

    return res


@router.post("/login")
async def login(req: LoginRequest):
    """Authenticates a student by email and password."""
    res = login_user(email=req.email, password=req.password)
    if not res["success"]:
        raise HTTPException(status_code=401, detail=res["message"])

    return res

