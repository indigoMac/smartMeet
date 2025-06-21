"""
Database models for SmartMeet application
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

Base = declarative_base()

# Association table for many-to-many relationship between users and meetings
meeting_participants = Table(
    'meeting_participants',
    Base.metadata,
    Column('meeting_id', String, ForeignKey('meetings.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('status', String, default='pending'),  # pending, accepted, declined
    Column('created_at', DateTime, default=func.now()),
    Column('updated_at', DateTime, default=func.now(), onupdate=func.now())
)

class User(Base):
    """User model for storing user information and authentication details"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    timezone = Column(String, default='UTC')
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    calendar_auths = relationship("CalendarAuth", back_populates="user", cascade="all, delete-orphan")
    organized_meetings = relationship("Meeting", back_populates="organizer", foreign_keys="Meeting.organizer_id")
    participated_meetings = relationship("Meeting", secondary=meeting_participants, back_populates="participants")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class CalendarAuth(Base):
    """Calendar authentication tokens for users"""
    __tablename__ = "calendar_auths"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # 'microsoft' or 'google'
    
    # OAuth tokens (encrypted in production)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Provider-specific user info
    provider_user_id = Column(String, nullable=True)
    provider_email = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="calendar_auths")
    
    def __repr__(self):
        return f"<CalendarAuth(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provider": self.provider,
            "provider_user_id": self.provider_user_id,
            "provider_email": self.provider_email,
            "is_active": self.is_active,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        }

class Meeting(Base):
    """Meeting model for storing meeting information and scheduling data"""
    __tablename__ = "meetings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organizer_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Meeting details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=30)
    
    # Meeting type and location
    meeting_type = Column(String, default='teams')  # teams, in_person, phone
    location = Column(String, nullable=True)
    meeting_url = Column(String, nullable=True)  # Teams/Zoom link
    
    # Scheduling
    proposed_times = Column(JSON, nullable=True)  # List of proposed time slots
    selected_time = Column(JSON, nullable=True)   # Final selected time
    timezone = Column(String, default='UTC')
    
    # Status
    status = Column(String, default='draft')  # draft, proposed, scheduled, cancelled, completed
    
    # External integration
    outlook_event_id = Column(String, nullable=True)
    google_event_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    scheduled_at = Column(DateTime, nullable=True)  # When meeting is scheduled for
    
    # Relationships
    organizer = relationship("User", back_populates="organized_meetings", foreign_keys=[organizer_id])
    participants = relationship("User", secondary=meeting_participants, back_populates="participated_meetings")
    
    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "organizer_id": self.organizer_id,
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "meeting_type": self.meeting_type,
            "location": self.location,
            "meeting_url": self.meeting_url,
            "proposed_times": self.proposed_times,
            "selected_time": self.selected_time,
            "timezone": self.timezone,
            "status": self.status,
            "outlook_event_id": self.outlook_event_id,
            "google_event_id": self.google_event_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "organizer": self.organizer.to_dict() if self.organizer else None,
            "participants": [p.to_dict() for p in self.participants] if self.participants else []
        }

class AvailabilityCache(Base):
    """Cache for storing user availability data to reduce API calls"""
    __tablename__ = "availability_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    cache_key = Column(String, nullable=False, index=True)  # Hash of query parameters
    
    # Cached data
    availability_data = Column(JSON, nullable=False)
    
    # Cache metadata
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<AvailabilityCache(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"

# Database utility functions
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, name: str = None) -> User:
    """Create a new user"""
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_calendar_auth(db: Session, user_id: str, provider: str) -> Optional[CalendarAuth]:
    """Get calendar authentication for user and provider"""
    return db.query(CalendarAuth).filter(
        CalendarAuth.user_id == user_id,
        CalendarAuth.provider == provider,
        CalendarAuth.is_active == True
    ).first()

def create_calendar_auth(
    db: Session, 
    user_id: str, 
    provider: str, 
    access_token: str,
    refresh_token: str = None,
    token_expires_at: datetime = None,
    provider_user_id: str = None,
    provider_email: str = None
) -> CalendarAuth:
    """Create or update calendar authentication"""
    # Check if auth already exists
    existing_auth = get_user_calendar_auth(db, user_id, provider)
    if existing_auth:
        # Update existing
        existing_auth.access_token = access_token
        existing_auth.refresh_token = refresh_token
        existing_auth.token_expires_at = token_expires_at
        existing_auth.provider_user_id = provider_user_id
        existing_auth.provider_email = provider_email
        existing_auth.is_active = True
        existing_auth.updated_at = func.now()
        db.commit()
        db.refresh(existing_auth)
        return existing_auth
    else:
        # Create new
        auth = CalendarAuth(
            user_id=user_id,
            provider=provider,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            provider_user_id=provider_user_id,
            provider_email=provider_email
        )
        db.add(auth)
        db.commit()
        db.refresh(auth)
        return auth

def create_meeting(
    db: Session,
    organizer_id: str,
    title: str,
    participant_emails: List[str],
    description: str = None,
    duration_minutes: int = 30,
    meeting_type: str = 'teams'
) -> Meeting:
    """Create a new meeting"""
    meeting = Meeting(
        organizer_id=organizer_id,
        title=title,
        description=description,
        duration_minutes=duration_minutes,
        meeting_type=meeting_type
    )
    
    # Add participants
    for email in participant_emails:
        user = get_user_by_email(db, email)
        if not user:
            user = create_user(db, email)
        meeting.participants.append(user)
    
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting 