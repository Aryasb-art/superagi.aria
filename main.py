#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Persian SuperAGI UI",
    description="Persian User Interface for SuperAGI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "gui", "persian_ui")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    logger.info(f"✅ Static files mounted from: {static_path}")
else:
    logger.warning(f"⚠️ Static directory not found: {static_path}")

@app.get("/")
async def read_root():
    """Main page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Persian SuperAGI</title>
        <style>
            body { 
                font-family: 'Tahoma', sans-serif; 
                background: #1a1a2e; 
                color: #fff; 
                text-align: center; 
                padding: 50px; 
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: #16213e; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 0 30px rgba(0,0,0,0.5);
            }
            h1 { 
                color: #4CAF50; 
                margin-bottom: 30px; 
                font-size: 2.5em;
            }
            .status { 
                background: #0f3460; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
            }
            .btn {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
                text-decoration: none;
                display: inline-block;
            }
            .btn:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Persian SuperAGI</h1>
            <div class="status">
                <h2>✅ سرور با موفقیت راه‌اندازی شد</h2>
                <p>آدرس سرور: <strong>0.0.0.0:5000</strong></p>
                <p>وضعیت: <span style="color: #4CAF50;">آنلاین</span></p>
            </div>
            <div>
                <a href="/health" class="btn">بررسی سلامت سیستم</a>
                <a href="/docs" class="btn">مستندات API</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Persian SuperAGI server is running",
        "version": "1.0.0",
        "host": "0.0.0.0",
        "port": 5000
    }

@app.get("/api/test")
async def api_test():
    """API test endpoint"""
    return {
        "success": True,
        "message": "API working correctly",
        "data": {
            "server": "Persian SuperAGI",
            "status": "operational",
            "timestamp": "2024-01-30"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Persian SuperAGI Server...")
    print("📍 Address: http://0.0.0.0:5000")
    print("📊 Health: http://0.0.0.0:5000/health")
    print("📖 Docs: http://0.0.0.0:5000/docs")

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5000,
            reload=False,
            access_log=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server Error: {e}")
        sys.exit(1)