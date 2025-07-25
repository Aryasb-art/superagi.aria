"""
Aria Emotion Agent - Advanced emotion detection and regulation agent.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
from database import get_db
from sqlalchemy.orm import Session
from ..base_agent import BaseAgent
from sqlalchemy import text


class AriaEmotionAgent(BaseAgent):
    """
    Advanced emotion detection and regulation agent with therapeutic suggestions.
    Combines pattern recognition with OpenAI GPT for comprehensive emotional analysis.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "agent_config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            agent_config = yaml.safe_load(f)
        
        super().__init__(
            name="AriaEmotionAgent",
            description="Advanced emotion detection and regulation agent with therapeutic suggestions",
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
                self.log("OpenAI GPT integration ready for emotion analysis")
            else:
                self.log("OpenAI API key not found, using pattern-based analysis", "warning")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}", "error")
            self.openai_available = False
        
        # Initialize database
        self._initialize_database()
        
        # Load configuration
        self.emotion_types = self.config.get("emotion_types", [])
        self.intensity_levels = self.config.get("intensity_levels", [])
        
        # Emotion detection patterns
        self.emotion_patterns = {
            "خشم": ["angry", "mad", "furious", "عصبانی", "خشمگین", "عصبانیت"],
            "استیصال": ["hopeless", "despair", "مأیوس", "ناامید", "استیصال"],
            "اضطراب": ["anxious", "nervous", "worried", "مضطرب", "نگران", "اضطراب"],
            "هیجان": ["excited", "thrilled", "هیجان", "هیجان‌زده", "شوق"],
            "بی‌انگیزگی": ["unmotivated", "lazy", "بی‌انگیزه", "بی‌حوصله", "کسل"],
            "رضایت": ["satisfied", "content", "راضی", "خشنود", "رضایت"],
            "خوشحالی": ["happy", "joyful", "خوشحال", "شاد", "خوشحالی"],
            "غم": ["sad", "depressed", "غمگین", "افسرده", "غم"],
            "سردرگمی": ["confused", "puzzled", "گیج", "سردرگم", "مبهوت"],
            "استرس": ["stressed", "pressure", "استرس", "فشار", "تنش"],
            "ترس": ["scared", "afraid", "ترسیده", "هراسان", "ترس"],
            "امید": ["hopeful", "optimistic", "امیدوار", "خوش‌بین", "امید"],
            "خنثی": ["neutral", "okay", "عادی", "خنثی", "معمولی"]
        }
        
        self.regulation_suggestions = {
            "خشم": [
                "🌬️ تنفس عمیق: ۱۰ بار نفس آهسته بکشید",
                "🚶 پیاده‌روی: حداقل ۱۰ دقیقه راه بروید",
                "✍️ نوشتن: احساساتتان را روی کاغذ بنویسید"
            ],
            "استیصال": [
                "📞 تماس: با دوست یا خانواده صحبت کنید",
                "🎯 هدف کوچک: یک کار ساده انجام دهید",
                "💡 کمک: از متخصص یا مشاور کمک بگیرید"
            ],
            "اضطراب": [
                "🧘 مدیتیشن: ۵ دقیقه آرام‌سازی",
                "📝 لیست: نگرانی‌هایتان را بنویسید",
                "🎵 موسیقی: موسیقی آرام‌بخش گوش کنید"
            ]
        }
        
        self.log("Emotion regulation agent initialized with therapeutic suggestions")
    
    def _initialize_database(self):
        """Initialize database table for emotional states"""
        try:
            db = next(get_db())
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS emotional_states (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER DEFAULT 1,
                    input_text TEXT NOT NULL,
                    emotion_type VARCHAR(50),
                    intensity VARCHAR(20),
                    suggestion TEXT,
                    confidence FLOAT,
                    context_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
            self.log("Emotional states table ready")
        except Exception as e:
            self.log(f"Database initialization error: {e}", "error")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze message for emotion detection and provide regulation suggestions.
        
        Args:
            message (str): The message to analyze
            context (Dict): Optional context information
            
        Returns:
            Dict: Response with emotion analysis and regulation suggestions
        """
        try:
            # Store in memory
            self.remember(f"User: {message}")
            
            # Perform emotion analysis
            analysis_result = self._analyze_emotion(message, context)
            
            # Generate regulation suggestions
            suggestions = self._generate_regulation_suggestions(analysis_result)
            
            # Store in database
            self._store_emotional_state(message, analysis_result, suggestions, context)
            
            # Format response
            response_content = self._format_emotion_response(analysis_result, suggestions)
            
            response = {
                "response_id": f"{self.agent_id}_{hash(message) % 100000}",
                "content": response_content,
                "emotion_analysis": analysis_result,
                "regulation_suggestions": suggestions,
                "handled_by": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "openai_used": self.openai_available,
                "error": None
            }
            
            self.remember(f"Agent: {response_content}")
            self.log(f"Emotion analysis: {analysis_result.get('emotion_type', 'unknown')} - {analysis_result.get('intensity', 'unknown')}")
            
            return response
            
        except Exception as e:
            error_response = {
                "response_id": f"error_{hash(str(e)) % 100000}",
                "content": f"خطا در تحلیل احساسات: {str(e)}",
                "handled_by": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "openai_used": False,
                "error": str(e)
            }
            
            self.log(f"Error in emotion analysis: {e}", "error")
            return error_response
    
    def _analyze_emotion(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze emotion using hybrid approach"""
        # Try pattern-based analysis first
        pattern_result = self._pattern_based_emotion_detection(message)
        
        # If OpenAI is available, use it for better accuracy
        if self.openai_available:
            openai_result = self._openai_emotion_analysis(message, context)
            # Combine results, preferring OpenAI for accuracy
            return {
                **openai_result,
                "pattern_result": pattern_result,
                "analysis_method": "hybrid"
            }
        
        # Fallback to pattern-based result
        return {
            **pattern_result,
            "analysis_method": "pattern_based"
        }
    
    def _pattern_based_emotion_detection(self, message: str) -> Dict[str, Any]:
        """Pattern-based emotion detection"""
        message_lower = message.lower()
        
        # Score each emotion type
        emotion_scores = {}
        for emotion, patterns in self.emotion_patterns.items():
            score = sum(1 for pattern in patterns if pattern in message_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            # Get dominant emotion
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            score = emotion_scores[dominant_emotion]
            
            # Determine intensity based on score and length
            if score >= 3 or len(message) > 100:
                intensity = "شدید"
            elif score >= 2:
                intensity = "متوسط"
            else:
                intensity = "خفیف"
            
            confidence = min(score * 0.3, 1.0)
            
            return {
                "emotion_type": dominant_emotion,
                "intensity": intensity,
                "confidence": confidence,
                "emotion_scores": emotion_scores,
                "detected_by": "pattern"
            }
        
        # Default to neutral
        return {
            "emotion_type": "خنثی",
            "intensity": "خفیف",
            "confidence": 0.5,
            "emotion_scores": {},
            "detected_by": "pattern"
        }
    
    def _openai_emotion_analysis(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """OpenAI-powered emotion analysis"""
        try:
            system_prompt = f"""
            You are an expert in emotional analysis. Analyze the user's message and provide:
            1. Primary emotion type from: {', '.join(self.emotion_types)}
            2. Intensity level from: {', '.join(self.intensity_levels)}
            3. Confidence score (0-1)
            4. Brief reasoning
            
            Respond in JSON format:
            {{
                "emotion_type": "emotion in Persian",
                "intensity": "intensity in Persian",
                "confidence": 0.85,
                "reasoning": "brief explanation in Persian"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.config.get("openai", {}).get("model", "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=self.config.get("openai", {}).get("max_tokens", 600),
                temperature=self.config.get("openai", {}).get("temperature", 0.3),
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "emotion_type": result.get("emotion_type", "خنثی"),
                "intensity": result.get("intensity", "خفیف"),
                "confidence": result.get("confidence", 0.5),
                "reasoning": result.get("reasoning", ""),
                "detected_by": "openai"
            }
            
        except Exception as e:
            self.log(f"OpenAI emotion analysis error: {e}", "error")
            return self._pattern_based_emotion_detection(message)
    
    def _generate_regulation_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate emotion regulation suggestions"""
        emotion_type = analysis.get("emotion_type", "خنثی")
        intensity = analysis.get("intensity", "خفیف")
        
        # Get base suggestions for emotion type
        base_suggestions = self.regulation_suggestions.get(emotion_type, [
            "🧘 آرامش: چند دقیقه استراحت کنید",
            "💭 تأمل: در مورد احساساتتان فکر کنید",
            "📝 نوشتن: احساساتتان را یادداشت کنید"
        ])
        
        # Adjust based on intensity
        if intensity == "شدید":
            urgent_suggestions = [
                "🚨 فوری: اگر احساس خطر می‌کنید، با متخصص تماس بگیرید",
                "🏃 حرکت: فعالیت بدنی انجام دهید",
                "🧘 تنفس: تکنیک‌های تنفس عمیق استفاده کنید"
            ]
            return urgent_suggestions + base_suggestions[:2]
        elif intensity == "متوسط":
            return base_suggestions
        else:
            gentle_suggestions = [
                "☕ استراحت: یک فنجان چای یا نوشیدنی آرام‌بخش بنوشید",
                "🌱 طبیعت: چند دقیقه در فضای باز بگذرانید",
                "📚 خواندن: چیزی آرام‌بخش بخوانید"
            ]
            return gentle_suggestions + base_suggestions[:1]
    
    def _store_emotional_state(self, message: str, analysis: Dict[str, Any], suggestions: List[str], context: Optional[Dict[str, Any]] = None):
        """Store emotional state in database"""
        try:
            user_id = context.get("user_id", 1) if context else 1
            
            db = next(get_db())
            db.execute(text("""
                INSERT INTO emotional_states (
                    user_id, input_text, emotion_type, intensity, suggestion, 
                    confidence, context_data, created_at
                ) VALUES (
                    :user_id, :input_text, :emotion_type, :intensity, :suggestion,
                    :confidence, :context_data, :created_at
                )
            """), {
                "user_id": user_id,
                "input_text": message,
                "emotion_type": analysis.get("emotion_type", ""),
                "intensity": analysis.get("intensity", ""),
                "suggestion": '\n'.join(suggestions),
                "confidence": analysis.get("confidence", 0.5),
                "context_data": json.dumps(context or {}),
                "created_at": datetime.utcnow()
            })
            db.commit()
            
            self.log("Emotional state stored in database")
            
        except Exception as e:
            self.log(f"Database storage error: {e}", "error")
    
    def _format_emotion_response(self, analysis: Dict[str, Any], suggestions: List[str]) -> str:
        """Format emotion analysis response"""
        emotion_emojis = {
            "خشم": "😠",
            "استیصال": "😞",
            "اضطراب": "😰",
            "هیجان": "🤩",
            "بی‌انگیزگی": "😴",
            "رضایت": "😊",
            "خوشحالی": "😄",
            "غم": "😢",
            "سردرگمی": "😕",
            "استرس": "😓",
            "ترس": "😨",
            "امید": "😌",
            "خنثی": "😐"
        }
        
        intensity_emojis = {
            "شدید": "🔴",
            "متوسط": "🟡",
            "خفیف": "🟢"
        }
        
        emotion_emoji = emotion_emojis.get(analysis.get("emotion_type", "خنثی"), "😐")
        intensity_emoji = intensity_emojis.get(analysis.get("intensity", "خفیف"), "🟢")
        
        response = f"🎭 **تحلیل احساسات**\n\n"
        response += f"**{emotion_emoji} احساس:** {analysis.get('emotion_type', 'نامشخص')}\n"
        response += f"**{intensity_emoji} شدت:** {analysis.get('intensity', 'نامشخص')}\n"
        response += f"**📊 اطمینان:** {analysis.get('confidence', 0.5):.1f}\n\n"
        
        if analysis.get("reasoning"):
            response += f"**💭 تحلیل:** {analysis['reasoning']}\n\n"
        
        response += "**💡 پیشنهادات تنظیم احساسات:**\n"
        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. {suggestion}\n"
        
        return response
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "supported_emotions": self.emotion_types,
            "intensity_levels": self.intensity_levels,
            "regulation_suggestions": True,
            "therapeutic_support": True,
            "openai_available": self.openai_available,
            "database_storage": True
        }