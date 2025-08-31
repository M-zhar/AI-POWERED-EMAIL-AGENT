from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....models.reminder import CalendarEvent
from ....models.email import User
from ....services.calendar_service import CalendarService
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    attendees: List[str]
    status: str

class CreateEventRequest(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = []
    timezone: Optional[str] = "UTC"

class UpdateEventRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None

# Initialize service
calendar_service = CalendarService()

@router.get("/events", response_model=List[CalendarEventResponse])
async def get_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get calendar events"""
    query = db.query(CalendarEvent)
    
    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.end_time <= end_date)
    
    events = query.order_by(CalendarEvent.start_time).limit(limit).all()
    return events

@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get specific calendar event"""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/events", response_model=CalendarEventResponse)
async def create_event(
    request: CreateEventRequest,
    db: Session = Depends(get_db)
):
    """Create new calendar event"""
    # Create local event record
    event = CalendarEvent(
        user_id=1,  # Simplified - would get from JWT token
        title=request.title,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time,
        location=request.location,
        attendees=request.attendees or [],
        status="confirmed"
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Try to create in Google Calendar if connected
    try:
        user = db.query(User).filter(User.id == 1).first()
        if user and user.calendar_token:
            token_data = {
                "access_token": user.calendar_token,
                "refresh_token": user.calendar_refresh_token,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": calendar_service.client_id,
                "client_secret": calendar_service.client_secret,
                "scopes": calendar_service.scopes
            }
            
            service = calendar_service.build_service(token_data)
            
            google_event = calendar_service.create_event(service, {
                "title": request.title,
                "description": request.description,
                "start_time": request.start_time.isoformat(),
                "end_time": request.end_time.isoformat(),
                "location": request.location,
                "attendees": request.attendees,
                "timezone": request.timezone
            })
            
            if google_event:
                event.google_event_id = google_event['google_event_id']
                db.commit()
    
    except Exception as e:
        logger.error(f"Failed to create Google Calendar event: {e}")
        # Continue anyway - local event is created
    
    return event

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    request: UpdateEventRequest,
    db: Session = Depends(get_db)
):
    """Update calendar event"""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update local event
    if request.title is not None:
        event.title = request.title
    if request.description is not None:
        event.description = request.description
    if request.start_time is not None:
        event.start_time = request.start_time
    if request.end_time is not None:
        event.end_time = request.end_time
    if request.location is not None:
        event.location = request.location
    if request.attendees is not None:
        event.attendees = request.attendees
    
    db.commit()
    
    # Try to update Google Calendar event
    try:
        if event.google_event_id:
            user = db.query(User).filter(User.id == event.user_id).first()
            if user and user.calendar_token:
                token_data = {
                    "access_token": user.calendar_token,
                    "refresh_token": user.calendar_refresh_token,
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": calendar_service.client_id,
                    "client_secret": calendar_service.client_secret,
                    "scopes": calendar_service.scopes
                }
                
                service = calendar_service.build_service(token_data)
                
                update_data = {}
                if request.title is not None:
                    update_data["title"] = request.title
                if request.description is not None:
                    update_data["description"] = request.description
                if request.start_time is not None:
                    update_data["start_time"] = request.start_time.isoformat()
                if request.end_time is not None:
                    update_data["end_time"] = request.end_time.isoformat()
                if request.location is not None:
                    update_data["location"] = request.location
                
                calendar_service.update_event(service, event.google_event_id, update_data)
    
    except Exception as e:
        logger.error(f"Failed to update Google Calendar event: {e}")
    
    return event

@router.delete("/events/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete calendar event"""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Try to delete from Google Calendar
    try:
        if event.google_event_id:
            user = db.query(User).filter(User.id == event.user_id).first()
            if user and user.calendar_token:
                token_data = {
                    "access_token": user.calendar_token,
                    "refresh_token": user.calendar_refresh_token,
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": calendar_service.client_id,
                    "client_secret": calendar_service.client_secret,
                    "scopes": calendar_service.scopes
                }
                
                service = calendar_service.build_service(token_data)
                calendar_service.delete_event(service, event.google_event_id)
    
    except Exception as e:
        logger.error(f"Failed to delete Google Calendar event: {e}")
    
    # Delete local event
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}

@router.get("/events/sync")
async def sync_calendar_events(db: Session = Depends(get_db)):
    """Sync events from Google Calendar"""
    user = db.query(User).filter(User.id == 1).first()  # Simplified
    
    if not user or not user.calendar_token:
        raise HTTPException(status_code=401, detail="Google Calendar not connected")
    
    try:
        token_data = {
            "access_token": user.calendar_token,
            "refresh_token": user.calendar_refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": calendar_service.client_id,
            "client_secret": calendar_service.client_secret,
            "scopes": calendar_service.scopes
        }
        
        service = calendar_service.build_service(token_data)
        google_events = calendar_service.get_upcoming_events(service, max_results=50)
        
        synced_count = 0
        for google_event in google_events:
            # Check if event already exists
            existing = db.query(CalendarEvent).filter(
                CalendarEvent.google_event_id == google_event['google_event_id']
            ).first()
            
            if not existing:
                event = CalendarEvent(
                    user_id=user.id,
                    google_event_id=google_event['google_event_id'],
                    title=google_event['title'],
                    description=google_event['description'],
                    start_time=datetime.fromisoformat(google_event['start_time'].replace('Z', '+00:00')),
                    end_time=datetime.fromisoformat(google_event['end_time'].replace('Z', '+00:00')),
                    location=google_event.get('location', ''),
                    attendees=google_event.get('attendees', []),
                    organizer=google_event.get('organizer', ''),
                    status=google_event.get('status', 'confirmed')
                )
                
                db.add(event)
                synced_count += 1
        
        db.commit()
        
        return {"message": f"Synced {synced_count} events from Google Calendar"}
    
    except Exception as e:
        logger.error(f"Calendar sync error: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync calendar events")

@router.get("/events/free-time")
async def find_free_time(
    duration_minutes: int = 60,
    days_ahead: int = 7,
    db: Session = Depends(get_db)
):
    """Find free time slots"""
    user = db.query(User).filter(User.id == 1).first()  # Simplified
    
    if not user or not user.calendar_token:
        # Return basic free time based on local events
        now = datetime.utcnow()
        end_time = now + timedelta(days=days_ahead)
        
        busy_events = db.query(CalendarEvent).filter(
            CalendarEvent.start_time >= now,
            CalendarEvent.end_time <= end_time,
            CalendarEvent.user_id == user.id if user else 1
        ).all()
        
        # Simple free time calculation (9 AM to 5 PM weekdays)
        free_slots = []
        current_date = now.date()
        
        for day in range(days_ahead):
            if current_date.weekday() < 5:  # Monday to Friday
                day_start = datetime.combine(current_date, datetime.min.time().replace(hour=9))
                day_end = datetime.combine(current_date, datetime.min.time().replace(hour=17))
                
                # Check for conflicts (simplified)
                slot_start = day_start
                while slot_start + timedelta(minutes=duration_minutes) <= day_end:
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    # Check if slot conflicts with existing events
                    conflict = False
                    for event in busy_events:
                        if (slot_start < event.end_time and slot_end > event.start_time):
                            conflict = True
                            break
                    
                    if not conflict:
                        free_slots.append({
                            "start": slot_start.isoformat(),
                            "end": slot_end.isoformat()
                        })
                    
                    slot_start += timedelta(hours=1)
            
            current_date += timedelta(days=1)
        
        return {"free_slots": free_slots[:10]}
    
    try:
        token_data = {
            "access_token": user.calendar_token,
            "refresh_token": user.calendar_refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": calendar_service.client_id,
            "client_secret": calendar_service.client_secret,
            "scopes": calendar_service.scopes
        }
        
        service = calendar_service.build_service(token_data)
        free_slots = calendar_service.find_free_time(service, duration_minutes, days_ahead)
        
        return {"free_slots": free_slots}
    
    except Exception as e:
        logger.error(f"Free time search error: {e}")
        raise HTTPException(status_code=500, detail="Failed to find free time")