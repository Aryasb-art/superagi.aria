"""
Summary Agent for text summarization using OpenAI GPT and database storage.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from openai import OpenAI

from .base_agent import BaseAgent
from database import get_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database model for summaries
Base = declarative_base()

class Summary(Base):
    """Database model for storing text summaries."""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SummaryAgent(BaseAgent):
    """
    Summary Agent that processes text summarization requests using OpenAI GPT.
    Stores summaries in PostgreSQL database for retrieval and analysis.
    """
    
    def __init__(self):
        super().__init__(
            name="SummaryAgent",
            description="AI agent for comprehensive text summarization with database storage"
        )
        
        # Initialize OpenAI client
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("[SummaryAgent] OPENAI_API_KEY not found in environment variables")
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            logger.info("[SummaryAgent] Initialized with OpenAI GPT integration")
        
        # Database setup
        self.database_url = os.environ.get("DATABASE_URL")
        if self.database_url:
            self.engine = create_engine(self.database_url)
            self._create_summaries_table()
        else:
            logger.warning("[SummaryAgent] DATABASE_URL not found")
            self.engine = None
    
    def _create_summaries_table(self):
        """Create summaries table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("[SummaryAgent] Summaries table ready")
        except Exception as e:
            logger.error(f"[SummaryAgent] Error creating summaries table: {e}")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process summarization request and generate response.
        
        Args:
            message (str): The message containing text to summarize
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the summary
        """
        try:
            # Log the incoming request
            logger.info(f"[SummaryAgent] Processing summarization request")
            self.log(f"Received summarization request: {message[:100]}...")
            
            # Extract text content from message
            text_to_summarize = self._extract_text_content(message)
            
            if not text_to_summarize or len(text_to_summarize.strip()) < 50:
                return {
                    "agent": self.name,
                    "response": "❌ **خطا:** متن ورودی باید حداقل 50 کاراکتر باشد.\n\nلطفاً متن طولانی‌تری وارد کنید.",
                    "success": False,
                    "timestamp": self._get_current_timestamp()
                }
            
            # Generate summary using OpenAI
            summary_result = self._generate_summary(text_to_summarize)
            
            if not summary_result["success"]:
                return {
                    "agent": self.name,
                    "response": f"❌ **خطا در خلاصه‌سازی:** {summary_result['error']}",
                    "success": False,
                    "timestamp": self._get_current_timestamp()
                }
            
            # Save to database
            summary_id = self._save_to_database(text_to_summarize, summary_result["summary"])
            
            # Format response
            response_content = self._format_summary_response(
                summary_result["summary"], 
                text_to_summarize, 
                summary_id
            )
            
            # Remember this interaction
            self.remember(f"خلاصه‌سازی متن {len(text_to_summarize)} کاراکتری - موفق")
            
            return {
                "agent": self.name,
                "response": response_content,
                "success": True,
                "summary_id": summary_id,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            error_msg = f"Error in summarization: {str(e)}"
            logger.error(f"[SummaryAgent] {error_msg}")
            self.log(f"خطا در خلاصه‌سازی: {error_msg}", "error")
            
            return {
                "agent": self.name,
                "response": f"❌ **خطای سیستم:** {error_msg}",
                "success": False,
                "timestamp": self._get_current_timestamp()
            }
    
    def _extract_text_content(self, message: str) -> str:
        """Extract the main text content from the message."""
        # Remove common prefixes
        prefixes_to_remove = [
            "خلاصه کن:", "خلاصه:", "summarize:", "summary:",
            "خلاصه‌سازی:", "خلاصه کردن:"
        ]
        
        text = message.strip()
        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
                break
        
        return text
    
    def _generate_summary(self, text: str) -> Dict[str, Any]:
        """
        Generate summary using OpenAI GPT.
        
        Args:
            text (str): Text to summarize
            
        Returns:
            Dict: Summary result with success status
        """
        if not self.openai_client:
            return {
                "success": False,
                "error": "OpenAI API key not configured"
            }
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """شما یک متخصص خلاصه‌سازی هستید. وظیفه شما تولید خلاصه‌های دقیق، مفید و ساختاریافته است.

قوانین خلاصه‌سازی:
1. خلاصه باید حداکثر 30% طول متن اصلی باشد
2. نکات کلیدی و مهم را حفظ کنید
3. ساختار منطقی داشته باشد
4. به زبان فارسی پاسخ دهید
5. از bullet points استفاده کنید اگر متن دارای فهرست باشد
6. عنوان‌های مناسب اضافه کنید

فرمت پاسخ:
📝 **خلاصه متن**

**نکات کلیدی:**
• نکته اول
• نکته دوم
• نکته سوم

**نتیجه‌گیری:**
خلاصه‌ای از نتیجه نهایی"""
                    },
                    {
                        "role": "user",
                        "content": f"لطفاً این متن را خلاصه کنید:\n\n{text}"
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"[SummaryAgent] OpenAI API error: {e}")
            return {
                "success": False,
                "error": f"خطای API OpenAI: {str(e)}"
            }
    
    def _save_to_database(self, original_text: str, summary: str) -> Optional[int]:
        """
        Save summary to database.
        
        Args:
            original_text (str): Original text
            summary (str): Generated summary
            
        Returns:
            Optional[int]: Summary ID if successful, None otherwise
        """
        if not self.engine:
            logger.warning("[SummaryAgent] Database not configured")
            return None
        
        try:
            # Create database session
            db = next(get_db())
            
            # Create new summary record
            new_summary = Summary(
                original_text=original_text,
                summary=summary
            )
            
            db.add(new_summary)
            db.commit()
            db.refresh(new_summary)
            
            summary_id = new_summary.id
            logger.info(f"[SummaryAgent] Summary saved to database with ID: {summary_id}")
            
            return summary_id
            
        except Exception as e:
            logger.error(f"[SummaryAgent] Database save error: {e}")
            return None
        finally:
            if 'db' in locals():
                db.close()
    
    def _format_summary_response(self, summary: str, original_text: str, summary_id: Optional[int]) -> str:
        """Format the summary response for display."""
        char_count_original = len(original_text)
        char_count_summary = len(summary)
        compression_ratio = round((1 - char_count_summary / char_count_original) * 100, 1)
        
        response = f"""✅ **خلاصه‌سازی موفق**

{summary}

---

📊 **آمار خلاصه‌سازی:**
• متن اصلی: {char_count_original:,} کاراکتر
• خلاصه: {char_count_summary:,} کاراکتر
• میزان فشرده‌سازی: {compression_ratio}%
• زمان پردازش: {datetime.now().strftime('%H:%M:%S')}"""

        if summary_id:
            response += f"\n• شناسه ذخیره: #{summary_id}"
        
        return response
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "متن‌های طولانی خلاصه‌سازی",
            "ذخیره خلاصه در دیتابیس", 
            "تولید خلاصه ساختاریافته",
            "محاسبه آمار فشرده‌سازی",
            "پشتیبانی از متون فارسی و انگلیسی"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for summaries."""
        if not self.engine:
            return {"error": "Database not configured"}
        
        try:
            db = next(get_db())
            
            # Count total summaries
            total_summaries = db.query(Summary).count()
            
            # Get recent summaries count (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            recent_summaries = db.query(Summary).filter(
                Summary.created_at >= yesterday
            ).count()
            
            return {
                "total_summaries": total_summaries,
                "recent_summaries": recent_summaries,
                "database_status": "connected"
            }
            
        except Exception as e:
            logger.error(f"[SummaryAgent] Database stats error: {e}")
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()