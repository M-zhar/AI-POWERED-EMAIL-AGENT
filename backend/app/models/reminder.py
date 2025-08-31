from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ReminderTypeEnum(str, enum.Enum):
    TASK = "task"
    MEETING = "meeting"
    FOLLOWUP = "followup"
    DEADLINE = "deadline"
    CALL = "call"

class ReminderPriorityEnum(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)
    
    # Reminder content
    title = Column(String, index=True)
    description = Column(Text)
    
    # Scheduling
    due_date = Column(DateTime)
    reminder_time = Column(DateTime)  # When to send notification
    
    # Classification
    type = Column(String, default=ReminderTypeEnum.TASK)
    priority = Column(String, default=ReminderPriorityEnum.MEDIUM)
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    is_snoozed = Column(Boolean, default=False)
    snooze_until = Column(DateTime)
    
    # Notifications
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)
    
    # Calendar integration
    calendar_event_id = Column(String)  # Google Calendar event ID
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    email = relationship("Email", back_populates="reminders")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    google_event_id = Column(String, unique=True)
    
    # Event details
    title = Column(String)
    description = Column(Text)
    location = Column(String)
    
    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    timezone = Column(String)
    
    # Attendees
    attendees = Column(JSON)  # List of email addresses
    organizer = Column(String)
    
    # Status
    status = Column(String)  # confirmed, tentative, cancelled
    
    # AI-generated
    created_from_email = Column(Integer, ForeignKey("emails.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)