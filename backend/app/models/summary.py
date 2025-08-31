from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class EmailSummary(Base):
    __tablename__ = "email_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    
    # AI-generated content
    summary = Column(Text)
    key_points = Column(JSON)  # List of key points
    action_items = Column(JSON)  # List of action items
    entities = Column(JSON)  # Named entities extracted
    
    # Analysis scores
    sentiment_score = Column(Float)  # -1 to 1
    urgency_score = Column(Float)   # 1 to 10
    complexity_score = Column(Float)  # 1 to 10
    
    # Reply suggestions
    suggested_response = Column(Text)
    response_tone = Column(String)  # professional, friendly, brief
    
    # Processing metadata
    model_used = Column(String)  # gpt-4, claude-3, etc.
    processing_time = Column(Float)  # seconds
    confidence_score = Column(Float)  # 0 to 1
    
    # Relationships
    email = relationship("Email", back_populates="summaries")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReplyTemplate(Base):
    __tablename__ = "reply_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    name = Column(String)
    template = Column(Text)
    tone = Column(String)  # professional, friendly, brief
    category = Column(String)  # work, personal, etc.
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)