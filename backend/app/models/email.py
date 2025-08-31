from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class PriorityEnum(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CategoryEnum(str, enum.Enum):
    WORK = "work"
    PERSONAL = "personal"
    PROMOTIONAL = "promotional"
    SOCIAL = "social"

class SentimentEnum(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    gmail_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Email content
    sender = Column(String, index=True)
    recipient = Column(String)
    subject = Column(String, index=True)
    body = Column(Text)
    html_body = Column(Text)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    has_attachment = Column(Boolean, default=False)
    thread_id = Column(String)
    
    # AI Analysis
    priority = Column(String, default=PriorityEnum.MEDIUM)
    category = Column(String, default=CategoryEnum.WORK)
    sentiment = Column(String, default=SentimentEnum.NEUTRAL)
    urgency_score = Column(Float, default=5.0)  # 1-10 scale
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="emails")
    summaries = relationship("EmailSummary", back_populates="email")
    reminders = relationship("Reminder", back_populates="email")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    
    # OAuth tokens
    gmail_token = Column(Text)
    gmail_refresh_token = Column(Text)
    calendar_token = Column(Text)
    calendar_refresh_token = Column(Text)
    
    # Settings
    is_active = Column(Boolean, default=True)
    timezone = Column(String, default="UTC")
    
    # Relationships
    emails = relationship("Email", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)