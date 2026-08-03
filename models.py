from datetime import datetime,timezone

from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String ,nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    events_organized = relationship("Event", back_populates="organizer")
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
    title = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, default="Technical")
    location = Column(String)  # GMaps integration later
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_free = Column(Boolean, default=True)
    format = Column(String, nullable=False)
    max_attendees = Column(Integer, default=100)
    volunteers_required = Column(Integer, default=5)
    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organizer = relationship("User", back_populates="events_organized")
    created_at = Column(DateTime, default=datetime.utcnow)