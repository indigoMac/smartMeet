#!/usr/bin/env python3
"""
SmartMeet API Backend Development Server
Simple script to run the FastAPI development server.
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting SmartMeet API on port {port}")
    print(f"📁 Project root: {project_root}")
    print(f"🌐 API will be available at: http://localhost:{port}")
    print(f"📖 API docs available at: http://localhost:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 