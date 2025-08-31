import openai
import anthropic
from typing import Dict, List, Any, Optional
import json
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Initialize OpenAI
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        
        # Initialize Anthropic
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def summarize_email(self, email_content: str, model: str = "openai") -> Dict[str, Any]:
        """Generate email summary using LLM"""
        prompt = f"""
        Analyze the following email and provide a comprehensive summary:

        Email Content:
        {email_content}

        Please provide a JSON response with the following structure:
        {{
            "summary": "Brief 2-3 sentence summary of the email",
            "key_points": ["List of 3-5 key points from the email"],
            "action_items": ["List of specific actions required"],
            "sentiment": "positive/neutral/negative",
            "urgency_score": 1-10,
            "category": "work/personal/promotional/social",
            "priority": "high/medium/low",
            "entities": {{
                "people": ["Names mentioned"],
                "organizations": ["Companies/organizations"],
                "dates": ["Important dates"],
                "locations": ["Places mentioned"]
            }}
        }}
        """
        
        try:
            if model == "openai" and settings.OPENAI_API_KEY:
                return await self._openai_completion(prompt)
            elif model == "anthropic" and settings.ANTHROPIC_API_KEY:
                return await self._anthropic_completion(prompt)
            else:
                raise ValueError(f"Model {model} not available or API key missing")
        
        except Exception as e:
            logger.error(f"Error in email summarization: {e}")
            return self._fallback_summary(email_content)
    
    async def generate_reply(self, email_content: str, tone: str = "professional", context: str = "") -> str:
        """Generate email reply using LLM"""
        tone_instructions = {
            "professional": "Write a professional, formal response",
            "friendly": "Write a warm, friendly response",
            "brief": "Write a concise, brief response"
        }
        
        prompt = f"""
        Generate a {tone} email reply to the following email:

        Original Email:
        {email_content}

        Additional Context:
        {context}

        Instructions:
        - {tone_instructions.get(tone, "Write a professional response")}
        - Be helpful and appropriate
        - Include proper greeting and closing
        - Keep it concise but complete
        - Do not include subject line
        
        Reply:
        """
        
        try:
            if settings.OPENAI_API_KEY:
                response = await openai.ChatCompletion.acreate(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful email assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            
            elif settings.ANTHROPIC_API_KEY:
                response = await self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return self._fallback_reply(tone)
    
    async def extract_tasks_and_events(self, email_content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract tasks and calendar events from email"""
        prompt = f"""
        Analyze the following email and extract any tasks, meetings, or events that should be added to a calendar or task list:

        Email Content:
        {email_content}

        Please provide a JSON response with the following structure:
        {{
            "tasks": [
                {{
                    "title": "Task title",
                    "description": "Task description",
                    "due_date": "YYYY-MM-DD or null",
                    "priority": "high/medium/low",
                    "type": "task/followup/deadline"
                }}
            ],
            "events": [
                {{
                    "title": "Event title",
                    "description": "Event description",
                    "start_time": "YYYY-MM-DD HH:MM or null",
                    "end_time": "YYYY-MM-DD HH:MM or null",
                    "location": "Location or null",
                    "attendees": ["email1@example.com"],
                    "type": "meeting/call/event"
                }}
            ]
        }}
        
        Only extract items that are clearly actionable or scheduled. Return empty arrays if no tasks or events are found.
        """
        
        try:
            if settings.OPENAI_API_KEY:
                response = await openai.ChatCompletion.acreate(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts tasks and events from emails."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content)
                return result
        
        except Exception as e:
            logger.error(f"Error extracting tasks and events: {e}")
            return {"tasks": [], "events": []}
    
    async def _openai_completion(self, prompt: str) -> Dict[str, Any]:
        """Get completion from OpenAI"""
        response = await openai.ChatCompletion.acreate(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful email analysis assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    async def _anthropic_completion(self, prompt: str) -> Dict[str, Any]:
        """Get completion from Anthropic Claude"""
        response = await self.anthropic_client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        return json.loads(content)
    
    def _fallback_summary(self, email_content: str) -> Dict[str, Any]:
        """Fallback summary when LLM is unavailable"""
        return {
            "summary": f"Email summary unavailable. Content preview: {email_content[:100]}...",
            "key_points": ["LLM service unavailable"],
            "action_items": [],
            "sentiment": "neutral",
            "urgency_score": 5,
            "category": "work",
            "priority": "medium",
            "entities": {"people": [], "organizations": [], "dates": [], "locations": []}
        }
    
    def _fallback_reply(self, tone: str) -> str:
        """Fallback reply when LLM is unavailable"""
        replies = {
            "professional": "Thank you for your email. I will review this and get back to you soon.",
            "friendly": "Hi! Thanks for reaching out. I'll take a look at this and respond shortly.",
            "brief": "Thanks for the email. Will respond soon."
        }
        return replies.get(tone, replies["professional"])