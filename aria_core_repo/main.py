from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta, datetime
from typing import Optional
import uvicorn

from database import engine, get_db
from models import Base, User
from schemas import UserCreate, UserLogin, UserResponse, Token, RefreshToken
from auth import (
    authenticate_user,
    create_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_active_user,
    get_user_by_email
)
from config import settings
from agents.master_agent import master_agent
from agents.interactive_security_check_agent import InteractiveSecurityCheckAgent
from agents.reward_agent import RewardAgent
from pydantic import BaseModel

# Agent message schemas  
class AgentMessage(BaseModel):
    message: str
    context: Optional[dict] = None

class AgentResponse(BaseModel):
    response_id: str
    content: str
    handled_by: str
    timestamp: str
    success: bool
    error: Optional[str] = None

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Authentication System",
    description="A secure authentication system with JWT tokens and PostgreSQL",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Security scheme
security = HTTPBearer()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FastAPI Authentication System",
        "version": "1.0.0",
        "endpoints": {
            "register": "/register",
            "login": "/login",
            "refresh": "/refresh",
            "profile": "/profile",
            "protected": "/protected"
        }
    }

@app.get("/ui")
async def get_ui():
    """Serve the frontend UI."""
    return FileResponse("frontend/index.html")

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = create_user(
            db=db,
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        return db_user
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshToken, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        token_data = verify_token(refresh_data.refresh_token, "refresh")
        
        # Get user from database
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@app.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile."""
    return current_user

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    """A protected route that requires authentication."""
    return {
        "message": f"Hello {current_user.email}! This is a protected route.",
        "user_id": current_user.id,
        "timestamp": "2025-07-06T00:00:00Z"
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with system diagnostics."""
    try:
        # Check database connectivity
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check agent system
    agent_count = len(master_agent.sub_agents)
    
    # Check OpenAI connectivity (if available)
    import os
    openai_status = "not_configured"
    if os.getenv('OPENAI_API_KEY'):
        openai_status = "configured"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system_info": {
            "database": db_status,
            "agents": {
                "total": agent_count,
                "names": list(master_agent.sub_agents.keys())
            },
            "openai": openai_status,
            "server": "running"
        }
    }

# Agent endpoints
@app.post("/agent", response_model=AgentResponse)
async def chat_with_agent(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Send a message to the MasterAgent and receive a response.
    Requires authentication.
    """
    try:
        # Add user context to the message
        context = message.context or {}
        context.update({
            "sender": current_user.email,
            "user_id": current_user.id,
            "authenticated": True
        })
        
        # Get response from master agent
        response = master_agent.respond(message.message, context)
        
        return AgentResponse(**response)
        
    except Exception as e:
        return AgentResponse(
            response_id="error",
            content=f"خطا در پردازش پیام: {str(e)}",
            handled_by="system",
            timestamp=datetime.utcnow().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/status")
async def get_agent_status(current_user: User = Depends(get_current_active_user)):
    """
    Get the status of the agent system.
    Requires authentication.
    """
    return master_agent.get_system_status()

@app.get("/agent/status/public")
async def get_agent_status_public():
    """
    Get the status of the agent system (public endpoint).
    No authentication required for monitoring.
    """
    try:
        status = master_agent.get_system_status()
        return {
            "status": "success",
            "agent_system": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/agent/public", response_model=AgentResponse)
async def public_chat_with_agent(message: AgentMessage):
    """
    Public endpoint to chat with MasterAgent (no authentication required).
    For testing purposes.
    """
    try:
        # Add public context
        context = message.context or {}
        context.update({
            "sender": "anonymous",
            "authenticated": False
        })
        
        # Get response from master agent
        response = master_agent.respond(message.message, context)
        
        return AgentResponse(**response)
        
    except Exception as e:
        return AgentResponse(
            response_id="error",
            content=f"خطا در پردازش پیام: {str(e)}",
            handled_by="system",
            timestamp=datetime.utcnow().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/memory", response_model=AgentResponse)
async def test_agent_memory(message: AgentMessage):
    """
    Test endpoint for agent memory functionality.
    Supports commands: 'show memory', 'clear memory', or any message to add to memory.
    """
    try:
        # Add memory test context
        context = message.context or {}
        context.update({
            "sender": "memory_test",
            "authenticated": False
        })
        
        # Get response from master agent
        response = master_agent.respond(message.message, context)
        
        return AgentResponse(**response)
        
    except Exception as e:
        return AgentResponse(
            response_id="error",
            content=f"خطا در تست حافظه: {str(e)}",
            handled_by="system",
            timestamp=datetime.utcnow().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/utility", response_model=AgentResponse)
async def utility_agent_endpoint(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Direct endpoint to interact with UtilityAgent.
    Requires authentication.
    """
    try:
        # Get the utility agent from master agent
        utility_agent = master_agent.sub_agents.get("UtilityAgent")
        if not utility_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="UtilityAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="UtilityAgent not found"
            )
        
        # Process message with utility agent
        response = utility_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=response["response_id"],
            content=response["content"],
            handled_by=response["handled_by"],
            timestamp=response["timestamp"],
            success=response["success"],
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در پردازش پیام: {str(e)}",
            handled_by="UtilityAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/utility/public", response_model=AgentResponse)
async def utility_agent_public_endpoint(message: AgentMessage):
    """
    Public endpoint to interact with UtilityAgent (no authentication required).
    For testing purposes.
    """
    try:
        # Get the utility agent from master agent
        utility_agent = master_agent.sub_agents.get("UtilityAgent")
        if not utility_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="UtilityAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="UtilityAgent not found"
            )
        
        # Process message with utility agent
        response = utility_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=response["response_id"],
            content=response["content"],
            handled_by=response["handled_by"],
            timestamp=response["timestamp"],
            success=response["success"],
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در پردازش پیام: {str(e)}",
            handled_by="UtilityAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/tool", response_model=AgentResponse)
async def tool_agent_endpoint(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Direct endpoint to interact with ToolAgent.
    Requires authentication.
    """
    try:
        # Get the tool agent from master agent
        tool_agent = master_agent.sub_agents.get("ToolAgent")
        if not tool_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="ToolAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="ToolAgent not found"
            )
        
        # Process message with tool agent
        response = tool_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=response["response_id"],
            content=response["content"],
            handled_by=response["handled_by"],
            timestamp=response["timestamp"],
            success=response["success"],
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در پردازش وظیفه: {str(e)}",
            handled_by="ToolAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/tool/public", response_model=AgentResponse)
async def tool_agent_public_endpoint(message: AgentMessage):
    """
    Public endpoint to interact with ToolAgent (no authentication required).
    For testing purposes.
    """
    try:
        # Get the tool agent from master agent
        tool_agent = master_agent.sub_agents.get("ToolAgent")
        if not tool_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="ToolAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="ToolAgent not found"
            )
        
        # Process message with tool agent
        response = tool_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=response["response_id"],
            content=response["content"],
            handled_by=response["handled_by"],
            timestamp=response["timestamp"],
            success=response["success"],
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در پردازش وظیفه: {str(e)}",
            handled_by="ToolAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/summary", response_model=AgentResponse)
async def summary_agent_endpoint(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Direct endpoint to interact with SummaryAgent.
    Requires authentication.
    """
    try:
        # Get the summary agent from master agent
        summary_agent = master_agent.sub_agents.get("SummaryAgent")
        if not summary_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="SummaryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="SummaryAgent not found"
            )
        
        # Process message with summary agent
        response = summary_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"summary_{response.get('summary_id', 'unknown')}",
            content=response.get("response", "خطا در خلاصه‌سازی"),
            handled_by="SummaryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در خلاصه‌سازی: {str(e)}",
            handled_by="SummaryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/summary/public", response_model=AgentResponse)
