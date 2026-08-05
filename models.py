from datetime import datetime, timezone
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(String, default="on-duty")
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # status = Column(String, default="on-duty")
    # Relationships
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    events_organized: Mapped[List["Event"]] = relationship("Event", back_populates="organizer")
    passes: Mapped[List["Pass"]] = relationship("Pass", back_populates="user", cascade="all, delete-orphan")

    attendence: Mapped[List["Attendence"]] = relationship("Attendence", back_populates="user", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, default="Technical")
    location = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_free = Column(Boolean, default=True)
    format = Column(String, nullable=False)
    max_attendees = Column(Integer, default=100)
    volunteers_required = Column(Integer, default=5)

    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organizer: Mapped["User"] = relationship("User", back_populates="events_organized")

    # Relationships
    passes: Mapped[List["Pass"]] = relationship("Pass", back_populates="event", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    importance = Column(String, default="medium")
    location = Column(String)
    status = Column(String, default="unassigned")

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="tasks")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Pass(Base):
    __tablename__ = "passes"
    status = Column(String, default="generated")
    id = Column(Integer, primary_key=True, index=True)
    pass_uid = Column(String ,nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="passes")
    user: Mapped["User"] = relationship("User", back_populates="passes")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Attendence(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="absent")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="attendence")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))