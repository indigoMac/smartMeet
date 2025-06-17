from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import gc
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Any, Optional
import httpx
import jwt
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from contextlib import asynccontextmanager
import psutil
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.info("🚀 SmartMeet API - Starting initialization...")

# Load environment variables from .env file in project root (only for local development)
env_path = Path(__file__).parent.parent.parent / ".env"
# Only load .env file if we're not in Railway (Railway sets its own environment variables)
if env_path.exists() and not any(key.startswith('RAILWAY_') for key in os.environ.keys()):
    load_dotenv(env_path)
    logger.info(f"📁 Loaded .env file from {env_path}")
else:
    logger.info("🌐 Running in Railway environment, using Railway environment variables")

# Environment variables
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

logger.info("🔧 Environment variables loaded")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 SmartMeet API starting up...")
    logger.info(f"Environment variables loaded:")
    logger.info(f"- MICROSOFT_CLIENT_ID: {'✓' if MICROSOFT_CLIENT_ID else '✗'}")
    logger.info(f"- GOOGLE_CLIENT_ID: {'✓' if GOOGLE_CLIENT_ID else '✗'}")
    logger.info(f"- FRONTEND_URL: {FRONTEND_URL}")
    
    # Debug: Print all environment variables that start with common prefixes
    logger.info("🔍 Debug - Environment variables:")
    for key, value in os.environ.items():
        if any(key.startswith(prefix) for prefix in ['MICROSOFT_', 'GOOGLE_', 'FRONTEND_', 'RAILWAY_', 'PORT']):
            # Mask sensitive values
            display_value = value if key in ['FRONTEND_URL', 'PORT'] or key.startswith('RAILWAY_') else '***masked***'
            logger.info(f"  {key}={display_value}")
    
    # Additional Railway debugging
    port = os.getenv("PORT", "8080")
    logger.info(f"🔧 Server will bind to port: {port}")
    logger.info(f"🔧 Railway environment detected: {'✓' if any(key.startswith('RAILWAY_') for key in os.environ.keys()) else '✗'}")
    
    # Memory optimization for Railway
    if any(key.startswith('RAILWAY_') for key in os.environ.keys()):
        logger.info("🧠 Applying memory optimizations for Railway...")
        # Force garbage collection
        gc.collect()
        # Set garbage collection thresholds more aggressively
        gc.set_threshold(700, 10, 10)
        logger.info(f"🧠 Memory optimization applied. GC thresholds: {gc.get_threshold()}")
    
    logger.info("✅ Startup complete - FastAPI app is ready to serve requests")
    
    yield
    
    # Shutdown
    logger.info("🛑 SmartMeet API shutting down...")
    # Final cleanup
    gc.collect()
    logger.info("✅ Shutdown complete")

logger.info("🏗️ Creating FastAPI app instance...")
app = FastAPI(title="SmartMeet API", version="1.0.0", lifespan=lifespan)
logger.info("✅ FastAPI app created successfully")