async def summary_agent_public_endpoint(message: AgentMessage):
    """
    Public endpoint to interact with SummaryAgent (no authentication required).
    For testing purposes.
    """
    try:
        # Get the summary agent from master agent
        summary_agent = master_agent.sub_agents.get("SummaryAgent")
        if not summary_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="SummaryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="SummaryAgent not found"
            )
        
        # Process message with summary agent
        response = summary_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"summary_{response.get('summary_id', 'unknown')}",
            content=response.get("response", "خطا در خلاصه‌سازی"),
            handled_by="SummaryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در خلاصه‌سازی: {str(e)}",
            handled_by="SummaryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/longterm/save")
async def save_longterm_memory(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Save a long-term memory (authenticated endpoint).
    """
    try:
        # Get the longterm memory agent from master agent
        memory_agent = master_agent.sub_agents.get("LongTermMemoryAgent")
        if not memory_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="LongTermMemoryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="LongTermMemoryAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process message with memory agent
        response = memory_agent.respond(f"ذخیره کن: {message.message}", context)
        
        return AgentResponse(
            response_id=f"memory_{response.get('memory_id', 'unknown')}",
            content=response.get("response", "خطا در ذخیره حافظه"),
            handled_by="LongTermMemoryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در ذخیره حافظه: {str(e)}",
            handled_by="LongTermMemoryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/longterm/fetch")
async def fetch_longterm_memories(current_user: User = Depends(get_current_active_user)):
    """
    Fetch recent long-term memories (authenticated endpoint).
    """
    try:
        # Get the longterm memory agent from master agent
        memory_agent = master_agent.sub_agents.get("LongTermMemoryAgent")
        if not memory_agent:
            return AgentResponse(
                response_id=f"error_{hash('fetch') % 100000}",
                content="LongTermMemoryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="LongTermMemoryAgent not found"
            )
        
        # Add user context
        context = {"user_id": current_user.id}
        
        # Process fetch request
        response = memory_agent.respond("نشان بده آخرین حافظه‌ها", context)
        
        return AgentResponse(
            response_id=f"fetch_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در دریافت حافظه‌ها"),
            handled_by="LongTermMemoryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در دریافت حافظه‌ها: {str(e)}",
            handled_by="LongTermMemoryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/longterm/save/public")
async def save_longterm_memory_public(message: AgentMessage):
    """
    Save a long-term memory (public endpoint for testing).
    """
    try:
        # Get the longterm memory agent from master agent
        memory_agent = master_agent.sub_agents.get("LongTermMemoryAgent")
        if not memory_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="LongTermMemoryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="LongTermMemoryAgent not found"
            )
        
        # Process message with memory agent (no user context for public endpoint)
        response = memory_agent.respond(f"ذخیره کن: {message.message}", message.context)
        
        return AgentResponse(
            response_id=f"memory_{response.get('memory_id', 'unknown')}",
            content=response.get("response", "خطا در ذخیره حافظه"),
            handled_by="LongTermMemoryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در ذخیره حافظه: {str(e)}",
            handled_by="LongTermMemoryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/longterm/fetch/public")
async def fetch_longterm_memories_public():
    """
    Fetch recent long-term memories (public endpoint for testing).
    """
    try:
        # Get the longterm memory agent from master agent
        memory_agent = master_agent.sub_agents.get("LongTermMemoryAgent")
        if not memory_agent:
            return AgentResponse(
                response_id=f"error_{hash('fetch') % 100000}",
                content="LongTermMemoryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="LongTermMemoryAgent not found"
            )
        
        # Process fetch request (no user context for public endpoint)
        response = memory_agent.respond("نشان بده آخرین حافظه‌ها", None)
        
        return AgentResponse(
            response_id=f"fetch_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در دریافت حافظه‌ها"),
            handled_by="LongTermMemoryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در دریافت حافظه‌ها: {str(e)}",
            handled_by="LongTermMemoryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/conceptual/save")
async def save_conceptual_memory(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Save and analyze a conceptual memory (authenticated endpoint).
    """
    try:
        # Get the conceptual memory agent from master agent
        conceptual_agent = master_agent.sub_agents.get("ConceptualMemoryAgent")
        if not conceptual_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="ConceptualMemoryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="ConceptualMemoryAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process message with conceptual agent
        response = conceptual_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=f"concept_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل مفهوم"),
            handled_by="ConceptualMemoryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل مفهوم: {str(e)}",
            handled_by="ConceptualMemoryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/conceptual/latest")
async def get_latest_conceptual_memories(current_user: User = Depends(get_current_active_user)):
    """
    Get latest conceptual memories (authenticated endpoint).
    """
    try:
        # Get the conceptual memory agent from master agent
        conceptual_agent = master_agent.sub_agents.get("ConceptualMemoryAgent")
        if not conceptual_agent:
            return AgentResponse(
                response_id=f"error_{hash('latest') % 100000}",
                content="ConceptualMemoryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="ConceptualMemoryAgent not found"
            )
        
        # Add user context
        context = {"user_id": current_user.id}
        
        # Process latest request
        response = conceptual_agent.respond("آخرین مفاهیم", context)
        
        return AgentResponse(
            response_id=f"latest_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در دریافت مفاهیم"),
            handled_by="ConceptualMemoryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در دریافت مفاهیم: {str(e)}",
            handled_by="ConceptualMemoryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/conceptual/save/public")
async def save_conceptual_memory_public(message: AgentMessage):
    """
    Save and analyze a conceptual memory (public endpoint for testing).
    """
    try:
        # Get the conceptual memory agent from master agent
        conceptual_agent = master_agent.sub_agents.get("ConceptualMemoryAgent")
        if not conceptual_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="ConceptualMemoryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="ConceptualMemoryAgent not found"
            )
        
        # Process message with conceptual agent (no user context for public endpoint)
        response = conceptual_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"concept_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل مفهوم"),
            handled_by="ConceptualMemoryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل مفهوم: {str(e)}",
            handled_by="ConceptualMemoryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/conceptual/latest/public")
async def get_latest_conceptual_memories_public():
    """
    Get latest conceptual memories (public endpoint for testing).
    """
    try:
        # Get the conceptual memory agent from master agent
        conceptual_agent = master_agent.sub_agents.get("ConceptualMemoryAgent")
        if not conceptual_agent:
            return AgentResponse(
                response_id=f"error_{hash('latest') % 100000}",
                content="ConceptualMemoryAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="ConceptualMemoryAgent not found"
            )
        
        # Process latest request (no user context for public endpoint)
        response = conceptual_agent.respond("آخرین مفاهیم", None)
        
        return AgentResponse(
            response_id=f"latest_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در دریافت مفاهیم"),
            handled_by="ConceptualMemoryAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در دریافت مفاهیم: {str(e)}",
            handled_by="ConceptualMemoryAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/repetitive/observe")
