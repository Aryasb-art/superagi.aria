"""
Aria Summary Agent - Specialized text summarization agent with database storage.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
from database import get_db
from sqlalchemy.orm import Session
from ..base_agent import BaseAgent
from sqlalchemy import text


class AriaSummaryAgent(BaseAgent):
    """
    Specialized agent for text summarization with database storage.
    Uses OpenAI GPT-4o for high-quality summarization.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "agent_config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            agent_config = yaml.safe_load(f)
        
        super().__init__(
            name="AriaSummaryAgent",
            description="AI agent for comprehensive text summarization with database storage",
            config=config or agent_config
        )
        
        # Initialize OpenAI client
        self.openai_client = None
        self.openai_available = False
        
        try:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = OpenAI(api_key=openai_api_key)
                self.openai_available = True
                self.log("OpenAI GPT integration ready for summarization")
            else:
                self.log("OpenAI API key not found, using fallback responses", "warning")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}", "error")
            self.openai_available = False
        
        # Initialize database
        self._initialize_database()
        
        # Configuration
        self.min_text_length = self.config.get("processing", {}).get("min_text_length", 50)
        self.max_text_length = self.config.get("processing", {}).get("max_text_length", 10000)
    
    def _initialize_database(self):
        """Initialize database table for summaries"""
        try:
            db = next(get_db())
            # Create summaries table if it doesn't exist
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS summaries (
                    id SERIAL PRIMARY KEY,
                    original_text TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
            self.log("Summaries table ready")
        except Exception as e:
            self.log(f"Database initialization error: {e}", "error")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a summary response and store in database.
        
        Args:
            message (str): The text to summarize
            context (Dict): Optional context information
            
        Returns:
            Dict: Response with summary and storage information
        """
        try:
            # Store in memory
            self.remember(f"User: {message}")
            
            # Validate input
            if len(message.strip()) < self.min_text_length:
                return {
                    "response_id": f"summary_error_{hash(message) % 100000}",
                    "content": f"متن برای خلاصه‌سازی کوتاه است. حداقل {self.min_text_length} کاراکتر لازم است.",
                    "handled_by": self.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": False,
                    "error": "Text too short"
                }
            
            if len(message) > self.max_text_length:
                return {
                    "response_id": f"summary_error_{hash(message) % 100000}",
                    "content": f"متن برای خلاصه‌سازی طولانی است. حداکثر {self.max_text_length} کاراکتر مجاز است.",
                    "handled_by": self.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": False,
                    "error": "Text too long"
                }
            
            # Generate summary
            summary = self._generate_summary(message)
            
            # Store in database
            storage_result = self._store_summary(message, summary)
            
            # Calculate compression ratio
            compression_ratio = len(summary) / len(message) if len(message) > 0 else 0
            
            response = {
                "response_id": f"{self.agent_id}_{hash(message) % 100000}",
                "content": summary,
                "original_length": len(message),
                "summary_length": len(summary),
                "compression_ratio": f"{compression_ratio:.2f}",
                "stored_in_database": storage_result,
                "handled_by": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "openai_used": self.openai_available,
                "error": None
            }
            
            self.remember(f"Agent: {summary}")
            self.log(f"Generated summary with {compression_ratio:.2f} compression ratio")
            
            return response
            
        except Exception as e:
            error_response = {
                "response_id": f"error_{hash(str(e)) % 100000}",
                "content": f"خطا در خلاصه‌سازی: {str(e)}",
                "handled_by": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "openai_used": False,
                "error": str(e)
            }
            
            self.log(f"Error in summarization: {e}", "error")
            return error_response
    
    def _generate_summary(self, text: str) -> str:
        """Generate summary using OpenAI GPT"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a skilled summarizer. Provide a concise, accurate summary that captures the key points and main ideas. Respond in Persian."
                        },
                        {
                            "role": "user",
                            "content": f"لطفاً این متن را خلاصه کنید:\n\n{text}"
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 1000),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI summarization error: {e}", "error")
                return f"خطا در خلاصه‌سازی با OpenAI: {str(e)}"
        else:
            # Fallback: Simple extraction of first few sentences
            sentences = text.split('.')[:3]
            return f"خلاصه (روش پایه): {'. '.join(sentences)}..."
    
    def _store_summary(self, original_text: str, summary: str) -> bool:
        """Store summary in database"""
        try:
            db = next(get_db())
            db.execute(text("""
                INSERT INTO summaries (original_text, summary, created_at)
                VALUES (:original_text, :summary, :created_at)
            """), {
                "original_text": original_text,
                "summary": summary,
                "created_at": datetime.utcnow()
            })
            db.commit()
            self.log("Summary stored in database")
            return True
        except Exception as e:
            self.log(f"Database storage error: {e}", "error")
            return False
    
    def get_recent_summaries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent summaries from database"""
        try:
            db = next(get_db())
            result = db.execute(text("""
                SELECT id, original_text, summary, created_at
                FROM summaries
                ORDER BY created_at DESC
                LIMIT :limit
            """), {"limit": limit})
            
            summaries = []
            for row in result:
                summaries.append({
                    "id": row[0],
                    "original_text": row[1][:100] + "..." if len(row[1]) > 100 else row[1],
                    "summary": row[2],
                    "created_at": row[3].isoformat() if row[3] else None
                })
            
            return summaries
        except Exception as e:
            self.log(f"Error retrieving summaries: {e}", "error")
            return []
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics"""
        try:
            db = next(get_db())
            result = db.execute(text("""
                SELECT 
                    COUNT(*) as total_summaries,
                    AVG(LENGTH(summary)) as avg_summary_length,
                    AVG(LENGTH(original_text)) as avg_original_length
                FROM summaries
            """))
            
            row = result.fetchone()
            if row:
                return {
                    "total_summaries": row[0],
                    "avg_summary_length": round(row[1] or 0, 2),
                    "avg_original_length": round(row[2] or 0, 2),
                    "avg_compression_ratio": round((row[1] or 0) / (row[2] or 1), 2)
                }
            
            return {
                "total_summaries": 0,
                "avg_summary_length": 0,
                "avg_original_length": 0,
                "avg_compression_ratio": 0
            }
        except Exception as e:
            self.log(f"Error getting statistics: {e}", "error")
            return {"error": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "supported_tasks": ["text_summarization"],
            "database_storage": True,
            "openai_available": self.openai_available,
            "min_text_length": self.min_text_length,
            "max_text_length": self.max_text_length,
            "model": self.config.get("openai", {}).get("model", "gpt-4o")
        }