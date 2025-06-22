"""
SmartMeet API Backend
FastAPI application for the SmartMeet meeting scheduling platform.
"""

import os
import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import from shared packages
from models import (
    Base, User, Meeting, CalendarAuth,
    create_user, create_meeting
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth Configuration
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Support both localhost and production
FRONTEND_URL = os.getenv("FRONTEND_URL")
if not FRONTEND_URL:
    raise ValueError("FRONTEND_URL environment variable is required")

# # Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartmeet.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    redirect_uri: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Initialize database on startup
    logger.info("🚀 Starting SmartMeet API...")
    init_database()
    logger.info("✅ Database initialized")
    yield
    logger.info("👋 Shutting down SmartMeet API...")

# Create FastAPI app
app = FastAPI(
    title="SmartMeet API",
    description="Meeting scheduling platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to SmartMeet API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "smartmeet-api"}

# OAuth Endpoints
@app.get("/connect/microsoft")
async def microsoft_oauth_start():
    """Start Microsoft OAuth flow"""
    try:
        state = secrets.token_urlsafe(32)
        
        # Microsoft OAuth URL
        auth_url = (
            f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize?"
            f"client_id={MICROSOFT_CLIENT_ID}&"
            f"response_type=code&"
            f"redirect_uri={FRONTEND_URL}/assets/oauth-callback.html&"
            f"scope=https://graph.microsoft.com/Calendars.Read.Shared https://graph.microsoft.com/User.Read&"
            f"state={state}&"
            f"response_mode=query"
        )
        
        logger.info(f"🔗 Generated Microsoft OAuth URL with state: {state}")
        return {"auth_url": auth_url, "state": state}
    
    except Exception as e:
        logger.error(f"❌ Microsoft OAuth start error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start OAuth: {str(e)}")

@app.post("/connect/microsoft/callback")
async def microsoft_oauth_callback(request: OAuthCallbackRequest, db=Depends(get_db)):
    """Handle Microsoft OAuth callback"""
    try:
        logger.info(f"🔄 Processing Microsoft OAuth callback for code: {request.code[:20]}...")
        
        # Exchange code for access token
        token_url = f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/token"
        
        token_data = {
            "client_id": MICROSOFT_CLIENT_ID,
            "client_secret": MICROSOFT_CLIENT_SECRET,
            "code": request.code,
            "redirect_uri": request.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            
            if token_response.status_code != 200:
                logger.error(f"❌ Token exchange failed: {token_response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            token_json = token_response.json()
            access_token = token_json.get("access_token")
            refresh_token = token_json.get("refresh_token")
            expires_in = token_json.get("expires_in", 3600)
            
            # Get user info from Microsoft Graph
            user_info_response = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_info_response.status_code != 200:
                logger.error(f"❌ Failed to get user info: {user_info_response.text}")
                raise HTTPException(status_code=400, detail="Failed to get user information")
            
            user_info = user_info_response.json()
            user_email = user_info.get("mail") or user_info.get("userPrincipalName")
            user_name = user_info.get("displayName", "Unknown User")
            provider_user_id = user_info.get("id")
        
        # Create or get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = create_user(db, email=user_email, name=user_name)
            logger.info(f"✅ Created new user: {user_email}")
        
        # Create or update calendar auth
        calendar_auth = db.query(CalendarAuth).filter(
            CalendarAuth.user_id == user.id,
            CalendarAuth.provider == "microsoft"
        ).first()
        
        if calendar_auth:
            # Update existing auth
            calendar_auth.access_token = access_token
            calendar_auth.refresh_token = refresh_token
            calendar_auth.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            calendar_auth.provider_user_id = provider_user_id
            calendar_auth.provider_email = user_email
            calendar_auth.is_active = True
            calendar_auth.updated_at = datetime.utcnow()
            logger.info(f"🔄 Updated existing calendar auth for user: {user_email}")
        else:
            # Create new auth
            calendar_auth = CalendarAuth(
                id=str(uuid.uuid4()),
                user_id=user.id,
                provider="microsoft",
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
                provider_user_id=provider_user_id,
                provider_email=user_email,
                is_active=True
            )
            db.add(calendar_auth)
            logger.info(f"✅ Created new calendar auth for user: {user_email}")
        
        db.commit()
        
        return {
            "success": True,
            "access_token": access_token,
            "user_id": user.id,
            "user_email": user_email,
            "provider": "microsoft",
            "message": "Successfully connected Microsoft calendar"
        }
        
    except Exception as e:
        logger.error(f"❌ Microsoft OAuth callback error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@app.get("/connect/google")
async def google_oauth_start():
    """Start Google OAuth flow"""
    try:
        state = secrets.token_urlsafe(32)
        
        # Google OAuth URL
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"response_type=code&"
            f"redirect_uri={FRONTEND_URL}/connect/google/callback&"
            f"scope=https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/userinfo.email&"
            f"state={state}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        logger.info(f"🔗 Generated Google OAuth URL with state: {state}")
        return {"auth_url": auth_url, "state": state}
    
    except Exception as e:
        logger.error(f"❌ Google OAuth start error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start OAuth: {str(e)}")

@app.get("/connect/google/callback")
async def google_oauth_callback(code: str, state: str, db=Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        logger.info(f"🔄 Processing Google OAuth callback for code: {code[:20]}...")
        
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": f"{FRONTEND_URL}/connect/google/callback",
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            
            if token_response.status_code != 200:
                logger.error(f"❌ Token exchange failed: {token_response.text}")
                return RedirectResponse(f"{FRONTEND_URL}/connect/google/callback?error=token_exchange_failed")
            
            token_json = token_response.json()
            access_token = token_json.get("access_token")
            refresh_token = token_json.get("refresh_token")
            expires_in = token_json.get("expires_in", 3600)
            
            # Get user info from Google
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_info_response.status_code != 200:
                logger.error(f"❌ Failed to get user info: {user_info_response.text}")
                return RedirectResponse(f"{FRONTEND_URL}/connect/google/callback?error=user_info_failed")
            
            user_info = user_info_response.json()
            user_email = user_info.get("email")
            user_name = user_info.get("name", "Unknown User")
            provider_user_id = user_info.get("id")
        
        # Create or get user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = create_user(db, email=user_email, name=user_name)
            logger.info(f"✅ Created new user: {user_email}")
        
        # Create or update calendar auth
        calendar_auth = db.query(CalendarAuth).filter(
            CalendarAuth.user_id == user.id,
            CalendarAuth.provider == "google"
        ).first()
        
        if calendar_auth:
            # Update existing auth
            calendar_auth.access_token = access_token
            calendar_auth.refresh_token = refresh_token
            calendar_auth.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            calendar_auth.provider_user_id = provider_user_id
            calendar_auth.provider_email = user_email
            calendar_auth.is_active = True
            calendar_auth.updated_at = datetime.utcnow()
            logger.info(f"🔄 Updated existing calendar auth for user: {user_email}")
        else:
            # Create new auth
            calendar_auth = CalendarAuth(
                id=str(uuid.uuid4()),
                user_id=user.id,
                provider="google",
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
                provider_user_id=provider_user_id,
                provider_email=user_email,
                is_active=True
            )
            db.add(calendar_auth)
            logger.info(f"✅ Created new calendar auth for user: {user_email}")
        
        db.commit()
        
        # Redirect to success page
        return RedirectResponse(f"{FRONTEND_URL}/success?provider=google&user_id={user.id}")
        
    except Exception as e:
        logger.error(f"❌ Google OAuth callback error: {e}")
        db.rollback()
        return RedirectResponse(f"{FRONTEND_URL}/connect/google/callback?error=callback_failed")

# User endpoints
@app.get("/api/users")
async def get_users(db=Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "name": u.name, "created_at": u.created_at} for u in users]

@app.get("/api/users/{user_id}")
async def get_user(user_id: str, db=Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "name": user.name, "created_at": user.created_at}

# Meeting endpoints
@app.get("/api/meetings")
async def get_meetings(db=Depends(get_db)):
    """Get all meetings"""
    meetings = db.query(Meeting).all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "organizer_id": m.organizer_id,
            "status": m.status,
            "created_at": m.created_at
        }
        for m in meetings
    ]

@app.get("/api/meetings/{meeting_id}")
async def get_meeting(meeting_id: str, db=Depends(get_db)):
    """Get meeting by ID"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "id": meeting.id,
        "title": meeting.title,
        "description": meeting.description,
        "organizer_id": meeting.organizer_id,
        "participant_emails": meeting.participant_emails,
        "proposed_times": meeting.proposed_times,
        "status": meeting.status,
        "duration_minutes": meeting.duration_minutes,
        "meeting_type": meeting.meeting_type,
        "created_at": meeting.created_at
    }

# Calendar authentication endpoints
@app.get("/api/auth/calendar/{user_id}")
async def get_calendar_auths(user_id: str, db=Depends(get_db)):
    """Get calendar authentications for a user"""
    auths = db.query(CalendarAuth).filter(CalendarAuth.user_id == user_id).all()
    return [
        {
            "id": auth.id,
            "provider": auth.provider,
            "provider_email": auth.provider_email,
            "is_active": auth.is_active,
            "created_at": auth.created_at
        }
        for auth in auths
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 