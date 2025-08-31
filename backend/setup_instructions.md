# AI Email Agent - Production Setup Instructions

## 1. Environment Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Gmail API credentials
- OpenAI API key (or Anthropic Claude API key)

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt

# Install spaCy model for NLP
python -m spacy download en_core_web_sm
```

## 2. API Keys and Credentials Setup

### Gmail API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URIs:
   - `http://localhost:8000/auth/gmail/callback` (development)
   - `https://yourdomain.com/auth/gmail/callback` (production)

### OpenAI API Setup
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create API key
3. Set up billing and usage limits

### Anthropic Claude API Setup (Alternative)
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create API key
3. Set up billing

### Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**CRITICAL: Update these values in your .env file:**

```env
# Database - Replace with your PostgreSQL connection
DATABASE_URL=postgresql://username:password@localhost:5432/email_agent_db

# Security - Generate a strong secret key
SECRET_KEY=your-super-secret-key-here-generate-a-strong-one

# Gmail API - From Google Cloud Console
GMAIL_CLIENT_ID=your-gmail-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REDIRECT_URI=http://localhost:8000/auth/gmail/callback

# Google Calendar API
GOOGLE_CALENDAR_CLIENT_ID=your-calendar-client-id.apps.googleusercontent.com
GOOGLE_CALENDAR_CLIENT_SECRET=your-calendar-client-secret

# OpenAI API - From OpenAI Platform
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic Claude API (optional alternative)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Email Settings (for sending replies)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 3. Database Setup

### PostgreSQL Setup
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE email_agent_db;
CREATE USER email_agent_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE email_agent_db TO email_agent_user;
\q
```

### Redis Setup
```bash
# Install Redis (Ubuntu/Debian)
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Database Migration
```bash
# The app will create tables automatically on startup
# Or you can use Alembic for migrations:
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 4. Running the Application

### Development
```bash
# Start the FastAPI server
cd backend
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production with Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UnicornWorker --bind 0.0.0.0:8000
```

## 5. Frontend Integration

Update your React frontend to use the FastAPI backend:

```typescript
// In your React app, update the API base URL
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Example API calls
const fetchEmails = async () => {
  const response = await fetch(`${API_BASE_URL}/emails`);
  return response.json();
};

const generateSummary = async (emailId: number) => {
  const response = await fetch(`${API_BASE_URL}/summaries/${emailId}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'openai' })
  });
  return response.json();
};
```

## 6. Production Deployment

### Docker Setup
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UnicornWorker", "--bind", "0.0.0.0:8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/email_agent_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    env_file:
      - .env

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: email_agent_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/email-agent
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        root /var/www/email-agent/build;
        try_files $uri $uri/ /index.html;
    }
}
```

## 7. Background Tasks (Optional)

### Celery Setup for Background Processing
```bash
# Install Celery
pip install celery[redis]

# Start Celery worker
celery -A app.core.celery worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A app.core.celery beat --loglevel=info
```

## 8. Monitoring and Logging

### Health Checks
- API Health: `GET /health`
- Service Status: `GET /api/v1/status`

### Logging
Logs are configured in `app/main.py`. In production:
- Set `LOG_LEVEL=INFO` or `LOG_LEVEL=WARNING`
- Use structured logging with tools like ELK stack

### Monitoring
Consider adding:
- Prometheus metrics
- Sentry for error tracking
- APM tools like New Relic or DataDog

## 9. Security Considerations

### Production Security
1. **Environment Variables**: Never commit `.env` files
2. **HTTPS**: Use SSL certificates (Let's Encrypt)
3. **CORS**: Restrict origins in production
4. **Rate Limiting**: Add rate limiting middleware
5. **Authentication**: Implement proper JWT authentication
6. **API Keys**: Rotate API keys regularly
7. **Database**: Use connection pooling and read replicas

### Example Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/emails")
@limiter.limit("100/minute")
async def get_emails(request: Request):
    # Your endpoint logic
```

## 10. Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### API Testing
Use the interactive docs at `http://localhost:8000/docs` to test endpoints.

## 11. Scaling Considerations

### Horizontal Scaling
- Use load balancers (nginx, HAProxy)
- Multiple API instances behind load balancer
- Separate read/write database replicas

### Caching
- Redis for session storage and caching
- Cache email summaries and frequently accessed data

### Queue Management
- Use Celery with Redis/RabbitMQ for background tasks
- Separate queues for different task types (email processing, AI generation)

## 12. Cost Optimization

### AI API Usage
- Cache AI responses to avoid duplicate API calls
- Use cheaper models for simple tasks
- Implement request batching where possible
- Set usage limits and monitoring

### Database
- Use connection pooling
- Implement proper indexing
- Archive old emails to reduce query times

This setup provides a production-ready AI email agent with proper error handling, security, and scalability considerations.