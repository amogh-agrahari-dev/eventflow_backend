
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
from models import User, Event
from schemas import Token, UserCreate, UserResponse, LoginRequest, EventCreate, EventResponse
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

@app.get("/", )
def root():
    return {"message": "Welcome To EventHub"}
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


@app.post("/events/create", status_code=status.HTTP_201_CREATED, response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    # 1. Verify the user exists
    user = db.query(User).filter(User.id == event.organizer_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 2. Create the event
    new_event = Event(**event.model_dump())

    # 3. Save to database
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # 4. Return the new event
    return new_event

@app.get("/events/all", response_model=list[EventResponse])
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events

@app.get("/events/{user_id}", response_model=list[EventResponse])
def get_user_events(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    events = db.query(Event).filter(Event.organizer_id == user_id).all()
    return events

@app.delete("/events/{event_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, user_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if(user_id != event.organizer_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        db.delete(event)
        db.commit()
    return {"message": f"Event with id {event_id} deleted"}
