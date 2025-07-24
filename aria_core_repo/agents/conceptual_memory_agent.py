"""
Conceptual Memory Agent for analyzing and storing conceptual sentences and events.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, func, create_engine, desc
from sqlalchemy.orm import sessionmaker

from .base_agent import BaseAgent
from database import Base, engine, SessionLocal


class ConceptualMemory(Base):
    """Database model for storing conceptual memories."""
    __tablename__ = "conceptual_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    raw_text = Column(Text, nullable=False)
    concept = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)  # هدف، ارزش، تجربه، اولویت، ترس، انگیزه، نگرانی، الهام‌بخش
    sentiment = Column(String(50), nullable=False)  # مثبت، منفی، خنثی
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConceptualMemoryAgent(BaseAgent):
    """
    Conceptual Memory Agent that analyzes and stores conceptual sentences and events.
    Uses PostgreSQL database for persistent storage with concept extraction and sentiment analysis.
    """
    
    def __init__(self):
        super().__init__("ConceptualMemoryAgent", "تحلیلگر مفاهیم و ذخیره‌ساز وقایع")
        self.log("Initialized with PostgreSQL database integration")
        
        # Create table if it doesn't exist
        self._create_conceptual_table()
        
        # Concept categories in Persian
        self.categories = {
            "هدف": ["هدف", "آرزو", "خواسته", "می‌خواهم", "قصد دارم"],
            "ارزش": ["مهم", "ارزش", "اعتقاد", "باور", "اصل"],
            "تجربه": ["تجربه", "یاد گرفتم", "متوجه شدم", "فهمیدم"],
            "اولویت": ["اولویت", "اول", "مهم‌تر", "اصلی"],
            "ترس": ["ترس", "نگران", "می‌ترسم", "نگرانی"],
            "انگیزه": ["انگیزه", "دوست دارم", "عاشق", "علاقه"],
            "نگرانی": ["نگرانی", "مشکل", "دردسر", "چالش"],
            "الهام‌بخش": ["الهام", "انگیزه‌بخش", "جالب", "فوق‌العاده"]
        }
        
        # Sentiment keywords
        self.sentiment_keywords = {
            "مثبت": ["عاشق", "دوست", "خوب", "عالی", "موفق", "خوشحال", "راضی"],
            "منفی": ["بد", "ناراحت", "مشکل", "ترس", "نگران", "غمگین"],
            "خنثی": ["معمولی", "عادی", "نرمال"]
        }
        
        # Try to initialize OpenAI
        try:
            from openai import OpenAI
            self.openai_api_key = os.environ.get("OPENAI_API_KEY")
            if self.openai_api_key:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.openai_available = True
                self.log("OpenAI GPT integration ready")
            else:
                self.openai_available = False
                self.log("OpenAI API key not found, using keyword detection fallback")
        except Exception as e:
            self.openai_available = False
            self.log(f"OpenAI not available: {e}, using keyword detection fallback")
        
        self.log("Conceptual memory categories initialized")
    
    def _create_conceptual_table(self):
        """Create conceptual_memories table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            self.log("Conceptual memories table ready")
        except Exception as e:
            self.log(f"Error creating conceptual memories table: {e}", level="error")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process conceptual memory requests and generate response.
        
        Args:
            message (str): The message containing conceptual content
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the conceptual analysis result
        """
        try:
            self.log(f"Processing conceptual request: {message[:100]}...")
            
            # Remember the user message
            self.remember(message)
            
            # Detect operation type
            operation = self._detect_operation(message)
            
            if operation == "save":
                result = self._analyze_and_save_concept(message, context)
                return {"response": result.get("response", "")}
            elif operation == "latest":
                result = self._fetch_latest_concepts(message, context)
                return {"response": result.get("response", "")}
            else:
                result = self._generate_help_response()
                return {"response": result.get("response", "")}
                
        except Exception as e:
            self.log(f"Error processing conceptual request: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل مفهومی:** {str(e)}"
            }
    
    def _detect_operation(self, message: str) -> str:
        """Detect the type of conceptual operation requested."""
        message_lower = message.lower()
        
        save_keywords = ["تحلیل کن:", "مفهوم:", "analyze:", "ذخیره مفهوم", "concept:"]
        latest_keywords = ["آخرین مفاهیم", "latest", "نشان بده مفاهیم", "مفاهیم اخیر"]
        
        if any(keyword in message_lower for keyword in save_keywords):
            return "save"
        elif any(keyword in message_lower for keyword in latest_keywords):
            return "latest"
        else:
            # Default to save for conceptual content
            return "save"
    
    def _analyze_and_save_concept(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze conceptual content and save to database."""
        try:
            # Extract raw text
            raw_text = self._extract_conceptual_content(message)
            
            if not raw_text:
                return {
                    "response": "❌ **محتوای مفهومی یافت نشد.** لطفاً جمله یا مفهوم خود را مشخص کنید.",
                    "success": False,
                    "timestamp": self._get_current_timestamp()
                }
            
            # Analyze concept using GPT or keyword detection
            if self.openai_available:
                analysis = self._analyze_with_gpt(raw_text)
            else:
                analysis = self._analyze_with_keywords(raw_text)
            
            user_id = context.get("user_id") if context else None
            
            # Save to database
            concept_id = self._save_to_database(
                raw_text=raw_text,
                concept=analysis["concept"],
                category=analysis["category"],
                sentiment=analysis["sentiment"],
                user_id=user_id
            )
            
            if concept_id:
                response = self._format_save_response(concept_id, raw_text, analysis)
                return {
                    "response": response,
                    "success": True,
                    "concept_id": concept_id,
                    "timestamp": self._get_current_timestamp()
                }
            else:
                return {
                    "response": "❌ **خطا در ذخیره مفهوم** در دیتابیس.",
                    "success": False,
                    "timestamp": self._get_current_timestamp()
                }
                
        except Exception as e:
            self.log(f"Error analyzing and saving concept: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل مفهوم:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _analyze_with_gpt(self, text: str) -> Dict[str, str]:
        """Analyze concept using OpenAI GPT."""
        try:
            prompt = f"""تحلیل این جمله و استخراج اطلاعات زیر به زبان فارسی:

جمله: "{text}"

لطفاً پاسخ را در قالب JSON ارائه دهید:
{{
    "concept": "مفهوم کلیدی جمله",
    "category": "یکی از: هدف، ارزش، تجربه، اولویت، ترس، انگیزه، نگرانی، الهام‌بخش",
    "sentiment": "یکی از: مثبت، منفی، خنثی"
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and clean results
            return {
                "concept": result.get("concept", "نامشخص")[:200],
                "category": result.get("category", "تجربه"),
                "sentiment": result.get("sentiment", "خنثی")
            }
            
        except Exception as e:
            self.log(f"GPT analysis failed: {e}, falling back to keyword detection")
            return self._analyze_with_keywords(text)
    
    def _analyze_with_keywords(self, text: str) -> Dict[str, str]:
        """Analyze concept using keyword detection fallback."""
        text_lower = text.lower()
        
        # Detect category
        detected_category = "تجربه"  # default
        for category, keywords in self.categories.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_category = category
                break
        
        # Detect sentiment
        detected_sentiment = "خنثی"  # default
        for sentiment, keywords in self.sentiment_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_sentiment = sentiment
                break
        
        # Extract main concept (first significant words)
        words = text.split()
        concept = " ".join(words[:5]) if len(words) >= 5 else text
        
        return {
            "concept": concept[:200],
            "category": detected_category,
            "sentiment": detected_sentiment
        }
    
    def _fetch_latest_concepts(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch latest conceptual memories from database."""
        try:
            user_id = context.get("user_id") if context else None
            limit = self._extract_limit(message)
            
            concepts = self._fetch_from_database(user_id, limit)
            
            if concepts:
                response = self._format_latest_response(concepts)
                return {
                    "response": response,
                    "success": True,
                    "concepts": concepts,
                    "count": len(concepts),
                    "timestamp": self._get_current_timestamp()
                }
            else:
                return {
                    "response": "🧠 **هیچ مفهومی یافت نشد.** شاید هنوز چیزی تحلیل نکرده‌اید.",
                    "success": True,
                    "concepts": [],
                    "count": 0,
                    "timestamp": self._get_current_timestamp()
                }
                
        except Exception as e:
            self.log(f"Error fetching concepts: {e}", level="error")
            return {
                "response": f"❌ **خطا در دریافت مفاهیم:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _extract_conceptual_content(self, message: str) -> str:
        """Extract the main conceptual content from the message."""
        content = message
        prefixes = ["تحلیل کن:", "مفهوم:", "analyze:", "concept:", "ذخیره مفهوم:"]
        
        for prefix in prefixes:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
                break
        
        return content
    
    def _extract_limit(self, message: str) -> int:
        """Extract limit number from message."""
        import re
        numbers = re.findall(r'\d+', message)
        return int(numbers[0]) if numbers else 10
    
    def _save_to_database(self, raw_text: str, concept: str, category: str, sentiment: str, user_id: Optional[int] = None) -> Optional[int]:
        """Save conceptual memory to database."""
        try:
            db = SessionLocal()
            conceptual_memory = ConceptualMemory(
                user_id=user_id,
                raw_text=raw_text,
                concept=concept,
                category=category,
                sentiment=sentiment
            )
            db.add(conceptual_memory)
            db.commit()
            db.refresh(conceptual_memory)
            concept_id = conceptual_memory.id
            db.close()
            
            self.log(f"Conceptual memory saved with ID: {concept_id}")
            return concept_id
            
        except Exception as e:
            self.log(f"Database save error: {e}", level="error")
            return None
    
    def _fetch_from_database(self, user_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Fetch conceptual memories from database."""
        try:
            db = SessionLocal()
            query = db.query(ConceptualMemory)
            
            if user_id:
                query = query.filter(ConceptualMemory.user_id == user_id)
            
            concepts = query.order_by(desc(ConceptualMemory.created_at)).limit(limit).all()
            
            result = []
            for concept in concepts:
                result.append({
                    "id": concept.id,
                    "raw_text": concept.raw_text,
                    "concept": concept.concept,
                    "category": concept.category,
                    "sentiment": concept.sentiment,
                    "created_at": concept.created_at.isoformat() if concept.created_at else None
                })
            
            db.close()
            return result
            
        except Exception as e:
            self.log(f"Database fetch error: {e}", level="error")
            return []
    
    def _format_save_response(self, concept_id: int, raw_text: str, analysis: Dict[str, str]) -> str:
        """Format the save response."""
        category_emoji = {
            "هدف": "🎯",
            "ارزش": "💎", 
            "تجربه": "📚",
            "اولویت": "⭐",
            "ترس": "😰",
            "انگیزه": "💪",
            "نگرانی": "😟",
            "الهام‌بخش": "✨"
        }
        
        sentiment_emoji = {
            "مثبت": "😊",
            "منفی": "😔", 
            "خنثی": "😐"
        }
        
        response = f"✅ **مفهوم تحلیل و ذخیره شد!**\n\n"
        response += f"📝 **متن اصلی:** {raw_text[:100]}{'...' if len(raw_text) > 100 else ''}\n"
        response += f"🧠 **مفهوم کلیدی:** {analysis['concept']}\n"
        response += f"{category_emoji.get(analysis['category'], '📁')} **دسته:** {analysis['category']}\n"
        response += f"{sentiment_emoji.get(analysis['sentiment'], '😐')} **احساس:** {analysis['sentiment']}\n"
        response += f"🆔 **شناسه:** #{concept_id}\n"
        response += f"⏰ **زمان تحلیل:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return response
    
    def _format_latest_response(self, concepts: List[Dict]) -> str:
        """Format the latest concepts response."""
        category_emoji = {
            "هدف": "🎯",
            "ارزش": "💎", 
            "تجربه": "📚",
            "اولویت": "⭐",
            "ترس": "😰",
            "انگیزه": "💪",
            "نگرانی": "😟",
            "الهام‌بخش": "✨"
        }
        
        sentiment_emoji = {
            "مثبت": "😊",
            "منفی": "😔", 
            "خنثی": "😐"
        }
        
        response = f"🧠 **آخرین مفاهیم تحلیل شده** ({len(concepts)} مورد):\n\n"
        
        for i, concept in enumerate(concepts[:5], 1):
            cat_emoji = category_emoji.get(concept['category'], '📁')
            sent_emoji = sentiment_emoji.get(concept['sentiment'], '😐')
            
            response += f"**{i}.** {cat_emoji} `{concept['category']}` {sent_emoji}\n"
            response += f"   **مفهوم:** {concept['concept']}\n"
            response += f"   **متن:** {concept['raw_text'][:60]}{'...' if len(concept['raw_text']) > 60 else ''}\n"
            response += f"   🕒 {concept['created_at'][:19].replace('T', ' ')} | 🆔 #{concept['id']}\n\n"
        
        if len(concepts) > 5:
            response += f"... و {len(concepts) - 5} مفهوم دیگر\n\n"
        
        response += "💡 **نکته:** برای تحلیل مفهوم جدید، جمله خود را بنویسید."
        
        return response
    
    def _generate_help_response(self) -> Dict[str, Any]:
        """Generate help response for conceptual operations."""
        response = """🧠 **راهنمای تحلیل مفهومی**

**دستورات موجود:**
• جمله یا مفهوم خود را بنویسید - تحلیل خودکار
• `آخرین مفاهیم` - نمایش آخرین تحلیل‌ها

**دسته‌بندی‌ها:**
• هدف 🎯، ارزش 💎، تجربه 📚، اولویت ⭐
• ترس 😰، انگیزه 💪، نگرانی 😟، الهام‌بخش ✨

**تحلیل احساسات:**
• مثبت 😊، منفی 😔، خنثی 😐

**مثال:**
`من عاشق یادگیری تدریجی هستم و به آن اعتقاد دارم`

**نکات:**
• سیستم مفهوم کلیدی، دسته‌بندی و احساس را تشخیص می‌دهد
• تحلیل با OpenAI GPT یا keyword detection انجام می‌شود
• تمام مفاهیم در دیتابیس ذخیره می‌شوند"""
        
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
            "تحلیل مفهومی جملات",
            "استخراج مفاهیم کلیدی", 
            "دسته‌بندی مفاهیم",
            "تحلیل احساسات",
            "ذخیره مفاهیم در دیتابیس",
            "نمایش آخرین تحلیل‌ها"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for conceptual memories."""
        try:
            db = SessionLocal()
            
            total_concepts = db.query(ConceptualMemory).count()
            categories = db.query(ConceptualMemory.category).distinct().all()
            sentiments = db.query(ConceptualMemory.sentiment).distinct().all()
            recent_concepts = db.query(ConceptualMemory).order_by(desc(ConceptualMemory.created_at)).limit(5).all()
            
            db.close()
            
            return {
                "total_concepts": total_concepts,
                "categories": [cat[0] for cat in categories],
                "sentiments": [sent[0] for sent in sentiments],
                "recent_count": len(recent_concepts),
                "table_name": "conceptual_memories",
                "openai_available": self.openai_available
            }
            
        except Exception as e:
            self.log(f"Error getting database stats: {e}", level="error")
            return {
                "total_concepts": 0,
                "categories": [],
                "sentiments": [],
                "recent_count": 0,
                "error": str(e)
            }