async def observe_repetitive_patterns(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Observe and analyze repetitive patterns (authenticated endpoint).
    """
    try:
        # Get the repetitive learning agent from master agent
        repetitive_agent = master_agent.sub_agents.get("RepetitiveLearningAgent")
        if not repetitive_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="RepetitiveLearningAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="RepetitiveLearningAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process message with repetitive agent
        response = repetitive_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=f"repetitive_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل الگوی تکراری"),
            handled_by="RepetitiveLearningAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در مشاهده الگوهای تکراری: {str(e)}",
            handled_by="RepetitiveLearningAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/repetitive/frequent")
async def get_frequent_patterns(current_user: User = Depends(get_current_active_user)):
    """
    Get frequent repetitive patterns (authenticated endpoint).
    """
    try:
        # Get the repetitive learning agent from master agent
        repetitive_agent = master_agent.sub_agents.get("RepetitiveLearningAgent")
        if not repetitive_agent:
            return AgentResponse(
                response_id=f"error_{hash('frequent') % 100000}",
                content="RepetitiveLearningAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="RepetitiveLearningAgent not found"
            )
        
        # Add user context
        context = {"user_id": current_user.id}
        
        # Process frequent request
        response = repetitive_agent.respond("الگوهای تکراری", context)
        
        return AgentResponse(
            response_id=f"frequent_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در دریافت الگوهای تکراری"),
            handled_by="RepetitiveLearningAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در دریافت الگوهای تکراری: {str(e)}",
            handled_by="RepetitiveLearningAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/repetitive/observe/public")
async def observe_repetitive_patterns_public(message: AgentMessage):
    """
    Observe and analyze repetitive patterns (public endpoint for testing).
    """
    try:
        # Get the repetitive learning agent from master agent
        repetitive_agent = master_agent.sub_agents.get("RepetitiveLearningAgent")
        if not repetitive_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="RepetitiveLearningAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="RepetitiveLearningAgent not found"
            )
        
        # Process message with repetitive agent (no user context for public endpoint)
        response = repetitive_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"repetitive_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل الگوی تکراری"),
            handled_by="RepetitiveLearningAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل الگوی تکراری: {str(e)}",
            handled_by="RepetitiveLearningAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/repetitive/frequent/public")
async def get_frequent_patterns_public():
    """
    Get frequent repetitive patterns (public endpoint for testing).
    """
    try:
        # Get the repetitive learning agent from master agent
        repetitive_agent = master_agent.sub_agents.get("RepetitiveLearningAgent")
        if not repetitive_agent:
            return AgentResponse(
                response_id=f"error_{hash('frequent') % 100000}",
                content="RepetitiveLearningAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="RepetitiveLearningAgent not found"
            )
        
        # Process frequent request (no user context for public endpoint)
        response = repetitive_agent.respond("الگوهای تکراری", None)
        
        return AgentResponse(
            response_id=f"frequent_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در دریافت الگوهای تکراری"),
            handled_by="RepetitiveLearningAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در دریافت الگوهای تکراری: {str(e)}",
            handled_by="RepetitiveLearningAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/knowledge-graph/build")
async def build_knowledge_graph(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Build knowledge graph from text (authenticated endpoint).
    """
    try:
        # Get the knowledge graph agent from master agent
        kg_agent = master_agent.sub_agents.get("KnowledgeGraphAgent")
        if not kg_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="KnowledgeGraphAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="KnowledgeGraphAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process message with knowledge graph agent
        response = kg_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=f"kg_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در ساخت گراف دانش"),
            handled_by="KnowledgeGraphAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در ساخت گراف دانش: {str(e)}",
            handled_by="KnowledgeGraphAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/knowledge-graph/list")
async def list_knowledge_graphs(current_user: User = Depends(get_current_active_user)):
    """
    List knowledge graphs (authenticated endpoint).
    """
    try:
        # Get the knowledge graph agent from master agent
        kg_agent = master_agent.sub_agents.get("KnowledgeGraphAgent")
        if not kg_agent:
            return AgentResponse(
                response_id=f"error_{hash('list') % 100000}",
                content="KnowledgeGraphAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="KnowledgeGraphAgent not found"
            )
        
        # Add user context
        context = {"user_id": current_user.id}
        
        # Process list request
        response = kg_agent.respond("لیست گراف‌های دانش", context)
        
        return AgentResponse(
            response_id=f"list_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در نمایش گراف‌های دانش"),
            handled_by="KnowledgeGraphAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در نمایش گراف‌های دانش: {str(e)}",
            handled_by="KnowledgeGraphAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/knowledge-graph/build/public")
async def build_knowledge_graph_public(message: AgentMessage):
    """
    Build knowledge graph from text (public endpoint for testing).
    """
    try:
        # Get the knowledge graph agent from master agent
        kg_agent = master_agent.sub_agents.get("KnowledgeGraphAgent")
        if not kg_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="KnowledgeGraphAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="KnowledgeGraphAgent not found"
            )
        
        # Process message with knowledge graph agent (no user context for public endpoint)
        response = kg_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"kg_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در ساخت گراف دانش"),
            handled_by="KnowledgeGraphAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در ساخت گراف دانش: {str(e)}",
            handled_by="KnowledgeGraphAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/knowledge-graph/list/public")
async def list_knowledge_graphs_public():
    """
    List knowledge graphs (public endpoint for testing).
    """
    try:
        # Get the knowledge graph agent from master agent
        kg_agent = master_agent.sub_agents.get("KnowledgeGraphAgent")
        if not kg_agent:
            return AgentResponse(
                response_id=f"error_{hash('list') % 100000}",
                content="KnowledgeGraphAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="KnowledgeGraphAgent not found"
            )
        
        # Process list request (no user context for public endpoint)
        response = kg_agent.respond("لیست گراف‌های دانش", None)
        
        return AgentResponse(
            response_id=f"list_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در نمایش گراف‌های دانش"),
            handled_by="KnowledgeGraphAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در نمایش گراف‌های دانش: {str(e)}",
            handled_by="KnowledgeGraphAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/suggester/complete")
