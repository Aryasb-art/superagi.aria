
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import pydantic

print(f'Pydantic version: {pydantic.VERSION}')

# Import controllers
try:
    from superagi.controllers.agent import router as agent_router
    from superagi.controllers.user import router as user_router
    from superagi.controllers.config import router as config_router
    print("✅ Controllers imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    agent_router = None
    user_router = None
    config_router = None

app = FastAPI(title="SuperAGI Persian UI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers if available
if agent_router:
    app.include_router(agent_router, prefix="/agents")
if user_router:
    app.include_router(user_router, prefix="/users")
if config_router:
    app.include_router(config_router, prefix="/config")

@app.get("/")
async def root():
    return {"message": "SuperAGI Persian UI is running", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "pydantic_version": pydantic.VERSION}

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working", "timestamp": "2025-01-28"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
