from main import app
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from schemas import Token, UserCreate, UserResponse
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from database import get_db
@app.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password and save user
    hashed_pwd = hash_password(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_pwd, name=user_data.name,role=user_data.role, created_at=user_data.created_at)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Retrieve user from Neon database (using username field for email)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue JWT token
    access_token = create_access_token(data={"sub": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Protected endpoint requiring a valid JWT Bearer token."""
    return current_user