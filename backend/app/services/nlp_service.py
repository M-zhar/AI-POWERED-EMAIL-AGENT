import spacy
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import re
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime, timedelta
import dateutil.parser as date_parser

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        try:
            # Load spaCy model (download with: python -m spacy download en_core_web_sm)
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize classifiers (you would train these with your data)
        self.priority_classifier = None
        self.category_classifier = None
        
        # Urgency keywords
        self.urgency_keywords = {
            "high": ["urgent", "asap", "immediately", "emergency", "critical", "deadline", "today"],
            "medium": ["soon", "this week", "important", "please", "need", "required"],
            "low": ["when you can", "no rush", "fyi", "for your information"]
        }
    
    def analyze_email(self, email_content: str, subject: str = "") -> Dict[str, Any]:
        """Comprehensive email analysis"""
        full_text = f"{subject} {email_content}"
        
        return {
            "sentiment": self.analyze_sentiment(full_text),
            "urgency_score": self.calculate_urgency_score(full_text),
            "priority": self.classify_priority(full_text),
            "category": self.classify_category(full_text),
            "entities": self.extract_entities(full_text),
            "keywords": self.extract_keywords(full_text),
            "dates": self.extract_dates(full_text),
            "action_items": self.extract_action_items(email_content)
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Convert to categorical
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "confidence": abs(polarity)
            }
        
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "polarity": 0, "subjectivity": 0, "confidence": 0}
    
    def calculate_urgency_score(self, text: str) -> float:
        """Calculate urgency score based on keywords and patterns"""
        text_lower = text.lower()
        score = 5.0  # Base score
        
        # Check urgency keywords
        for level, keywords in self.urgency_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if level == "high":
                        score += 2.0
                    elif level == "medium":
                        score += 1.0
                    elif level == "low":
                        score -= 1.0
        
        # Check for time-sensitive patterns
        time_patterns = [
            r"by (?:today|tomorrow|end of day|eod)",
            r"deadline.*(?:today|tomorrow|this week)",
            r"need.*(?:asap|immediately|urgently)",
            r"meeting.*(?:today|tomorrow|in \d+ hours?)"
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, text_lower):
                score += 1.5
        
        # Check for question marks (might indicate need for response)
        question_count = text.count('?')
        score += min(question_count * 0.5, 2.0)
        
        # Normalize to 1-10 scale
        return max(1.0, min(10.0, score))
    
    def classify_priority(self, text: str) -> str:
        """Classify email priority"""
        urgency_score = self.calculate_urgency_score(text)
        
        if urgency_score >= 7:
            return "high"
        elif urgency_score >= 4:
            return "medium"
        else:
            return "low"
    
    def classify_category(self, text: str) -> str:
        """Classify email category"""
        text_lower = text.lower()
        
        # Simple keyword-based classification
        work_keywords = ["meeting", "project", "deadline", "report", "client", "business", "office"]
        personal_keywords = ["family", "friend", "personal", "vacation", "birthday", "wedding"]
        promotional_keywords = ["sale", "discount", "offer", "promotion", "deal", "buy", "shop"]
        social_keywords = ["linkedin", "facebook", "twitter", "social", "network", "connect"]
        
        work_score = sum(1 for keyword in work_keywords if keyword in text_lower)
        personal_score = sum(1 for keyword in personal_keywords if keyword in text_lower)
        promotional_score = sum(1 for keyword in promotional_keywords if keyword in text_lower)
        social_score = sum(1 for keyword in social_keywords if keyword in text_lower)
        
        scores = {
            "work": work_score,
            "personal": personal_score,
            "promotional": promotional_score,
            "social": social_score
        }
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "work"
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return {"people": [], "organizations": [], "locations": [], "dates": []}
        
        try:
            doc = self.nlp(text)
            
            entities = {
                "people": [],
                "organizations": [],
                "locations": [],
                "dates": []
            }
            
            for ent in doc.ents:
                if ent.label_ in ["PERSON"]:
                    entities["people"].append(ent.text)
                elif ent.label_ in ["ORG"]:
                    entities["organizations"].append(ent.text)
                elif ent.label_ in ["GPE", "LOC"]:
                    entities["locations"].append(ent.text)
                elif ent.label_ in ["DATE", "TIME"]:
                    entities["dates"].append(ent.text)
            
            # Remove duplicates
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
        
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return {"people": [], "organizations": [], "locations": [], "dates": []}
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords using TF-IDF"""
        try:
            # Simple keyword extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Remove common stop words
            stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "man", "new", "now", "old", "see", "two", "way", "who", "boy", "did", "its", "let", "put", "say", "she", "too", "use"}
            
            keywords = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Count frequency
            word_freq = {}
            for word in keywords:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_keywords[:max_keywords]]
        
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return []
    
    def extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates and times from text"""
        dates = []
        
        # Common date patterns
        date_patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b(?:today|tomorrow|yesterday)\b',
            r'\b(?:next|this)\s+(?:week|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group()
                try:
                    # Try to parse the date
                    parsed_date = date_parser.parse(date_text, fuzzy=True)
                    dates.append({
                        "text": date_text,
                        "parsed": parsed_date.isoformat(),
                        "position": match.span()
                    })
                except:
                    # If parsing fails, still record the text
                    dates.append({
                        "text": date_text,
                        "parsed": None,
                        "position": match.span()
                    })
        
        return dates
    
    def extract_action_items(self, text: str) -> List[str]:
        """Extract potential action items from email"""
        action_items = []
        
        # Action patterns
        action_patterns = [
            r'(?:please|could you|can you|would you)\s+([^.!?]+)',
            r'(?:need to|have to|must|should)\s+([^.!?]+)',
            r'(?:action required|action needed|todo|to do):\s*([^.!?]+)',
            r'(?:deadline|due)\s+([^.!?]+)',
            r'(?:schedule|arrange|set up)\s+([^.!?]+)'
        ]
        
        for pattern in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                action_text = match.group(1).strip()
                if len(action_text) > 10:  # Filter out very short matches
                    action_items.append(action_text)
        
        return action_items[:5]  # Limit to top 5 action items