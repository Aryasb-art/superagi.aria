
import os
import signal
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import pydantic

def cleanup_port():
    """Kill any existing processes on port 5000"""
    try:
        os.system("pkill -f 'uvicorn.*main:app' > /dev/null 2>&1")
        os.system("lsof -ti:5000 | xargs -r kill -9 > /dev/null 2>&1")
    except:
        pass

def signal_handler(signum, frame):
    """Handle shutdown gracefully"""
    print("\n🛑 Shutting down server...")
    cleanup_port()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Clean up port before starting
cleanup_port()

print(f'🚀 Starting SuperAGI Persian UI...')
print(f'📦 Pydantic version: {pydantic.VERSION}')

app = FastAPI(title="SuperAGI Persian UI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Persian UI static files
app.mount("/persian", StaticFiles(directory="gui/persian_ui", html=True), name="persian_ui")

@app.get("/")
async def root():
    return {
        "message": "🎯 SuperAGI Persian UI is running successfully!",
        "status": "✅ healthy",
        "pydantic_version": pydantic.VERSION,
        "persian_ui_url": "/persian/"
    }

@app.get("/ui")
async def persian_ui():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/persian/")

@app.get("/persian")
async def persian_ui_direct():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/persian/")

@app.get("/health")
async def health():
    return {
        "status": "✅ healthy",
        "service": "SuperAGI Persian UI",
        "pydantic_version": pydantic.VERSION
    }

@app.get("/test")
async def test_endpoint():
    return {
        "message": "🧪 Test endpoint working perfectly!",
        "timestamp": "2025-01-28"
    }

if __name__ == "__main__":
    print("🚀 Starting uvicorn server...")
    try:
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=5000, 
            reload=False,  # Disable reload to prevent conflicts
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server error: {e}")
        cleanup_port()
        sys.exit(1)
