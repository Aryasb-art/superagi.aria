"""
Long-term Memory Agent for storing, retrieving, and managing user memories.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, func, create_engine, desc
from sqlalchemy.orm import sessionmaker

from .base_agent import BaseAgent
from database import Base, engine, SessionLocal


class LongTermMemory(Base):
    """Database model for storing long-term memories."""
    __tablename__ = "longterm_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # هدف، تجربه، درس، یادآوری، احساس، یادداشت
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LongTermMemoryAgent(BaseAgent):
    """
    Long-term Memory Agent that handles storing, retrieving, and managing user memories.
    Uses PostgreSQL database for persistent storage with categorization and tagging.
    """
    
    def __init__(self):
        super().__init__("LongTermMemoryAgent", "مدیر حافظه بلندمدت")
        self.log("Initialized with PostgreSQL database integration")
        
        # Create table if it doesn't exist
        self._create_memories_table()
        
        # Memory categories in Persian
        self.categories = {
            "هدف": "goal",
            "تجربه": "experience", 
            "درس": "lesson",
            "یادآوری": "reminder",
            "احساس": "feeling",
            "یادداشت": "note",
            "ایده": "idea",
            "برنامه": "plan"
        }
        
        self.log("Long-term memory categories initialized")
    
    def _create_memories_table(self):
        """Create longterm_memories table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            self.log("Long-term memories table ready")
        except Exception as e:
            self.log(f"Error creating memories table: {e}", level="error")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process memory-related requests and generate response.
        
        Args:
            message (str): The message containing memory request
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the memory operation result
        """
        try:
            self.log(f"Processing memory request: {message[:100]}...")
            
            # Remember the user message
            self.remember(message)
            
            # Extract operation type and content
            operation = self._detect_operation(message)
            
            if operation == "save":
                result = self._save_memory(message, context)
                return {"response": result.get("response", "")}
            elif operation == "fetch":
                result = self._fetch_memories(message, context)
                return {"response": result.get("response", "")}
            elif operation == "search":
                result = self._search_memories(message, context)
                return {"response": result.get("response", "")}
            else:
                result = self._generate_help_response()
                return {"response": result.get("response", "")}
                
        except Exception as e:
            self.log(f"Error processing memory request: {e}", level="error")
            return {
                "response": f"❌ **خطا در مدیریت حافظه:** {str(e)}"
            }
    
    def _detect_operation(self, message: str) -> str:
        """Detect the type of memory operation requested."""
        message_lower = message.lower()
        
        save_keywords = ["ذخیره", "save", "یادداشت", "بنویس", "ثبت", "یاد بگیر"]
        fetch_keywords = ["نشان بده", "fetch", "واکشی", "دریافت", "لیست", "آخرین"]
        search_keywords = ["جستجو", "search", "پیدا کن", "بگرد"]
        
        if any(keyword in message_lower for keyword in save_keywords):
            return "save"
        elif any(keyword in message_lower for keyword in fetch_keywords):
            return "fetch"
        elif any(keyword in message_lower for keyword in search_keywords):
            return "search"
        else:
            return "help"
    
    def _save_memory(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Save a new memory to the database."""
        try:
            # Extract content and category from message
            content = self._extract_memory_content(message)
            category = self._extract_category(message)
            tags = self._extract_tags(message)
            user_id = context.get("user_id") if context else None
            
            if not content:
                return {
                    "response": "❌ **محتوای حافظه یافت نشد.** لطفاً متن حافظه را مشخص کنید.",
                    "success": False,
                    "timestamp": self._get_current_timestamp()
                }
            
            # Save to database
            memory_id = self._save_to_database(content, category, tags, user_id)
            
            if memory_id:
                response = self._format_save_response(memory_id, content, category, tags)
                return {
                    "response": response,
                    "success": True,
                    "memory_id": memory_id,
                    "timestamp": self._get_current_timestamp()
                }
            else:
                return {
                    "response": "❌ **خطا در ذخیره حافظه** در دیتابیس.",
                    "success": False,
                    "timestamp": self._get_current_timestamp()
                }
                
        except Exception as e:
            self.log(f"Error saving memory: {e}", level="error")
            return {
                "response": f"❌ **خطا در ذخیره حافظه:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _fetch_memories(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch recent memories from the database."""
        try:
            user_id = context.get("user_id") if context else None
            limit = self._extract_limit(message)
            category = self._extract_category(message)
            
            memories = self._fetch_from_database(user_id, limit, category)
            
            if memories:
                response = self._format_fetch_response(memories)
                return {
                    "response": response,
                    "success": True,
                    "memories": memories,
                    "count": len(memories),
                    "timestamp": self._get_current_timestamp()
                }
            else:
                return {
                    "response": "📝 **هیچ حافظه‌ای یافت نشد.** شاید هنوز چیزی ذخیره نکرده‌اید.",
                    "success": True,
                    "memories": [],
                    "count": 0,
                    "timestamp": self._get_current_timestamp()
                }
                
        except Exception as e:
            self.log(f"Error fetching memories: {e}", level="error")
            return {
                "response": f"❌ **خطا در دریافت حافظه‌ها:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _search_memories(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search memories based on keywords."""
        try:
            search_term = self._extract_search_term(message)
            user_id = context.get("user_id") if context else None
            
            if not search_term:
                return {
                    "response": "❌ **کلمه جستجو یافت نشد.** لطفاً کلمه‌ای برای جستجو وارد کنید.",
                    "success": False,
                    "timestamp": self._get_current_timestamp()
                }
            
            memories = self._search_in_database(search_term, user_id)
            
            if memories:
                response = self._format_search_response(memories, search_term)
                return {
                    "response": response,
                    "success": True,
                    "memories": memories,
                    "search_term": search_term,
                    "count": len(memories),
                    "timestamp": self._get_current_timestamp()
                }
            else:
                return {
                    "response": f"🔍 **نتیجه‌ای برای '{search_term}' یافت نشد.**",
                    "success": True,
                    "memories": [],
                    "search_term": search_term,
                    "count": 0,
                    "timestamp": self._get_current_timestamp()
                }
                
        except Exception as e:
            self.log(f"Error searching memories: {e}", level="error")
            return {
                "response": f"❌ **خطا در جستجو:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _extract_memory_content(self, message: str) -> str:
        """Extract the main memory content from the message."""
        # Remove common prefixes
        content = message
        prefixes = ["ذخیره کن:", "save:", "یادداشت:", "ثبت کن:", "یاد بگیر:"]
        
        for prefix in prefixes:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
                break
        
        return content
    
    def _extract_category(self, message: str) -> str:
        """Extract category from message or default to 'یادداشت'."""
        message_lower = message.lower()
        
        for persian_cat, english_cat in self.categories.items():
            if persian_cat in message_lower or english_cat in message_lower:
                return persian_cat
        
        return "یادداشت"  # Default category
    
    def _extract_tags(self, message: str) -> str:
        """Extract tags from message (looking for #tag format)."""
        import re
        tags = re.findall(r'#(\w+)', message)
        return ", ".join(tags) if tags else ""
    
    def _extract_limit(self, message: str) -> int:
        """Extract limit number from message."""
        import re
        numbers = re.findall(r'\d+', message)
        return int(numbers[0]) if numbers else 10
    
    def _extract_search_term(self, message: str) -> str:
        """Extract search term from message."""
        # Remove search prefixes
        content = message
        prefixes = ["جستجو:", "search:", "پیدا کن:", "بگرد:"]
        
        for prefix in prefixes:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
                break
        
        return content
    
    def _save_to_database(self, content: str, category: str, tags: str, user_id: Optional[int] = None) -> Optional[int]:
        """Save memory to database."""
        try:
            db = SessionLocal()
            memory = LongTermMemory(
                user_id=user_id,
                content=content,
                category=category,
                tags=tags
            )
            db.add(memory)
            db.commit()
            db.refresh(memory)
            memory_id = memory.id
            db.close()
            
            self.log(f"Memory saved with ID: {memory_id}")
            return memory_id
            
        except Exception as e:
            self.log(f"Database save error: {e}", level="error")
            return None
    
    def _fetch_from_database(self, user_id: Optional[int] = None, limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        """Fetch memories from database."""
        try:
            db = SessionLocal()
            query = db.query(LongTermMemory)
            
            if user_id:
                query = query.filter(LongTermMemory.user_id == user_id)
            
            if category and category != "همه":
                query = query.filter(LongTermMemory.category == category)
            
            memories = query.order_by(desc(LongTermMemory.created_at)).limit(limit).all()
            
            result = []
            for memory in memories:
                result.append({
                    "id": memory.id,
                    "content": memory.content,
                    "category": memory.category,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None,
                    "updated_at": memory.updated_at.isoformat() if memory.updated_at else None
                })
            
            db.close()
            return result
            
        except Exception as e:
            self.log(f"Database fetch error: {e}", level="error")
            return []
    
    def _search_in_database(self, search_term: str, user_id: Optional[int] = None) -> List[Dict]:
        """Search memories in database."""
        try:
            db = SessionLocal()
            query = db.query(LongTermMemory)
            
            if user_id:
                query = query.filter(LongTermMemory.user_id == user_id)
            
            # Search in content, category, and tags
            search_filter = (
                LongTermMemory.content.ilike(f"%{search_term}%") |
                LongTermMemory.category.ilike(f"%{search_term}%") |
                LongTermMemory.tags.ilike(f"%{search_term}%")
            )
            
            memories = query.filter(search_filter).order_by(desc(LongTermMemory.created_at)).limit(20).all()
            
            result = []
            for memory in memories:
                result.append({
                    "id": memory.id,
                    "content": memory.content,
                    "category": memory.category,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None,
                    "updated_at": memory.updated_at.isoformat() if memory.updated_at else None
                })
            
            db.close()
            return result
            
        except Exception as e:
            self.log(f"Database search error: {e}", level="error")
            return []
    
    def _format_save_response(self, memory_id: int, content: str, category: str, tags: str) -> str:
        """Format the save response."""
        response = f"✅ **حافظه ذخیره شد!**\n\n"
        response += f"📝 **محتوا:** {content[:100]}{'...' if len(content) > 100 else ''}\n"
        response += f"📁 **دسته:** {category}\n"
        
        if tags:
            response += f"🏷️ **تگ‌ها:** {tags}\n"
        
        response += f"🆔 **شناسه:** #{memory_id}\n"
        response += f"⏰ **زمان ذخیره:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return response
    
    def _format_fetch_response(self, memories: List[Dict]) -> str:
        """Format the fetch response."""
        response = f"📚 **آخرین حافظه‌های ذخیره شده** ({len(memories)} مورد):\n\n"
        
        for i, memory in enumerate(memories[:5], 1):
            response += f"**{i}.** `{memory['category']}` - "
            response += f"{memory['content'][:80]}{'...' if len(memory['content']) > 80 else ''}\n"
            response += f"   🕒 {memory['created_at'][:19].replace('T', ' ')}"
            
            if memory['tags']:
                response += f" | 🏷️ {memory['tags']}"
            
            response += f" | 🆔 #{memory['id']}\n\n"
        
        if len(memories) > 5:
            response += f"... و {len(memories) - 5} مورد دیگر\n\n"
        
        response += "💡 **نکته:** برای جستجو از دستور 'جستجو: کلمه' استفاده کنید."
        
        return response
    
    def _format_search_response(self, memories: List[Dict], search_term: str) -> str:
        """Format the search response."""
        response = f"🔍 **نتایج جستجو برای '{search_term}'** ({len(memories)} مورد):\n\n"
        
        for i, memory in enumerate(memories[:5], 1):
            response += f"**{i}.** `{memory['category']}` - "
            response += f"{memory['content'][:80]}{'...' if len(memory['content']) > 80 else ''}\n"
            response += f"   🕒 {memory['created_at'][:19].replace('T', ' ')}"
            
            if memory['tags']:
                response += f" | 🏷️ {memory['tags']}"
            
            response += f" | 🆔 #{memory['id']}\n\n"
        
        if len(memories) > 5:
            response += f"... و {len(memories) - 5} نتیجه دیگر"
        
        return response
    
    def _generate_help_response(self) -> Dict[str, Any]:
        """Generate help response for memory operations."""
        response = """🧠 **راهنمای حافظه بلندمدت**

**دستورات موجود:**
• `ذخیره کن: متن حافظه` - ذخیره حافظه جدید
• `نشان بده آخرین حافظه‌ها` - نمایش آخرین موارد
• `جستجو: کلمه` - جستجو در حافظه‌ها

**دسته‌بندی‌ها:**
• هدف، تجربه، درس، یادآوری، احساس، یادداشت، ایده، برنامه

**مثال:**
`ذخیره کن: باید فردا جلسه مهم داشته باشم #کار #مهم`

**نکات:**
• از # برای تگ‌گذاری استفاده کنید
• حافظه‌ها به صورت خودکار دسته‌بندی می‌شوند
• جستجو در تمام محتوا، دسته‌ها و تگ‌ها انجام می‌شود"""
        
        return {
            "response": response,
            "success": True,
            "timestamp": self._get_current_timestamp()
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "ذخیره حافظه بلندمدت",
            "دریافت آخرین حافظه‌ها", 
            "جستجو در حافظه‌ها",
            "دسته‌بندی حافظه‌ها",
            "تگ‌گذاری حافظه‌ها",
            "مدیریت حافظه کاربران"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for memories."""
        try:
            db = SessionLocal()
            
            total_memories = db.query(LongTermMemory).count()
            categories = db.query(LongTermMemory.category).distinct().all()
            recent_memories = db.query(LongTermMemory).order_by(desc(LongTermMemory.created_at)).limit(5).all()
            
            db.close()
            
            return {
                "total_memories": total_memories,
                "categories": [cat[0] for cat in categories],
                "recent_count": len(recent_memories),
                "table_name": "longterm_memories"
            }
            
        except Exception as e:
            self.log(f"Error getting database stats: {e}", level="error")
            return {
                "total_memories": 0,
                "categories": [],
                "recent_count": 0,
                "error": str(e)
            }