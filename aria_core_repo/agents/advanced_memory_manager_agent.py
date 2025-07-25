"""
Advanced Memory Manager Agent for centralized memory management across all agents.
Handles classification, storage, access control, and summarization of memory data.
Supports memory types: short-term, long-term, mission-specific, and reflective memory.
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import deque
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from openai import OpenAI

# Import base agent
from .base_agent import BaseAgent

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///memory_manager.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# OpenAI setup
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class MemoryEntry(Base):
    """Database model for memory entries."""
    __tablename__ = "memory_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    agent_name = Column(String(100), nullable=False)
    memory_type = Column(String(50), nullable=False)  # short_term, long_term, mission_specific, reflective
    mission_id = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, nullable=True)
    importance_score = Column(Integer, default=1)  # 1-10 scale
    access_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

class MemorySummary(Base):
    """Database model for memory summaries."""
    __tablename__ = "memory_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_type = Column(String(50), nullable=False)
    agent_name = Column(String(100), nullable=True)
    summary_text = Column(Text, nullable=False)
    entry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AdvancedMemoryManagerAgent(BaseAgent):
    """
    Advanced Memory Manager Agent for centralized memory management.
    
    Features:
    - Memory type classification (short-term, long-term, mission-specific, reflective)
    - Intelligent storage with importance scoring
    - Access control and tracking
    - Automatic summarization using OpenAI GPT
    - Memory purging with retention policies
    - Cross-agent memory sharing
    """
    
    def __init__(self):
        super().__init__('AdvancedMemoryManagerAgent')
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        Base.metadata.create_all(bind=engine)
        
        # Memory type configurations
        self.memory_types = {
            "short_term": {
                "retention_days": 7,
                "max_entries": 1000,
                "importance_threshold": 3
            },
            "long_term": {
                "retention_days": 365,
                "max_entries": 10000,
                "importance_threshold": 5
            },
            "mission_specific": {
                "retention_days": 30,
                "max_entries": 5000,
                "importance_threshold": 4
            },
            "reflective": {
                "retention_days": 90,
                "max_entries": 2000,
                "importance_threshold": 6
            }
        }
        
        # Classification keywords for memory types
        self.classification_keywords = {
            "short_term": [
                "فعلا", "الان", "امروز", "فوری", "سریع", "currently", "now", "today", "urgent", "quick",
                "temporary", "موقت", "زودگذر", "immediate", "instant"
            ],
            "long_term": [
                "همیشه", "مدام", "دائمی", "مهم", "یادگیری", "always", "permanent", "important", "learning",
                "remember", "knowledge", "skill", "habit", "routine", "دانش", "عادت", "مهارت"
            ],
            "mission_specific": [
                "پروژه", "کار", "وظیفه", "هدف", "برنامه", "project", "task", "mission", "goal", "plan",
                "assignment", "objective", "target", "deadline", "مأموریت", "تکلیف"
            ],
            "reflective": [
                "فکر", "تأمل", "بررسی", "تجربه", "درس", "think", "reflect", "review", "experience", "lesson",
                "insight", "wisdom", "understanding", "بینش", "حکمت", "درک", "تحلیل"
            ]
        }
        
        self.logger.info(f"[{self.name}] Initialized with PostgreSQL database integration for advanced memory management")
        self.logger.info(f"[{self.name}] Memory types configured: {list(self.memory_types.keys())}")

    def get_db(self) -> Session:
        """Get database session."""
        return SessionLocal()

    def classify_memory_type(self, content: str, meta_data: Dict = None) -> str:
        """
        Classify memory type based on content and meta_data.
        
        Args:
            content: The memory content text
            meta_data: Optional meta_data dictionary
            
        Returns:
            Memory type: short_term, long_term, mission_specific, or reflective
        """
        content_lower = content.lower()
        
        # Check for explicit mission context
        if meta_data and meta_data.get("mission_id"):
            return "mission_specific"
        
        # Score each memory type based on keyword matches
        type_scores = {}
        for mem_type, keywords in self.classification_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            type_scores[mem_type] = score
        
        # Use GPT for intelligent classification if no clear keyword match
        if max(type_scores.values()) == 0:
            try:
                gpt_classification = self._classify_with_gpt(content)
                if gpt_classification in self.memory_types:
                    return gpt_classification
            except Exception as e:
                self.logger.warning(f"[{self.name}] GPT classification failed: {e}")
        
        # Return type with highest score, default to short_term
        return max(type_scores, key=type_scores.get) if max(type_scores.values()) > 0 else "short_term"

    def _classify_with_gpt(self, content: str) -> str:
        """Use OpenAI GPT to classify memory type."""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a memory classification expert. Classify the following text into one of these memory types:
                        - short_term: Temporary, immediate information
                        - long_term: Important, permanent knowledge
                        - mission_specific: Task or project-related information
                        - reflective: Insights, experiences, lessons learned
                        
                        Respond with only the memory type name."""
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            classification = response.choices[0].message.content.strip().lower()
            return classification if classification in self.memory_types else "short_term"
            
        except Exception as e:
            self.logger.error(f"[{self.name}] GPT classification error: {e}")
            return "short_term"

    def calculate_importance_score(self, content: str, memory_type: str, meta_data: Dict = None) -> int:
        """
        Calculate importance score for memory entry (1-10 scale).
        
        Args:
            content: Memory content
            memory_type: Type of memory
            meta_data: Optional meta_data
            
        Returns:
            Importance score between 1-10
        """
        base_score = 3  # Default importance
        
        # Adjust based on memory type
        type_adjustments = {
            "short_term": 0,
            "long_term": 3,
            "mission_specific": 2,
            "reflective": 4
        }
        
        score = base_score + type_adjustments.get(memory_type, 0)
        
        # Boost for certain keywords
        importance_keywords = [
            "مهم", "ضروری", "اساسی", "کلیدی", "بحرانی",
            "important", "crucial", "essential", "key", "critical",
            "urgent", "priority", "significant"
        ]
        
        content_lower = content.lower()
        keyword_boost = sum(1 for keyword in importance_keywords if keyword in content_lower)
        score += min(keyword_boost, 3)  # Max 3 points from keywords
        
        # Adjust based on length (longer content might be more important)
        if len(content) > 500:
            score += 1
        elif len(content) > 200:
            score += 0.5
        
        # Metadata adjustments
        if meta_data:
            if meta_data.get("priority") == "high":
                score += 2
            elif meta_data.get("priority") == "medium":
                score += 1
            
            if meta_data.get("source") == "user_explicit":
                score += 1
        
        return max(1, min(10, int(score)))

    def analyze_and_store(self, memory_entry: Dict, user_id: Optional[int] = None) -> Dict:
        """
        Analyze and store memory entry with classification and importance scoring.
        
        Args:
            memory_entry: Dictionary containing memory data
            user_id: Optional user identifier
            
        Returns:
            Dictionary with storage status and metadata
        """
        try:
            content = memory_entry.get("content", "")
            agent_name = memory_entry.get("agent_name", "unknown")
            meta_data = memory_entry.get("metadata", {})
            
            # Classify memory type
            memory_type = self.classify_memory_type(content, meta_data)
            
            # Calculate importance score
            importance_score = self.calculate_importance_score(content, memory_type, meta_data)
            
            # Check if importance meets threshold
            threshold = self.memory_types[memory_type]["importance_threshold"]
            if importance_score < threshold:
                return {
                    "status": "rejected",
                    "reason": f"Importance score {importance_score} below threshold {threshold}",
                    "type": memory_type,
                    "importance_score": importance_score
                }
            
            # Calculate expiration date
            retention_days = self.memory_types[memory_type]["retention_days"]
            expires_at = datetime.utcnow() + timedelta(days=retention_days)
            
            # Store in database
            db = self.get_db()
            try:
                entry = MemoryEntry(
                    user_id=user_id,
                    agent_name=agent_name,
                    memory_type=memory_type,
                    mission_id=memory_entry.get("mission_id"),
                    content=content,
                    meta_data=meta_data,
                    importance_score=importance_score,
                    expires_at=expires_at
                )
                
                db.add(entry)
                db.commit()
                
                # Check if we need to purge old entries
                self._enforce_retention_policy(db, memory_type)
                
                self.logger.info(f"[{self.name}] Stored memory entry: type={memory_type}, importance={importance_score}")
                
                return {
                    "status": "stored",
                    "type": memory_type,
                    "importance_score": importance_score,
                    "entry_id": entry.id,
                    "expires_at": expires_at.isoformat()
                }
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Error storing memory: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def retrieve(self, memory_type: str, user_id: Optional[int] = None, mission_id: Optional[str] = None, 
                limit: int = 100, min_importance: int = 1) -> List[Dict]:
        """
        Retrieve memory entries based on criteria.
        
        Args:
            memory_type: Type of memory to retrieve
            user_id: Optional user filter
            mission_id: Optional mission filter
            limit: Maximum number of entries to return
            min_importance: Minimum importance score
            
        Returns:
            List of memory entries
        """
        try:
            db = self.get_db()
            try:
                query = db.query(MemoryEntry).filter(
                    MemoryEntry.memory_type == memory_type,
                    MemoryEntry.is_active == True,
                    MemoryEntry.importance_score >= min_importance
                )
                
                if user_id:
                    query = query.filter(MemoryEntry.user_id == user_id)
                
                if mission_id:
                    query = query.filter(MemoryEntry.mission_id == mission_id)
                
                # Order by importance and recency
                entries = query.order_by(
                    MemoryEntry.importance_score.desc(),
                    MemoryEntry.created_at.desc()
                ).limit(limit).all()
                
                # Update access count
                for entry in entries:
                    entry.access_count += 1
                db.commit()
                
                # Convert to dictionaries
                result = []
                for entry in entries:
                    result.append({
                        "id": entry.id,
                        "agent_name": entry.agent_name,
                        "content": entry.content,
                        "metadata": entry.meta_data,
                        "importance_score": entry.importance_score,
                        "access_count": entry.access_count,
                        "created_at": entry.created_at.isoformat(),
                        "mission_id": entry.mission_id
                    })
                
                self.logger.info(f"[{self.name}] Retrieved {len(result)} {memory_type} entries")
                return result
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Error retrieving memories: {e}")
            return []

    def summarize(self, memory_type: str, user_id: Optional[int] = None, force_refresh: bool = False) -> Dict:
        """
        Generate or retrieve summary of memory type.
        
        Args:
            memory_type: Type of memory to summarize
            user_id: Optional user filter
            force_refresh: Force regeneration of summary
            
        Returns:
            Dictionary with summary information
        """
        try:
            db = self.get_db()
            try:
                # Check for existing recent summary
                if not force_refresh:
                    recent_summary = db.query(MemorySummary).filter(
                        MemorySummary.memory_type == memory_type,
                        MemorySummary.created_at > datetime.utcnow() - timedelta(hours=1)
                    ).first()
                    
                    if recent_summary:
                        return {
                            "summary": recent_summary.summary_text,
                            "entry_count": recent_summary.entry_count,
                            "created_at": recent_summary.created_at.isoformat(),
                            "cached": True
                        }
                
                # Retrieve memories for summarization
                memories = self.retrieve(memory_type, user_id, limit=500, min_importance=3)
                
                if not memories:
                    return {
                        "summary": f"هیچ {memory_type} حافظه‌ای برای خلاصه‌سازی یافت نشد",
                        "entry_count": 0,
                        "created_at": datetime.utcnow().isoformat(),
                        "cached": False
                    }
                
                # Generate summary using GPT
                summary_text = self._generate_summary_with_gpt(memories, memory_type)
                
                # Store summary
                summary_entry = MemorySummary(
                    memory_type=memory_type,
                    summary_text=summary_text,
                    entry_count=len(memories)
                )
                
                db.add(summary_entry)
                db.commit()
                
                self.logger.info(f"[{self.name}] Generated summary for {memory_type}: {len(memories)} entries")
                
                return {
                    "summary": summary_text,
                    "entry_count": len(memories),
                    "created_at": datetime.utcnow().isoformat(),
                    "cached": False
                }
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Error generating summary: {e}")
            return {
                "summary": f"خطا در تولید خلاصه: {str(e)}",
                "entry_count": 0,
                "created_at": datetime.utcnow().isoformat(),
                "cached": False
            }

    def _generate_summary_with_gpt(self, memories: List[Dict], memory_type: str) -> str:
        """Generate summary using OpenAI GPT."""
        try:
            # Prepare content for summarization
            content_items = []
            for memory in memories[:50]:  # Limit to avoid token limits
                content_items.append(f"- {memory['content']}")
            
            content_text = "\n".join(content_items)
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a memory summarization expert. Create a comprehensive summary of the following {memory_type} memories in Persian. 
                        
                        Focus on:
                        - Key themes and patterns
                        - Most important information
                        - Actionable insights
                        - Emotional or contextual significance
                        
                        Format your response as a structured summary with clear sections."""
                    },
                    {
                        "role": "user",
                        "content": f"خلاصه کن این {memory_type} حافظه‌ها:\n\n{content_text}"
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"[{self.name}] GPT summarization error: {e}")
            return f"خطا در خلاصه‌سازی با GPT: {str(e)}"

    def purge(self, memory_type: str, older_than: Optional[datetime] = None, 
              min_importance: int = 1, dry_run: bool = False) -> Dict:
        """
        Purge memory entries based on criteria.
        
        Args:
            memory_type: Type of memory to purge
            older_than: Optional datetime threshold
            min_importance: Minimum importance to keep
            dry_run: If True, only count entries without deleting
            
        Returns:
            Dictionary with purge results
        """
        try:
            db = self.get_db()
            try:
                query = db.query(MemoryEntry).filter(
                    MemoryEntry.memory_type == memory_type,
                    MemoryEntry.is_active == True
                )
                
                if older_than:
                    query = query.filter(MemoryEntry.created_at < older_than)
                else:
                    # Default to expired entries
                    query = query.filter(MemoryEntry.expires_at < datetime.utcnow())
                
                # Keep high importance entries
                query = query.filter(MemoryEntry.importance_score < min_importance)
                
                entries = query.all()
                count = len(entries)
                
                if not dry_run:
                    for entry in entries:
                        entry.is_active = False
                    db.commit()
                    self.logger.info(f"[{self.name}] Purged {count} {memory_type} entries")
                
                return {
                    "status": "success",
                    "purged_count": count,
                    "memory_type": memory_type,
                    "dry_run": dry_run,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Error purging memories: {e}")
            return {
                "status": "error",
                "error": str(e),
                "purged_count": 0
            }

    def _enforce_retention_policy(self, db: Session, memory_type: str):
        """Enforce retention policy for memory type."""
        try:
            config = self.memory_types[memory_type]
            max_entries = config["max_entries"]
            
            # Count current entries
            count = db.query(MemoryEntry).filter(
                MemoryEntry.memory_type == memory_type,
                MemoryEntry.is_active == True
            ).count()
            
            if count > max_entries:
                # Remove oldest, least important entries
                excess = count - max_entries
                old_entries = db.query(MemoryEntry).filter(
                    MemoryEntry.memory_type == memory_type,
                    MemoryEntry.is_active == True
                ).order_by(
                    MemoryEntry.importance_score.asc(),
                    MemoryEntry.created_at.asc()
                ).limit(excess).all()
                
                for entry in old_entries:
                    entry.is_active = False
                
                db.commit()
                self.logger.info(f"[{self.name}] Enforced retention policy: removed {excess} old {memory_type} entries")
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Error enforcing retention policy: {e}")

    def get_memory_statistics(self) -> Dict:
        """Get comprehensive memory statistics."""
        try:
            db = self.get_db()
            try:
                stats = {}
                
                for memory_type in self.memory_types.keys():
                    count = db.query(MemoryEntry).filter(
                        MemoryEntry.memory_type == memory_type,
                        MemoryEntry.is_active == True
                    ).count()
                    
                    avg_importance = db.query(func.avg(MemoryEntry.importance_score)).filter(
                        MemoryEntry.memory_type == memory_type,
                        MemoryEntry.is_active == True
                    ).scalar() or 0
                    
                    stats[memory_type] = {
                        "count": count,
                        "avg_importance": round(float(avg_importance), 2),
                        "max_allowed": self.memory_types[memory_type]["max_entries"],
                        "retention_days": self.memory_types[memory_type]["retention_days"]
                    }
                
                return {
                    "status": "success",
                    "statistics": stats,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Error getting statistics: {e}")
            return {"status": "error", "error": str(e)}

    def respond(self, message: str, context: Dict = None) -> Dict:
        """
        Handle memory management commands and queries.
        
        Args:
            message: Input message
            context: Optional context dictionary
            
        Returns:
            Response dictionary
        """
        try:
            message_lower = message.lower()
            
            # Memory storage commands
            if any(word in message_lower for word in ["ذخیره", "نگهداری", "store", "save"]):
                memory_entry = {
                    "content": message,
                    "agent_name": context.get("agent_name", "user") if context else "user",
                    "metadata": context or {}
                }
                result = self.analyze_and_store(memory_entry)
                return {
                    "response": f"حافظه ذخیره شد: نوع={result.get('type')}, اهمیت={result.get('importance_score')}",
                    "success": result.get("status") == "stored",
                    "timestamp": datetime.now().isoformat(),
                    "data": result
                }
            
            # Memory retrieval commands
            elif any(word in message_lower for word in ["بازیابی", "جستجو", "retrieve", "search"]):
                memory_type = "short_term"  # Default
                for mtype in self.memory_types.keys():
                    if mtype in message_lower:
                        memory_type = mtype
                        break
                
                memories = self.retrieve(memory_type, limit=10)
                return {
                    "response": f"بازیابی شد {len(memories)} حافظه از نوع {memory_type}",
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "data": {"memories": memories, "type": memory_type}
                }
            
            # Memory summary commands
            elif any(word in message_lower for word in ["خلاصه", "summary", "summarize"]):
                memory_type = "short_term"  # Default
                for mtype in self.memory_types.keys():
                    if mtype in message_lower:
                        memory_type = mtype
                        break
                
                summary = self.summarize(memory_type)
                return {
                    "response": f"خلاصه {memory_type}: {summary['summary']}",
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "data": summary
                }
            
            # Statistics commands
            elif any(word in message_lower for word in ["آمار", "statistics", "stats"]):
                stats = self.get_memory_statistics()
                return {
                    "response": f"آمار حافظه: {stats.get('statistics', {})}",
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "data": stats
                }
            
            # Default response
            else:
                return {
                    "response": "سیستم مدیریت حافظه پیشرفته آماده است. دستورات: ذخیره، بازیابی، خلاصه، آمار",
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "data": {"available_commands": ["store", "retrieve", "summary", "statistics"]}
                }
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Error in respond: {e}")
            return {
                "response": f"خطا در مدیریت حافظه: {str(e)}",
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }