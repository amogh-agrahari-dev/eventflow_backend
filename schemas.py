from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str
    role: str = "user"

class EventCreate(BaseModel):
    title: str
    description: str | None = None
    category: str = "Technical"
    location: str | None = None
    start_time: datetime
    end_time: datetime
    is_free: bool = True
    format: str
    max_attendees: int = 100
    volunteers_required: int = 5
    organizer_id: int

# 2. Schema for outgoing data (API responses)
class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    category: str
    location: str | None = None
    start_time: datetime
    end_time: datetime
    is_free: bool
    format: str
    max_attendees: int
    volunteers_required: int
    organizer_id: int
    created_at: datetime

    # Instructs Pydantic to read from a SQLAlchemy ORM model
    model_config = ConfigDict(from_attributes=True)
class UserResponse(BaseModel):
    id: int
    name: Optional[str]
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str