"""
SmartMeet Database Package
Shared database models and connections for the monorepo
"""

from .models import (
    Base,
    User,
    CalendarAuth, 
    Meeting,
    AvailabilityCache,
    meeting_participants,
    get_user_by_email,
    create_user,
    get_user_calendar_auth,
    create_calendar_auth,
    create_meeting
)

from .connection import (
    engine,
    SessionLocal,
    get_db,
    get_db_session,
    create_tables,
    drop_tables,
    reset_database,
    check_database_connection,
    init_database
)

__all__ = [
    # Models
    "Base",
    "User", 
    "CalendarAuth",
    "Meeting",
    "AvailabilityCache", 
    "meeting_participants",
    
    # Model utilities
    "get_user_by_email",
    "create_user",
    "get_user_calendar_auth", 
    "create_calendar_auth",
    "create_meeting",
    
    # Database connection
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_session",
    "create_tables",
    "drop_tables", 
    "reset_database",
    "check_database_connection",
    "init_database"
] 