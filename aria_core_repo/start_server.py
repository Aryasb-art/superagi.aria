#!/usr/bin/env python3
"""
Simplified server startup script to avoid initialization loops.
"""
import uvicorn
import sys
import asyncio
from datetime import datetime

def main():
    """Start the FastAPI server with minimal initialization."""
    print(f"[{datetime.now()}] Starting FastAPI server...")
    
    try:
        # Import main app
        from main import app
        print(f"[{datetime.now()}] FastAPI app imported successfully")
        
        # Start uvicorn server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5000,
            reload=False,  # Disable reload to prevent loops
            log_level="info"
        )
        
    except Exception as e:
        print(f"[{datetime.now()}] Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()