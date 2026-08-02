
from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, status
# 1. Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from models import User
from schemas import Token, UserCreate, UserResponse, LoginRequest
from sqlalchemy.orm import Session

# Create database tables automatically
Base.metadata.create_all(bind=engine)
app = FastAPI(title="FastAPI + Neon JWT Auth")
origins = [
    "http://localhost:3000",  # Typical React / Next.js default port
    "http://localhost:3001",  # Typical Vite default port
    "https://eventflow-frontend-tau.vercel.app"
]

# 3. Add CORSMiddleware to your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from specified origins
    allow_credentials=True,  # Allows cookies/authorization headers (JWT Bearer)
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers (Authorization, Content-Type, etc.)
)
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
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        name=user_data.name,
        role=user_data.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=Token)
def login(
    credentials: LoginRequest,  # Accepts JSON body: {"email": "...", "password": "..."}
    db: Session = Depends(get_db),
):
    # Query database using credentials.email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue JWT token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Protected endpoint requiring a valid JWT Bearer token."""
    return current_user

# @app.post(
#     "/events/",
#     response_model=EventResponse,
#     status_code=status.HTTP_201_CREATED,
#     summary="Create a new event"
# )
# def create_event(
#     event_data: EventCreate,
#     db: Session = Depends(get_db), # Requires user to be logged in
# ):
#     user_email = event_data.organizer_email
#     if not user_email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Authenticated user missing email address."
#         )
#
#     # Instantiate event model with user's email
#     new_event = Event(
#         name=event_data.name,
#         description=event_data.description,
#         location=event_data.location,
#         time=event_data.time,
#         isPaid=event_data.isPaid,
#         organizer_email=user_email  # Set string email directly
#     )
#
#     db.add(new_event)
#     db.commit()
#     db.refresh(new_event)
#
#     return new_event