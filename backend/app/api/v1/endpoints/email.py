from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....models.email import Email, User
from ....services.gmail_service import GmailService
from ....services.llm_service import LLMService
from ....services.nlp_service import NLPService
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class EmailResponse(BaseModel):
    id: int
    gmail_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    timestamp: datetime
    is_read: bool
    priority: str
    category: str
    sentiment: str
    urgency_score: float
    has_attachment: bool

class EmailSyncRequest(BaseModel):
    max_results: Optional[int] = 50
    query: Optional[str] = ""

class EmailReplyRequest(BaseModel):
    email_id: int
    reply_text: str
    tone: Optional[str] = "professional"

# Initialize services
gmail_service = GmailService()
llm_service = LLMService()
nlp_service = NLPService()

@router.get("/emails", response_model=List[EmailResponse])
async def get_emails(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get emails with filtering options"""
    query = db.query(Email)
    
    if category:
        query = query.filter(Email.category == category)
    if priority:
        query = query.filter(Email.priority == priority)
    if is_read is not None:
        query = query.filter(Email.is_read == is_read)
    
    emails = query.offset(skip).limit(limit).all()
    return emails

@router.get("/emails/{email_id}", response_model=EmailResponse)
async def get_email(email_id: int, db: Session = Depends(get_db)):
    """Get specific email by ID"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.post("/emails/sync")
async def sync_emails(
    request: EmailSyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Sync emails from Gmail"""
    # This would typically get user from JWT token
    user = db.query(User).first()  # Simplified for demo
    
    if not user or not user.gmail_token:
        raise HTTPException(status_code=401, detail="Gmail not connected")
    
    try:
        # Build Gmail service
        token_data = {
            "access_token": user.gmail_token,
            "refresh_token": user.gmail_refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": gmail_service.client_id,
            "client_secret": gmail_service.client_secret,
            "scopes": gmail_service.scopes
        }
        
        service = gmail_service.build_service(token_data)
        
        # Fetch emails
        gmail_emails = gmail_service.fetch_emails(
            service, 
            query=request.query, 
            max_results=request.max_results
        )
        
        # Process emails in background
        background_tasks.add_task(process_emails, gmail_emails, user.id, db)
        
        return {"message": f"Syncing {len(gmail_emails)} emails", "count": len(gmail_emails)}
    
    except Exception as e:
        logger.error(f"Email sync error: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync emails")

@router.post("/emails/{email_id}/mark-read")
async def mark_email_read(email_id: int, db: Session = Depends(get_db)):
    """Mark email as read"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email.is_read = True
    db.commit()
    
    return {"message": "Email marked as read"}

@router.post("/emails/{email_id}/reply")
async def send_reply(
    email_id: int,
    request: EmailReplyRequest,
    db: Session = Depends(get_db)
):
    """Send reply to email"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    user = email.user
    if not user.gmail_token:
        raise HTTPException(status_code=401, detail="Gmail not connected")
    
    try:
        # Build Gmail service
        token_data = {
            "access_token": user.gmail_token,
            "refresh_token": user.gmail_refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": gmail_service.client_id,
            "client_secret": gmail_service.client_secret,
            "scopes": gmail_service.scopes
        }
        
        service = gmail_service.build_service(token_data)
        
        # Send reply
        result = gmail_service.send_email(
            service,
            to=email.sender,
            subject=f"Re: {email.subject}",
            body=request.reply_text
        )
        
        return {"message": "Reply sent successfully", "message_id": result.get('id')}
    
    except Exception as e:
        logger.error(f"Reply send error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reply")

@router.post("/emails/{email_id}/generate-reply")
async def generate_reply(
    email_id: int,
    tone: str = "professional",
    db: Session = Depends(get_db)
):
    """Generate AI reply for email"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    try:
        reply = await llm_service.generate_reply(
            email_content=f"Subject: {email.subject}\n\n{email.body}",
            tone=tone
        )
        
        return {"reply": reply, "tone": tone}
    
    except Exception as e:
        logger.error(f"Reply generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate reply")

async def process_emails(gmail_emails: List[dict], user_id: int, db: Session):
    """Background task to process and analyze emails"""
    for gmail_email in gmail_emails:
        try:
            # Check if email already exists
            existing = db.query(Email).filter(Email.gmail_id == gmail_email['gmail_id']).first()
            if existing:
                continue
            
            # Analyze email with NLP
            analysis = nlp_service.analyze_email(
                gmail_email['body'], 
                gmail_email['subject']
            )
            
            # Create email record
            email = Email(
                gmail_id=gmail_email['gmail_id'],
                user_id=user_id,
                sender=gmail_email['sender'],
                recipient=gmail_email['recipient'],
                subject=gmail_email['subject'],
                body=gmail_email['body'],
                html_body=gmail_email.get('html_body', ''),
                timestamp=datetime.fromisoformat(gmail_email['timestamp'].replace('Z', '+00:00')),
                has_attachment=gmail_email['has_attachment'],
                thread_id=gmail_email['thread_id'],
                priority=analysis['priority'],
                category=analysis['category'],
                sentiment=analysis['sentiment']['sentiment'],
                urgency_score=analysis['urgency_score'],
                is_processed=True,
                processed_at=datetime.utcnow()
            )
            
            db.add(email)
            db.commit()
            
            # Generate summary with LLM
            try:
                summary_data = await llm_service.summarize_email(
                    f"Subject: {email.subject}\n\n{email.body}"
                )
                
                # Save summary (you would create EmailSummary model)
                # This is where you'd save the LLM-generated summary
                
            except Exception as e:
                logger.error(f"Summary generation failed for email {email.id}: {e}")
        
        except Exception as e:
            logger.error(f"Email processing failed: {e}")
            continue