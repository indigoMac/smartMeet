#!/usr/bin/env python3
"""
SmartMeet Development Helper
Provides commands for common development tasks.

Usage:
    python dev.py <command> [options]

Commands:
    setup       - Setup development environment
    api         - Start API backend server
    db          - Database management commands
    test        - Run tests
    lint        - Run linting
    help        - Show this help message
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
API_DIR = PROJECT_ROOT / "apps" / "api-backend"
DATABASE_TOOL = PROJECT_ROOT / "tools" / "database" / "manage.py"

def cmd_setup(args):
    """Setup development environment"""
    print("🛠️  Setting up SmartMeet development environment...")
    
    # Install API backend dependencies
    print("\n📦 Installing API backend dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", 
        str(API_DIR / "requirements.txt")
    ], check=True)
    
    # Install database package dependencies
    print("\n📦 Installing database package dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", 
        str(PROJECT_ROOT / "packages" / "database" / "requirements.txt")
    ], check=True)
    
    # Setup database
    print("\n🗄️  Setting up database...")
    subprocess.run([
        sys.executable, str(DATABASE_TOOL), "migrate"
    ], check=True)
    
    # Seed database with test data
    print("\n🌱 Seeding database with test data...")
    subprocess.run([
        sys.executable, str(DATABASE_TOOL), "db:seed"
    ], check=True)
    
    print("\n✅ Development environment setup complete!")
    print("🚀 Run 'python dev.py api' to start the API server")

def cmd_api(args):
    """Start API backend server"""
    print("🚀 Starting SmartMeet API backend...")
    os.chdir(API_DIR)
    subprocess.run([sys.executable, "run.py"])

def cmd_db(args):
    """Database management commands"""
    if not args.db_command:
        print("Available database commands:")
        subprocess.run([sys.executable, str(DATABASE_TOOL), "--help"])
        return
    
    # Pass through all db arguments to the database tool
    db_args = [sys.executable, str(DATABASE_TOOL)] + args.db_command
    subprocess.run(db_args)

def cmd_test(args):
    """Run tests"""
    print("🧪 Running tests...")
    print("⚠️  Test framework not yet implemented")

def cmd_lint(args):
    """Run linting"""
    print("🔍 Running linting...")
    print("⚠️  Linting not yet implemented")

def cmd_help(args):
    """Show help message"""
    print(__doc__)

def main():
    """Main command dispatcher"""
    parser = argparse.ArgumentParser(description="SmartMeet Development Helper")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    subparsers.add_parser('setup', help='Setup development environment')
    
    # API command
    subparsers.add_parser('api', help='Start API backend server')
    
    # Database command with pass-through arguments
    db_parser = subparsers.add_parser('db', help='Database management commands')
    db_parser.add_argument('db_command', nargs='*', help='Database command and arguments')
    
    # Other commands
    subparsers.add_parser('test', help='Run tests')
    subparsers.add_parser('lint', help='Run linting')
    subparsers.add_parser('help', help='Show help message')
    
    args = parser.parse_args()
    
    if not args.command:
        cmd_help(args)
        return
    
    # Command mapping
    commands = {
        'setup': cmd_setup,
        'api': cmd_api,
        'db': cmd_db,
        'test': cmd_test,
        'lint': cmd_lint,
        'help': cmd_help
    }
    
    command_func = commands.get(args.command)
    if command_func:
        try:
            command_func(args)
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Command failed with exit code {e.returncode}")
            sys.exit(e.returncode)
        except Exception as e:
            print(f"\n💥 Error: {e}")
            sys.exit(1)
    else:
        print(f"❌ Unknown command: {args.command}")
        cmd_help(args)
        sys.exit(1)

if __name__ == '__main__':
    main() 