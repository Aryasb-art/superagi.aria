"""
Goal Inference Agent for detecting intent and goals from user input using hybrid pattern + GPT analysis.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON, Float
from sqlalchemy.orm import sessionmaker

from .base_agent import BaseAgent
from database import Base, engine, SessionLocal


class GoalInference(Base):
    """Database model for storing goal inference results and their metadata."""
    __tablename__ = "goal_inferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    input_text = Column(Text, nullable=False)  # Original input text
    goal = Column(String(100), nullable=False)  # Detected goal
    intent_category = Column(String(50), nullable=False)  # Intent category
    confidence = Column(String(20), nullable=False)  # Confidence level: high/medium/low
    detected_by = Column(String(50), nullable=False)  # Detection method
    context_data = Column(JSON, nullable=False)  # Context used for analysis
    analysis_details = Column(JSON, nullable=False)  # Detailed analysis results
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GoalInferenceAgent(BaseAgent):
    """
    Goal Inference Agent that detects intent and goals from user input using
    hybrid pattern recognition and GPT analysis.
    """
    
    def __init__(self):
        super().__init__("GoalInferenceAgent", "ایجنت تشخیص هدف و نیت کاربر")
        self.log("Initialized with PostgreSQL database integration for goal inference storage")
        
        # Create table if it doesn't exist
        self._create_goal_inference_table()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        self._initialize_openai()
        
        # Goal categories with Persian labels
        self.goal_categories = {
            "action/initiation": "شروع/اقدام",
            "decision/choice": "تصمیم‌گیری/انتخاب",
            "concern/worry": "نگرانی/دغدغه",
            "motivation/energy": "انگیزه/انرژی",
            "confusion/help": "سردرگمی/کمک",
            "planning/organization": "برنامه‌ریزی/سازماندهی",
            "learning/knowledge": "یادگیری/دانش",
            "health/wellness": "سلامت/تندرستی",
            "relationship/social": "رابطه/اجتماعی",
            "career/work": "شغل/کار",
            "general/other": "عمومی/سایر"
        }
        
        # Pattern-based detection rules
        self.goal_patterns = {
            "action/initiation": {
                "keywords": ["شروع", "بزنم", "آغاز", "شروع کنم", "انجام", "اقدام", "عمل"],
                "phrases": ["می‌خواهم شروع", "باید شروع", "چطور شروع", "کجا شروع"],
                "confidence": "high"
            },
            "decision/choice": {
                "keywords": ["انتخاب", "تصمیم", "انتخاب کنم", "تصمیم بگیرم", "ترجیح", "بهتر"],
                "phrases": ["کدام انتخاب", "چه تصمیمی", "بهتر است", "کدام بهتر"],
                "confidence": "high"
            },
            "concern/worry": {
                "keywords": ["نگران", "نگرانی", "ترس", "دغدغه", "مشکل", "خطر"],
                "phrases": ["نگران هستم", "ترس دارم", "مشکل دارم", "نگرانم این"],
                "confidence": "high"
            },
            "motivation/energy": {
                "keywords": ["انگیزه", "انرژی", "حوصله", "دلگرمی", "امید", "رغبت"],
                "phrases": ["انگیزه ندارم", "حوصله ندارم", "انرژی ندارم", "دلم نمی‌خواهد"],
                "confidence": "high"
            },
            "confusion/help": {
                "keywords": ["سردرگم", "گیج", "نمی‌دانم", "کمک", "راهنمایی", "نمی‌فهمم"],
                "phrases": ["سردرگم هستم", "نمی‌دانم چطور", "کمک کنید", "راهنمایی کنید"],
                "confidence": "high"
            },
            "planning/organization": {
                "keywords": ["برنامه", "تنظیم", "سازمان", "زمان‌بندی", "ترتیب", "نظم"],
                "phrases": ["برنامه ریختن", "برنامه‌ریزی کنم", "سازمان دهم", "ترتیب دهم"],
                "confidence": "medium"
            },
            "learning/knowledge": {
                "keywords": ["یاد", "یادگیری", "آموزش", "مطالعه", "درس", "دانش"],
                "phrases": ["یاد بگیرم", "مطالعه کنم", "آموزش ببینم", "دانش کسب"],
                "confidence": "medium"
            },
            "health/wellness": {
                "keywords": ["سلامت", "ورزش", "رژیم", "تناسب", "تندرستی", "خواب"],
                "phrases": ["سالم باشم", "ورزش کنم", "رژیم بگیرم", "تناسب اندام"],
                "confidence": "medium"
            }
        }
        
        self.log("Goal inference patterns and categories initialized")
    
    def _create_goal_inference_table(self):
        """Create goal_inferences table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            self.log("Goal inferences table ready")
        except Exception as e:
            self.log(f"Error creating goal inferences table: {e}", level="error")
    
    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available."""
        try:
            import openai
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.log("OpenAI GPT integration ready for advanced goal inference")
            else:
                self.log("OpenAI API key not found, using pattern-based inference only")
        except ImportError:
            self.log("OpenAI library not available, using pattern-based inference only")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}, using pattern-based inference only")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process goal inference requests and generate response.
        
        Args:
            message (str): The message for goal inference analysis
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing inference results and metadata
        """
        try:
            self.log(f"Processing goal inference request: {message[:100]}...")
            
            # Remember the user message
            self.remember(message)
            
            # Perform goal inference analysis
            result = self._analyze_goal_and_intent(message, context)
            
            # Save to database if analysis successful
            if result.get("success", False):
                self._save_goal_inference(
                    context.get("user_id") if context else None,
                    message,
                    result["analysis"]
                )
            
            return {"response": result.get("response", "")}
                
        except Exception as e:
            self.log(f"Error processing goal inference request: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل هدف:** {str(e)}"
            }
    
    def _analyze_goal_and_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze goal and intent using hybrid pattern + GPT approach."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Step 1: Pattern-based analysis
            pattern_result = self._pattern_based_analysis(message)
            
            # Step 2: Get memory context for better understanding
            memory_context = self._get_memory_context(message)
            
            # Step 3: GPT-based analysis if patterns are inconclusive
            gpt_result = None
            if pattern_result["confidence"] != "high" and self.openai_client:
                gpt_result = self._gpt_based_analysis(message, memory_context)
            
            # Step 4: Combine results and determine final inference
            final_result = self._combine_analysis_results(pattern_result, gpt_result, memory_context)
            
            # Step 5: Format response
            response = self._format_goal_inference_response(final_result, message)
            
            return {
                "response": response,
                "analysis": final_result,
                "success": True,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error in goal and intent analysis: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل هدف و نیت:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _pattern_based_analysis(self, message: str) -> Dict[str, Any]:
        """Perform pattern-based goal detection."""
        message_lower = message.lower()
        detected_goals = []
        
        for category, patterns in self.goal_patterns.items():
            score = 0
            matched_keywords = []
            matched_phrases = []
            
            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in message_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Check phrases (weighted more heavily)
            for phrase in patterns["phrases"]:
                if phrase in message_lower:
                    score += 2
                    matched_phrases.append(phrase)
            
            if score > 0:
                confidence = "high" if score >= 2 else "medium" if score >= 1 else "low"
                detected_goals.append({
                    "category": category,
                    "score": score,
                    "confidence": confidence,
                    "matched_keywords": matched_keywords,
                    "matched_phrases": matched_phrases
                })
        
        # Sort by score and select best match
        detected_goals.sort(key=lambda x: x["score"], reverse=True)
        
        if detected_goals:
            best_match = detected_goals[0]
            return {
                "goal": self.goal_categories.get(best_match["category"], best_match["category"]),
                "intent_category": best_match["category"],
                "confidence": best_match["confidence"],
                "detected_by": "pattern",
                "pattern_details": best_match,
                "all_matches": detected_goals
            }
        else:
            return {
                "goal": "نامشخص",
                "intent_category": "general/other",
                "confidence": "low",
                "detected_by": "pattern",
                "pattern_details": {"score": 0, "matched_keywords": [], "matched_phrases": []},
                "all_matches": []
            }
    
    def _get_memory_context(self, message: str) -> Dict[str, Any]:
        """Get context from agent memories for better understanding."""
        context = {
            "short_term_memories": [],
            "recent_themes": [],
            "user_patterns": []
        }
        
        # Analyze short-term memory if available
        if hasattr(self, 'memory') and self.memory:
            recent_messages = list(self.memory)[-5:]  # Last 5 messages
            context["short_term_memories"] = recent_messages
            
            # Extract themes from recent messages
            all_text = " ".join(recent_messages + [message])
            context["recent_themes"] = self._extract_contextual_themes(all_text)
        
        return context
    
    def _extract_contextual_themes(self, text: str) -> List[str]:
        """Extract contextual themes from text."""
        themes = []
        text_lower = text.lower()
        
        theme_keywords = {
            "work": ["کار", "شغل", "پروژه", "وظیفه", "مسئولیت"],
            "health": ["سلامت", "ورزش", "رژیم", "تناسب", "خواب"],
            "learning": ["یاد", "آموزش", "مطالعه", "درس", "دانش"],
            "relationship": ["رابطه", "دوست", "خانواده", "همکار"],
            "personal": ["شخصی", "خودم", "زندگی", "احساس"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]  # Top 3 themes
    
    def _gpt_based_analysis(self, message: str, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform GPT-based goal and intent analysis."""
        try:
            prompt = f"""
            تحلیل هدف و نیت پشت این متن فارسی:
            
            متن: "{message}"
            
            زمینه: حافظه کوتاه‌مدت شامل {', '.join(memory_context.get('short_term_memories', [])[:3])}
            موضوعات اخیر: {', '.join(memory_context.get('recent_themes', []))}
            
            لطفاً هدف اصلی، دسته‌بندی نیت، و سطح اطمینان را مشخص کن.
            دسته‌بندی‌های ممکن: action/initiation, decision/choice, concern/worry, motivation/energy, confusion/help, planning/organization, learning/knowledge, health/wellness, relationship/social, career/work, general/other
            
            پاسخ را فقط در قالب JSON برگردان:
            {{
                "goal": "توضیح کوتاه هدف",
                "intent_category": "یکی از دسته‌بندی‌های بالا",
                "confidence": "high/medium/low",
                "reasoning": "دلیل تشخیص",
                "key_indicators": ["کلیدواژه‌های مهم"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["detected_by"] = "gpt"
            
            self.log(f"GPT analysis completed with confidence: {result.get('confidence', 'unknown')}")
            return result
            
        except Exception as e:
            self.log(f"GPT analysis failed: {e}")
            return {
                "goal": "تحلیل ناموفق",
                "intent_category": "general/other",
                "confidence": "low",
                "detected_by": "gpt_failed",
                "error": str(e)
            }
    
    def _combine_analysis_results(self, pattern_result: Dict, gpt_result: Optional[Dict], memory_context: Dict) -> Dict[str, Any]:
        """Combine pattern and GPT analysis results to determine final inference."""
        
        # If pattern analysis has high confidence, use it
        if pattern_result["confidence"] == "high":
            final_result = pattern_result.copy()
            final_result["detected_by"] = "pattern (high confidence)"
            
        # If GPT analysis available and pattern confidence is low/medium
        elif gpt_result and gpt_result.get("confidence") in ["high", "medium"]:
            # Use GPT result but mark as hybrid
            final_result = {
                "goal": gpt_result.get("goal", pattern_result["goal"]),
                "intent_category": gpt_result.get("intent_category", pattern_result["intent_category"]),
                "confidence": gpt_result.get("confidence", "medium"),
                "detected_by": "hybrid (pattern + GPT)",
                "gpt_details": gpt_result,
                "pattern_details": pattern_result.get("pattern_details", {})
            }
            
        # Fall back to pattern result
        else:
            final_result = pattern_result.copy()
            if gpt_result:
                final_result["detected_by"] = "hybrid (pattern primary)"
                final_result["gpt_details"] = gpt_result
            
        # Add memory context
        final_result["memory_context"] = memory_context
        final_result["analysis_timestamp"] = self._get_current_timestamp()
        
        return final_result
    
    def _format_goal_inference_response(self, analysis: Dict[str, Any], original_message: str) -> str:
        """Format the goal inference analysis response."""
        
        goal = analysis.get("goal", "نامشخص")
        intent_category = analysis.get("intent_category", "general/other")
        confidence = analysis.get("confidence", "low")
        detected_by = analysis.get("detected_by", "unknown")
        
        # Confidence emoji
        confidence_emoji = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🔴"
        
        # Category emoji
        category_emojis = {
            "action/initiation": "🚀",
            "decision/choice": "🤔",
            "concern/worry": "😟",
            "motivation/energy": "💪",
            "confusion/help": "❓",
            "planning/organization": "📋",
            "learning/knowledge": "📚",
            "health/wellness": "🏃‍♂️",
            "relationship/social": "👥",
            "career/work": "💼",
            "general/other": "💭"
        }
        
        category_emoji = category_emojis.get(intent_category, "💭")
        
        response = f"🎯 **تحلیل هدف و نیت:**\n\n"
        
        # Main analysis in JSON format
        json_result = {
            "goal": goal,
            "intent_category": intent_category,
            "confidence": confidence,
            "detected_by": detected_by
        }
        
        response += f"```json\n{json.dumps(json_result, ensure_ascii=False, indent=2)}\n```\n\n"
        
        # Detailed explanation
        response += f"**📊 جزئیات تحلیل:**\n"
        response += f"• {category_emoji} **هدف شناسایی شده:** {goal}\n"
        response += f"• 🏷️ **دسته‌بندی:** {self.goal_categories.get(intent_category, intent_category)}\n"
        response += f"• {confidence_emoji} **سطح اطمینان:** {confidence}\n"
        response += f"• 🔍 **روش تشخیص:** {detected_by}\n\n"
        
        # Pattern details if available
        if "pattern_details" in analysis:
            pattern = analysis["pattern_details"]
            if pattern.get("matched_keywords") or pattern.get("matched_phrases"):
                response += f"**🔤 کلیدواژه‌های تشخیص داده شده:**\n"
                if pattern.get("matched_keywords"):
                    response += f"• کلمات: {', '.join(pattern['matched_keywords'])}\n"
                if pattern.get("matched_phrases"):
                    response += f"• عبارات: {', '.join(pattern['matched_phrases'])}\n"
                response += "\n"
        
        # GPT reasoning if available
        if "gpt_details" in analysis and analysis["gpt_details"].get("reasoning"):
            response += f"**🤖 تحلیل GPT:** {analysis['gpt_details']['reasoning']}\n\n"
        
        # Memory context if available
        memory_ctx = analysis.get("memory_context", {})
        if memory_ctx.get("recent_themes"):
            response += f"**🧠 موضوعات حافظه:** {', '.join(memory_ctx['recent_themes'])}\n\n"
        
        response += "💡 **نکته:** این تحلیل بر اساس الگوها و زمینه پیام شما انجام شده است."
        
        return response
    
    def _save_goal_inference(self, user_id: Optional[int], input_text: str, analysis: Dict[str, Any]) -> int:
        """Save goal inference result to database."""
        try:
            db = SessionLocal()
            
            goal_inference = GoalInference(
                user_id=user_id,
                input_text=input_text,
                goal=analysis.get("goal", "نامشخص"),
                intent_category=analysis.get("intent_category", "general/other"),
                confidence=analysis.get("confidence", "low"),
                detected_by=analysis.get("detected_by", "unknown"),
                context_data=analysis.get("memory_context", {}),
                analysis_details=analysis
            )
            
            db.add(goal_inference)
            db.commit()
            db.refresh(goal_inference)
            
            inference_id = goal_inference.id
            self.log(f"Goal inference saved with ID: {inference_id}")
            
            db.close()
            return inference_id
            
        except Exception as e:
            self.log(f"Error saving goal inference: {e}", level="error")
            return 0
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "تشخیص هدف از متن",
            "تحلیل نیت کاربر", 
            "دسته‌بندی اهداف",
            "تحلیل ترکیبی (الگو + GPT)",
            "تحلیل زمینه حافظه",
            "خروجی JSON ساختاریافته",
            "ذخیره نتایج تحلیل",
            "ارزیابی سطح اطمینان"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for goal inferences."""
        try:
            db = SessionLocal()
            
            total_inferences = db.query(GoalInference).count()
            recent_inferences = db.query(GoalInference).filter(
                GoalInference.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
            ).count()
            
            # Count by confidence level
            confidence_counts = {}
            for level in ["high", "medium", "low"]:
                count = db.query(GoalInference).filter(GoalInference.confidence == level).count()
                confidence_counts[level] = count
            
            # Count by intent category
            category_counts = {}
            inferences = db.query(GoalInference).all()
            for inference in inferences:
                category = inference.intent_category
                category_counts[category] = category_counts.get(category, 0) + 1
            
            db.close()
            
            return {
                "total_inferences": total_inferences,
                "recent_inferences": recent_inferences,
                "confidence_distribution": confidence_counts,
                "category_distribution": category_counts,
                "table_name": "goal_inferences"
            }
            
        except Exception as e:
            self.log(f"Error getting database stats: {e}", level="error")
            return {
                "total_inferences": 0,
                "recent_inferences": 0,
                "confidence_distribution": {},
                "category_distribution": {},
                "error": str(e)
            }