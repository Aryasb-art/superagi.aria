import os
import signal
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import pydantic
from datetime import datetime
from typing import Optional, Dict, Any
import logging

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

class AriaChatRequest(pydantic.BaseModel):
    message: str
    context: Dict[str, Any] = {}

# Assuming AriaMasterAgent and logger are defined elsewhere in your project
class AriaMasterAgent:  # Placeholder for the actual AriaMasterAgent class
    def __init__(self, *args, **kwargs):
        pass

    def respond(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # This is just a dummy implementation. Replace with actual logic.
        return {"response": f"Echo: {message}", "metadata": context}

class logger: # Placeholder for the actual logger
    @staticmethod
    def error(message):
        print(f"Error: {message}")

@app.post("/aria/chat")
async def aria_chat(request: AriaChatRequest):
    """
    Enhanced Aria Robot chat endpoint with Agent Pool and Master Agent coordination
    """
    try:
        from superagi.agents.aria_agents.aria_agent_pool import AriaAgentPool

        # Initialize global agent pool if not exists
        if not hasattr(app.state, "agent_pool"):
            app.state.agent_pool = AriaAgentPool(max_agents_per_type=5)

        # Enhanced context for better decision making
        enhanced_context = {
            "user_context": request.context,
            "session": datetime.now().isoformat(),
            "user_id": request.context.get("user_id", "anonymous"),
            "conversation_history": request.context.get("history", []),
            "preferred_language": "persian"
        }

        # Submit task to agent pool with priority
        priority = request.context.get("priority", 1)
        task_id = app.state.agent_pool.submit_task(
            message=request.message,
            context=enhanced_context,
            priority=priority
        )

        # For immediate response, we'll still use Master Agent
        # but in production, you'd wait for pool result
        master_agent = AriaMasterAgent(None, "master-001")
        response = master_agent.respond(request.message, enhanced_context)

        # Get pool metrics for monitoring
        pool_status = app.state.agent_pool.get_pool_status()

        return {
            "success": True,
            "response": response.get("response", "No response generated"),
            "agent": "AriaMasterAgent",
            "task_id": task_id,
            "pool_metrics": {
                "total_agents": pool_status.get("total_agents", 0),
                "active_tasks": pool_status.get("active_tasks", 0),
                "queue_size": pool_status.get("queue_size", 0)
            },
            "metadata": {
                **response.get("metadata", {}),
                "task_analysis": response.get("task_analysis", {}),
                "coordination_plan": response.get("coordination_plan", {}),
                "agents_used": response.get("coordination_plan", {}).get("agents", []),
                "execution_time": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Aria chat error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "fallback_response": "متأسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید.",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/aria/status")
async def aria_system_status():
    """
    System status endpoint for monitoring agent health
    """
    try:
        from superagi.agents.aria_agents.aria_controller import AriaController

        controller = AriaController(None)
        agent_types = [
            "AriaMasterAgent", "AriaUtilityAgent", "AriaToolAgent", 
            "AriaMemoryAgent", "AriaSummaryAgent", "AriaGoalAgent", "AriaEmotionAgent"
        ]

        agent_status = {}
        for agent_type in agent_types:
            try:
                agent = controller.create_agent(agent_type)
                agent_status[agent_type] = {
                    "status": "healthy",
                    "capabilities": agent.get_capabilities() if hasattr(agent, 'get_capabilities') else []
                }
            except Exception as e:
                agent_status[agent_type] = {
                    "status": "error",
                    "error": str(e)
                }

        healthy_agents = len([a for a in agent_status.values() if a["status"] == "healthy"])
        total_agents = len(agent_status)

        # Get agent pool status if available
        pool_status = {}
        if hasattr(app.state, "agent_pool"):
            pool_status = app.state.agent_pool.get_pool_status()

        return {
            "system_status": "healthy" if healthy_agents == total_agents else "degraded",
            "healthy_agents": f"{healthy_agents}/{total_agents}",
            "agents": agent_status,
            "pool_status": pool_status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logging.exception("Exception occurred in /aria/status endpoint")
        return {
            "system_status": "error",
            "error": "An internal error has occurred.",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/aria/pool/metrics")
async def get_pool_metrics():
    """
    Detailed agent pool metrics
    """
    try:
        if not hasattr(app.state, "agent_pool"):
            return {"error": "Agent pool not initialized"}

        metrics = app.state.agent_pool.get_pool_status()
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.exception("Exception occurred in /aria/pool/metrics endpoint")
        return {
            "success": False,
            "error": "An internal error has occurred.",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn

    print("🚀 شروع Persian UI Server...")
    print("📍 آدرس: http://0.0.0.0:5000")
    print("📁 Static files: /gui/persian_ui/")

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
        print(f"❌ خطا در راه‌اندازی سرور: {e}")
        sys.exit(1)