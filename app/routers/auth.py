from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginIn, LoginOut, RegisterIn, RegisterOut, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()

    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email sudah terdaftar")
    if db.scalar(select(User).where(User.username == data.username)):
        raise HTTPException(409, "Username sudah dipakai")

    user = User(
        username=data.username,
        email=email,
        password_hash=hash_password(data.password), 
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  
        db.rollback()
        raise HTTPException(409, "Username atau email sudah terdaftar")
    db.refresh(user)

    return RegisterOut(message="Registrasi berhasil. Silakan login.", user=UserOut.model_validate(user))


@router.post("/login", response_model=LoginOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Email atau password salah")

    return LoginOut(token=create_access_token(user.id), user=UserOut.model_validate(user))
