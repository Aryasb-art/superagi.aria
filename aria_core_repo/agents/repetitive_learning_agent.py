"""
Repetitive Learning Agent for detecting and learning from repeated concepts, goals, and phrases over time.
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
from sqlalchemy import Column, Integer, String, Text, DateTime, func, create_engine, desc
from sqlalchemy.orm import sessionmaker

from .base_agent import BaseAgent
from database import Base, engine, SessionLocal


class RepetitivePattern(Base):
    """Database model for storing repetitive patterns and phrases."""
    __tablename__ = "repetitive_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    phrase = Column(String(500), nullable=False)
    count = Column(Integer, default=1)
    category = Column(String(100), nullable=False)  # هدف، نگرانی، علاقه، عادت، تکرار
    last_occurred_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RepetitiveLearningAgent(BaseAgent):
    """
    Repetitive Learning Agent that detects and learns from repeated concepts, goals, and phrases.
    Analyzes short-term and long-term memory to identify patterns and repetitive elements.
    """
    
    def __init__(self):
        super().__init__("RepetitiveLearningAgent", "تحلیلگر الگوهای تکراری و یادگیری از تکرار")
        self.log("Initialized with PostgreSQL database integration for pattern detection")
        
        # Create table if it doesn't exist
        self._create_repetitive_table()
        
        # Repetition thresholds
        self.min_repetition_threshold = 3  # Minimum repetitions to consider as pattern
        self.warning_threshold = 5  # Threshold for warnings
        self.critical_threshold = 10  # Critical repetition level
        
        # Pattern categories in Persian
        self.pattern_categories = {
            "هدف": ["هدف", "می‌خواهم", "قصد دارم", "برنامه دارم", "آرزو"],
            "نگرانی": ["نگران", "ترس", "مشکل", "دردسر", "استرس"],
            "علاقه": ["دوست دارم", "عاشق", "علاقه", "خوشم می‌آید"],
            "عادت": ["همیشه", "معمولاً", "هر روز", "مدام", "عادت"],
            "تکرار": ["دوباره", "بازم", "یکبار دیگر", "مجدد"]
        }
        
        # Keywords for pattern detection
        self.important_keywords = [
            "هدف", "آرزو", "می‌خواهم", "باید", "لازم", "مهم", "ضروری",
            "نگران", "ترس", "مشکل", "استرس", "دردسر",
            "دوست دارم", "عاشق", "علاقه", "خوشم",
            "همیشه", "معمولاً", "مدام", "عادت", "تکرار"
        ]
        
        self.log("Repetitive pattern categories and thresholds initialized")
    
    def _create_repetitive_table(self):
        """Create repetitive_patterns table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            self.log("Repetitive patterns table ready")
        except Exception as e:
            self.log(f"Error creating repetitive patterns table: {e}", level="error")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process repetitive pattern requests and generate response.
        
        Args:
            message (str): The message containing pattern analysis request
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the pattern analysis result
        """
        try:
            self.log(f"Processing repetitive pattern request: {message[:100]}...")
            
            # Remember the user message
            self.remember(message)
            
            # Detect operation type
            operation = self._detect_operation(message)
            
            if operation == "observe":
                result = self._observe_and_analyze(message, context)
                return {"response": result.get("response", "")}
            elif operation == "frequent":
                result = self._get_frequent_patterns(message, context)
                return {"response": result.get("response", "")}
            elif operation == "analyze_all":
                result = self._analyze_all_memories(context)
                return {"response": result.get("response", "")}
            else:
                # Default: observe the current message
                result = self._observe_and_analyze(message, context)
                return {"response": result.get("response", "")}
                
        except Exception as e:
            self.log(f"Error processing repetitive pattern request: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل الگوی تکراری:** {str(e)}"
            }
    
    def _detect_operation(self, message: str) -> str:
        """Detect the type of repetitive pattern operation requested."""
        message_lower = message.lower()
        
        observe_keywords = ["مشاهده", "observe", "تحلیل", "analyze", "بررسی", "check"]
        frequent_keywords = ["تکراری", "frequent", "الگو", "pattern", "مکرر", "repeated"]
        analyze_keywords = ["تحلیل همه", "analyze all", "بررسی کل", "check all"]
        
        if any(keyword in message_lower for keyword in analyze_keywords):
            return "analyze_all"
        elif any(keyword in message_lower for keyword in frequent_keywords):
            return "frequent"
        elif any(keyword in message_lower for keyword in observe_keywords):
            return "observe"
        else:
            return "observe"
    
    def _observe_and_analyze(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Observe current message and analyze for repetitive patterns."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Extract key phrases from the message
            key_phrases = self._extract_key_phrases(message)
            
            if not key_phrases:
                return {
                    "response": "📊 **تحلیل الگوی تکراری:** هیچ عبارت کلیدی قابل تحلیل یافت نشد.",
                    "success": True,
                    "timestamp": self._get_current_timestamp()
                }
            
            # Check each phrase for repetitions
            detected_patterns = []
            for phrase, category in key_phrases:
                pattern_info = self._check_repetition(phrase, category, user_id)
                if pattern_info:
                    detected_patterns.append(pattern_info)
            
            # Analyze memory for additional patterns
            memory_patterns = self._analyze_recent_memory(user_id)
            
            response = self._format_observation_response(detected_patterns, memory_patterns)
            
            return {
                "response": response,
                "success": True,
                "patterns_detected": len(detected_patterns),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error in observe and analyze: {e}", level="error")
            return {
                "response": f"❌ **خطا در مشاهده الگو:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _get_frequent_patterns(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get frequently repeated patterns from database."""
        try:
            user_id = context.get("user_id") if context else None
            limit = self._extract_limit(message)
            
            patterns = self._fetch_frequent_patterns(user_id, limit)
            
            if patterns:
                response = self._format_frequent_response(patterns)
                return {
                    "response": response,
                    "success": True,
                    "patterns": patterns,
                    "count": len(patterns),
                    "timestamp": self._get_current_timestamp()
                }
            else:
                return {
                    "response": "🔍 **الگوهای تکراری:** هنوز الگوی تکراری خاصی شناسایی نشده است.",
                    "success": True,
                    "patterns": [],
                    "count": 0,
                    "timestamp": self._get_current_timestamp()
                }
                
        except Exception as e:
            self.log(f"Error fetching frequent patterns: {e}", level="error")
            return {
                "response": f"❌ **خطا در دریافت الگوهای تکراری:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _analyze_all_memories(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze all existing memories for repetitive patterns."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Analyze long-term memories
            longterm_patterns = self._analyze_longterm_memory(user_id)
            
            # Analyze conceptual memories  
            conceptual_patterns = self._analyze_conceptual_memory(user_id)
            
            # Combine and process all patterns
            all_patterns = longterm_patterns + conceptual_patterns
            processed_patterns = self._process_pattern_list(all_patterns, user_id)
            
            response = self._format_analysis_response(processed_patterns)
            
            return {
                "response": response,
                "success": True,
                "total_patterns": len(processed_patterns),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error analyzing all memories: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل کلی حافظه‌ها:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _extract_key_phrases(self, text: str) -> List[Tuple[str, str]]:
        """Extract key phrases and their categories from text."""
        phrases = []
        text_lower = text.lower()
        
        # Check for important keywords and extract surrounding context
        for keyword in self.important_keywords:
            if keyword in text_lower:
                # Find the sentence or phrase containing this keyword
                sentences = re.split(r'[.!?؟]', text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        phrase = sentence.strip()
                        if len(phrase) > 5:  # Minimum phrase length
                            category = self._categorize_phrase(phrase)
                            phrases.append((phrase, category))
        
        # Also extract meaningful noun phrases
        # Simple pattern matching for Persian phrases
        patterns = [
            r'هدف\s+\w+',
            r'می‌خواهم\s+.{5,50}',
            r'نگران\s+.{5,50}',
            r'دوست\s+دارم\s+.{5,50}',
            r'باید\s+.{5,50}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                category = self._categorize_phrase(match)
                phrases.append((match.strip(), category))
        
        # Remove duplicates
        unique_phrases = list(set(phrases))
        return unique_phrases[:10]  # Limit to top 10 phrases
    
    def _categorize_phrase(self, phrase: str) -> str:
        """Categorize a phrase based on its content."""
        phrase_lower = phrase.lower()
        
        for category, keywords in self.pattern_categories.items():
            if any(keyword in phrase_lower for keyword in keywords):
                return category
        
        return "تکرار"  # Default category
    
    def _check_repetition(self, phrase: str, category: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Check if a phrase is repetitive and update database."""
        try:
            # Clean and normalize phrase
            normalized_phrase = self._normalize_phrase(phrase)
            
            # Check database for existing pattern
            db = SessionLocal()
            existing_pattern = db.query(RepetitivePattern).filter(
                RepetitivePattern.phrase == normalized_phrase
            )
            
            if user_id:
                existing_pattern = existing_pattern.filter(RepetitivePattern.user_id == user_id)
            
            existing_pattern = existing_pattern.first()
            
            if existing_pattern:
                # Update existing pattern
                existing_pattern.count += 1
                existing_pattern.last_occurred_at = datetime.now()
                db.commit()
                
                pattern_info = {
                    "id": existing_pattern.id,
                    "phrase": existing_pattern.phrase,
                    "count": existing_pattern.count,
                    "category": existing_pattern.category,
                    "is_repetitive": existing_pattern.count >= self.min_repetition_threshold,
                    "warning_level": self._get_warning_level(existing_pattern.count)
                }
                
                self.log(f"Updated repetitive pattern: {normalized_phrase} (count: {existing_pattern.count})")
            else:
                # Create new pattern
                new_pattern = RepetitivePattern(
                    user_id=user_id,
                    phrase=normalized_phrase,
                    count=1,
                    category=category
                )
                db.add(new_pattern)
                db.commit()
                db.refresh(new_pattern)
                
                pattern_info = {
                    "id": new_pattern.id,
                    "phrase": new_pattern.phrase,
                    "count": 1,
                    "category": new_pattern.category,
                    "is_repetitive": False,
                    "warning_level": "جدید"
                }
                
                self.log(f"Created new pattern: {normalized_phrase}")
            
            db.close()
            return pattern_info
            
        except Exception as e:
            self.log(f"Error checking repetition: {e}", level="error")
            return None
    
    def _normalize_phrase(self, phrase: str) -> str:
        """Normalize phrase for comparison."""
        # Remove extra spaces, punctuation, and normalize
        normalized = re.sub(r'\s+', ' ', phrase.strip())
        normalized = re.sub(r'[.!?؟،]', '', normalized)
        return normalized[:500]  # Limit length
    
    def _get_warning_level(self, count: int) -> str:
        """Get warning level based on repetition count."""
        if count >= self.critical_threshold:
            return "بحرانی"
        elif count >= self.warning_threshold:
            return "هشدار"
        elif count >= self.min_repetition_threshold:
            return "قابل توجه"
        else:
            return "عادی"
    
    def _analyze_recent_memory(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Analyze recent memory for patterns."""
        patterns = []
        
        # Get recent messages from short-term memory
        recent_memory = self.recall(10)  # Last 10 messages
        
        # Extract text from memory messages
        memory_texts = []
        for memory_item in recent_memory:
            if isinstance(memory_item, dict) and 'content' in memory_item:
                memory_texts.append(memory_item['content'])
        
        # Analyze for repeated elements
        if memory_texts:
            # Count word frequencies
            all_words = []
            for text in memory_texts:
                words = self._extract_meaningful_words(text)
                all_words.extend(words)
            
            word_counts = Counter(all_words)
            frequent_words = [(word, count) for word, count in word_counts.items() 
                             if count >= 2 and len(word) > 3]
            
            for word, count in frequent_words[:5]:  # Top 5 frequent words
                patterns.append({
                    "phrase": word,
                    "count": count,
                    "category": "حافظه کوتاه‌مدت",
                    "source": "short_term_memory"
                })
        
        return patterns
    
    def _extract_meaningful_words(self, text: str) -> List[str]:
        """Extract meaningful words from text."""
        # Simple tokenization and filtering
        words = re.findall(r'\b\w{4,}\b', text.lower())  # Words with 4+ characters
        
        # Filter out common words
        stop_words = {'است', 'که', 'این', 'آن', 'در', 'با', 'به', 'از', 'را', 'و', 'یا'}
        meaningful_words = [word for word in words if word not in stop_words]
        
        return meaningful_words
    
    def _analyze_longterm_memory(self, user_id: Optional[int] = None) -> List[str]:
        """Analyze long-term memory for repetitive patterns."""
        try:
            db = SessionLocal()
            
            # Import here to avoid circular imports
            from .longterm_memory_agent import LongTermMemory
            
            query = db.query(LongTermMemory)
            if user_id:
                query = query.filter(LongTermMemory.user_id == user_id)
            
            memories = query.order_by(desc(LongTermMemory.created_at)).limit(50).all()
            
            # Extract content from memories
            memory_contents = [memory.content for memory in memories if memory.content]
            
            db.close()
            return memory_contents
            
        except Exception as e:
            self.log(f"Error analyzing long-term memory: {e}", level="error")
            return []
    
    def _analyze_conceptual_memory(self, user_id: Optional[int] = None) -> List[str]:
        """Analyze conceptual memory for repetitive patterns."""
        try:
            db = SessionLocal()
            
            # Import here to avoid circular imports
            from .conceptual_memory_agent import ConceptualMemory
            
            query = db.query(ConceptualMemory)
            if user_id:
                query = query.filter(ConceptualMemory.user_id == user_id)
            
            concepts = query.order_by(desc(ConceptualMemory.created_at)).limit(50).all()
            
            # Extract raw text and concepts
            conceptual_contents = []
            for concept in concepts:
                if concept.raw_text:
                    conceptual_contents.append(concept.raw_text)
                if concept.concept:
                    conceptual_contents.append(concept.concept)
            
            db.close()
            return conceptual_contents
            
        except Exception as e:
            self.log(f"Error analyzing conceptual memory: {e}", level="error")
            return []
    
    def _process_pattern_list(self, text_list: List[str], user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Process a list of texts to find repetitive patterns."""
        patterns = []
        
        # Combine all texts
        combined_text = ' '.join(text_list)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(combined_text)
        
        # Count phrase frequencies in individual texts
        phrase_counts = {}
        for phrase, category in key_phrases:
            normalized_phrase = self._normalize_phrase(phrase)
            count = sum(1 for text in text_list if normalized_phrase.lower() in text.lower())
            
            if count >= 2:  # Appears in at least 2 different texts
                phrase_counts[normalized_phrase] = {
                    "count": count,
                    "category": category,
                    "phrase": phrase
                }
        
        # Convert to pattern format and save to database
        for phrase, info in phrase_counts.items():
            if info["count"] >= self.min_repetition_threshold:
                # Save or update in database
                pattern_info = self._check_repetition(phrase, info["category"], user_id)
                if pattern_info:
                    patterns.append(pattern_info)
        
        return patterns
    
    def _fetch_frequent_patterns(self, user_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Fetch frequent patterns from database."""
        try:
            db = SessionLocal()
            query = db.query(RepetitivePattern).filter(
                RepetitivePattern.count >= self.min_repetition_threshold
            )
            
            if user_id:
                query = query.filter(RepetitivePattern.user_id == user_id)
            
            patterns = query.order_by(desc(RepetitivePattern.count)).limit(limit).all()
            
            result = []
            for pattern in patterns:
                result.append({
                    "id": pattern.id,
                    "phrase": pattern.phrase,
                    "count": pattern.count,
                    "category": pattern.category,
                    "warning_level": self._get_warning_level(pattern.count),
                    "last_occurred": pattern.last_occurred_at.isoformat() if pattern.last_occurred_at else None,
                    "created_at": pattern.created_at.isoformat() if pattern.created_at else None
                })
            
            db.close()
            return result
            
        except Exception as e:
            self.log(f"Database fetch error: {e}", level="error")
            return []
    
    def _extract_limit(self, message: str) -> int:
        """Extract limit number from message."""
        import re
        numbers = re.findall(r'\d+', message)
        return int(numbers[0]) if numbers else 10
    
    def _format_observation_response(self, detected_patterns: List[Dict], memory_patterns: List[Dict]) -> str:
        """Format the observation response."""
        response = "🔍 **تحلیل الگوی تکراری:**\n\n"
        
        if detected_patterns:
            response += "**🔴 الگوهای شناسایی شده:**\n"
            for i, pattern in enumerate(detected_patterns[:5], 1):
                warning_emoji = self._get_warning_emoji(pattern.get("warning_level", "عادی"))
                response += f"**{i}.** {warning_emoji} `{pattern['category']}` - {pattern['phrase'][:50]}{'...' if len(pattern['phrase']) > 50 else ''}\n"
                response += f"   🔢 تکرار: {pattern['count']} بار | وضعیت: {pattern['warning_level']}\n\n"
        
        if memory_patterns:
            response += "**📊 الگوهای حافظه کوتاه‌مدت:**\n"
            for i, pattern in enumerate(memory_patterns[:3], 1):
                response += f"**{i}.** `{pattern['category']}` - {pattern['phrase'][:40]}\n"
                response += f"   🔢 تکرار: {pattern['count']} بار\n\n"
        
        if not detected_patterns and not memory_patterns:
            response += "✅ **هیچ الگوی تکراری قابل توجهی یافت نشد.**\n\n"
        
        response += "💡 **نکته:** برای مشاهده تمام الگوهای تکراری از دستور 'الگوهای تکراری' استفاده کنید."
        
        return response
    
    def _format_frequent_response(self, patterns: List[Dict]) -> str:
        """Format the frequent patterns response."""
        response = f"🔍 **الگوهای تکراری شناسایی شده** ({len(patterns)} مورد):\n\n"
        
        for i, pattern in enumerate(patterns[:10], 1):
            warning_emoji = self._get_warning_emoji(pattern['warning_level'])
            category_emoji = self._get_category_emoji(pattern['category'])
            
            response += f"**{i}.** {warning_emoji} {category_emoji} `{pattern['category']}`\n"
            response += f"   **عبارت:** {pattern['phrase'][:60]}{'...' if len(pattern['phrase']) > 60 else ''}\n"
            response += f"   🔢 **تکرار:** {pattern['count']} بار | 🚨 **وضعیت:** {pattern['warning_level']}\n"
            response += f"   🕒 آخرین بار: {pattern['last_occurred'][:19].replace('T', ' ')} | 🆔 #{pattern['id']}\n\n"
        
        if len(patterns) > 10:
            response += f"... و {len(patterns) - 10} الگوی دیگر\n\n"
        
        response += "💡 **توصیه:** الگوهای با وضعیت 'بحرانی' نیاز به توجه ویژه دارند."
        
        return response
    
    def _format_analysis_response(self, patterns: List[Dict]) -> str:
        """Format the complete analysis response."""
        response = f"📊 **تحلیل کامل الگوهای تکراری** ({len(patterns)} مورد شناسایی شده):\n\n"
        
        if patterns:
            # Group by warning level
            critical_patterns = [p for p in patterns if p.get("warning_level") == "بحرانی"]
            warning_patterns = [p for p in patterns if p.get("warning_level") == "هشدار"]
            notable_patterns = [p for p in patterns if p.get("warning_level") == "قابل توجه"]
            
            if critical_patterns:
                response += f"🚨 **الگوهای بحرانی** ({len(critical_patterns)} مورد):\n"
                for pattern in critical_patterns[:3]:
                    response += f"   • {pattern['phrase'][:50]} - {pattern['count']} تکرار\n"
                response += "\n"
            
            if warning_patterns:
                response += f"⚠️ **الگوهای هشدار** ({len(warning_patterns)} مورد):\n"
                for pattern in warning_patterns[:3]:
                    response += f"   • {pattern['phrase'][:50]} - {pattern['count']} تکرار\n"
                response += "\n"
            
            if notable_patterns:
                response += f"📝 **الگوهای قابل توجه** ({len(notable_patterns)} مورد):\n"
                for pattern in notable_patterns[:3]:
                    response += f"   • {pattern['phrase'][:50]} - {pattern['count']} تکرار\n"
                response += "\n"
            
            response += f"**📈 آمار کلی:**\n"
            response += f"• مجموع الگوهای تکراری: {len(patterns)}\n"
            response += f"• الگوهای بحرانی: {len(critical_patterns)}\n"
            response += f"• الگوهای هشدار: {len(warning_patterns)}\n"
            response += f"• الگوهای قابل توجه: {len(notable_patterns)}\n\n"
            
        else:
            response += "✅ **هیچ الگوی تکراری قابل توجهی در حافظه‌های موجود یافت نشد.**\n\n"
        
        response += "💡 **توصیه:** برای مدیریت بهتر، الگوهای تکراری را بررسی و در صورت نیاز به اهداف فعال اضافه کنید."
        
        return response
    
    def _get_warning_emoji(self, warning_level: str) -> str:
        """Get emoji for warning level."""
        warning_emojis = {
            "بحرانی": "🚨",
            "هشدار": "⚠️",
            "قابل توجه": "📝",
            "عادی": "ℹ️",
            "جدید": "🆕"
        }
        return warning_emojis.get(warning_level, "📊")
    
    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category."""
        category_emojis = {
            "هدف": "🎯",
            "نگرانی": "😟",
            "علاقه": "❤️",
            "عادت": "🔄",
            "تکرار": "🔁"
        }
        return category_emojis.get(category, "📁")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "تشخیص الگوهای تکراری",
            "تحلیل حافظه کوتاه‌مدت و بلندمدت",
            "دسته‌بندی الگوها",
            "هشدار برای تکرارهای مهم",
            "ذخیره الگوها در دیتابیس",
            "تحلیل آماری تکرارها"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for repetitive patterns."""
        try:
            db = SessionLocal()
            
            total_patterns = db.query(RepetitivePattern).count()
            critical_patterns = db.query(RepetitivePattern).filter(
                RepetitivePattern.count >= self.critical_threshold
            ).count()
            warning_patterns = db.query(RepetitivePattern).filter(
                RepetitivePattern.count >= self.warning_threshold
            ).count()
            categories = db.query(RepetitivePattern.category).distinct().all()
            
            db.close()
            
            return {
                "total_patterns": total_patterns,
                "critical_patterns": critical_patterns,
                "warning_patterns": warning_patterns,
                "categories": [cat[0] for cat in categories],
                "table_name": "repetitive_patterns",
                "thresholds": {
                    "min_repetition": self.min_repetition_threshold,
                    "warning": self.warning_threshold,
                    "critical": self.critical_threshold
                }
            }
            
        except Exception as e:
            self.log(f"Error getting database stats: {e}", level="error")
            return {
                "total_patterns": 0,
                "critical_patterns": 0,
                "warning_patterns": 0,
                "categories": [],
                "error": str(e)
            }