async def complete_suggestion(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Generate text completion suggestions (authenticated endpoint).
    """
    try:
        # Get the auto suggester agent from master agent
        suggester_agent = master_agent.sub_agents.get("AutoSuggesterAgent")
        if not suggester_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="AutoSuggesterAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="AutoSuggesterAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process completion request
        response = suggester_agent.respond(f"ادامه: {message.message}", context)
        
        return AgentResponse(
            response_id=f"complete_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تولید پیشنهادات ادامه"),
            handled_by="AutoSuggesterAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تولید پیشنهادات ادامه: {str(e)}",
            handled_by="AutoSuggesterAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/suggester/hints")
async def get_contextual_hints(current_user: User = Depends(get_current_active_user)):
    """
    Get contextual hints and suggestions (authenticated endpoint).
    """
    try:
        # Get the auto suggester agent from master agent
        suggester_agent = master_agent.sub_agents.get("AutoSuggesterAgent")
        if not suggester_agent:
            return AgentResponse(
                response_id=f"error_{hash('hints') % 100000}",
                content="AutoSuggesterAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="AutoSuggesterAgent not found"
            )
        
        # Add user context
        context = {"user_id": current_user.id}
        
        # Generate hints based on recent activity
        response = suggester_agent.respond("راهنماهای زمینه‌ای", context)
        
        return AgentResponse(
            response_id=f"hints_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در تولید راهنماها"),
            handled_by="AutoSuggesterAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تولید راهنماها: {str(e)}",
            handled_by="AutoSuggesterAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/suggester/complete/public")
async def complete_suggestion_public(message: AgentMessage):
    """
    Generate text completion suggestions (public endpoint for testing).
    """
    try:
        # Get the auto suggester agent from master agent
        suggester_agent = master_agent.sub_agents.get("AutoSuggesterAgent")
        if not suggester_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="AutoSuggesterAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="AutoSuggesterAgent not found"
            )
        
        # Process completion request (no user context for public endpoint)
        response = suggester_agent.respond(f"ادامه: {message.message}", message.context)
        
        return AgentResponse(
            response_id=f"complete_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تولید پیشنهادات ادامه"),
            handled_by="AutoSuggesterAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تولید پیشنهادات ادامه: {str(e)}",
            handled_by="AutoSuggesterAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/suggester/hints/public")
async def get_contextual_hints_public():
    """
    Get contextual hints and suggestions (public endpoint for testing).
    """
    try:
        # Get the auto suggester agent from master agent
        suggester_agent = master_agent.sub_agents.get("AutoSuggesterAgent")
        if not suggester_agent:
            return AgentResponse(
                response_id=f"error_{hash('hints') % 100000}",
                content="AutoSuggesterAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="AutoSuggesterAgent not found"
            )
        
        # Generate hints (no user context for public endpoint)
        response = suggester_agent.respond("راهنماهای زمینه‌ای", None)
        
        return AgentResponse(
            response_id=f"hints_{hash(str(response)) % 100000}",
            content=response.get("response", "خطا در تولید راهنماها"),
            handled_by="AutoSuggesterAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تولید راهنماها: {str(e)}",
            handled_by="AutoSuggesterAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/goal-inference/analyze")
async def analyze_goal_inference(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze goal and intent from user input (authenticated endpoint).
    """
    try:
        # Get the goal inference agent from master agent
        inference_agent = master_agent.sub_agents.get("GoalInferenceAgent")
        if not inference_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="GoalInferenceAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="GoalInferenceAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process goal inference request
        response = inference_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=f"inference_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل هدف و نیت"),
            handled_by="GoalInferenceAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل هدف: {str(e)}",
            handled_by="GoalInferenceAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/goal-inference/analyze/public")
async def analyze_goal_inference_public(message: AgentMessage):
    """
    Analyze goal and intent from user input (public endpoint for testing).
    """
    try:
        # Get the goal inference agent from master agent
        inference_agent = master_agent.sub_agents.get("GoalInferenceAgent")
        if not inference_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="GoalInferenceAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="GoalInferenceAgent not found"
            )
        
        # Process goal inference request (no user context for public endpoint)
        response = inference_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"inference_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل هدف و نیت"),
            handled_by="GoalInferenceAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل هدف: {str(e)}",
            handled_by="GoalInferenceAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/emotion-regulation/analyze")
async def analyze_emotion_regulation(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze emotion and provide regulation suggestions (authenticated endpoint).
    """
    try:
        # Get the emotion regulation agent from master agent
        emotion_agent = master_agent.sub_agents.get("EmotionRegulationAgent")
        if not emotion_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="EmotionRegulationAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="EmotionRegulationAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process emotion regulation request
        response = emotion_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=f"emotion_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل هیجان"),
            handled_by="EmotionRegulationAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل هیجان: {str(e)}",
            handled_by="EmotionRegulationAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/emotion-regulation/analyze/public")
async def analyze_emotion_regulation_public(message: AgentMessage):
    """
    Analyze emotion and provide regulation suggestions (public endpoint for testing).
    """
    try:
        # Get the emotion regulation agent from master agent
        emotion_agent = master_agent.sub_agents.get("EmotionRegulationAgent")
        if not emotion_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="EmotionRegulationAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="EmotionRegulationAgent not found"
            )
        
        # Process emotion regulation request (no user context for public endpoint)
        response = emotion_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"emotion_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل هیجان"),
            handled_by="EmotionRegulationAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل هیجان: {str(e)}",
            handled_by="EmotionRegulationAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/decision-support/analyze")
async def analyze_decision_support(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze decision with multi-dimensional assessment (authenticated endpoint).
    """
    try:
        # Get the decision support agent from master agent
        decision_agent = master_agent.sub_agents.get("DecisionSupportAgent")
        if not decision_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="DecisionSupportAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="DecisionSupportAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process decision support request
        response = decision_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=f"decision_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل تصمیم"),
            handled_by="DecisionSupportAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل تصمیم: {str(e)}",
            handled_by="DecisionSupportAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/decision-support/analyze/public")
async def analyze_decision_support_public(message: AgentMessage):
    """
    Analyze decision with multi-dimensional assessment (public endpoint for testing).
    """
    try:
        # Get the decision support agent from master agent
        decision_agent = master_agent.sub_agents.get("DecisionSupportAgent")
        if not decision_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="DecisionSupportAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="DecisionSupportAgent not found"
            )
        
        # Process decision support request (no user context for public endpoint)
        response = decision_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"decision_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در تحلیل تصمیم"),
            handled_by="DecisionSupportAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل تصمیم: {str(e)}",
            handled_by="DecisionSupportAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/decision-support/list")
