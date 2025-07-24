"""
Aria Memory Agent - Advanced memory management agent with PostgreSQL integration.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime
from database import get_db
from sqlalchemy.orm import Session
from ..base_agent import BaseAgent
from sqlalchemy import text


class AriaMemoryAgent(BaseAgent):
    """
    Advanced memory management agent with PostgreSQL integration.
    Handles long-term memory storage with categorization and tagging.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "agent_config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            agent_config = yaml.safe_load(f)
        
        super().__init__(
            name="AriaMemoryAgent",
            description="مدیر حافظه بلندمدت - Advanced memory management agent with PostgreSQL integration",
            config=config or agent_config
        )
        
        # Initialize database
        self._initialize_database()
        
        # Memory categories
        self.memory_categories = self.config.get("memory_categories", [])
        
        self.log("Memory agent initialized with PostgreSQL integration")
    
    def _initialize_database(self):
        """Initialize database table for long-term memories"""
        try:
            db = next(get_db())
            # Create longterm_memories table if it doesn't exist
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS longterm_memories (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER DEFAULT 1,
                    content TEXT NOT NULL,
                    category VARCHAR(50),
                    tags TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
            self.log("Long-term memories table ready")
        except Exception as e:
            self.log(f"Database initialization error: {e}", "error")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle memory operations based on message content.
        
        Args:
            message (str): The message containing memory request
            context (Dict): Optional context information
            
        Returns:
            Dict: Response with memory operation results
        """
        try:
            # Store in memory
            self.remember(f"User: {message}")
            
            # Parse message for memory operations
            if self._is_save_request(message):
                result = self._save_memory(message, context)
            elif self._is_retrieve_request(message):
                result = self._retrieve_memories(message, context)
            elif self._is_search_request(message):
                result = self._search_memories(message, context)
            else:
                result = self._general_memory_response(message)
            
            response = {
                "response_id": f"{self.agent_id}_{hash(message) % 100000}",
                "content": result,
                "handled_by": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "error": None
            }
            
            self.remember(f"Agent: {result}")
            self.log(f"Processed memory request: {message[:50]}...")
            
            return response
            
        except Exception as e:
            error_response = {
                "response_id": f"error_{hash(str(e)) % 100000}",
                "content": f"خطا در عملیات حافظه: {str(e)}",
                "handled_by": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": str(e)
            }
            
            self.log(f"Error in memory operation: {e}", "error")
            return error_response
    
    def _is_save_request(self, message: str) -> bool:
        """Check if message is a save request"""
        keywords = ["save", "store", "remember", "ذخیره", "یادآوری", "نگهداری"]
        return any(keyword in message.lower() for keyword in keywords)
    
    def _is_retrieve_request(self, message: str) -> bool:
        """Check if message is a retrieve request"""
        keywords = ["retrieve", "get", "fetch", "بازیابی", "دریافت", "یادآوری"]
        return any(keyword in message.lower() for keyword in keywords)
    
    def _is_search_request(self, message: str) -> bool:
        """Check if message is a search request"""
        keywords = ["search", "find", "جستجو", "یافتن", "پیدا"]
        return any(keyword in message.lower() for keyword in keywords)
    
    def _save_memory(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Save memory to database"""
        try:
            # Extract content, category, and tags from message
            content = self._extract_content(message)
            category = self._extract_category(message)
            tags = self._extract_tags(message)
            
            user_id = context.get("user_id", 1) if context else 1
            
            db = next(get_db())
            db.execute(text("""
                INSERT INTO longterm_memories (user_id, content, category, tags, created_at, updated_at)
                VALUES (:user_id, :content, :category, :tags, :created_at, :updated_at)
            """), {
                "user_id": user_id,
                "content": content,
                "category": category,
                "tags": tags,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            db.commit()
            
            self.log(f"Memory saved: {content[:50]}...")
            return f"✅ حافظه ذخیره شد\n📝 محتوا: {content[:100]}{'...' if len(content) > 100 else ''}\n🏷️ دسته: {category}\n🔖 برچسب‌ها: {', '.join(tags) if tags else 'ندارد'}"
            
        except Exception as e:
            self.log(f"Error saving memory: {e}", "error")
            return f"❌ خطا در ذخیره حافظه: {str(e)}"
    
    def _retrieve_memories(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Retrieve memories from database"""
        try:
            user_id = context.get("user_id", 1) if context else 1
            category = self._extract_category(message)
            limit = self._extract_limit(message)
            
            db = next(get_db())
            
            if category:
                result = db.execute(text("""
                    SELECT id, content, category, tags, created_at
                    FROM longterm_memories
                    WHERE user_id = :user_id AND category = :category
                    ORDER BY created_at DESC
                    LIMIT :limit
                """), {"user_id": user_id, "category": category, "limit": limit})
            else:
                result = db.execute(text("""
                    SELECT id, content, category, tags, created_at
                    FROM longterm_memories
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                """), {"user_id": user_id, "limit": limit})
            
            memories = []
            for row in result:
                memories.append({
                    "id": row[0],
                    "content": row[1],
                    "category": row[2],
                    "tags": row[3] or [],
                    "created_at": row[4].isoformat() if row[4] else None
                })
            
            if not memories:
                return "🔍 هیچ حافظه‌ای یافت نشد"
            
            response = f"📚 {len(memories)} حافظه یافت شد:\n\n"
            for i, memory in enumerate(memories, 1):
                response += f"{i}. 📝 {memory['content'][:100]}{'...' if len(memory['content']) > 100 else ''}\n"
                response += f"   🏷️ {memory['category']} | 🔖 {', '.join(memory['tags']) if memory['tags'] else 'ندارد'}\n"
                response += f"   📅 {memory['created_at'][:10] if memory['created_at'] else 'نامشخص'}\n\n"
            
            return response
            
        except Exception as e:
            self.log(f"Error retrieving memories: {e}", "error")
            return f"❌ خطا در بازیابی حافظه: {str(e)}"
    
    def _search_memories(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Search memories in database"""
        try:
            user_id = context.get("user_id", 1) if context else 1
            search_term = self._extract_search_term(message)
            
            if not search_term:
                return "🔍 لطفاً عبارت جستجو را مشخص کنید"
            
            db = next(get_db())
            result = db.execute(text("""
                SELECT id, content, category, tags, created_at
                FROM longterm_memories
                WHERE user_id = :user_id AND (
                    LOWER(content) LIKE LOWER(:search_term) OR
                    LOWER(category) LIKE LOWER(:search_term) OR
                    array_to_string(tags, ' ') LIKE LOWER(:search_term)
                )
                ORDER BY created_at DESC
                LIMIT 10
            """), {"user_id": user_id, "search_term": f"%{search_term}%"})
            
            memories = []
            for row in result:
                memories.append({
                    "id": row[0],
                    "content": row[1],
                    "category": row[2],
                    "tags": row[3] or [],
                    "created_at": row[4].isoformat() if row[4] else None
                })
            
            if not memories:
                return f"🔍 هیچ حافظه‌ای برای '{search_term}' یافت نشد"
            
            response = f"🔍 {len(memories)} حافظه برای '{search_term}' یافت شد:\n\n"
            for i, memory in enumerate(memories, 1):
                response += f"{i}. 📝 {memory['content'][:100]}{'...' if len(memory['content']) > 100 else ''}\n"
                response += f"   🏷️ {memory['category']} | 🔖 {', '.join(memory['tags']) if memory['tags'] else 'ندارد'}\n\n"
            
            return response
            
        except Exception as e:
            self.log(f"Error searching memories: {e}", "error")
            return f"❌ خطا در جستجو: {str(e)}"
    
    def _extract_content(self, message: str) -> str:
        """Extract content from message"""
        # Simple extraction - remove common keywords
        keywords = ["save", "store", "remember", "ذخیره", "یادآوری", "نگهداری"]
        content = message
        for keyword in keywords:
            content = content.replace(keyword, "").strip()
        return content or message
    
    def _extract_category(self, message: str) -> str:
        """Extract category from message"""
        for category in self.memory_categories:
            if category in message:
                return category
        return "عمومی"
    
    def _extract_tags(self, message: str) -> List[str]:
        """Extract tags from message"""
        # Simple tag extraction - look for hashtags or specific patterns
        tags = []
        words = message.split()
        for word in words:
            if word.startswith('#'):
                tags.append(word[1:])
        return tags
    
    def _extract_limit(self, message: str) -> int:
        """Extract limit from message"""
        # Look for numbers in message
        import re
        numbers = re.findall(r'\d+', message)
        return int(numbers[0]) if numbers else 10
    
    def _extract_search_term(self, message: str) -> str:
        """Extract search term from message"""
        keywords = ["search", "find", "جستجو", "یافتن", "پیدا"]
        for keyword in keywords:
            if keyword in message.lower():
                parts = message.lower().split(keyword)
                if len(parts) > 1:
                    return parts[1].strip()
        return message.strip()
    
    def _general_memory_response(self, message: str) -> str:
        """General memory response"""
        return f"🧠 حافظه فعال است. می‌توانید از دستورات زیر استفاده کنید:\n\n" \
               f"• ذخیره <محتوا> - برای ذخیره حافظه جدید\n" \
               f"• بازیابی <دسته> - برای بازیابی حافظه‌ها\n" \
               f"• جستجو <عبارت> - برای جستجو در حافظه‌ها\n\n" \
               f"دسته‌های موجود: {', '.join(self.memory_categories)}"
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            db = next(get_db())
            result = db.execute(text("""
                SELECT 
                    COUNT(*) as total_memories,
                    COUNT(DISTINCT category) as unique_categories,
                    COUNT(DISTINCT user_id) as unique_users
                FROM longterm_memories
            """))
            
            row = result.fetchone()
            if row:
                return {
                    "total_memories": row[0],
                    "unique_categories": row[1],
                    "unique_users": row[2]
                }
            
            return {
                "total_memories": 0,
                "unique_categories": 0,
                "unique_users": 0
            }
        except Exception as e:
            self.log(f"Error getting statistics: {e}", "error")
            return {"error": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "supported_operations": ["save", "retrieve", "search"],
            "memory_categories": self.memory_categories,
            "database_storage": True,
            "tagging_support": True
        }