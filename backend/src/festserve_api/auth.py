# auth.py
# Authentication and authorization utilities for FestServe

import os
import datetime
import uuid
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from festserve_api import models
from festserve_api.database import get_db


# Secret key for JWT. In production, set via environment variable.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Utility functions


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_advertiser(
    db: Session, email: str, password: str
) -> Optional[models.Advertiser]:
    user = (
        db.query(models.Advertiser)
        .filter(models.Advertiser.contact_email == email)
        .first()
    )
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def authenticate_scanner(
    db: Session, username: str, password: str
) -> Optional[models.ScannerUser]:
    user = (
        db.query(models.ScannerUser)
        .filter(models.ScannerUser.username == username)
        .first()
    )
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(
    data: dict, expires_delta: Optional[datetime.timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (
        expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Choose model based on role
    if role == "advertiser":
        user_uuid = uuid.UUID(user_id)
        user = (
            db.query(models.Advertiser)
            .filter(models.Advertiser.advertiser_id == user_uuid)
            .first()
        )
    else:
        user_uuid = uuid.UUID(user_id)
        user = (
            db.query(models.ScannerUser)
            .filter(models.ScannerUser.user_id == user_uuid)
            .first()
        )
    if user is None:
        raise credentials_exception
    return user


# Auth router
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # Determine whether this is an advertiser or scanner login
    # Use form_data.scopes to indicate role: e.g., ["advertiser"] or ["scanner"]
    if "advertiser" in form_data.scopes:
        user = authenticate_advertiser(db, form_data.username, form_data.password)
        role = "advertiser"
    else:
        user = authenticate_scanner(db, form_data.username, form_data.password)
        role = "scanner"
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={
            "sub": str(user.advertiser_id if role == "advertiser" else user.user_id),
            "role": role,
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user
