"""
Emotion Regulation Agent for detecting and regulating user emotions during system interactions.
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


class EmotionalState(Base):
    """Database model for storing emotional states and regulation suggestions."""
    __tablename__ = "emotional_states"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    input_text = Column(Text, nullable=False)  # Original input text
    emotion_type = Column(String(50), nullable=False)  # Detected emotion
    intensity = Column(String(20), nullable=False)  # mild/moderate/intense
    suggestion = Column(Text, nullable=False)  # Regulation suggestion
    confidence = Column(String(20), nullable=False)  # Confidence level
    context_data = Column(JSON, nullable=False)  # Context used for analysis
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmotionRegulationAgent(BaseAgent):
    """
    Emotion Regulation Agent that detects emotions and provides regulation suggestions
    using hybrid pattern recognition and GPT analysis.
    """
    
    def __init__(self):
        super().__init__("EmotionRegulationAgent", "ایجنت تنظیم هیجانات و احساسات")
        self.log("Initialized with PostgreSQL database integration for emotional state storage")
        
        # Create table if it doesn't exist
        self._create_emotional_states_table()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        self._initialize_openai()
        
        # Emotion categories with Persian labels
        self.emotion_categories = {
            "anger": "خشم",
            "frustration": "استیصال", 
            "anxiety": "اضطراب",
            "excitement": "هیجان",
            "demotivation": "بی‌انگیزگی",
            "satisfaction": "رضایت",
            "happiness": "خوشحالی",
            "sadness": "غم",
            "confusion": "سردرگمی",
            "stress": "استرس",
            "fear": "ترس",
            "hope": "امید",
            "neutral": "خنثی"
        }
        
        # Intensity levels with Persian labels
        self.intensity_levels = {
            "mild": "خفیف",
            "moderate": "متوسط", 
            "intense": "شدید"
        }
        
        # Pattern-based emotion detection rules
        self.emotion_patterns = {
            "anger": {
                "keywords": ["عصبانی", "خشم", "کلافه", "دق", "حرص", "عصبی"],
                "phrases": ["عصبانی هستم", "حرصم میاد", "کلافه شدم", "دق کردم"],
                "intensity_indicators": {
                    "intense": ["خیلی عصبانی", "فوق‌العاده حرص", "بشدت کلافه"],
                    "moderate": ["عصبانی", "حرص", "کلافه"],
                    "mild": ["کمی عصبی", "نسبتا حرص"]
                }
            },
            "frustration": {
                "keywords": ["استیصال", "ناامید", "مأیوس", "بی‌نتیجه", "بی‌فایده"],
                "phrases": ["در استیصال", "ناامید شدم", "بی‌نتیجه است", "هیچ فایده‌ای ندارد"],
                "intensity_indicators": {
                    "intense": ["کاملا ناامید", "مأیوس تمام", "بی‌نتیجه محض"],
                    "moderate": ["ناامید", "استیصال", "مأیوس"],
                    "mild": ["کمی ناامید", "تا حدی بی‌نتیجه"]
                }
            },
            "anxiety": {
                "keywords": ["اضطراب", "نگران", "استرس", "ترس", "نگرانی"],
                "phrases": ["اضطراب دارم", "نگران هستم", "استرس دارم", "ترس می‌کنم"],
                "intensity_indicators": {
                    "intense": ["اضطراب شدید", "بسیار نگران", "پانیک"],
                    "moderate": ["اضطراب", "نگران", "استرس"],
                    "mild": ["کمی نگران", "اندکی استرس"]
                }
            },
            "excitement": {
                "keywords": ["هیجان", "شوق", "ذوق", "انرژی", "جوش"],
                "phrases": ["هیجان دارم", "شوق دارم", "ذوق کردم", "انرژی دارم"],
                "intensity_indicators": {
                    "intense": ["هیجان زیاد", "بسیار شوق", "فوق‌العاده ذوق"],
                    "moderate": ["هیجان", "شوق", "ذوق"],
                    "mild": ["کمی هیجان", "اندکی شوق"]
                }
            },
            "demotivation": {
                "keywords": ["بی‌انگیزه", "حوصله", "خسته", "کسل", "بی‌رمق"],
                "phrases": ["انگیزه ندارم", "حوصله ندارم", "خسته‌ام", "کسل شدم"],
                "intensity_indicators": {
                    "intense": ["کاملا بی‌انگیزه", "هیچ حوصله", "بسیار خسته"],
                    "moderate": ["بی‌انگیزه", "حوصله ندارم", "خسته"],
                    "mild": ["کمی بی‌حوصله", "اندکی خسته"]
                }
            },
            "happiness": {
                "keywords": ["خوشحال", "شاد", "خرسند", "مسرور", "خوش"],
                "phrases": ["خوشحال هستم", "شاد هستم", "خرسندم", "خوشم آمد"],
                "intensity_indicators": {
                    "intense": ["بسیار خوشحال", "فوق‌العاده شاد", "بی‌نهایت خرسند"],
                    "moderate": ["خوشحال", "شاد", "خرسند"],
                    "mild": ["کمی خوشحال", "نسبتا شاد"]
                }
            },
            "sadness": {
                "keywords": ["غمگین", "ناراحت", "افسرده", "محزون", "دلگیر"],
                "phrases": ["غمگین هستم", "ناراحت هستم", "افسرده‌ام", "دلم گرفته"],
                "intensity_indicators": {
                    "intense": ["بسیار غمگین", "شدیدا ناراحت", "عمیقا افسرده"],
                    "moderate": ["غمگین", "ناراحت", "افسرده"],
                    "mild": ["کمی غمگین", "اندکی ناراحت"]
                }
            }
        }
        
        # Regulation suggestions for each emotion
        self.regulation_suggestions = {
            "anger": {
                "mild": "چند نفس عمیق بکش و کمی صبر کن. گاهی فاصله گرفتن کمک می‌کند.",
                "moderate": "توقف کن و ۱۰ عدد بشمار. سعی کن دلیل عصبانیت‌ت را تحلیل کنی.",
                "intense": "حتما الان توقف کن! برو قدم بزن یا ورزش کن تا انرژی منفی تخلیه شود."
            },
            "frustration": {
                "mild": "شاید روش دیگری امتحان کنی. گاهی تغییر رویکرد راه‌حل است.",
                "moderate": "از کار فاصله بگیر و چیز دیگری انجام بده. بعدا با ذهن تازه برگرد.",
                "intense": "توقف کن و چند نفس عمیق بکش. شاید بهتر باشه چند دقیقه استراحت ذهنی داشته باشی."
            },
            "anxiety": {
                "mild": "تنفس آرام و منظم کن. یادت باشه که همه چیز درست می‌شود.",
                "moderate": "تکنیک ۵-۴-۳-۲-۱ رو امتحان کن: ۵ چیز ببین، ۴ صدا بشنو، ۳ چیز لمس کن.",
                "intense": "فورا جایی آرام بشین و تنفس عمیق کن. اگه نیاز داشتی با کسی صحبت کن."
            },
            "demotivation": {
                "mild": "یک هدف کوچک برای خودت تعریف کن و شروع کن. گاهی شروع سخت‌ترین قسمت است.",
                "moderate": "برو یه کار ساده انجام بده که احساس موفقیت بهت بده، بعد به کار اصلی برگرد.",
                "intense": "امروز خودت رو درگیر نکن. استراحت کن، ورزش کن یا کاری که دوست داری انجام بده."
            },
            "excitement": {
                "mild": "انرژی‌ت عالیه! از این فرصت استفاده کن و کارهای مهم رو پیش ببر.",
                "moderate": "هیجان‌ت رو به کار مفید تبدیل کن. چیزی که مدت‌هاست می‌خواستی انجام بدی.",
                "intense": "کمی آروم باش تا تصمیمات عجولانه نگیری. انرژی‌ت رو کانالیزه کن."
            },
            "happiness": {
                "mild": "از این حس خوب لذت ببر و سعی کن حفظش کنی.",
                "moderate": "عالیه! از این انرژی مثبت برای انجام کارهای مهم استفاده کن.",
                "intense": "حس فوق‌العاده‌ای داری! این فرصت رو از دست نده و کارهای چالشی رو شروع کن."
            },
            "sadness": {
                "mild": "اجازه بده این احساس باشه، ولی زیاد طولش نده. چیزی کوچک برای خودت انجام بده.",
                "moderate": "با کسی که دوستش داری صحبت کن یا کاری کن که حالت رو بهتر می‌کنه.",
                "intense": "الان وقت مراقبت از خودته. استراحت کن، آب بخور و در صورت نیاز کمک بگیر."
            }
        }
        
        self.log("Emotion detection patterns and regulation suggestions initialized")
    
    def _create_emotional_states_table(self):
        """Create emotional_states table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            self.log("Emotional states table ready")
        except Exception as e:
            self.log(f"Error creating emotional states table: {e}", level="error")
    
    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available."""
        try:
            import openai
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.log("OpenAI GPT integration ready for emotion analysis")
            else:
                self.log("OpenAI API key not found, using pattern-based emotion detection only")
        except ImportError:
            self.log("OpenAI library not available, using pattern-based emotion detection only")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}, using pattern-based emotion detection only")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process emotion regulation requests and generate response.
        
        Args:
            message (str): The message for emotion analysis
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing emotion analysis and regulation suggestions
        """
        try:
            self.log(f"Processing emotion regulation request: {message[:100]}...")
            
            # Remember the user message
            self.remember(message)
            
            # Perform emotion analysis
            result = self._analyze_emotion_and_suggest_regulation(message, context)
            
            # Save to database if analysis successful
            if result.get("success", False):
                self._save_emotional_state(
                    context.get("user_id") if context else None,
                    message,
                    result["analysis"]
                )
            
            return {"response": result.get("response", "")}
                
        except Exception as e:
            self.log(f"Error processing emotion regulation request: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل هیجان:** {str(e)}"
            }
    
    def _analyze_emotion_and_suggest_regulation(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze emotion and provide regulation suggestions using hybrid approach."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Step 1: Pattern-based emotion analysis
            pattern_result = self._pattern_based_emotion_analysis(message)
            
            # Step 2: Get memory context for better understanding
            memory_context = self._get_memory_context(message)
            
            # Step 3: GPT-based analysis if patterns are inconclusive
            gpt_result = None
            if pattern_result["confidence"] != "high" and self.openai_client:
                gpt_result = self._gpt_based_emotion_analysis(message, memory_context)
            
            # Step 4: Combine results and determine final emotion analysis
            final_result = self._combine_emotion_analysis_results(pattern_result, gpt_result, memory_context)
            
            # Step 5: Generate regulation suggestion
            regulation_suggestion = self._generate_regulation_suggestion(
                final_result["emotion"], 
                final_result["intensity"],
                memory_context
            )
            final_result["regulation_suggestion"] = regulation_suggestion
            
            # Step 6: Format response
            response = self._format_emotion_regulation_response(final_result, message)
            
            return {
                "response": response,
                "analysis": final_result,
                "success": True,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error in emotion analysis: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل هیجان:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _pattern_based_emotion_analysis(self, message: str) -> Dict[str, Any]:
        """Perform pattern-based emotion detection."""
        message_lower = message.lower()
        detected_emotions = []
        
        for emotion_type, patterns in self.emotion_patterns.items():
            score = 0
            matched_keywords = []
            matched_phrases = []
            detected_intensity = "mild"
            
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
            
            # Determine intensity based on matched patterns
            for intensity, indicators in patterns["intensity_indicators"].items():
                for indicator in indicators:
                    if indicator in message_lower:
                        detected_intensity = intensity
                        score += 1
                        break
            
            if score > 0:
                confidence = "high" if score >= 3 else "medium" if score >= 2 else "low"
                detected_emotions.append({
                    "emotion": emotion_type,
                    "score": score,
                    "intensity": detected_intensity,
                    "confidence": confidence,
                    "matched_keywords": matched_keywords,
                    "matched_phrases": matched_phrases
                })
        
        # Sort by score and select best match
        detected_emotions.sort(key=lambda x: x["score"], reverse=True)
        
        if detected_emotions:
            best_match = detected_emotions[0]
            return {
                "emotion": best_match["emotion"],
                "intensity": best_match["intensity"],
                "confidence": best_match["confidence"],
                "detected_by": "pattern",
                "pattern_details": best_match,
                "all_matches": detected_emotions
            }
        else:
            return {
                "emotion": "neutral",
                "intensity": "mild",
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
            "emotional_patterns": []
        }
        
        # Analyze short-term memory if available
        if hasattr(self, 'memory') and self.memory:
            recent_messages = list(self.memory)[-5:]  # Last 5 messages
            context["short_term_memories"] = recent_messages
            
            # Extract emotional themes from recent messages
            all_text = " ".join(recent_messages + [message])
            context["recent_themes"] = self._extract_emotional_themes(all_text)
            context["emotional_patterns"] = self._detect_emotional_patterns(recent_messages)
        
        return context
    
    def _extract_emotional_themes(self, text: str) -> List[str]:
        """Extract emotional themes from text."""
        themes = []
        text_lower = text.lower()
        
        theme_keywords = {
            "work_stress": ["کار", "پروژه", "وظیفه", "مسئولیت", "ددلاین"],
            "motivation": ["انگیزه", "هدف", "موفقیت", "پیشرفت"],
            "anxiety": ["نگرانی", "ترس", "اضطراب", "استرس"],
            "frustration": ["ناامیدی", "استیصال", "بی‌نتیجه", "کلافگی"],
            "happiness": ["خوشحالی", "شادی", "رضایت", "موفقیت"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]  # Top 3 themes
    
    def _detect_emotional_patterns(self, messages: List[str]) -> List[str]:
        """Detect emotional patterns in recent messages."""
        patterns = []
        
        if len(messages) >= 2:
            # Check for escalating negativity
            negative_words = ["بد", "ناراحت", "عصبی", "کلافه", "خسته"]
            negative_counts = [sum(1 for word in negative_words if word in msg.lower()) for msg in messages]
            
            if len(negative_counts) >= 2 and negative_counts[-1] > negative_counts[-2]:
                patterns.append("escalating_negativity")
            
            # Check for repeated frustration
            frustration_words = ["نمی‌تونم", "نمی‌شه", "مشکل", "بی‌فایده"]
            if sum(1 for msg in messages for word in frustration_words if word in msg.lower()) >= 2:
                patterns.append("repeated_frustration")
        
        return patterns
    
    def _gpt_based_emotion_analysis(self, message: str, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform GPT-based emotion analysis."""
        try:
            context_info = ""
            if memory_context.get("recent_themes"):
                context_info = f"موضوعات اخیر: {', '.join(memory_context['recent_themes'])}"
            if memory_context.get("emotional_patterns"):
                context_info += f"\nالگوهای احساسی: {', '.join(memory_context['emotional_patterns'])}"
            
            prompt = f"""
            تحلیل هیجان و احساس در این متن فارسی:
            
            متن: "{message}"
            
            زمینه: {context_info}
            
            لطفاً هیجان غالب، شدت آن، و پیشنهاد تنظیم هیجان ارائه بده.
            هیجانات ممکن: خشم، استیصال، اضطراب، هیجان، بی‌انگیزگی، رضایت، خوشحالی، غم، سردرگمی، استرس، ترس، امید، خنثی
            شدت: mild (خفیف), moderate (متوسط), intense (شدید)
            
            پاسخ را فقط در قالب JSON برگردان:
            {{
                "emotion": "نام هیجان",
                "intensity": "mild/moderate/intense", 
                "confidence": "high/medium/low",
                "reasoning": "دلیل تشخیص",
                "key_indicators": ["نشانگرهای کلیدی"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["detected_by"] = "gpt"
            
            self.log(f"GPT emotion analysis completed with confidence: {result.get('confidence', 'unknown')}")
            return result
            
        except Exception as e:
            self.log(f"GPT emotion analysis failed: {e}")
            return {
                "emotion": "neutral",
                "intensity": "mild",
                "confidence": "low",
                "detected_by": "gpt_failed",
                "error": str(e)
            }
    
    def _combine_emotion_analysis_results(self, pattern_result: Dict, gpt_result: Optional[Dict], memory_context: Dict) -> Dict[str, Any]:
        """Combine pattern and GPT analysis results to determine final emotion."""
        
        # If pattern analysis has high confidence, use it
        if pattern_result["confidence"] == "high":
            final_result = pattern_result.copy()
            final_result["detected_by"] = "pattern (high confidence)"
            
        # If GPT analysis available and pattern confidence is low/medium
        elif gpt_result and gpt_result.get("confidence") in ["high", "medium"]:
            # Map GPT emotion to our categories if needed
            gpt_emotion = gpt_result.get("emotion", "neutral")
            if gpt_emotion in self.emotion_categories.values():
                # Find the key for this Persian emotion
                for eng_key, persian_val in self.emotion_categories.items():
                    if persian_val == gpt_emotion:
                        gpt_emotion = eng_key
                        break
            
            final_result = {
                "emotion": gpt_emotion,
                "intensity": gpt_result.get("intensity", "mild"),
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
    
    def _generate_regulation_suggestion(self, emotion: str, intensity: str, memory_context: Dict[str, Any]) -> str:
        """Generate personalized regulation suggestion based on emotion and context."""
        
        # Get base suggestion from predefined patterns
        base_suggestion = self.regulation_suggestions.get(emotion, {}).get(intensity, 
            "چند نفس عمیق بکش و کمی استراحت کن. احساسات گذرا هستند.")
        
        # Customize based on memory context
        emotional_patterns = memory_context.get("emotional_patterns", [])
        
        if "escalating_negativity" in emotional_patterns:
            base_suggestion += " توجه: احساسات منفی‌ت در حال تشدید است. بهتر است فعلا از تصمیم‌گیری مهم خودداری کنی."
        
        if "repeated_frustration" in emotional_patterns:
            base_suggestion += " مکررا احساس ناامیدی داری. شاید وقت آن رسیده که رویکرد کلی‌ت را تغییر دهی."
        
        # Add goal-oriented suggestions for specific emotions
        if emotion in ["demotivation", "sadness"] and "work_stress" in memory_context.get("recent_themes", []):
            base_suggestion += " می‌تونی به بخش اهداف برو و یه هدف کوچک برای خودت تعریف کنی."
        
        return base_suggestion
    
    def _format_emotion_regulation_response(self, analysis: Dict[str, Any], original_message: str) -> str:
        """Format the emotion regulation analysis response."""
        
        emotion = analysis.get("emotion", "neutral")
        intensity = analysis.get("intensity", "mild")
        confidence = analysis.get("confidence", "low")
        regulation_suggestion = analysis.get("regulation_suggestion", "چند نفس عمیق بکش.")
        detected_by = analysis.get("detected_by", "unknown")
        
        # Get Persian labels
        emotion_persian = self.emotion_categories.get(emotion, emotion)
        intensity_persian = self.intensity_levels.get(intensity, intensity)
        
        # Confidence and intensity emojis
        confidence_emoji = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🔴"
        
        intensity_emoji = {"mild": "🔵", "moderate": "🟠", "intense": "🔴"}.get(intensity, "🔵")
        
        # Emotion emojis
        emotion_emojis = {
            "anger": "😠", "frustration": "😤", "anxiety": "😰", "excitement": "😄",
            "demotivation": "😕", "satisfaction": "😊", "happiness": "😁", 
            "sadness": "😢", "confusion": "😕", "stress": "😫", "fear": "😨",
            "hope": "🤗", "neutral": "😐"
        }
        emotion_emoji = emotion_emojis.get(emotion, "😐")
        
        response = f"💝 **تحلیل و تنظیم هیجان:**\n\n"
        
        # Main analysis in JSON format
        json_result = {
            "emotion": emotion_persian,
            "intensity": intensity,
            "regulation_suggestion": regulation_suggestion,
            "confidence": confidence
        }
        
        response += f"```json\n{json.dumps(json_result, ensure_ascii=False, indent=2)}\n```\n\n"
        
        # Detailed explanation
        response += f"**📊 جزئیات تحلیل:**\n"
        response += f"• {emotion_emoji} **هیجان شناسایی شده:** {emotion_persian}\n"
        response += f"• {intensity_emoji} **شدت:** {intensity_persian}\n"
        response += f"• {confidence_emoji} **سطح اطمینان:** {confidence}\n"
        response += f"• 🔍 **روش تشخیص:** {detected_by}\n\n"
        
        # Regulation suggestion
        response += f"**🎯 پیشنهاد تنظیم هیجان:**\n"
        response += f"💡 {regulation_suggestion}\n\n"
        
        # Pattern details if available
        if "pattern_details" in analysis:
            pattern = analysis["pattern_details"]
            if pattern.get("matched_keywords") or pattern.get("matched_phrases"):
                response += f"**🔍 نشانگرهای تشخیص داده شده:**\n"
                if pattern.get("matched_keywords"):
                    response += f"• کلمات: {', '.join(pattern['matched_keywords'])}\n"
                if pattern.get("matched_phrases"):
                    response += f"• عبارات: {', '.join(pattern['matched_phrases'])}\n"
                response += "\n"
        
        # GPT reasoning if available
        if "gpt_details" in analysis and analysis["gpt_details"].get("reasoning"):
            response += f"**🤖 تحلیل GPT:** {analysis['gpt_details']['reasoning']}\n\n"
        
        # Memory context warnings
        memory_ctx = analysis.get("memory_context", {})
        if memory_ctx.get("emotional_patterns"):
            response += f"**⚠️ الگوهای احساسی:** {', '.join(memory_ctx['emotional_patterns'])}\n\n"
        
        response += "💝 **نکته:** این تحلیل بر اساس محتوای پیام و الگوهای احساسی شما انجام شده است."
        
        return response
    
    def _save_emotional_state(self, user_id: Optional[int], input_text: str, analysis: Dict[str, Any]) -> int:
        """Save emotional state to database."""
        try:
            db = SessionLocal()
            
            emotional_state = EmotionalState(
                user_id=user_id,
                input_text=input_text,
                emotion_type=analysis.get("emotion", "neutral"),
                intensity=analysis.get("intensity", "mild"),
                suggestion=analysis.get("regulation_suggestion", "چند نفس عمیق بکش."),
                confidence=analysis.get("confidence", "low"),
                context_data=analysis.get("memory_context", {})
            )
            
            db.add(emotional_state)
            db.commit()
            db.refresh(emotional_state)
            
            state_id = emotional_state.id
            self.log(f"Emotional state saved with ID: {state_id}")
            
            db.close()
            return state_id
            
        except Exception as e:
            self.log(f"Error saving emotional state: {e}", level="error")
            return 0
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "تشخیص هیجان از متن",
            "تعیین شدت هیجان", 
            "پیشنهاد تنظیم هیجان",
            "تحلیل ترکیبی (الگو + GPT)",
            "تحلیل زمینه حافظه",
            "خروجی JSON ساختاریافته",
            "ذخیره وضعیت احساسی",
            "تشخیص الگوهای احساسی",
            "پیشنهادات شخصی‌سازی شده"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for emotional states."""
        try:
            db = SessionLocal()
            
            total_states = db.query(EmotionalState).count()
            recent_states = db.query(EmotionalState).filter(
                EmotionalState.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
            ).count()
            
            # Count by emotion type
            emotion_counts = {}
            states = db.query(EmotionalState).all()
            for state in states:
                emotion = state.emotion_type
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            # Count by intensity
            intensity_counts = {}
            for level in ["mild", "moderate", "intense"]:
                count = db.query(EmotionalState).filter(EmotionalState.intensity == level).count()
                intensity_counts[level] = count
            
            db.close()
            
            return {
                "total_states": total_states,
                "recent_states": recent_states,
                "emotion_distribution": emotion_counts,
                "intensity_distribution": intensity_counts,
                "table_name": "emotional_states"
            }
            
        except Exception as e:
            self.log(f"Error getting database stats: {e}", level="error")
            return {
                "total_states": 0,
                "recent_states": 0,
                "emotion_distribution": {},
                "intensity_distribution": {},
                "error": str(e)
            }