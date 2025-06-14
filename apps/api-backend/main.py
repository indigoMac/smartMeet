from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Any
import httpx
import jwt
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in project root (only for local development)
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists() and not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv(env_path)

app = FastAPI(title="SmartMeet API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    print("🚀 SmartMeet API starting up...")
    print(f"Environment variables loaded:")
    print(f"- MICROSOFT_CLIENT_ID: {'✓' if MICROSOFT_CLIENT_ID else '✗'}")
    print(f"- GOOGLE_CLIENT_ID: {'✓' if GOOGLE_CLIENT_ID else '✗'}")
    print(f"- FRONTEND_URL: {FRONTEND_URL}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Pydantic models
class AvailabilityRequest(BaseModel):
    emails: List[str]
    start_time: str
    end_time: str
    duration_minutes: int = 30

class MeetingProposal(BaseModel):
    meeting_id: str
    emails: List[str]
    proposed_times: List[Dict[str, Any]]

# In-memory storage (replace with database in production)
meetings_db = {}
tokens_db = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/connect/microsoft")
async def microsoft_oauth_start():
    """Start Microsoft OAuth flow"""
    if not MICROSOFT_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Microsoft OAuth not configured")
    
    state = str(uuid.uuid4())
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={MICROSOFT_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={MICROSOFT_REDIRECT_URI}"
        f"&scope=https://graph.microsoft.com/Calendars.Read.Shared offline_access"
        f"&state={state}"
        f"&response_mode=query"
    )
    return {"auth_url": auth_url, "state": state}

@app.get("/connect/microsoft/callback")
async def microsoft_oauth_callback(code: str, state: str):
    """Handle Microsoft OAuth callback"""
    try:
        # Exchange code for tokens
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        token_data = {
            "client_id": MICROSOFT_CLIENT_ID,
            "client_secret": MICROSOFT_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": MICROSOFT_REDIRECT_URI,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            tokens = response.json()
        
        if "access_token" not in tokens:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Store tokens (in production, associate with user)
        user_id = str(uuid.uuid4())
        tokens_db[user_id] = {
            "microsoft": tokens,
            "provider": "microsoft",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Redirect to success page
        return RedirectResponse(url=f"{FRONTEND_URL}/success?provider=microsoft&user_id={user_id}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@app.get("/connect/google")
async def google_oauth_start():
    """Start Google OAuth flow"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    state = str(uuid.uuid4())
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&scope=https://www.googleapis.com/auth/calendar.readonly"
        f"&state={state}"
        f"&access_type=offline"
    )
    return {"auth_url": auth_url, "state": state}

@app.get("/connect/google/callback")
async def google_oauth_callback(code: str, state: str):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            tokens = response.json()
        
        if "access_token" not in tokens:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Store tokens (in production, associate with user)
        user_id = str(uuid.uuid4())
        tokens_db[user_id] = {
            "google": tokens,
            "provider": "google", 
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Redirect to success page
        return RedirectResponse(url=f"{FRONTEND_URL}/success?provider=google&user_id={user_id}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@app.post("/availability")
async def calculate_availability(request: AvailabilityRequest):
    """Calculate mutual availability across multiple calendars"""
    meeting_id = str(uuid.uuid4())
    
    # In production, this would:
    # 1. Fetch free/busy data from each calendar
    # 2. Calculate mutual availability
    # 3. Return optimal meeting times
    
    # Mock response for now
    proposed_times = [
        {
            "start": "2024-01-15T14:00:00Z",
            "end": "2024-01-15T14:30:00Z",
            "confidence": 0.9
        },
        {
            "start": "2024-01-15T15:00:00Z", 
            "end": "2024-01-15T15:30:00Z",
            "confidence": 0.8
        },
        {
            "start": "2024-01-16T10:00:00Z",
            "end": "2024-01-16T10:30:00Z",
            "confidence": 0.95
        }
    ]
    
    meeting_data = {
        "meeting_id": meeting_id,
        "emails": request.emails,
        "proposed_times": proposed_times,
        "created_at": datetime.utcnow().isoformat()
    }
    
    meetings_db[meeting_id] = meeting_data
    
    return {
        "meeting_id": meeting_id,
        "proposed_times": proposed_times,
        "portal_url": f"{FRONTEND_URL}/availability/{meeting_id}"
    }

@app.get("/availability/{meeting_id}")
async def get_availability(meeting_id: str):
    """Get meeting availability data"""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meetings_db[meeting_id]

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SmartMeet API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "microsoft_oauth": "/connect/microsoft",
            "google_oauth": "/connect/google",
            "availability": "/availability"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 