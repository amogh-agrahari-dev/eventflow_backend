import secrets
import string
from http.client import HTTPResponse
from random import random

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
from models import User, Event, Task, Pass, Attendence
from schemas import Token, UserCreate, UserResponse, LoginRequest, EventCreate, EventResponse, TaskResponse, TaskCreate, \
    PassCreate, PassResponse, AttendenceResponse, AttendenceCreate
from sqlalchemy.orm import Session

# Create database tables automatically
Base.metadata.create_all(bind=engine)
app = FastAPI(title="EventHub API")
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

@app.post("/tasks/create", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task assigned to a user."""
    # Verify the referenced user exists
    user = db.query(User).filter(User.id == task.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {task.user_id} not found"
        )

    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/{user_id}", response_model=list[TaskResponse])
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks

@app.delete("/tasks/{task_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(task_id: int, user_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if(user_id != task.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        db.delete(task)
        db.commit()
    return {"message": f"Event with id {task_id} deleted"}

@app.post("/pass/create", status_code=status.HTTP_201_CREATED, response_model=PassResponse)
def create_pass(pass1:PassCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == pass1.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    alphanumeric = string.ascii_letters + string.digits
    secure_string = ''.join(secrets.choice(alphanumeric) for _ in range(12))
    new_pass = Pass(
        event_id=pass1.event_id,
        user_id=pass1.user_id,
        pass_uid=secure_string,
    )

    db.add(new_pass)
    db.commit()
    db.refresh(new_pass)
    return new_pass

@app.get("/passes/{user_id}", response_model=list[PassResponse])
def get_pass(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    passes = db.query(Pass).filter(Pass.user_id == user_id).all()
    return passes

@app.put("/passes/{user_id}", response_model=PassResponse)
def update_pass(user_id: int, pass1: PassCreate, db: Session = Depends(get_db)):
    # Only the authenticated user may update their own pass

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    pass2 = db.query(Pass).filter(Pass.user_id == user_id).first()
    if not pass2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pass not found")

    # Update only the status field
    pass2.status = pass1.status

    db.commit()
    db.refresh(pass2)
    return pass2

@app.delete("/passes/{pass_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pass(pass_id: int,user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    pass1 = db.query(Pass).filter(Pass.pass_id == pass_id).first()
    if not pass1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pass not found")
    if user_id != pass1.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        db.delete(pass1)
        db.commit()
        return {"message": "Pass deleted"}

@app.post("/attendence/mark", response_model=AttendenceResponse)
def mark_attendence(attendence:AttendenceCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == attendence.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db_attendence = Attendence(**attendence.model_dump())
    db.add(db_attendence)
    db.commit()
    return db_attendence

@app.put("/users/{user_id}", response_model=UserResponse)
def update_status_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db_user.status = user.status
    db.commit()
    return db_user