# CORS middleware
logger.info("🌐 Adding CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://smart-meet-five.vercel.app",
        "https://smart-meet-add-in.vercel.app", 
        "http://localhost:3000",
        "https://localhost:3000",
        "*"  # Keep as fallback
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
logger.info("✅ CORS middleware added")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Skip detailed logging for health checks to avoid overhead
    if request.url.path in ["/health", "/ready"]:
        return await call_next(request)
    
    start_time = datetime.utcnow()
    logger.info(f"📥 Incoming request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"📤 Response: {response.status_code} | Time: {process_time:.3f}s")
        
        # Only do memory monitoring occasionally, not on every request
        if process_time > 1.0:  # Only for slow requests
            try:
                process = psutil.Process(os.getpid())
                memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                logger.info(f"🧠 Memory usage after slow request: {memory_usage:.1f}MB")
                
                # Force garbage collection if memory usage is high
                if memory_usage > 200:  # Increased threshold
                    gc.collect()
                    logger.info("🧹 Garbage collection triggered")
            except Exception as e:
                logger.warning(f"⚠️ Memory monitoring error: {e}")
        
        return response
    except Exception as e:
        logger.error(f"❌ Request failed: {request.method} {request.url} - Error: {str(e)}")
        raise

logger.info("✅ Request logging middleware added")

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

class MeetingRequest(BaseModel):
    emails: List[str]
    subject: str
    duration_minutes: int = 30
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    time_zone: str = "UTC"
    meeting_type: str = "teams"  # teams, in_person, phone
    location: Optional[str] = None
    body: Optional[str] = None

class CalendarEvent(BaseModel):
    id: str
    subject: str
    start: str
    end: str
    is_all_day: bool
    show_as: str  # free, busy, tentative, out_of_office

# In-memory storage (replace with database in production)
meetings_db = {}
tokens_db = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("🏥 Health check requested")
    try:
        # Basic health check with memory info
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        
        health_data = {
            "status": "healthy", 
            "timestamp": datetime.utcnow().isoformat(),
            "memory_mb": round(memory_usage, 1),
            "uptime_seconds": round((datetime.utcnow() - datetime.utcnow()).total_seconds(), 1)
        }
        logger.info(f"✅ Health check passed - Memory: {memory_usage:.1f}MB")
        return health_data
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Railway"""
    logger.info("🚦 Readiness check requested")
    try:
        # Check if essential services are available
        ready_data = {
            "status": "ready", 
            "timestamp": datetime.utcnow().isoformat(),
            "environment": "railway" if any(key.startswith('RAILWAY_') for key in os.environ.keys()) else "local",
            "port": os.getenv("PORT", "8080")
        }
        logger.info("✅ Readiness check passed")
        return ready_data
    except Exception as e:
        logger.error(f"❌ Readiness check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Readiness check failed: {str(e)}")

@app.get("/startup-test")
async def startup_test():
    """Test endpoint to verify the app is running properly"""
    logger.info("🧪 Startup test requested")
    try:
        import sys
        import platform
        
        test_data = {
            "message": "SmartMeet API is running successfully!",
            "timestamp": datetime.utcnow().isoformat(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "environment_vars": {
                "PORT": os.getenv("PORT", "not set"),
                "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT", "not set"),
                "MICROSOFT_CLIENT_ID": "set" if MICROSOFT_CLIENT_ID else "not set",
                "GOOGLE_CLIENT_ID": "set" if GOOGLE_CLIENT_ID else "not set"
            }
        }
        logger.info("✅ Startup test completed successfully")
        return test_data
    except Exception as e:
        logger.error(f"❌ Startup test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Startup test failed: {str(e)}")

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
        f"&scope=https://graph.microsoft.com/Calendars.ReadWrite https://graph.microsoft.com/Calendars.ReadWrite.Shared offline_access"
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

async def get_user_calendar_events(access_token: str, start_time: str, end_time: str) -> List[CalendarEvent]:
    """Fetch user's calendar events from Microsoft Graph"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Format times for Graph API
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    url = f"https://graph.microsoft.com/v1.0/me/calendar/calendarView"
    params = {
        "startDateTime": start_dt.isoformat(),
        "endDateTime": end_dt.isoformat(),
        "$select": "id,subject,start,end,isAllDay,showAs"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch calendar events")
        
        data = response.json()
        events = []
        
        for event in data.get("value", []):
            events.append(CalendarEvent(
                id=event["id"],
                subject=event["subject"],
                start=event["start"]["dateTime"],
                end=event["end"]["dateTime"],
                is_all_day=event["isAllDay"],
                show_as=event["showAs"]
            ))
        
        return events

async def get_free_busy_info(access_token: str, emails: List[str], start_time: str, end_time: str) -> Dict[str, List[Dict]]:
    """Get free/busy information for multiple users"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Format times for Graph API
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    url = "https://graph.microsoft.com/v1.0/me/calendar/getSchedule"
    
    payload = {
        "schedules": emails,
        "startTime": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "UTC"
        },
        "endTime": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "UTC"
        },
        "availabilityViewInterval": 15
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch free/busy information")
        
        data = response.json()
        return {schedule["scheduleId"]: schedule["busyViewData"] for schedule in data.get("value", [])}

def find_optimal_meeting_times(free_busy_data: Dict[str, List[Dict]], duration_minutes: int, start_time: str, end_time: str) -> List[Dict]:
    """Algorithm to find optimal meeting times based on free/busy data"""
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    duration_delta = timedelta(minutes=duration_minutes)
    
    optimal_times = []
    current_time = start_dt
    
    while current_time + duration_delta <= end_dt:
        # Skip non-business hours (9 AM - 5 PM UTC)
        if current_time.hour < 9 or current_time.hour >= 17:
            current_time += timedelta(minutes=15)
            continue
        
        # Skip weekends
        if current_time.weekday() >= 5:
            current_time += timedelta(days=1)
            current_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
            continue
        
        # Check if all participants are free during this time slot
        slot_end = current_time + duration_delta
        all_free = True
        busy_count = 0
        
        for email, busy_data in free_busy_data.items():
            for busy_period in busy_data:
                if busy_period == "2":  # Busy
                    busy_count += 1
                    all_free = False
                    break
        
        if all_free:
            confidence = 1.0
        else:
            # Calculate confidence based on how many people are busy
            confidence = max(0.1, 1.0 - (busy_count / len(free_busy_data)))
        
        if confidence >= 0.3:  # Only suggest times with at least 30% confidence
            optimal_times.append({
                "start": current_time.isoformat() + "Z",
                "end": slot_end.isoformat() + "Z",
                "confidence": confidence
            })
        
        current_time += timedelta(minutes=15)
        
        # Limit to top 10 suggestions
        if len(optimal_times) >= 10:
            break
    
    # Sort by confidence and return top 5
    optimal_times.sort(key=lambda x: x["confidence"], reverse=True)
    return optimal_times[:5]

async def create_meeting_in_outlook(access_token: str, meeting_request: MeetingRequest, selected_time: Dict) -> Dict:
    """Create a meeting in Outlook using Microsoft Graph"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Prepare attendees
    attendees = []
    for email in meeting_request.emails:
        attendees.append({
            "emailAddress": {
                "address": email,
                "name": email.split("@")[0]
            },
            "type": "required"
        })
    
    # Prepare meeting body
    body_content = meeting_request.body or f"Meeting scheduled via SmartMeet"
    if meeting_request.meeting_type == "teams":
        body_content += "\n\nThis meeting will include a Microsoft Teams link."
    
    # Create meeting payload
    meeting_payload = {
        "subject": meeting_request.subject,
        "body": {
            "contentType": "HTML",
            "content": body_content
        },
        "start": {
            "dateTime": selected_time["start"].replace("Z", ""),
            "timeZone": meeting_request.time_zone
        },
        "end": {
            "dateTime": selected_time["end"].replace("Z", ""),
            "timeZone": meeting_request.time_zone
        },
        "attendees": attendees,
        "isOnlineMeeting": meeting_request.meeting_type == "teams",
        "onlineMeetingProvider": "teamsForBusiness" if meeting_request.meeting_type == "teams" else None
    }
    
    if meeting_request.location:
        meeting_payload["location"] = {
            "displayName": meeting_request.location
        }
    
    url = "https://graph.microsoft.com/v1.0/me/events"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=meeting_payload)
        
        if response.status_code not in [200, 201]:
            raise HTTPException(status_code=400, detail="Failed to create meeting")
        
        return response.json()

@app.post("/availability")
async def calculate_availability(request: AvailabilityRequest, authorization: str = Header(None)):
    """Calculate mutual availability across multiple calendars"""
    meeting_id = str(uuid.uuid4())
    
    # Extract access token from Authorization header
    access_token = None
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.split(" ")[1]
    
    if access_token:
        try:
            # Get real free/busy data from Microsoft Graph
            free_busy_data = await get_free_busy_info(
                access_token, 
                request.emails, 
                request.start_time, 
                request.end_time
            )
            
            # Find optimal meeting times
            proposed_times = find_optimal_meeting_times(
                free_busy_data,
                request.duration_minutes,
                request.start_time,
                request.end_time
            )
            
        except Exception as e:
            # Fall back to mock data if Graph API fails
            logger.warning(f"Failed to fetch real calendar data: {e}")
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
    else:
        # Mock response when no access token provided
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

@app.post("/meetings/create")
async def create_meeting(meeting_request: MeetingRequest, selected_time_index: int, authorization: str = Header(None)):
    """Create a meeting in Outlook with the selected time"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")
    
    access_token = authorization.split(" ")[1]
    
    # First, get availability to find the selected time
    availability_request = AvailabilityRequest(
        emails=meeting_request.emails,
        start_time=meeting_request.start_time or datetime.utcnow().isoformat() + "Z",
        end_time=meeting_request.end_time or (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
        duration_minutes=meeting_request.duration_minutes
    )
    
    availability_result = await calculate_availability(availability_request, authorization)
    
    if selected_time_index >= len(availability_result["proposed_times"]):
        raise HTTPException(status_code=400, detail="Invalid time selection")
    
    selected_time = availability_result["proposed_times"][selected_time_index]
    
    # Create the meeting
    meeting_result = await create_meeting_in_outlook(access_token, meeting_request, selected_time)
    
    return {
        "meeting_id": meeting_result["id"],
        "subject": meeting_result["subject"],
        "start": meeting_result["start"]["dateTime"],
        "end": meeting_result["end"]["dateTime"],
        "web_link": meeting_result.get("webLink"),
        "teams_link": meeting_result.get("onlineMeeting", {}).get("joinUrl"),
        "attendees": [att["emailAddress"]["address"] for att in meeting_result.get("attendees", [])]
    }

@app.get("/availability/{meeting_id}")
async def get_availability(meeting_id: str):
    """Get meeting availability data"""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meetings_db[meeting_id]

@app.get("/test-cors")
async def test_cors():
    """Test CORS endpoint to verify connectivity from web portal"""
    logger.info("🧪 CORS test endpoint called")
    return {
        "message": "CORS test successful",
        "timestamp": datetime.utcnow().isoformat(),
        "headers_received": "OK"
    }

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

logger.info("🏁 Main module initialization complete - FastAPI app is ready") 