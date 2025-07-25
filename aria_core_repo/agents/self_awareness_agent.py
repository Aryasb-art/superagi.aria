"""
Self Awareness Agent for analyzing mental state, self-awareness level, and alignment between speech and goals/emotions.
"""

import json
import logging
import os
import random
from datetime import datetime
from typing import Dict, Any, Optional, List

from openai import OpenAI
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .base_agent import BaseAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SelfAwarenessLog(Base):
    """Database model for storing self-awareness analysis logs and metadata."""
    __tablename__ = "self_awareness_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    input_text = Column(Text, nullable=False)  # Original input text
    status = Column(String(20), nullable=False)  # ok, warning, alert
    alert = Column(Text, nullable=False)  # Alert message or suggestion
    confidence = Column(Float, nullable=False, default=0.0)  # Confidence score 0-1
    related_memory = Column(Text, nullable=True)  # Related memory or goal
    analysis_data = Column(Text, nullable=True)  # JSON string of analysis details
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SelfAwarenessAgent(BaseAgent):
    """
    Self Awareness Agent that analyzes mental state, self-awareness level, and alignment
    between speech and goals/emotions using OpenAI GPT-4o integration.
    """
    
    def __init__(self):
        super().__init__("SelfAwarenessAgent")
        
        # Create self-awareness logs table
        self._create_logs_table()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        self._initialize_openai()
        
        # Self-awareness keywords for pattern matching
        self.awareness_keywords = [
            "خستگی", "بی‌انگیزگی", "سردرگمی", "گم شدن", "هدف",
            "نمی‌دونم", "چی کار", "انگیزه", "تمرکز", "بی‌تمرکز",
            "tired", "confused", "lost", "motivation", "focus", "unfocused",
            "احساس خستگی", "نمی‌دونم دارم چی کار می‌کنم", "هدفی که داشتم چی بود؟",
            "انگیزه‌ام از بین رفته", "گیج شدم", "راه گم کردم"
        ]
        
        # Status categories and their indicators
        self.status_patterns = {
            "ok": ["خوب", "عالی", "روشن", "متمرکز", "انگیزه دارم", "confident", "clear", "focused"],
            "warning": ["خسته", "کمی گیج", "نیاز به استراحت", "tired", "slightly confused", "need break"],
            "alert": ["خیلی گیج", "کاملاً گم", "هیچ انگیزه‌ای ندارم", "very confused", "completely lost", "no motivation"]
        }
        
        logger.info(f"[{self.name}] Initialized with PostgreSQL database integration for self-awareness analysis")
    
    def _create_logs_table(self):
        """Create self_awareness_logs table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info(f"[{self.name}] Self-awareness logs table ready")
        except Exception as e:
            logger.error(f"[{self.name}] Failed to create self-awareness logs table: {e}")
    
    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                logger.info(f"[{self.name}] OpenAI GPT integration ready for self-awareness analysis")
            else:
                logger.warning(f"[{self.name}] OpenAI API key not found, using fallback pattern detection")
        except Exception as e:
            logger.error(f"[{self.name}] Failed to initialize OpenAI client: {e}")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process self-awareness analysis requests and generate response.
        
        Args:
            message (str): The message containing self-awareness analysis request
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing self-awareness analysis and recommendations
        """
        try:
            # Extract user ID from context if available
            user_id = context.get("user_id") if context else None
            
            # Analyze self-awareness
            analysis_result = self.analyze_self_awareness(message, context)
            
            # Save analysis to database
            log_id = self._save_analysis_log(
                user_id=user_id,
                input_text=message,
                status=analysis_result["status"],
                alert=analysis_result["alert"],
                confidence=analysis_result["confidence"],
                related_memory=analysis_result.get("related_memory", ""),
                analysis_data=json.dumps(analysis_result, ensure_ascii=False)
            )
            
            # Format response
            response_content = self._format_analysis_response(analysis_result)
            
            # Remember the interaction
            self.remember(f"User: {message}")
            self.remember(f"Self-awareness analysis: {analysis_result['status']} (confidence: {analysis_result['confidence']:.1f})")
            
            return {
                "response_id": f"awareness_{log_id}",
                "content": response_content,
                "handled_by": self.name,
                "timestamp": self._get_current_timestamp(),
                "success": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error in respond: {e}")
            return {
                "response_id": f"awareness_{random.randint(1000, 99999)}",
                "content": f"خطا در تحلیل خودآگاهی: {str(e)}",
                "handled_by": self.name,
                "timestamp": self._get_current_timestamp(),
                "success": False,
                "error": str(e)
            }
    
    def analyze_self_awareness(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze self-awareness level and mental state alignment.
        
        Args:
            message (str): The input text to analyze
            context (Dict): Optional context information
            
        Returns:
            Dict: Analysis result with status, confidence, alert, and related_memory
        """
        try:
            # Get memory context
            memory_context = self._analyze_memory_context(message)
            
            # Try GPT-powered analysis first
            if self.openai_client:
                try:
                    return self._analyze_with_gpt(message, memory_context)
                except Exception as e:
                    logger.warning(f"[{self.name}] GPT analysis failed: {e}")
            
            # Fallback to pattern-based analysis
            return self._analyze_with_patterns(message, memory_context)
            
        except Exception as e:
            logger.error(f"[{self.name}] Error in analyze_self_awareness: {e}")
            return {
                "status": "warning",
                "confidence": 0.3,
                "alert": "خطا در تحلیل خودآگاهی - لطفاً دوباره تلاش کنید",
                "related_memory": "خطا در سیستم"
            }
    
    def _analyze_memory_context(self, message: str) -> Dict[str, Any]:
        """Analyze memory context from short-term memory and other agents."""
        try:
            context = {
                "themes": self._extract_themes(message),
                "urgency": self._assess_urgency(message),
                "category": self._categorize_message(message),
                "short_term_memory": self.get_recent_memory(5),
                "awareness_indicators": self._detect_awareness_indicators(message)
            }
            return context
        except Exception as e:
            logger.error(f"[{self.name}] Error analyzing memory context: {e}")
            return {"themes": [], "urgency": "low", "category": "general"}
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract dominant themes from text."""
        themes = []
        theme_keywords = {
            "هدف": ["هدف", "آرزو", "خواسته", "می‌خواهم", "goal", "want", "wish"],
            "انگیزه": ["انگیزه", "انرژی", "شور", "motivation", "energy", "passion"],
            "خستگی": ["خسته", "کوفته", "بی‌حال", "tired", "exhausted", "weary"],
            "سردرگمی": ["گیج", "سردرگم", "نمی‌دونم", "confused", "lost", "don't know"],
            "تمرکز": ["تمرکز", "توجه", "focus", "attention", "concentrate"]
        }
        
        text_lower = text.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]  # Return top 3 themes
    
    def _categorize_message(self, message: str) -> str:
        """Categorize the message based on content."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["هدف", "آرزو", "می‌خواهم", "goal", "want"]):
            return "goal"
        elif any(word in message_lower for word in ["مشکل", "problem", "issue", "نگران", "worry"]):
            return "problem"
        elif any(word in message_lower for word in ["خسته", "tired", "کوفته", "exhausted"]):
            return "fatigue"
        elif any(word in message_lower for word in ["گیج", "confused", "سردرگم", "lost"]):
            return "confusion"
        else:
            return "general"
    
    def _assess_urgency(self, message: str) -> str:
        """Assess urgency level of the message."""
        message_lower = message.lower()
        
        high_urgency = ["فوری", "urgent", "خیلی", "very", "کاملاً", "completely"]
        medium_urgency = ["نیاز", "need", "باید", "should", "مهم", "important"]
        
        if any(word in message_lower for word in high_urgency):
            return "high"
        elif any(word in message_lower for word in medium_urgency):
            return "medium"
        else:
            return "low"
    
    def _detect_awareness_indicators(self, message: str) -> List[str]:
        """Detect self-awareness indicators in the message."""
        indicators = []
        message_lower = message.lower()
        
        awareness_patterns = {
            "self_reflection": ["فکر می‌کنم", "احساس می‌کنم", "متوجه شدم", "i think", "i feel", "i realize"],
            "goal_awareness": ["هدفم", "می‌خواهم", "قصد دارم", "my goal", "i want", "i intend"],
            "confusion": ["نمی‌دونم", "گیج", "سردرگم", "don't know", "confused", "lost"],
            "fatigue": ["خسته", "کوفته", "بی‌حال", "tired", "exhausted", "weary"],
            "motivation": ["انگیزه", "شور", "علاقه", "motivation", "passion", "interest"]
        }
        
        for indicator, keywords in awareness_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                indicators.append(indicator)
        
        return indicators
    
    def _analyze_with_gpt(self, message: str, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze self-awareness using OpenAI GPT-4o."""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """شما یک متخصص تحلیل خودآگاهی و وضعیت ذهنی هستید. وظیفه شما تحلیل متن ورودی کاربر و تشخیص:
                        1. سطح خودآگاهی (آیا کاربر از اهداف و وضعیت خود آگاه است؟)
                        2. تطابق گفتار با هدف (آیا کاربر در مسیر هدف است یا منحرف شده؟)
                        3. وضعیت ذهنی (خستگی، بی‌انگیزگی، تمرکز، انرژی)
                        4. نیاز به هشدار یا تنظیم مسیر

                        خروجی را در قالب JSON برگردانید:
                        {
                            "status": "ok" | "warning" | "alert",
                            "confidence": عدد بین 0 تا 1,
                            "alert": "متن هشدار یا پیشنهاد به فارسی",
                            "related_memory": "خاطره یا هدف مرتبط"
                        }
                        
                        معیارهای تصمیم‌گیری:
                        - ok: کاربر آگاه، متمرکز، و در مسیر هدف است
                        - warning: احتمال خستگی، بی‌تمرکزی، یا انحراف جزئی
                        - alert: نیاز فوری به تنظیم مسیر، خستگی شدید، یا گم شدن کامل
                        """
                    },
                    {
                        "role": "user",
                        "content": f"متن ورودی: {message}\n\nزمینه حافظه: {json.dumps(memory_context, ensure_ascii=False)}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize the result
            return {
                "status": result.get("status", "warning"),
                "confidence": max(0.0, min(1.0, result.get("confidence", 0.5))),
                "alert": result.get("alert", "تحلیل خودآگاهی انجام شد"),
                "related_memory": result.get("related_memory", "")
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] GPT analysis failed: {e}")
            raise e
    
    def _analyze_with_patterns(self, message: str, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze self-awareness using pattern-based detection."""
        try:
            message_lower = message.lower()
            confidence = 0.6  # Base confidence for pattern matching
            
            # Detect status based on patterns
            status = "ok"  # Default
            alert = "وضعیت ذهنی شما نرمال به نظر می‌رسد"
            related_memory = ""
            
            # Check for alert patterns
            alert_patterns = [
                "نمی‌دونم دارم چی کار می‌کنم", "کاملاً گم", "هیچ انگیزه‌ای ندارم",
                "don't know what i'm doing", "completely lost", "no motivation"
            ]
            
            if any(pattern in message_lower for pattern in alert_patterns):
                status = "alert"
                confidence = 0.8
                alert = "🔴 هشدار: نیاز فوری به تنظیم مسیر - لطفاً استراحت کنید و اهداف خود را بازنگری کنید"
                related_memory = "نیاز به بازنگری اهداف"
            
            # Check for warning patterns
            elif any(pattern in message_lower for pattern in ["خسته", "گیج", "بی‌تمرکز", "tired", "confused"]):
                status = "warning"
                confidence = 0.7
                alert = "🟡 احتیاط: احتمال خستگی یا بی‌تمرکزی - پیشنهاد استراحت کوتاه"
                related_memory = "نیاز به استراحت"
            
            # Check for positive patterns
            elif any(pattern in message_lower for pattern in ["خوب", "عالی", "متمرکز", "good", "great", "focused"]):
                status = "ok"
                confidence = 0.8
                alert = "🟢 عالی: وضعیت ذهنی مناسب - ادامه دهید"
                related_memory = "وضعیت مثبت"
            
            # Analyze themes for additional context
            themes = memory_context.get("themes", [])
            if "سردرگمی" in themes:
                if status == "ok":
                    status = "warning"
                confidence = min(confidence + 0.1, 1.0)
            
            return {
                "status": status,
                "confidence": confidence,
                "alert": alert,
                "related_memory": related_memory
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Pattern analysis failed: {e}")
            return {
                "status": "warning",
                "confidence": 0.3,
                "alert": "خطا در تحلیل - لطفاً دوباره تلاش کنید",
                "related_memory": "خطا در سیستم"
            }
    
    def _save_analysis_log(self, user_id: Optional[int], input_text: str, status: str,
                          alert: str, confidence: float, related_memory: str, analysis_data: str) -> int:
        """Save self-awareness analysis to database."""
        try:
            db = SessionLocal()
            
            log_entry = SelfAwarenessLog(
                user_id=user_id,
                input_text=input_text,
                status=status,
                alert=alert,
                confidence=confidence,
                related_memory=related_memory,
                analysis_data=analysis_data
            )
            
            db.add(log_entry)
            db.commit()
            
            log_id = log_entry.id
            db.close()
            
            logger.info(f"[{self.name}] Self-awareness analysis saved with ID: {log_id}")
            return log_id
            
        except Exception as e:
            logger.error(f"[{self.name}] Failed to save analysis: {e}")
            return random.randint(1000, 99999)
    
    def _format_analysis_response(self, analysis: Dict[str, Any]) -> str:
        """Format self-awareness analysis response."""
        try:
            status = analysis["status"]
            confidence = analysis["confidence"]
            alert = analysis["alert"]
            related_memory = analysis.get("related_memory", "")
            
            # Status emoji mapping
            status_emoji = {
                "ok": "🟢",
                "warning": "🟡",
                "alert": "🔴"
            }
            
            # Confidence bar
            confidence_bar = "█" * int(confidence * 5) + "░" * (5 - int(confidence * 5))
            
            response = f"""🧠 **تحلیل خودآگاهی:**

```json
{{
  "status": "{status}",
  "confidence": {confidence:.1f},
  "alert": "{alert}",
  "related_memory": "{related_memory}"
}}
```

**📊 نتایج تحلیل:**
• {status_emoji.get(status, "⚪")} **وضعیت:** {status}
• 📈 **اطمینان:** {confidence_bar} ({confidence:.1%})
• 💭 **حافظه مرتبط:** {related_memory}

**🎯 پیشنهاد:**
{alert}

🧠 **نکته:** این تحلیل بر اساس وضعیت ذهنی، تطابق اهداف، و حافظه انجام شده است."""
            
            return response
            
        except Exception as e:
            logger.error(f"[{self.name}] Error formatting response: {e}")
            return f"خطا در قالب‌بندی پاسخ: {str(e)}"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "تحلیل خودآگاهی",
            "تشخیص وضعیت ذهنی",
            "تحلیل تطابق گفتار با هدف",
            "هشدار خستگی و بی‌انگیزگی",
            "پیشنهاد تنظیم مسیر",
            "ذخیره تاریخچه تحلیل",
            "GPT-4o integration",
            "Pattern-based fallback"
        ]
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent self-awareness analysis logs."""
        try:
            db = SessionLocal()
            logs = db.query(SelfAwarenessLog).order_by(SelfAwarenessLog.created_at.desc()).limit(limit).all()
            
            result = []
            for log in logs:
                result.append({
                    "id": log.id,
                    "input_text": log.input_text,
                    "status": log.status,
                    "alert": log.alert,
                    "confidence": log.confidence,
                    "related_memory": log.related_memory,
                    "created_at": log.created_at.isoformat()
                })
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Error getting recent logs: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for self-awareness analysis."""
        try:
            db = SessionLocal()
            
            total_analyses = db.query(SelfAwarenessLog).count()
            ok_count = db.query(SelfAwarenessLog).filter(SelfAwarenessLog.status == "ok").count()
            warning_count = db.query(SelfAwarenessLog).filter(SelfAwarenessLog.status == "warning").count()
            alert_count = db.query(SelfAwarenessLog).filter(SelfAwarenessLog.status == "alert").count()
            
            db.close()
            
            return {
                "total_analyses": total_analyses,
                "ok_count": ok_count,
                "warning_count": warning_count,
                "alert_count": alert_count,
                "agent_name": self.name,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error getting database stats: {e}")
            return {"error": str(e)}