from datetime import datetime,timezone
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String ,nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # profile_pic = Column(String, nullable=True)

class Attendee(Base):
    __tablename__ = "attendees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    # events=[ForeignKey("events.id")]
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = datetime


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    location = Column(String)  # GMaps integration later
    time = Column(DateTime, nullable=False)
    isPaid = Column(Boolean, default=False)
    organizer_email = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)