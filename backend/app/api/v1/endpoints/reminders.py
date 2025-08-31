from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....models.reminder import Reminder, CalendarEvent
from ....models.email import Email
from ....services.llm_service import LLMService
from ....services.calendar_service import CalendarService
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class ReminderResponse(BaseModel):
    id: int
    title: str
    description: str
    due_date: datetime
    type: str
    priority: str
    is_completed: bool
    email_id: Optional[int]

class CreateReminderRequest(BaseModel):
    title: str
    description: str
    due_date: datetime
    type: str = "task"
    priority: str = "medium"
    email_id: Optional[int] = None

class UpdateReminderRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    is_completed: Optional[bool] = None

# Initialize services
llm_service = LLMService()
calendar_service = CalendarService()

@router.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(
    skip: int = 0,
    limit: int = 50,
    is_completed: Optional[bool] = None,
    priority: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get reminders with filtering"""
    query = db.query(Reminder)
    
    if is_completed is not None:
        query = query.filter(Reminder.is_completed == is_completed)
    if priority:
        query = query.filter(Reminder.priority == priority)
    if type:
        query = query.filter(Reminder.type == type)
    
    reminders = query.order_by(Reminder.due_date).offset(skip).limit(limit).all()
    return reminders

@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Get specific reminder"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@router.post("/reminders", response_model=ReminderResponse)
async def create_reminder(
    request: CreateReminderRequest,
    db: Session = Depends(get_db)
):
    """Create new reminder"""
    reminder = Reminder(
        user_id=1,  # Simplified - would get from JWT token
        title=request.title,
        description=request.description,
        due_date=request.due_date,
        type=request.type,
        priority=request.priority,
        email_id=request.email_id,
        reminder_time=request.due_date - timedelta(hours=1)  # Default 1 hour before
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    return reminder

@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    request: UpdateReminderRequest,
    db: Session = Depends(get_db)
):
    """Update reminder"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    if request.title is not None:
        reminder.title = request.title
    if request.description is not None:
        reminder.description = request.description
    if request.due_date is not None:
        reminder.due_date = request.due_date
    if request.priority is not None:
        reminder.priority = request.priority
    if request.is_completed is not None:
        reminder.is_completed = request.is_completed
        if request.is_completed:
            reminder.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(reminder)
    
    return reminder

@router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Delete reminder"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    
    return {"message": "Reminder deleted successfully"}

@router.post("/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Mark reminder as completed"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.is_completed = True
    reminder.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Reminder marked as completed"}

@router.post("/reminders/{reminder_id}/snooze")
async def snooze_reminder(
    reminder_id: int,
    snooze_until: datetime,
    db: Session = Depends(get_db)
):
    """Snooze reminder until specified time"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.is_snoozed = True
    reminder.snooze_until = snooze_until
    
    db.commit()
    
    return {"message": f"Reminder snoozed until {snooze_until}"}

@router.post("/reminders/extract-from-email/{email_id}")
async def extract_reminders_from_email(
    email_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Extract reminders and events from email using AI"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Extract tasks and events in background
    background_tasks.add_task(process_email_for_reminders, email_id, db)
    
    return {"message": "Processing email for reminders and events"}

@router.get("/reminders/overdue")
async def get_overdue_reminders(db: Session = Depends(get_db)):
    """Get overdue reminders"""
    now = datetime.utcnow()
    overdue = db.query(Reminder).filter(
        Reminder.due_date < now,
        Reminder.is_completed == False,
        Reminder.is_snoozed == False
    ).all()
    
    return {"count": len(overdue), "reminders": overdue}

@router.get("/reminders/upcoming")
async def get_upcoming_reminders(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get reminders due in next X hours"""
    now = datetime.utcnow()
    future = now + timedelta(hours=hours)
    
    upcoming = db.query(Reminder).filter(
        Reminder.due_date.between(now, future),
        Reminder.is_completed == False,
        Reminder.is_snoozed == False
    ).order_by(Reminder.due_date).all()
    
    return {"count": len(upcoming), "reminders": upcoming}

async def process_email_for_reminders(email_id: int, db: Session):
    """Background task to extract reminders from email"""
    try:
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            return
        
        # Extract tasks and events using LLM
        email_content = f"Subject: {email.subject}\n\n{email.body}"
        extracted = await llm_service.extract_tasks_and_events(email_content)
        
        # Create reminders for tasks
        for task_data in extracted.get('tasks', []):
            try:
                due_date = None
                if task_data.get('due_date'):
                    due_date = datetime.fromisoformat(task_data['due_date'])
                else:
                    # Default to 1 week from now if no due date
                    due_date = datetime.utcnow() + timedelta(days=7)
                
                reminder = Reminder(
                    user_id=email.user_id,
                    email_id=email_id,
                    title=task_data['title'],
                    description=task_data.get('description', ''),
                    due_date=due_date,
                    type=task_data.get('type', 'task'),
                    priority=task_data.get('priority', 'medium'),
                    reminder_time=due_date - timedelta(hours=2)
                )
                
                db.add(reminder)
                
            except Exception as e:
                logger.error(f"Failed to create reminder from task: {e}")
                continue
        
        # Create calendar events
        for event_data in extracted.get('events', []):
            try:
                if not event_data.get('start_time'):
                    continue
                
                start_time = datetime.fromisoformat(event_data['start_time'])
                end_time = start_time + timedelta(hours=1)  # Default 1 hour
                
                if event_data.get('end_time'):
                    end_time = datetime.fromisoformat(event_data['end_time'])
                
                calendar_event = CalendarEvent(
                    user_id=email.user_id,
                    title=event_data['title'],
                    description=event_data.get('description', ''),
                    start_time=start_time,
                    end_time=end_time,
                    location=event_data.get('location'),
                    attendees=event_data.get('attendees', []),
                    created_from_email=email_id
                )
                
                db.add(calendar_event)
                
                # Also create a reminder for the event
                reminder = Reminder(
                    user_id=email.user_id,
                    email_id=email_id,
                    title=f"Meeting: {event_data['title']}",
                    description=f"Upcoming meeting at {start_time}",
                    due_date=start_time,
                    type="meeting",
                    priority="medium",
                    reminder_time=start_time - timedelta(minutes=15)
                )
                
                db.add(reminder)
                
            except Exception as e:
                logger.error(f"Failed to create calendar event: {e}")
                continue
        
        db.commit()
        logger.info(f"Processed email {email_id} for reminders and events")
        
    except Exception as e:
        logger.error(f"Failed to process email {email_id} for reminders: {e}")
        db.rollback()