async def list_decision_support(current_user: User = Depends(get_current_active_user)):
    """
    List recent decision analyses (authenticated endpoint).
    """
    try:
        # Get the decision support agent from master agent
        decision_agent = master_agent.sub_agents.get("DecisionSupportAgent")
        if not decision_agent:
            return {"error": "DecisionSupportAgent در دسترس نیست", "decisions": []}
        
        # Get recent decisions
        decisions = decision_agent.get_recent_decisions(limit=20)
        
        return {
            "decisions": decisions,
            "count": len(decisions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"خطا در دریافت فهرست تصمیمات: {str(e)}",
            "decisions": [],
            "count": 0
        }

@app.get("/agent/decision-support/list/public")
async def list_decision_support_public():
    """
    List recent decision analyses (public endpoint for testing).
    """
    try:
        # Get the decision support agent from master agent
        decision_agent = master_agent.sub_agents.get("DecisionSupportAgent")
        if not decision_agent:
            return {"error": "DecisionSupportAgent در دسترس نیست", "decisions": []}
        
        # Get recent decisions
        decisions = decision_agent.get_recent_decisions(limit=10)
        
        return {
            "decisions": decisions,
            "count": len(decisions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"خطا در دریافت فهرست تصمیمات: {str(e)}",
            "decisions": [],
            "count": 0
        }

# Self-Awareness Agent endpoints
@app.post("/agent/self-awareness/analyze")
async def analyze_self_awareness(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze self-awareness and mental state (authenticated endpoint).
    """
    try:
        # Get the self-awareness agent from master agent
        awareness_agent = master_agent.sub_agents.get("SelfAwarenessAgent")
        if not awareness_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="SelfAwarenessAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="SelfAwarenessAgent not found"
            )
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process self-awareness analysis
        response = awareness_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=f"awareness_{hash(message.message) % 100000}",
            content=response.get("content", "خطا در تحلیل خودآگاهی"),
            handled_by="SelfAwarenessAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل خودآگاهی: {str(e)}",
            handled_by="SelfAwarenessAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/self-awareness/analyze/public")
async def analyze_self_awareness_public(message: AgentMessage):
    """
    Analyze self-awareness and mental state (public endpoint for testing).
    """
    try:
        # Get the self-awareness agent from master agent
        awareness_agent = master_agent.sub_agents.get("SelfAwarenessAgent")
        if not awareness_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="SelfAwarenessAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="SelfAwarenessAgent not found"
            )
        
        # Process self-awareness analysis (no user context for public endpoint)
        response = awareness_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"awareness_{hash(message.message) % 100000}",
            content=response.get("content", "خطا در تحلیل خودآگاهی"),
            handled_by="SelfAwarenessAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل خودآگاهی: {str(e)}",
            handled_by="SelfAwarenessAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/self-awareness/logs")
async def get_self_awareness_logs(current_user: User = Depends(get_current_active_user)):
    """
    Get recent self-awareness analysis logs (authenticated endpoint).
    """
    try:
        # Get the self-awareness agent from master agent
        awareness_agent = master_agent.sub_agents.get("SelfAwarenessAgent")
        if not awareness_agent:
            return AgentResponse(
                response_id=f"error_{hash('logs') % 100000}",
                content="SelfAwarenessAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="SelfAwarenessAgent not found"
            )
        
        # Get recent logs
        logs = awareness_agent.get_recent_logs(10)
        
        return {
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در دریافت گزارش‌ها: {str(e)}",
            handled_by="SelfAwarenessAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/self-awareness/logs/public")
async def get_self_awareness_logs_public():
    """
    Get recent self-awareness analysis logs (public endpoint for testing).
    """
    try:
        # Get the self-awareness agent from master agent
        awareness_agent = master_agent.sub_agents.get("SelfAwarenessAgent")
        if not awareness_agent:
            return {
                "error": "SelfAwarenessAgent not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get recent logs (no user context for public endpoint)
        logs = awareness_agent.get_recent_logs(10)
        
        return {
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Error getting logs: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/agent/security-check/analyze")
async def analyze_security_check(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze mental/cognitive security threats (authenticated endpoint).
    """
    try:
        # Get the security check agent from master agent
        security_agent = master_agent.sub_agents.get("InteractiveSecurityCheckAgent")
        if not security_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="InteractiveSecurityCheckAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="InteractiveSecurityCheckAgent not found"
            )
        
        # Add user context
        context = {"user_id": current_user.id}
        context.update(message.context or {})
        
        # Process security check request
        response = security_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=response.get("response_id", f"security_{hash(message.message) % 100000}"),
            content=response.get("content", "خطا در بررسی امنیت ذهنی"),
            handled_by="InteractiveSecurityCheckAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در بررسی امنیت: {str(e)}",
            handled_by="InteractiveSecurityCheckAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/security-check/analyze/public")
async def analyze_security_check_public(message: AgentMessage):
    """
    Analyze mental/cognitive security threats (public endpoint for testing).
    """
    try:
        # Get the security check agent from master agent
        security_agent = master_agent.sub_agents.get("InteractiveSecurityCheckAgent")
        if not security_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="InteractiveSecurityCheckAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="InteractiveSecurityCheckAgent not found"
            )
        
        # Process security check request (no user context for public endpoint)
        response = security_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=response.get("response_id", f"security_{hash(message.message) % 100000}"),
            content=response.get("content", "خطا در بررسی امنیت ذهنی"),
            handled_by="InteractiveSecurityCheckAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در بررسی امنیت: {str(e)}",
            handled_by="InteractiveSecurityCheckAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/security-check/list")
