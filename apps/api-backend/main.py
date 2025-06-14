from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import gc
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Any
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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
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

logger.info("🏁 Main module initialization complete - FastAPI app is ready") 