
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import pydantic

print(f'Pydantic version: {pydantic.VERSION}')

# Import controllers
from superagi.controllers.agent import router as agent_router
from superagi.controllers.user import router as user_router
from superagi.controllers.config import router as config_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router, prefix="/agents")
app.include_router(user_router, prefix="/users")
app.include_router(config_router, prefix="/config")

@app.get("/")
async def root():
    return {"message": "SuperAGI API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
