from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(tags=["Authentication"])

# This is the secret code only real doctors receive from the hospital admin
DOCTOR_REGISTRATION_CODE = os.getenv("DOCTOR_REGISTRATION_CODE", "HOSPITAL_GUINEA_2026")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

@router.post("/register", status_code=201, response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.role == "doctor":
        if not user.registration_code:
            raise HTTPException(
                status_code=403,
                detail="Doctors must provide a registration code to register"
            )
        if user.registration_code != DOCTOR_REGISTRATION_CODE:
            raise HTTPException(
                status_code=403,
                detail="Invalid registration code. Contact your hospital administrator."
            )

    if user.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be created through this endpoint."
        )

    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}
