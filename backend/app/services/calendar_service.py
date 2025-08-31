from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self):
        self.scopes = settings.CALENDAR_SCOPES
        self.client_id = settings.GOOGLE_CALENDAR_CLIENT_ID
        self.client_secret = settings.GOOGLE_CALENDAR_CLIENT_SECRET
    
    def build_service(self, token_data: Dict[str, Any]):
        """Build Calendar service with credentials"""
        credentials = Credentials(
            token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data["token_uri"],
            client_id=token_data["client_id"],
            client_secret=token_data["client_secret"],
            scopes=token_data["scopes"]
        )
        
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        
        return build('calendar', 'v3', credentials=credentials)
    
    def get_upcoming_events(self, service, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming calendar events"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            parsed_events = []
            for event in events:
                parsed_event = self._parse_event(event)
                parsed_events.append(parsed_event)
            
            return parsed_events
        
        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            return []
    
    def create_event(self, service, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new calendar event"""
        try:
            # Prepare event object
            event = {
                'summary': event_data['title'],
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data['start_time'],
                    'timeZone': event_data.get('timezone', 'UTC'),
                },
                'end': {
                    'dateTime': event_data['end_time'],
                    'timeZone': event_data.get('timezone', 'UTC'),
                },
            }
            
            # Add location if provided
            if event_data.get('location'):
                event['location'] = event_data['location']
            
            # Add attendees if provided
            if event_data.get('attendees'):
                event['attendees'] = [{'email': email} for email in event_data['attendees']]
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return self._parse_event(created_event)
        
        except HttpError as error:
            logger.error(f"Error creating calendar event: {error}")
            return None
    
    def update_event(self, service, event_id: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing calendar event"""
        try:
            # Get existing event
            existing_event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields
            if 'title' in event_data:
                existing_event['summary'] = event_data['title']
            if 'description' in event_data:
                existing_event['description'] = event_data['description']
            if 'start_time' in event_data:
                existing_event['start']['dateTime'] = event_data['start_time']
            if 'end_time' in event_data:
                existing_event['end']['dateTime'] = event_data['end_time']
            if 'location' in event_data:
                existing_event['location'] = event_data['location']
            
            # Update the event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=existing_event
            ).execute()
            
            return self._parse_event(updated_event)
        
        except HttpError as error:
            logger.error(f"Error updating calendar event: {error}")
            return None
    
    def delete_event(self, service, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
        
        except HttpError as error:
            logger.error(f"Error deleting calendar event: {error}")
            return False
    
    def find_free_time(self, service, duration_minutes: int = 60, days_ahead: int = 7) -> List[Dict[str, str]]:
        """Find free time slots in calendar"""
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Get busy times
            body = {
                "timeMin": time_min,
                "timeMax": time_max,
                "items": [{"id": "primary"}]
            }
            
            freebusy_result = service.freebusy().query(body=body).execute()
            busy_times = freebusy_result['calendars']['primary']['busy']
            
            # Find free slots (simplified logic)
            free_slots = []
            current_time = now.replace(minute=0, second=0, microsecond=0)
            
            for day in range(days_ahead):
                day_start = current_time.replace(hour=9)  # 9 AM
                day_end = current_time.replace(hour=17)   # 5 PM
                
                # Check each hour slot
                slot_start = day_start
                while slot_start + timedelta(minutes=duration_minutes) <= day_end:
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    # Check if slot conflicts with busy times
                    is_free = True
                    for busy in busy_times:
                        busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                        busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                        
                        if (slot_start < busy_end and slot_end > busy_start):
                            is_free = False
                            break
                    
                    if is_free:
                        free_slots.append({
                            'start': slot_start.isoformat() + 'Z',
                            'end': slot_end.isoformat() + 'Z'
                        })
                    
                    slot_start += timedelta(hours=1)
                
                current_time += timedelta(days=1)
            
            return free_slots[:10]  # Return top 10 slots
        
        except HttpError as error:
            logger.error(f"Error finding free time: {error}")
            return []
    
    def _parse_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Google Calendar event into our format"""
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        return {
            'google_event_id': event['id'],
            'title': event.get('summary', 'No Title'),
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'start_time': start,
            'end_time': end,
            'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
            'organizer': event.get('organizer', {}).get('email', ''),
            'status': event.get('status', 'confirmed'),
            'html_link': event.get('htmlLink', ''),
            'created': event.get('created', ''),
            'updated': event.get('updated', '')
        }