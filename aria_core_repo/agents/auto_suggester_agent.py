"""
Auto Suggester Agent for providing intelligent suggestions based on context and memory analysis.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import Column, Integer, String, Text, DateTime, func, create_engine, desc, JSON, Float
from sqlalchemy.orm import sessionmaker

from .base_agent import BaseAgent
from database import Base, engine, SessionLocal


class AutoSuggestion(Base):
    """Database model for storing auto suggestions and their metadata."""
    __tablename__ = "auto_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    input_text = Column(Text, nullable=False)  # Original input text
    suggestion = Column(Text, nullable=False)  # Generated suggestion
    suggestion_type = Column(String(50), nullable=False)  # Type of suggestion
    confidence = Column(Float, nullable=False, default=0.0)  # Confidence score 0-1
    context_data = Column(JSON, nullable=False)  # Context used for suggestion
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AutoSuggesterAgent(BaseAgent):
    """
    Auto Suggester Agent that provides intelligent suggestions based on context,
    memory analysis, and user patterns.
    """
    
    def __init__(self):
        super().__init__("AutoSuggesterAgent", "ایجنت پیشنهادات خودکار و تحلیل زمینه")
        self.log("Initialized with PostgreSQL database integration for suggestion storage")
        
        # Create table if it doesn't exist
        self._create_suggestions_table()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        self._initialize_openai()
        
        # Suggestion types with Persian labels
        self.suggestion_types = {
            "continue": "ادامه متن",
            "action": "اقدام بعدی", 
            "warning": "هشدار",
            "related": "مطالب مرتبط",
            "improvement": "بهبود",
            "question": "سوال راهنما",
            "goal": "هدف پیشنهادی",
            "reminder": "یادآوری"
        }
        
        # Context keywords for suggestion generation
        self.context_keywords = {
            "goal_keywords": ["هدف", "برنامه", "قصد", "می‌خواهم", "باید", "لازم"],
            "problem_keywords": ["مشکل", "خطا", "نمی‌توانم", "سخت", "دشوار", "چطور"],
            "completion_keywords": ["تمام", "کامل", "انجام", "درست", "موفق"],
            "learning_keywords": ["یاد", "تمرین", "مطالعه", "آموزش", "درس"],
            "health_keywords": ["ورزش", "سلامت", "تناسب", "رژیم", "خواب"],
            "work_keywords": ["کار", "شغل", "پروژه", "وظیفه", "مسئولیت"]
        }
        
        self.log("Auto suggestion types and context keywords initialized")
    
    def _create_suggestions_table(self):
        """Create auto_suggestions table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            self.log("Auto suggestions table ready")
        except Exception as e:
            self.log(f"Error creating auto suggestions table: {e}", level="error")
    
    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available."""
        try:
            import openai
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.log("OpenAI GPT integration ready for intelligent suggestions")
            else:
                self.log("OpenAI API key not found, using rule-based suggestions")
        except ImportError:
            self.log("OpenAI library not available, using rule-based suggestions")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}, using rule-based suggestions")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process auto suggestion requests and generate response.
        
        Args:
            message (str): The message containing suggestion request
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing suggestions and metadata
        """
        try:
            self.log(f"Processing auto suggestion request: {message[:100]}...")
            
            # Remember the user message
            self.remember(message)
            
            # Detect operation type
            operation = self._detect_operation(message)
            
            if operation == "complete":
                result = self._generate_completion_suggestions(message, context)
            elif operation == "hints":
                result = self._generate_contextual_hints(message, context)
            else:
                # Default: generate comprehensive suggestions
                result = self._generate_comprehensive_suggestions(message, context)
            
            return {"response": result.get("response", "")}
                
        except Exception as e:
            self.log(f"Error processing auto suggestion request: {e}", level="error")
            return {
                "response": f"❌ **خطا در تولید پیشنهادات:** {str(e)}"
            }
    
    def _detect_operation(self, message: str) -> str:
        """Detect the type of suggestion operation requested."""
        message_lower = message.lower()
        
        complete_keywords = ["ادامه", "complete", "تکمیل", "بقیه", "ادامه‌دار"]
        hints_keywords = ["راهنما", "hints", "پیشنهاد", "suggest", "کمک", "help"]
        
        if any(keyword in message_lower for keyword in complete_keywords):
            return "complete"
        elif any(keyword in message_lower for keyword in hints_keywords):
            return "hints"
        else:
            return "comprehensive"
    
    def _generate_completion_suggestions(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate text completion suggestions."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Analyze memory context
            memory_context = self._analyze_memory_context(message)
            
            # Generate suggestions
            suggestions = []
            
            if self.openai_client:
                suggestions.extend(self._generate_ai_completions(message, memory_context))
            
            # Add rule-based completions
            suggestions.extend(self._generate_rule_based_completions(message, memory_context))
            
            # Save suggestions to database
            for suggestion in suggestions[:3]:  # Save top 3
                self._save_suggestion(
                    user_id, message, suggestion["text"], 
                    suggestion["type"], suggestion["confidence"], memory_context
                )
            
            response = self._format_completion_response(suggestions, memory_context)
            
            return {
                "response": response,
                "success": True,
                "suggestions_count": len(suggestions),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error generating completion suggestions: {e}", level="error")
            return {
                "response": f"❌ **خطا در تولید ادامه متن:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _generate_contextual_hints(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate contextual hints and suggestions."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Analyze memory context
            memory_context = self._analyze_memory_context(message)
            
            # Generate different types of hints
            hints = []
            
            # Goal-based hints
            hints.extend(self._generate_goal_hints(message, memory_context))
            
            # Action hints
            hints.extend(self._generate_action_hints(message, memory_context))
            
            # Warning hints
            hints.extend(self._generate_warning_hints(message, memory_context))
            
            # Related content hints
            hints.extend(self._generate_related_hints(message, memory_context))
            
            # Save hints to database
            for hint in hints[:5]:  # Save top 5
                self._save_suggestion(
                    user_id, message, hint["text"],
                    hint["type"], hint["confidence"], memory_context
                )
            
            response = self._format_hints_response(hints, memory_context)
            
            return {
                "response": response,
                "success": True,
                "hints_count": len(hints),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error generating contextual hints: {e}", level="error")
            return {
                "response": f"❌ **خطا در تولید راهنماها:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _generate_comprehensive_suggestions(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate comprehensive suggestions combining completions and hints."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Analyze memory context
            memory_context = self._analyze_memory_context(message)
            
            # Generate all types of suggestions
            all_suggestions = []
            
            # Completions
            if self.openai_client:
                all_suggestions.extend(self._generate_ai_completions(message, memory_context))
            all_suggestions.extend(self._generate_rule_based_completions(message, memory_context))
            
            # Hints
            all_suggestions.extend(self._generate_goal_hints(message, memory_context))
            all_suggestions.extend(self._generate_action_hints(message, memory_context))
            all_suggestions.extend(self._generate_warning_hints(message, memory_context))
            
            # Sort by confidence and limit
            all_suggestions.sort(key=lambda x: x["confidence"], reverse=True)
            top_suggestions = all_suggestions[:8]
            
            # Save to database
            for suggestion in top_suggestions:
                self._save_suggestion(
                    user_id, message, suggestion["text"],
                    suggestion["type"], suggestion["confidence"], memory_context
                )
            
            response = self._format_comprehensive_response(top_suggestions, memory_context)
            
            return {
                "response": response,
                "success": True,
                "suggestions_count": len(top_suggestions),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error generating comprehensive suggestions: {e}", level="error")
            return {
                "response": f"❌ **خطا در تولید پیشنهادات:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _analyze_memory_context(self, message: str) -> Dict[str, Any]:
        """Analyze memory context from short-term memory and other agents."""
        context = {
            "short_term_memories": [],
            "dominant_themes": [],
            "recent_goals": [],
            "patterns": [],
            "sentiment": "neutral"
        }
        
        # Analyze short-term memory
        if self.memory:
            recent_messages = list(self.memory)[-5:]  # Last 5 messages
            context["short_term_memories"] = recent_messages
            
            # Extract themes
            all_text = " ".join(recent_messages + [message])
            context["dominant_themes"] = self._extract_themes(all_text)
        
        # Analyze current message context
        context["message_category"] = self._categorize_message(message)
        context["urgency_level"] = self._assess_urgency(message)
        
        return context
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract dominant themes from text."""
        themes = []
        text_lower = text.lower()
        
        for category, keywords in self.context_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches >= 2:  # Theme appears multiple times
                theme_name = category.replace("_keywords", "")
                themes.append(theme_name)
        
        return themes[:3]  # Top 3 themes
    
    def _categorize_message(self, message: str) -> str:
        """Categorize the message based on content."""
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in self.context_keywords["goal_keywords"]):
            return "goal"
        elif any(kw in message_lower for kw in self.context_keywords["problem_keywords"]):
            return "problem"
        elif any(kw in message_lower for kw in self.context_keywords["completion_keywords"]):
            return "completion"
        elif any(kw in message_lower for kw in self.context_keywords["learning_keywords"]):
            return "learning"
        else:
            return "general"
    
    def _assess_urgency(self, message: str) -> str:
        """Assess urgency level of the message."""
        urgent_keywords = ["فوری", "سریع", "حتماً", "الان", "امروز", "urgent"]
        moderate_keywords = ["مهم", "لازم", "باید", "important"]
        
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in urgent_keywords):
            return "high"
        elif any(kw in message_lower for kw in moderate_keywords):
            return "medium"
        else:
            return "low"
    
    def _generate_ai_completions(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered text completions."""
        try:
            prompt = f"""
            بر اساس متن زیر و زمینه ارائه شده، ۳ پیشنهاد برای ادامه متن ارائه بده.
            هر پیشنهاد باید منطقی، مفید و مرتبط باشد.
            
            متن: {message}
            زمینه: حافظه کوتاه‌مدت شامل {', '.join(context.get('short_term_memories', [])[:3])}
            موضوعات غالب: {', '.join(context.get('dominant_themes', []))}
            
            فقط ۳ پیشنهاد کوتاه در قالب JSON برگردان:
            {{"suggestions": [{"text": "...", "confidence": 0.8}]}}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            suggestions = []
            
            for item in result.get("suggestions", []):
                suggestions.append({
                    "text": item.get("text", ""),
                    "type": "continue",
                    "confidence": item.get("confidence", 0.7),
                    "source": "ai"
                })
            
            self.log(f"AI generated {len(suggestions)} completion suggestions")
            return suggestions
            
        except Exception as e:
            self.log(f"AI completion generation failed: {e}")
            return []
    
    def _generate_rule_based_completions(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate rule-based completions."""
        suggestions = []
        message_category = context.get("message_category", "general")
        
        if message_category == "goal":
            suggestions.append({
                "text": "و برای رسیدن به این هدف، قدم اول تعیین برنامه زمانی مشخص است.",
                "type": "continue",
                "confidence": 0.8,
                "source": "rule"
            })
            
        elif message_category == "problem":
            suggestions.append({
                "text": "برای حل این مشکل، بهتر است ابتدا علت اصلی را شناسایی کنیم.",
                "type": "continue", 
                "confidence": 0.7,
                "source": "rule"
            })
            
        elif message_category == "learning":
            suggestions.append({
                "text": "و برای یادگیری بهتر، تمرین منظم و مرور مطالب ضروری است.",
                "type": "continue",
                "confidence": 0.75,
                "source": "rule"
            })
        
        # Add general completion
        if len(message.split()) > 5:
            suggestions.append({
                "text": "همچنین لازم است در نظر بگیریم که...",
                "type": "continue",
                "confidence": 0.6,
                "source": "rule"
            })
        
        return suggestions
    
    def _generate_goal_hints(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate goal-related hints."""
        hints = []
        themes = context.get("dominant_themes", [])
        
        if "goal" in themes or context.get("message_category") == "goal":
            hints.append({
                "text": "💡 هدف خود را SMART (مشخص، قابل اندازه‌گیری، قابل دستیابی، مرتبط، زمان‌دار) تعریف کنید",
                "type": "goal",
                "confidence": 0.8,
                "source": "rule"
            })
            
        if "health" in themes:
            hints.append({
                "text": "🏃‍♂️ برای سلامتی، ورزش منظم ۳ بار در هفته توصیه می‌شود",
                "type": "goal",
                "confidence": 0.7,
                "source": "rule"
            })
            
        return hints
    
    def _generate_action_hints(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate action-oriented hints."""
        hints = []
        urgency = context.get("urgency_level", "low")
        
        if urgency == "high":
            hints.append({
                "text": "⚡ با توجه به فوریت موضوع، بهتر است فوراً شروع کنید",
                "type": "action",
                "confidence": 0.9,
                "source": "rule"
            })
            
        elif urgency == "medium":
            hints.append({
                "text": "📅 برای این کار مهم، یک زمان‌بندی مشخص تعیین کنید",
                "type": "action", 
                "confidence": 0.8,
                "source": "rule"
            })
        
        # Generic action hint
        hints.append({
            "text": "📝 قدم بعدی: لیستی از اقدامات لازم تهیه کنید",
            "type": "action",
            "confidence": 0.6,
            "source": "rule"
        })
        
        return hints
    
    def _generate_warning_hints(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate warning and caution hints."""
        hints = []
        message_lower = message.lower()
        
        # Check for potential risks
        risk_keywords = ["خطر", "ریسک", "مشکل", "اشتباه", "غلط"]
        if any(kw in message_lower for kw in risk_keywords):
            hints.append({
                "text": "⚠️ هشدار: قبل از ادامه، ریسک‌های احتمالی را بررسی کنید",
                "type": "warning",
                "confidence": 0.8,
                "source": "rule"
            })
        
        # Health-related warnings
        if any(kw in message_lower for kw in ["بی‌خوابی", "استرس", "خستگی"]):
            hints.append({
                "text": "🏥 توجه: اگر مشکل ادامه دارد، با متخصص مشورت کنید",
                "type": "warning",
                "confidence": 0.7,
                "source": "rule"
            })
        
        return hints
    
    def _generate_related_hints(self, message: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate hints about related content."""
        hints = []
        themes = context.get("dominant_themes", [])
        
        if "learning" in themes:
            hints.append({
                "text": "📚 مطالب مرتبط: منابع آموزشی تکمیلی جستجو کنید",
                "type": "related",
                "confidence": 0.6,
                "source": "rule"
            })
            
        if "work" in themes:
            hints.append({
                "text": "💼 پیشنهاد: با همکاران در این موضوع مشورت کنید",
                "type": "related",
                "confidence": 0.6,
                "source": "rule"
            })
        
        return hints
    
    def _save_suggestion(self, user_id: Optional[int], input_text: str, suggestion: str,
                        suggestion_type: str, confidence: float, context_data: Dict[str, Any]) -> int:
        """Save suggestion to database."""
        try:
            db = SessionLocal()
            
            auto_suggestion = AutoSuggestion(
                user_id=user_id,
                input_text=input_text,
                suggestion=suggestion,
                suggestion_type=suggestion_type,
                confidence=confidence,
                context_data=context_data
            )
            
            db.add(auto_suggestion)
            db.commit()
            db.refresh(auto_suggestion)
            
            suggestion_id = auto_suggestion.id
            self.log(f"Suggestion saved with ID: {suggestion_id}")
            
            db.close()
            return suggestion_id
            
        except Exception as e:
            self.log(f"Error saving suggestion: {e}", level="error")
            return 0
    
    def _format_completion_response(self, suggestions: List[Dict], context: Dict[str, Any]) -> str:
        """Format completion suggestions response."""
        response = "✨ **پیشنهادات ادامه متن:**\n\n"
        
        completions = [s for s in suggestions if s["type"] == "continue"][:3]
        
        if completions:
            for i, suggestion in enumerate(completions, 1):
                confidence_percent = int(suggestion["confidence"] * 100)
                confidence_emoji = "🟢" if confidence_percent > 80 else "🟡" if confidence_percent > 60 else "🔵"
                
                response += f"**{i}.** {suggestion['text']}\n"
                response += f"   {confidence_emoji} اطمینان: {confidence_percent}% | 🔄 منبع: {suggestion.get('source', 'rule')}\n\n"
        else:
            response += "❌ **هیچ پیشنهاد ادامه‌ای یافت نشد.**\n\n"
        
        # Add context info
        if context.get("dominant_themes"):
            response += f"**🎯 موضوعات شناسایی شده:** {', '.join(context['dominant_themes'])}\n"
        
        response += "\n💡 **نکته:** پیشنهادات بر اساس زمینه و حافظه شما تولید شده‌اند."
        
        return response
    
    def _format_hints_response(self, hints: List[Dict], context: Dict[str, Any]) -> str:
        """Format hints response."""
        response = "🔮 **راهنماها و پیشنهادات:**\n\n"
        
        if hints:
            # Group by type
            hint_groups = {}
            for hint in hints:
                hint_type = hint["type"]
                if hint_type not in hint_groups:
                    hint_groups[hint_type] = []
                hint_groups[hint_type].append(hint)
            
            for hint_type, group_hints in hint_groups.items():
                type_label = self.suggestion_types.get(hint_type, hint_type)
                response += f"**📋 {type_label}:**\n"
                
                for hint in group_hints[:2]:  # Max 2 per type
                    confidence_percent = int(hint["confidence"] * 100)
                    response += f"• {hint['text']}\n"
                    response += f"  💪 اطمینان: {confidence_percent}%\n\n"
        else:
            response += "❌ **هیچ راهنمایی یافت نشد.**\n\n"
        
        response += "💡 **نکته:** راهنماها بر اساس تحلیل متن و الگوهای شما ارائه شده‌اند."
        
        return response
    
    def _format_comprehensive_response(self, suggestions: List[Dict], context: Dict[str, Any]) -> str:
        """Format comprehensive suggestions response."""
        response = "🚀 **پیشنهادات هوشمند:**\n\n"
        
        if suggestions:
            # Group by type
            suggestion_groups = {}
            for suggestion in suggestions:
                stype = suggestion["type"]
                if stype not in suggestion_groups:
                    suggestion_groups[stype] = []
                suggestion_groups[stype].append(suggestion)
            
            for stype, group_suggestions in suggestion_groups.items():
                type_label = self.suggestion_types.get(stype, stype)
                type_emoji = self._get_type_emoji(stype)
                
                response += f"**{type_emoji} {type_label}:**\n"
                
                for suggestion in group_suggestions[:2]:  # Max 2 per type
                    confidence_percent = int(suggestion["confidence"] * 100)
                    confidence_emoji = "🟢" if confidence_percent > 80 else "🟡" if confidence_percent > 60 else "🔵"
                    
                    response += f"• {suggestion['text']}\n"
                    response += f"  {confidence_emoji} اطمینان: {confidence_percent}% | 🔄 {suggestion.get('source', 'rule')}\n\n"
        else:
            response += "❌ **هیچ پیشنهادی یافت نشد.**\n\n"
        
        # Add context summary
        response += "**📊 تحلیل زمینه:**\n"
        response += f"• دسته‌بندی: {context.get('message_category', 'عمومی')}\n"
        response += f"• فوریت: {context.get('urgency_level', 'پایین')}\n"
        if context.get("dominant_themes"):
            response += f"• موضوعات: {', '.join(context['dominant_themes'])}\n"
        
        response += "\n💡 **نکته:** پیشنهادات بر اساس تحلیل جامع متن، حافظه، و الگوهای شما تولید شده‌اند."
        
        return response
    
    def _get_type_emoji(self, suggestion_type: str) -> str:
        """Get emoji for suggestion type."""
        type_emojis = {
            "continue": "➡️",
            "action": "⚡",
            "warning": "⚠️",
            "related": "🔗",
            "improvement": "📈",
            "question": "❓",
            "goal": "🎯",
            "reminder": "⏰"
        }
        return type_emojis.get(suggestion_type, "💭")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "تولید پیشنهادات ادامه متن",
            "ارائه راهنماهای زمینه‌ای",
            "تحلیل حافظه کوتاه‌مدت",
            "شناسایی موضوعات غالب",
            "ارزیابی فوریت پیام",
            "پیشنهادات هدف‌محور",
            "هشدارهای هوشمند",
            "ذخیره و بازیابی پیشنهادات"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for auto suggestions."""
        try:
            db = SessionLocal()
            
            total_suggestions = db.query(AutoSuggestion).count()
            recent_suggestions = db.query(AutoSuggestion).filter(
                AutoSuggestion.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
            ).count()
            
            # Get average confidence
            suggestions = db.query(AutoSuggestion).all()
            avg_confidence = sum(s.confidence for s in suggestions) / len(suggestions) if suggestions else 0
            
            # Count by type
            type_counts = {}
            for suggestion in suggestions:
                stype = suggestion.suggestion_type
                type_counts[stype] = type_counts.get(stype, 0) + 1
            
            db.close()
            
            return {
                "total_suggestions": total_suggestions,
                "recent_suggestions": recent_suggestions,
                "avg_confidence": round(avg_confidence, 2),
                "type_distribution": type_counts,
                "table_name": "auto_suggestions"
            }
            
        except Exception as e:
            self.log(f"Error getting database stats: {e}", level="error")
            return {
                "total_suggestions": 0,
                "recent_suggestions": 0,
                "avg_confidence": 0,
                "type_distribution": {},
                "error": str(e)
            }