
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pydantic

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

@app.get("/")
async def root():
    return {
        "message": "🎯 SuperAGI Persian UI is running successfully!",
        "status": "✅ healthy",
        "pydantic_version": pydantic.VERSION
    }

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
