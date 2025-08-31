from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....models.email import Email
from ....models.summary import EmailSummary
from ....services.llm_service import LLMService
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class SummaryResponse(BaseModel):
    id: int
    email_id: int
    summary: str
    key_points: List[str]
    action_items: List[str]
    sentiment_score: float
    urgency_score: float
    suggested_response: Optional[str]
    response_tone: str
    confidence_score: float

class GenerateSummaryRequest(BaseModel):
    model: Optional[str] = "openai"  # or "anthropic"
    include_response: Optional[bool] = True
    response_tone: Optional[str] = "professional"

# Initialize service
llm_service = LLMService()

@router.get("/summaries/{email_id}", response_model=SummaryResponse)
async def get_email_summary(email_id: int, db: Session = Depends(get_db)):
    """Get summary for specific email"""
    summary = db.query(EmailSummary).filter(EmailSummary.email_id == email_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.post("/summaries/{email_id}/generate")
async def generate_email_summary(
    email_id: int,
    request: GenerateSummaryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate AI summary for email"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Check if summary already exists
    existing_summary = db.query(EmailSummary).filter(EmailSummary.email_id == email_id).first()
    if existing_summary:
        return {"message": "Summary already exists", "summary_id": existing_summary.id}
    
    # Generate summary in background
    background_tasks.add_task(
        create_email_summary, 
        email_id, 
        request.model, 
        request.include_response,
        request.response_tone,
        db
    )
    
    return {"message": "Summary generation started", "email_id": email_id}

@router.get("/summaries/{email_id}/status")
async def get_summary_status(email_id: int, db: Session = Depends(get_db)):
    """Check if summary exists for email"""
    summary = db.query(EmailSummary).filter(EmailSummary.email_id == email_id).first()
    return {
        "exists": summary is not None,
        "summary_id": summary.id if summary else None,
        "created_at": summary.created_at if summary else None
    }

@router.delete("/summaries/{summary_id}")
async def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    """Delete email summary"""
    summary = db.query(EmailSummary).filter(EmailSummary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    db.delete(summary)
    db.commit()
    
    return {"message": "Summary deleted successfully"}

@router.post("/summaries/batch-generate")
async def batch_generate_summaries(
    email_ids: List[int],
    model: str = "openai",
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate summaries for multiple emails"""
    # Verify all emails exist
    emails = db.query(Email).filter(Email.id.in_(email_ids)).all()
    if len(emails) != len(email_ids):
        raise HTTPException(status_code=404, detail="Some emails not found")
    
    # Filter out emails that already have summaries
    existing_summaries = db.query(EmailSummary).filter(EmailSummary.email_id.in_(email_ids)).all()
    existing_email_ids = {s.email_id for s in existing_summaries}
    
    new_email_ids = [eid for eid in email_ids if eid not in existing_email_ids]
    
    if not new_email_ids:
        return {"message": "All emails already have summaries", "count": 0}
    
    # Generate summaries in background
    for email_id in new_email_ids:
        background_tasks.add_task(create_email_summary, email_id, model, True, "professional", db)
    
    return {
        "message": f"Started generating {len(new_email_ids)} summaries",
        "count": len(new_email_ids),
        "skipped": len(existing_email_ids)
    }

async def create_email_summary(
    email_id: int, 
    model: str, 
    include_response: bool,
    response_tone: str,
    db: Session
):
    """Background task to create email summary"""
    try:
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            logger.error(f"Email {email_id} not found for summary generation")
            return
        
        # Generate summary with LLM
        start_time = datetime.utcnow()
        
        email_content = f"Subject: {email.subject}\n\nFrom: {email.sender}\nTo: {email.recipient}\n\n{email.body}"
        
        summary_data = await llm_service.summarize_email(email_content, model)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Generate response if requested
        suggested_response = None
        if include_response:
            try:
                suggested_response = await llm_service.generate_reply(
                    email_content, 
                    tone=response_tone
                )
            except Exception as e:
                logger.error(f"Response generation failed for email {email_id}: {e}")
        
        # Create summary record
        summary = EmailSummary(
            email_id=email_id,
            summary=summary_data.get('summary', ''),
            key_points=summary_data.get('key_points', []),
            action_items=summary_data.get('action_items', []),
            entities=summary_data.get('entities', {}),
            sentiment_score=summary_data.get('sentiment_score', 0.0),
            urgency_score=summary_data.get('urgency_score', 5.0),
            complexity_score=summary_data.get('complexity_score', 5.0),
            suggested_response=suggested_response,
            response_tone=response_tone,
            model_used=model,
            processing_time=processing_time,
            confidence_score=summary_data.get('confidence_score', 0.8)
        )
        
        db.add(summary)
        db.commit()
        
        logger.info(f"Summary created for email {email_id}")
        
    except Exception as e:
        logger.error(f"Summary generation failed for email {email_id}: {e}")
        db.rollback()