async def list_security_checks(current_user: User = Depends(get_current_active_user)):
    """
    List recent security check analyses (authenticated endpoint).
    """
    try:
        # Get the security check agent from master agent
        security_agent = master_agent.sub_agents.get("InteractiveSecurityCheckAgent")
        if not security_agent:
            return {
                "error": "InteractiveSecurityCheckAgent not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get recent security checks (with user context)
        security_checks = security_agent.list_recent_security_checks(10)
        
        return security_checks
        
    except Exception as e:
        return {
            "error": f"Error listing security checks: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/agent/security-check/list/public")
async def list_security_checks_public():
    """
    List recent security check analyses (public endpoint for testing).
    """
    try:
        # Get the security check agent from master agent
        security_agent = master_agent.sub_agents.get("InteractiveSecurityCheckAgent")
        if not security_agent:
            return {
                "error": "InteractiveSecurityCheckAgent not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get recent security checks (no user context for public endpoint)
        security_checks = security_agent.list_recent_security_checks(10)
        
        return security_checks
        
    except Exception as e:
        return {
            "error": f"Error listing security checks: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/agent/reward/analyze")
async def analyze_reward(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze for positive progress and generate reward feedback (authenticated endpoint).
    """
    try:
        # Get the reward agent from master agent
        reward_agent = master_agent.sub_agents.get("RewardAgent")
        if not reward_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="RewardAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="RewardAgent not found"
            )
        
        # Add user context
        context = {"user_id": current_user.id}
        context.update(message.context or {})
        
        # Process reward analysis request
        response = reward_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=response.get("response_id", f"reward_{hash(message.message) % 100000}"),
            content=response.get("content", "خطا در تحلیل پیشرفت"),
            handled_by="RewardAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل پاداش: {str(e)}",
            handled_by="RewardAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.post("/agent/reward/analyze/public")
async def analyze_reward_public(message: AgentMessage):
    """
    Analyze for positive progress and generate reward feedback (public endpoint for testing).
    """
    try:
        # Get the reward agent from master agent
        reward_agent = master_agent.sub_agents.get("RewardAgent")
        if not reward_agent:
            return AgentResponse(
                response_id=f"error_{hash(message.message) % 100000}",
                content="RewardAgent در دسترس نیست",
                handled_by="MasterAgent",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="RewardAgent not found"
            )
        
        # Process reward analysis request (no user context for public endpoint)
        response = reward_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=response.get("response_id", f"reward_{hash(message.message) % 100000}"),
            content=response.get("content", "خطا در تحلیل پیشرفت"),
            handled_by="RewardAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", False),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در تحلیل پاداش: {str(e)}",
            handled_by="RewardAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )

@app.get("/agent/reward/logs")
async def get_reward_logs(current_user: User = Depends(get_current_active_user)):
    """
    Get recent reward logs (authenticated endpoint).
    """
    try:
        # Get the reward agent from master agent
        reward_agent = master_agent.sub_agents.get("RewardAgent")
        if not reward_agent:
            return {
                "error": "RewardAgent not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get recent reward logs (with user context)
        reward_logs = reward_agent.list_recent_rewards(10)
        
        return reward_logs
        
    except Exception as e:
        return {
            "error": f"Error getting reward logs: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/agent/reward/logs/public")
async def get_reward_logs_public():
    """
    Get recent reward logs (public endpoint for testing).
    """
    try:
        # Get the reward agent from master agent
        reward_agent = master_agent.sub_agents.get("RewardAgent")
        if not reward_agent:
            return {
                "error": "RewardAgent not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get recent reward logs (no user context for public endpoint)
        reward_logs = reward_agent.list_recent_rewards(10)
        
        return reward_logs
        
    except Exception as e:
        return {
            "error": f"Error getting reward logs: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# BiasDetectionAgent endpoints
@app.post("/agent/bias-detection/analyze", response_model=AgentResponse)
async def analyze_bias(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze text for cognitive biases (authenticated endpoint).
    """
    try:
        bias_agent = master_agent.sub_agents.get("BiasDetectionAgent")
        if not bias_agent:
            raise HTTPException(status_code=404, detail="BiasDetectionAgent not found")
        
        # Analyze bias
        result = bias_agent.analyze_bias(message.message)
        
        # Format response
        response_content = f"""🧠 **تحلیل سوگیری شناختی:**

**🔍 نتیجه تحلیل:**
• 🎯 **سوگیری:** {', '.join(result['bias_type']) if result['bias_type'] else 'هیچ سوگیری شناسایی نشد'}
• 📊 **شدت:** {'█' * int(result['severity_score'] * 5)}{'░' * (5 - int(result['severity_score'] * 5))} ({result['severity_score']:.1%})
• 🤔 **اطمینان:** {result['confidence']:.1%}

**💡 پیشنهاد تأملی:**
{result['suggestion']}

**📋 شناسه:** {result['log_id']}"""
        
        return AgentResponse(
            response_id=result['log_id'],
            content=response_content,
            handled_by="BiasDetectionAgent",
            timestamp=datetime.now().isoformat(),
            success=result.get('success', True)
        )
    except Exception as e:
        logger.error(f"Error analyzing bias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/bias-detection/logs")
async def get_bias_logs(current_user: User = Depends(get_current_active_user)):
    """
    Get recent bias analysis logs (authenticated endpoint).
    """
    try:
        bias_agent = master_agent.sub_agents.get("BiasDetectionAgent")
        if not bias_agent:
            raise HTTPException(status_code=404, detail="BiasDetectionAgent not found")
        
        logs = bias_agent.get_bias_logs()
        return {
            "bias_logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting bias logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/bias-detection/analyze/public", response_model=AgentResponse)
async def analyze_bias_public(message: AgentMessage):
    """
    Analyze text for cognitive biases (public endpoint for testing).
    """
    try:
        bias_agent = master_agent.sub_agents.get("BiasDetectionAgent")
        if not bias_agent:
            raise HTTPException(status_code=404, detail="BiasDetectionAgent not found")
        
        # Analyze bias
        result = bias_agent.analyze_bias(message.message)
        
        # Format response
        response_content = f"""🧠 **تحلیل سوگیری شناختی:**

**🔍 نتیجه تحلیل:**
• 🎯 **سوگیری:** {', '.join(result['bias_type']) if result['bias_type'] else 'هیچ سوگیری شناسایی نشد'}
• 📊 **شدت:** {'█' * int(result['severity_score'] * 5)}{'░' * (5 - int(result['severity_score'] * 5))} ({result['severity_score']:.1%})
• 🤔 **اطمینان:** {result['confidence']:.1%}

**💡 پیشنهاد تأملی:**
{result['suggestion']}

**📋 شناسه:** {result['log_id']}"""
        
        return AgentResponse(
            response_id=result['log_id'],
            content=response_content,
            handled_by="BiasDetectionAgent",
            timestamp=datetime.now().isoformat(),
            success=result.get('success', True)
        )
    except Exception as e:
        logger.error(f"Error analyzing bias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/bias-detection/logs/public")
async def get_bias_logs_public():
    """
    Get recent bias analysis logs (public endpoint for testing).
    """
    try:
        bias_agent = master_agent.sub_agents.get("BiasDetectionAgent")
        if not bias_agent:
            raise HTTPException(status_code=404, detail="BiasDetectionAgent not found")
        
        logs = bias_agent.get_bias_logs()
        return {
            "bias_logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting bias logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Cognitive Distortion Agent Endpoints
@app.post("/agent/cognitive-distortion/analyze", response_model=AgentResponse)
async def analyze_cognitive_distortion(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze text for cognitive distortions (authenticated endpoint).
    """
    try:
        cognitive_distortion_agent = master_agent.sub_agents.get("CognitiveDistortionAgent")
        if not cognitive_distortion_agent:
            raise HTTPException(status_code=404, detail="CognitiveDistortionAgent not found")
        
        # Analyze distortion
        result = cognitive_distortion_agent.analyze_distortion(message.message)
        
        # Format response
        response_content = f"""🧠 **تحلیل تحریف‌های شناختی:**

**🔍 نتیجه تحلیل:**
• 🎯 **تحریف:** {', '.join(result['detected_types']) if result['detected_types'] else 'هیچ تحریف شناختی شناسایی نشد'}
• 📊 **شدت:** {'█' * int(result['severity_score'] * 5)}{'░' * (5 - int(result['severity_score'] * 5))} ({result['severity_score']:.1%})
• 🤔 **اطمینان:** {result['confidence']:.1%}

**💡 پیشنهاد بازسازی شناختی:**
{result['recommendation']}

**📋 شناسه:** {result['log_id']}"""
        
        return AgentResponse(
            response_id=result['log_id'],
            content=response_content,
            handled_by="CognitiveDistortionAgent",
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except Exception as e:
        logger.error(f"Error analyzing cognitive distortion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/cognitive-distortion/logs")
async def get_cognitive_distortion_logs(current_user: User = Depends(get_current_active_user)):
    """
    Get recent cognitive distortion analysis logs (authenticated endpoint).
    """
    try:
        cognitive_distortion_agent = master_agent.sub_agents.get("CognitiveDistortionAgent")
        if not cognitive_distortion_agent:
            raise HTTPException(status_code=404, detail="CognitiveDistortionAgent not found")
        
        logs = cognitive_distortion_agent.get_distortion_logs()
        return {
            "distortion_logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cognitive distortion logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/cognitive-distortion/analyze/public", response_model=AgentResponse)
async def analyze_cognitive_distortion_public(message: AgentMessage):
    """
    Analyze text for cognitive distortions (public endpoint).
    """
    try:
        cognitive_distortion_agent = master_agent.sub_agents.get("CognitiveDistortionAgent")
        if not cognitive_distortion_agent:
            raise HTTPException(status_code=404, detail="CognitiveDistortionAgent not found")
        
        # Analyze distortion
        result = cognitive_distortion_agent.analyze_distortion(message.message)
        
        # Format response
        response_content = f"""🧠 **تحلیل تحریف‌های شناختی:**

**🔍 نتیجه تحلیل:**
• 🎯 **تحریف:** {', '.join(result['detected_types']) if result['detected_types'] else 'هیچ تحریف شناختی شناسایی نشد'}
• 📊 **شدت:** {'█' * int(result['severity_score'] * 5)}{'░' * (5 - int(result['severity_score'] * 5))} ({result['severity_score']:.1%})
• 🤔 **اطمینان:** {result['confidence']:.1%}

**💡 پیشنهاد بازسازی شناختی:**
{result['recommendation']}

**📋 شناسه:** {result['log_id']}"""
        
        return AgentResponse(
            response_id=result['log_id'],
            content=response_content,
            handled_by="CognitiveDistortionAgent",
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except Exception as e:
        logger.error(f"Error analyzing cognitive distortion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/cognitive-distortion/logs/public")
async def get_cognitive_distortion_logs_public():
    """
    Get recent cognitive distortion analysis logs (public endpoint).
    """
    try:
        cognitive_distortion_agent = master_agent.sub_agents.get("CognitiveDistortionAgent")
        if not cognitive_distortion_agent:
            raise HTTPException(status_code=404, detail="CognitiveDistortionAgent not found")
        
        logs = cognitive_distortion_agent.get_distortion_logs()
        return {
            "distortion_logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cognitive distortion logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Ethical Reasoning Agent Endpoints
@app.post("/agent/ethical-reasoning/analyze", response_model=AgentResponse)
async def analyze_ethical_reasoning(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Analyze text for ethical reasoning and value alignment (authenticated endpoint).
    """
    try:
        ethical_agent = master_agent.sub_agents.get("EthicalReasoningAgent")
        if not ethical_agent:
            raise HTTPException(status_code=404, detail="EthicalReasoningAgent not found")
        
        # Analyze ethical reasoning
        result = ethical_agent.analyze_ethics(message.message)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        analysis = result['analysis']
        
        # Format response
        status_emoji = {'ok': '✅', 'warning': '🟡', 'alert': '🔴'}
        response_content = f"""🧭 **تحلیل استدلال اخلاقی:**

{status_emoji.get(analysis['status'], '❓')} **وضعیت اخلاقی:** {analysis['status']}

**📊 نتیجه تحلیل:**
• 🎯 **اطمینان:** {'█' * int(analysis['confidence'] * 5)}{'░' * (5 - int(analysis['confidence'] * 5))} ({analysis['confidence']:.1%})
• ⚠️ **امتیاز خطر:** {'█' * int(analysis['risk_score'] * 5)}{'░' * (5 - int(analysis['risk_score'] * 5))} ({analysis['risk_score']:.1%})
• 📚 **چارچوب‌های شناسایی شده:** {', '.join(analysis['framework_flags']) if analysis['framework_flags'] else 'هیچ چارچوب خاصی'}

**💡 راهنمایی اخلاقی:**
{analysis['ethical_guidance']}

**🔍 روش تحلیل:** {analysis['detection_method']}
**📋 شناسه:** {result['log_id']}"""
        
        return AgentResponse(
            response_id=result['log_id'],
            content=response_content,
            handled_by="EthicalReasoningAgent",
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing ethical reasoning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/ethical-reasoning/logs")
async def get_ethical_reasoning_logs(current_user: User = Depends(get_current_active_user)):
    """
    Get recent ethical reasoning analysis logs (authenticated endpoint).
    """
    try:
        ethical_agent = master_agent.sub_agents.get("EthicalReasoningAgent")
        if not ethical_agent:
            raise HTTPException(status_code=404, detail="EthicalReasoningAgent not found")
        
        logs = ethical_agent.get_ethical_logs()
        return {
            "ethical_logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ethical reasoning logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/ethical-reasoning/analyze/public", response_model=AgentResponse)
async def analyze_ethical_reasoning_public(message: AgentMessage):
    """
    Analyze text for ethical reasoning and value alignment (public endpoint).
    """
    try:
        ethical_agent = master_agent.sub_agents.get("EthicalReasoningAgent")
        if not ethical_agent:
            raise HTTPException(status_code=404, detail="EthicalReasoningAgent not found")
        
        # Analyze ethical reasoning
        result = ethical_agent.analyze_ethics(message.message)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        analysis = result['analysis']
        
        # Format response
        status_emoji = {'ok': '✅', 'warning': '🟡', 'alert': '🔴'}
        response_content = f"""🧭 **تحلیل استدلال اخلاقی:**

{status_emoji.get(analysis['status'], '❓')} **وضعیت اخلاقی:** {analysis['status']}

**📊 نتیجه تحلیل:**
• 🎯 **اطمینان:** {'█' * int(analysis['confidence'] * 5)}{'░' * (5 - int(analysis['confidence'] * 5))} ({analysis['confidence']:.1%})
• ⚠️ **امتیاز خطر:** {'█' * int(analysis['risk_score'] * 5)}{'░' * (5 - int(analysis['risk_score'] * 5))} ({analysis['risk_score']:.1%})
• 📚 **چارچوب‌های شناسایی شده:** {', '.join(analysis['framework_flags']) if analysis['framework_flags'] else 'هیچ چارچوب خاصی'}

**💡 راهنمایی اخلاقی:**
{analysis['ethical_guidance']}

**🔍 روش تحلیل:** {analysis['detection_method']}
**📋 شناسه:** {result['log_id']}"""
        
        return AgentResponse(
            response_id=result['log_id'],
            content=response_content,
            handled_by="EthicalReasoningAgent",
            timestamp=datetime.now().isoformat(),
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing ethical reasoning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/ethical-reasoning/logs/public")
async def get_ethical_reasoning_logs_public():
    """
    Get recent ethical reasoning analysis logs (public endpoint).
    """
    try:
        ethical_agent = master_agent.sub_agents.get("EthicalReasoningAgent")
        if not ethical_agent:
            raise HTTPException(status_code=404, detail="EthicalReasoningAgent not found")
        
        logs = ethical_agent.get_ethical_logs()
        return {
            "ethical_logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ethical reasoning logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/consensus/simulate")
async def simulate_consensus_decision(message: AgentMessage, current_user: User = Depends(get_current_active_user)):
    """
    Simulate consensus decision-making process (authenticated endpoint).
    """
    try:
        consensus_agent = master_agent.sub_agents.get("SimulatedConsensusAgent")
        if not consensus_agent:
            raise HTTPException(status_code=404, detail="SimulatedConsensusAgent not found")
        
        # Add user context
        context = message.context or {}
        context["user_id"] = current_user.id
        
        # Process message with consensus agent
        response = consensus_agent.respond(message.message, context)
        
        return AgentResponse(
            response_id=f"consensus_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در شبیه‌سازی تصمیم‌گیری گروهی"),
            handled_by="SimulatedConsensusAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", True),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در شبیه‌سازی تصمیم‌گیری گروهی: {str(e)}",
            handled_by="SimulatedConsensusAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )


@app.get("/agent/consensus/logs")
async def get_consensus_logs(current_user: User = Depends(get_current_active_user)):
    """
    Get recent consensus decision logs (authenticated endpoint).
    """
    try:
        consensus_agent = master_agent.sub_agents.get("SimulatedConsensusAgent")
        if not consensus_agent:
            raise HTTPException(status_code=404, detail="SimulatedConsensusAgent not found")
        
        logs = consensus_agent.get_consensus_logs()
        return {
            "consensus_logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "consensus_logs": [],
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }


@app.post("/agent/consensus/simulate/public")
async def simulate_consensus_decision_public(message: AgentMessage):
    """
    Simulate consensus decision-making process (public endpoint for testing).
    """
    try:
        consensus_agent = master_agent.sub_agents.get("SimulatedConsensusAgent")
        if not consensus_agent:
            raise HTTPException(status_code=404, detail="SimulatedConsensusAgent not found")
        
        # Process message with consensus agent (no user context for public endpoint)
        response = consensus_agent.respond(message.message, message.context)
        
        return AgentResponse(
            response_id=f"consensus_{hash(message.message) % 100000}",
            content=response.get("response", "خطا در شبیه‌سازی تصمیم‌گیری گروهی"),
            handled_by="SimulatedConsensusAgent",
            timestamp=response.get("timestamp", ""),
            success=response.get("success", True),
            error=response.get("error")
        )
        
    except Exception as e:
        return AgentResponse(
            response_id=f"error_{hash(str(e)) % 100000}",
            content=f"خطا در شبیه‌سازی تصمیم‌گیری گروهی: {str(e)}",
            handled_by="SimulatedConsensusAgent",
            timestamp=datetime.now().isoformat(),
            success=False,
            error=str(e)
        )


@app.get("/agent/consensus/logs/public")
async def get_consensus_logs_public():
    """
    Get recent consensus decision logs (public endpoint for testing).
    """
    try:
        consensus_agent = master_agent.sub_agents.get("SimulatedConsensusAgent")
        if not consensus_agent:
            raise HTTPException(status_code=404, detail="SimulatedConsensusAgent not found")
        
        logs = consensus_agent.get_consensus_logs()
        return {
            "consensus_logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "consensus_logs": [],
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }


# ===================== Advanced Memory Manager Agent Endpoints =====================

@app.post("/agent/memory/analyze")
async def analyze_memory(entry: dict, current_user: User = Depends(get_current_active_user)):
    """
    Analyze and store memory entry with classification and importance scoring (authenticated endpoint).
    """
    try:
        memory_agent = master_agent.sub_agents.get("AdvancedMemoryManagerAgent")
        if not memory_agent:
            raise HTTPException(status_code=404, detail="AdvancedMemoryManagerAgent not found")
        
        # Add user context to memory entry
        entry["user_id"] = current_user.id
        entry["metadata"] = entry.get("metadata", {})
        entry["metadata"]["user_email"] = current_user.email
        
        result = memory_agent.analyze_and_store(entry, current_user.id)
        
        return {
            "memory_analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "memory_analysis": {"status": "error", "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }


@app.get("/agent/memory/retrieve/{memory_type}")
async def retrieve_memory(memory_type: str, mission_id: str = None, limit: int = 100, 
                         min_importance: int = 1, current_user: User = Depends(get_current_active_user)):
    """
    Retrieve memory entries based on criteria (authenticated endpoint).
    """
    try:
        memory_agent = master_agent.sub_agents.get("AdvancedMemoryManagerAgent")
        if not memory_agent:
            raise HTTPException(status_code=404, detail="AdvancedMemoryManagerAgent not found")
        
        memories = memory_agent.retrieve(
            memory_type=memory_type,
            user_id=current_user.id,
            mission_id=mission_id,
            limit=limit,
            min_importance=min_importance
        )
        
        return {
            "memories": memories,
            "count": len(memories),
            "memory_type": memory_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "memories": [],
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }


@app.get("/agent/memory/summarize/{memory_type}")
async def summarize_memory_type(memory_type: str, force_refresh: bool = False, 
                               current_user: User = Depends(get_current_active_user)):
    """
    Generate or retrieve summary of memory type (authenticated endpoint).
    """
    try:
        memory_agent = master_agent.sub_agents.get("AdvancedMemoryManagerAgent")
        if not memory_agent:
            raise HTTPException(status_code=404, detail="AdvancedMemoryManagerAgent not found")
        
        summary = memory_agent.summarize(memory_type, current_user.id, force_refresh)
        
        return {
            "summary_data": summary,
            "memory_type": memory_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "summary_data": {"summary": f"خطا در خلاصه‌سازی: {str(e)}", "entry_count": 0},
            "timestamp": datetime.now().isoformat()
        }


@app.delete("/agent/memory/purge/{memory_type}")
async def purge_memory(memory_type: str, min_importance: int = 1, dry_run: bool = False,
                      current_user: User = Depends(get_current_active_user)):
    """
    Purge memory entries based on criteria (authenticated endpoint).
    """
    try:
        memory_agent = master_agent.sub_agents.get("AdvancedMemoryManagerAgent")
        if not memory_agent:
            raise HTTPException(status_code=404, detail="AdvancedMemoryManagerAgent not found")
        
        result = memory_agent.purge(
            memory_type=memory_type,
            min_importance=min_importance,
            dry_run=dry_run
        )
        
        return {
            "purge_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "purge_result": {"status": "error", "error": str(e), "purged_count": 0},
            "timestamp": datetime.now().isoformat()
        }


@app.get("/agent/memory/statistics")
async def get_memory_statistics(current_user: User = Depends(get_current_active_user)):
    """
    Get comprehensive memory statistics (authenticated endpoint).
    """
    try:
        memory_agent = master_agent.sub_agents.get("AdvancedMemoryManagerAgent")
        if not memory_agent:
            raise HTTPException(status_code=404, detail="AdvancedMemoryManagerAgent not found")
        
        stats = memory_agent.get_memory_statistics()
        
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "statistics": {"status": "error", "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }


# Public endpoints for testing
@app.post("/agent/memory/analyze/public")
async def analyze_memory_public(entry: dict):
    """
    Analyze and store memory entry (public endpoint for testing).
    """
    try:
        memory_agent = master_agent.sub_agents.get("AdvancedMemoryManagerAgent")
        if not memory_agent:
            raise HTTPException(status_code=404, detail="AdvancedMemoryManagerAgent not found")
        
        result = memory_agent.analyze_and_store(entry)
        
        return {
            "memory_analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "memory_analysis": {"status": "error", "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }


@app.get("/agent/memory/retrieve/{memory_type}/public")
async def retrieve_memory_public(memory_type: str, mission_id: str = None, limit: int = 100, 
                                min_importance: int = 1):
    """
    Retrieve memory entries (public endpoint for testing).
    """
    try:
        memory_agent = master_agent.sub_agents.get("AdvancedMemoryManagerAgent")
        if not memory_agent:
            raise HTTPException(status_code=404, detail="AdvancedMemoryManagerAgent not found")
        
        memories = memory_agent.retrieve(
            memory_type=memory_type,
            mission_id=mission_id,
            limit=limit,
            min_importance=min_importance
        )
        
        return {
            "memories": memories,
            "count": len(memories),
            "memory_type": memory_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "memories": [],
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }


@app.get("/agent/memory/statistics/public")
async def get_memory_statistics_public():
    """
    Get comprehensive memory statistics (public endpoint for testing).
    """
    try:
        memory_agent = master_agent.sub_agents.get("AdvancedMemoryManagerAgent")
        if not memory_agent:
            raise HTTPException(status_code=404, detail="AdvancedMemoryManagerAgent not found")
        
        stats = memory_agent.get_memory_statistics()
        
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "statistics": {"status": "error", "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
