#!/usr/bin/env python3
"""
SmartMeet Database Management Tool
Standalone database management commands that can be used by any service in the monorepo.

Usage:
    python tools/database/manage.py <command> [options]

Commands:
    migrate           - Run database migrations
    migration:status  - Show migration status
    rollback          - Rollback last migration
    generate:migration NAME - Generate new migration
    db:reset          - Reset database (drop and recreate tables)
    db:seed           - Seed database with test data
    console           - Start interactive Python console with database context
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cmd_migrate(args):
    """Run database migrations"""
    from packages.database import create_tables, check_database_connection
    
    logger.info("🗄️  Running database migrations...")
    
    if not check_database_connection():
        logger.error("❌ Database connection failed")
        sys.exit(1)
    
    try:
        create_tables()
        logger.info("✅ Migrations completed successfully")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

def cmd_migration_status(args):
    """Show migration status"""
    from packages.database import engine
    from sqlalchemy import inspect
    
    logger.info("🔍 Checking migration status...")
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.info("❌ No tables found - run 'python tools/database/manage.py migrate' to create tables")
        else:
            logger.info("✅ Database tables found:")
            for table in sorted(tables):
                logger.info(f"  📋 {table}")
                
    except Exception as e:
        logger.error(f"❌ Failed to check migration status: {e}")
        sys.exit(1)

def cmd_rollback(args):
    """Rollback last migration"""
    logger.warning("🔄 Rollback functionality not implemented yet")
    logger.info("💡 For now, use 'python tools/database/manage.py db:reset' to reset the database")

def cmd_generate_migration(args):
    """Generate new migration"""
    name = getattr(args, 'name', None)
    if not name:
        logger.error("❌ Migration name required. Usage: python tools/database/manage.py generate:migration --name 'migration_name'")
        sys.exit(1)
    
    logger.warning("📝 Migration generation not implemented yet")
    logger.info(f"💡 Would generate migration: {name}")

def cmd_db_reset(args):
    """Reset database"""
    from packages.database import reset_database
    
    # Confirmation prompt
    if not getattr(args, 'yes', False):
        response = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("❌ Database reset cancelled")
            return
    
    logger.info("🗄️  Resetting database...")
    try:
        reset_database()
        logger.info("✅ Database reset completed")
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        sys.exit(1)

def cmd_db_seed(args):
    """Seed database with test data"""
    from packages.database import (
        get_db_session, User, Meeting, CalendarAuth, 
        create_user, create_meeting, create_calendar_auth
    )
    from datetime import datetime, timedelta
    import uuid
    
    logger.info("🌱 Seeding database with test data...")
    
    try:
        with get_db_session() as db:
            # Create test users
            users_data = [
                {"email": "john.doe@company.com", "name": "John Doe"},
                {"email": "jane.smith@company.com", "name": "Jane Smith"},
                {"email": "bob.wilson@external.com", "name": "Bob Wilson"},
                {"email": "alice.brown@partner.com", "name": "Alice Brown"},
                {"email": "charlie.davis@client.com", "name": "Charlie Davis"}
            ]
            
            created_users = []
            for user_data in users_data:
                existing_user = db.query(User).filter(User.email == user_data["email"]).first()
                if not existing_user:
                    user = create_user(db, user_data["email"], user_data["name"])
                    created_users.append(user)
                    logger.info(f"✅ Created user: {user.email}")
                else:
                    created_users.append(existing_user)
                    logger.info(f"👤 User already exists: {existing_user.email}")
            
            # Create sample calendar auths (mock tokens)
            for i, user in enumerate(created_users[:3]):  # First 3 users get calendar auth
                provider = "microsoft" if i % 2 == 0 else "google"
                existing_auth = db.query(CalendarAuth).filter(
                    CalendarAuth.user_id == user.id,
                    CalendarAuth.provider == provider
                ).first()
                
                if not existing_auth:
                    auth = create_calendar_auth(
                        db=db,
                        user_id=user.id,
                        provider=provider,
                        access_token=f"mock_access_token_{provider}_{i}",
                        refresh_token=f"mock_refresh_token_{provider}_{i}",
                        token_expires_at=datetime.utcnow() + timedelta(hours=1),
                        provider_user_id=f"provider_user_{i}",
                        provider_email=user.email
                    )
                    logger.info(f"✅ Created {provider} auth for {user.email}")
            
            # Create sample meetings
            meetings_data = [
                {
                    "title": "Quarterly Business Review",
                    "description": "Q4 business review with stakeholders",
                    "duration_minutes": 60,
                    "meeting_type": "teams",
                    "participant_emails": ["jane.smith@company.com", "bob.wilson@external.com"]
                },
                {
                    "title": "Product Demo",
                    "description": "Demo of new features for client",
                    "duration_minutes": 30,
                    "meeting_type": "teams",
                    "participant_emails": ["alice.brown@partner.com", "charlie.davis@client.com"]
                },
                {
                    "title": "Team Standup",
                    "description": "Daily team standup meeting",
                    "duration_minutes": 15,
                    "meeting_type": "teams",
                    "participant_emails": ["jane.smith@company.com"]
                }
            ]
            
            organizer = created_users[0]  # John Doe as organizer
            for meeting_data in meetings_data:
                existing_meeting = db.query(Meeting).filter(
                    Meeting.title == meeting_data["title"],
                    Meeting.organizer_id == organizer.id
                ).first()
                
                if not existing_meeting:
                    meeting = create_meeting(
                        db=db,
                        organizer_id=organizer.id,
                        title=meeting_data["title"],
                        participant_emails=meeting_data["participant_emails"],
                        description=meeting_data["description"],
                        duration_minutes=meeting_data["duration_minutes"],
                        meeting_type=meeting_data["meeting_type"]
                    )
                    
                    # Add some proposed times
                    base_time = datetime.utcnow() + timedelta(days=1)
                    proposed_times = [
                        {
                            "start": (base_time + timedelta(hours=i * 2)).isoformat(),
                            "end": (base_time + timedelta(hours=i * 2, minutes=meeting_data["duration_minutes"])).isoformat()
                        }
                        for i in range(3)
                    ]
                    meeting.proposed_times = proposed_times
                    db.commit()
                    
                    logger.info(f"✅ Created meeting: {meeting.title}")
                else:
                    logger.info(f"📅 Meeting already exists: {existing_meeting.title}")
        
        logger.info("✅ Database seeding completed successfully")
        logger.info("💡 You can now test the API with the seeded data")
        
    except Exception as e:
        logger.error(f"❌ Database seeding failed: {e}")
        sys.exit(1)

def cmd_console(args):
    """Start interactive Python console with database context"""
    import code
    from packages.database import (
        get_db_session, engine, User, Meeting, CalendarAuth, Base
    )
    
    logger.info("🐍 Starting SmartMeet database console...")
    logger.info("💡 Available objects:")
    logger.info("  - get_db_session: database session context manager")
    logger.info("  - User, Meeting, CalendarAuth: database models")
    logger.info("  - engine: SQLAlchemy engine")
    logger.info("  - Base: SQLAlchemy declarative base")
    logger.info("")
    logger.info("💡 Example usage:")
    logger.info("  with get_db_session() as db:")
    logger.info("      users = db.query(User).all()")
    logger.info("      print([u.email for u in users])")
    
    # Create interactive namespace
    namespace = {
        'get_db_session': get_db_session,
        'engine': engine,
        'User': User,
        'Meeting': Meeting,
        'CalendarAuth': CalendarAuth,
        'Base': Base
    }
    
    code.interact(local=namespace)

def main():
    """Main command dispatcher"""
    parser = argparse.ArgumentParser(description="SmartMeet Database Management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Database commands
    subparsers.add_parser('migrate', help='Run database migrations')
    subparsers.add_parser('migration:status', help='Show migration status')
    subparsers.add_parser('rollback', help='Rollback last migration')
    
    generate_parser = subparsers.add_parser('generate:migration', help='Generate new migration')
    generate_parser.add_argument('--name', required=True, help='Migration name')
    
    reset_parser = subparsers.add_parser('db:reset', help='Reset database (drop and recreate tables)')
    reset_parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt')
    
    subparsers.add_parser('db:seed', help='Seed database with test data')
    subparsers.add_parser('console', help='Start interactive Python console')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Command mapping
    commands = {
        'migrate': cmd_migrate,
        'migration:status': cmd_migration_status,
        'rollback': cmd_rollback,
        'generate:migration': cmd_generate_migration,
        'db:reset': cmd_db_reset,
        'db:seed': cmd_db_seed,
        'console': cmd_console
    }
    
    command_func = commands.get(args.command)
    if command_func:
        command_func(args)
    else:
        logger.error(f"❌ Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 