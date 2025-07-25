"""
CognitiveDistortionAgent - Cognitive distortion detection and analysis agent.
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque

from openai import OpenAI
from sqlalchemy import create_engine, Column, String, Float, Text, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from agents.base_agent import BaseAgent
from database import SessionLocal, Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database model for cognitive distortion logs
class CognitiveDistortionLog(Base):
    __tablename__ = 'cognitive_distortion_logs'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_text = Column(Text)
    detected_types = Column(Text)  # JSON string of detected distortions
    severity_score = Column(Float)
    recommendation = Column(Text)
    related_emotion = Column(Text)
    related_goal = Column(Text)

# Create tables
Base.metadata.create_all(bind=engine)

class CognitiveDistortionAgent(BaseAgent):
    """
    Advanced cognitive distortion detection and analysis agent.
    Detects and analyzes common cognitive distortions in user input.
    """
    
    def __init__(self):
        super().__init__("CognitiveDistortionAgent")
        self.description = "Cognitive distortion detection and analysis agent"
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        # Supported cognitive distortions with patterns
        self.distortion_patterns = {
            'all_or_nothing': {
                'keywords': ['always', 'never', 'completely', 'totally', 'entirely', 'absolutely', 'perfect', 'failure', 'ruined'],
                'phrases': ['always happens', 'never works', 'complete failure', 'total disaster', 'perfectly fine', 'entirely wrong'],
                'persian_name': 'تفکر همه یا هیچ',
                'description': 'دیدن موقعیت‌ها در دو قطب افراطی بدون در نظر گیری حالت‌های میانی'
            },
            'overgeneralization': {
                'keywords': ['everyone', 'nobody', 'everything', 'nothing', 'all', 'none', 'typical', 'usual'],
                'phrases': ['this always happens', 'nobody likes me', 'everything goes wrong', 'nothing works', 'all the time'],
                'persian_name': 'تعمیم افراطی',
                'description': 'نتیجه‌گیری کلی بر اساس یک واقعه منفرد'
            },
            'catastrophizing': {
                'keywords': ['disaster', 'terrible', 'awful', 'horrible', 'worst', 'catastrophe', 'ruined', 'destroyed'],
                'phrases': ['this is terrible', 'worst thing ever', 'complete disaster', 'everything is ruined', 'awful situation'],
                'persian_name': 'فاجعه‌سازی',
                'description': 'بزرگ‌نمایی منفی موقعیت‌ها و تصور بدترین حالت ممکن'
            },
            'labeling': {
                'keywords': ['I am', 'he is', 'she is', 'they are', 'stupid', 'idiot', 'loser', 'failure', 'worthless'],
                'phrases': ['I am stupid', 'I am a failure', 'I am worthless', 'he is an idiot', 'she is useless'],
                'persian_name': 'برچسب‌زدن',
                'description': 'نامیدن خود یا دیگران با صفات منفی به جای توصیف رفتار'
            },
            'personalization': {
                'keywords': ['my fault', 'because of me', 'I caused', 'I should have', 'my responsibility'],
                'phrases': ['it\'s my fault', 'because of me', 'I caused this', 'I should have prevented', 'my responsibility'],
                'persian_name': 'شخصی‌سازی',
                'description': 'مسئول دانستن خود برای رویدادهای منفی که کنترل کاملی روی آن‌ها ندارید'
            },
            'mind_reading': {
                'keywords': ['he thinks', 'she thinks', 'they think', 'probably thinks', 'must think', 'obviously thinks'],
                'phrases': ['he thinks I am', 'she probably thinks', 'they must think', 'obviously thinks', 'I know what they think'],
                'persian_name': 'ذهن‌خوانی',
                'description': 'فرض کردن که می‌دانید دیگران چه فکر می‌کنند بدون شواهد'
            },
            'emotional_reasoning': {
                'keywords': ['I feel', 'feels like', 'I sense', 'seems like', 'appears that', 'must be true'],
                'phrases': ['I feel stupid so I must be', 'feels like nobody cares', 'seems like I\'m worthless', 'appears that I failed'],
                'persian_name': 'استدلال عاطفی',
                'description': 'باور به این که احساسات شما حقیقت را منعکس می‌کنند'
            },
            'filtering': {
                'keywords': ['only', 'just', 'except', 'but', 'however', 'although', 'despite', 'ignore'],
                'phrases': ['only bad things', 'just the negative', 'except for failures', 'but the problems', 'ignore the good'],
                'persian_name': 'فیلتر کردن',
                'description': 'تمرکز منحصر بر جنبه‌های منفی و نادیده گرفتن مثبت‌ها'
            },
            'blaming': {
                'keywords': ['because of', 'fault of', 'blame', 'caused by', 'responsible for', 'due to'],
                'phrases': ['because of them', 'fault of others', 'they are to blame', 'caused by circumstances', 'not my fault'],
                'persian_name': 'سرزنش',
                'description': 'مسئول دانستن دیگران یا شرایط برای مشکلات شخصی'
            },
            'fortune_telling': {
                'keywords': ['will happen', 'going to', 'will be', 'definitely will', 'certainly will', 'bound to'],
                'phrases': ['will definitely fail', 'going to be terrible', 'will never work', 'bound to go wrong', 'certainly will happen'],
                'persian_name': 'پیشگویی',
                'description': 'پیش‌بینی منفی آینده بدون شواهد کافی'
            }
        }
        
        logger.info(f"[{self.name}] Cognitive distortion detection patterns and analysis framework initialized")
        
        # Initialize database
        self._init_database()
        
        logger.info(f"[{self.name}] OpenAI GPT integration ready for distortion analysis")
        logger.info(f"[{self.name}] Initialized with PostgreSQL database integration for distortion tracking")
    
    def _init_database(self):
        """Initialize database tables for distortion logging"""
        try:
            # Create tables if they don't exist
            Base.metadata.create_all(bind=engine)
            logger.info(f"[{self.name}] Cognitive distortion logs table ready")
        except Exception as e:
            logger.error(f"[{self.name}] Database initialization failed: {e}")
    
    def _detect_distortion_patterns(self, text: str) -> Dict[str, Any]:
        """
        Detect cognitive distortions using pattern matching.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: Detected distortions with scores
        """
        detected_distortions = []
        severity_scores = []
        
        text_lower = text.lower()
        
        for distortion_type, pattern_info in self.distortion_patterns.items():
            score = 0.0
            matches = 0
            
            # Check keywords
            for keyword in pattern_info['keywords']:
                if keyword.lower() in text_lower:
                    score += 0.1
                    matches += 1
            
            # Check phrases (higher weight)
            for phrase in pattern_info['phrases']:
                if phrase.lower() in text_lower:
                    score += 0.3
                    matches += 1
            
            # Calculate final score
            if matches > 0:
                final_score = min(score, 1.0)
                if final_score >= 0.3:  # Minimum threshold
                    detected_distortions.append(distortion_type)
                    severity_scores.append(final_score)
        
        return {
            'detected_distortions': detected_distortions,
            'severity_scores': severity_scores,
            'method': 'pattern_matching'
        }
    
    def _analyze_distortion_with_gpt(self, text: str) -> Dict[str, Any]:
        """
        Analyze cognitive distortions using OpenAI GPT-4o.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: GPT analysis results
        """
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """شما یک تحلیلگر تخصصی تحریف‌های شناختی هستید. متن ورودی را تحلیل کنید و تحریف‌های شناختی احتمالی را شناسایی کنید.

تحریف‌های قابل تشخیص:
- all_or_nothing: تفکر همه یا هیچ
- overgeneralization: تعمیم افراطی
- catastrophizing: فاجعه‌سازی
- labeling: برچسب‌زدن
- personalization: شخصی‌سازی
- mind_reading: ذهن‌خوانی
- emotional_reasoning: استدلال عاطفی
- filtering: فیلتر کردن
- blaming: سرزنش
- fortune_telling: پیشگویی

پاسخ را در قالب JSON ارائه دهید:
{
  "distortion_detected": true/false,
  "detected_types": ["distortion1", "distortion2", ...],
  "severity_score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "reasoning": "دلیل تشخیص",
  "recommendation": "پیشنهاد بازسازی شناختی",
  "related_emotion": "احساس مرتبط",
  "related_goal": "هدف مرتبط"
}"""
                    },
                    {
                        "role": "user",
                        "content": f"متن برای تحلیل: {text}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'detected_distortions': result.get('detected_types', []),
                'severity_score': result.get('severity_score', 0.0),
                'confidence': result.get('confidence', 0.0),
                'reasoning': result.get('reasoning', ''),
                'recommendation': result.get('recommendation', ''),
                'related_emotion': result.get('related_emotion', ''),
                'related_goal': result.get('related_goal', ''),
                'method': 'gpt_analysis'
            }
        except Exception as e:
            logger.error(f"[{self.name}] GPT analysis failed: {e}")
            return {
                'detected_distortions': [],
                'severity_score': 0.0,
                'confidence': 0.0,
                'reasoning': 'تحلیل GPT ناموفق بود',
                'recommendation': 'لطفاً دوباره تلاش کنید',
                'related_emotion': '',
                'related_goal': '',
                'method': 'gpt_failed'
            }
    
    def _generate_reframing_suggestion(self, distortion_types: List[str], severity: float, related_emotion: str = '', related_goal: str = '') -> str:
        """
        Generate a cognitive reframing suggestion based on detected distortions.
        
        Args:
            distortion_types (List[str]): List of detected distortion types
            severity (float): Severity score
            related_emotion (str): Related emotion if detected
            related_goal (str): Related goal if detected
            
        Returns:
            str: Reframing suggestion
        """
        if not distortion_types:
            return "فکر شما متعادل به نظر می‌رسد. ادامه دهید!"
        
        # Base suggestions for each distortion type
        suggestions = {
            'all_or_nothing': "آیا واقعاً فقط دو حالت وجود دارد؟ حالت‌های میانی را در نظر بگیرید.",
            'overgeneralization': "آیا این همیشه اتفاق می‌افتد؟ شواهد مخالف را بررسی کنید.",
            'catastrophizing': "آیا واقعاً بدترین حالت ممکن است؟ احتمالات دیگر را در نظر بگیرید.",
            'labeling': "به جای برچسب‌زدن، رفتار خاص را توصیف کنید.",
            'personalization': "آیا واقعاً همه چیز مسئولیت شماست؟ عوامل دیگر را در نظر بگیرید.",
            'mind_reading': "آیا واقعاً می‌دانید دیگران چه فکر می‌کنند؟ شواهد مستقیم بخواهید.",
            'emotional_reasoning': "احساسات شما واقعی هستند، اما لزوماً واقعیت را منعکس نمی‌کنند.",
            'filtering': "جنبه‌های مثبت و منفی را به طور متعادل بررسی کنید.",
            'blaming': "تمرکز بر آنچه می‌توانید کنترل کنید، نه سرزنش دیگران.",
            'fortune_telling': "آیا واقعاً می‌توانید آینده را پیش‌بینی کنید؟ شواهد موجود را بررسی کنید."
        }
        
        # Get primary suggestion
        primary_distortion = distortion_types[0]
        suggestion = suggestions.get(primary_distortion, "سعی کنید فکر خود را از زاویه دیگری بررسی کنید.")
        
        # Add severity-based advice
        if severity >= 0.7:
            suggestion = f"⚠️ **{self.distortion_patterns[primary_distortion]['persian_name']}** تأثیر قابل توجهی دارد. {suggestion}"
        elif severity >= 0.4:
            suggestion = f"📝 **{self.distortion_patterns[primary_distortion]['persian_name']}** ممکن است وجود داشته باشد. {suggestion}"
        else:
            suggestion = f"ℹ️ **{self.distortion_patterns[primary_distortion]['persian_name']}** خفیف شناسایی شد. {suggestion}"
        
        # Add emotional context if available
        if related_emotion:
            suggestion += f"\n\n**احساس مرتبط:** {related_emotion}"
        
        if related_goal:
            suggestion += f"\n**هدف مرتبط:** {related_goal}"
        
        return suggestion
    
    def analyze_distortion(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for cognitive distortions using hybrid approach.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: Distortion analysis results
        """
        if not text or len(text.strip()) < 10:
            return {
                'detected_types': [],
                'severity_score': 0.0,
                'recommendation': 'لطفاً متن بیشتری وارد کنید',
                'related_emotion': '',
                'related_goal': '',
                'confidence': 0.0,
                'reasoning': 'متن ورودی کافی نیست',
                'log_id': None
            }
        
        self.remember(f"Distortion analysis for: {text[:50]}...")
        
        # Try GPT analysis first
        gpt_result = self._analyze_distortion_with_gpt(text)
        
        # Fallback to pattern matching if GPT fails
        if gpt_result['method'] == 'gpt_failed':
            pattern_result = self._detect_distortion_patterns(text)
            distortion_types = pattern_result['detected_distortions']
            severity = max(pattern_result['severity_scores']) if pattern_result['severity_scores'] else 0.0
            confidence = 0.6  # Pattern matching confidence
            reasoning = 'تحلیل بر اساس الگوهای از پیش تعریف شده'
            related_emotion = ''
            related_goal = ''
        else:
            distortion_types = gpt_result['detected_distortions']
            severity = gpt_result['severity_score']
            confidence = gpt_result['confidence']
            reasoning = gpt_result['reasoning']
            related_emotion = gpt_result['related_emotion']
            related_goal = gpt_result['related_goal']
        
        # Generate reframing suggestion
        suggestion = self._generate_reframing_suggestion(
            distortion_types, severity, related_emotion, related_goal
        )
        
        # Save to database
        distortion_log_id = str(uuid.uuid4())
        detected_types_str = ', '.join(distortion_types) if distortion_types else ''
        
        # Only save if there are actual distortions detected or if severity > 0
        if detected_types_str or severity > 0:
            self._save_distortion_log(
                distortion_log_id, text, detected_types_str, severity, 
                suggestion, related_emotion, related_goal
            )
        
        self.remember(f"Distortion analysis completed: {len(distortion_types)} distortions detected with {severity:.2f} severity")
        
        return {
            'detected_types': distortion_types,
            'severity_score': severity,
            'recommendation': suggestion,
            'related_emotion': related_emotion,
            'related_goal': related_goal,
            'confidence': confidence,
            'reasoning': reasoning,
            'log_id': distortion_log_id
        }
    
    def _save_distortion_log(self, log_id: str, input_text: str, detected_types_str: str, 
                           severity: float, suggestion: str, related_emotion: str, related_goal: str):
        """Save distortion analysis to database"""
        try:
            session = SessionLocal()
            
            distortion_log = CognitiveDistortionLog(
                id=log_id,
                timestamp=datetime.utcnow(),
                input_text=input_text,
                detected_types=detected_types_str,
                severity_score=severity,
                recommendation=suggestion,
                related_emotion=related_emotion,
                related_goal=related_goal
            )
            
            session.add(distortion_log)
            session.commit()
            session.close()
            
            logger.info(f"[{self.name}] Distortion log saved with ID: {log_id}")
        except Exception as e:
            logger.error(f"[{self.name}] Failed to save distortion log: {e}")
    
    def get_distortion_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent distortion analysis logs.
        
        Args:
            limit (int): Number of logs to retrieve
            
        Returns:
            List[Dict]: Recent distortion logs
        """
        try:
            session = SessionLocal()
            
            logs = session.query(CognitiveDistortionLog).order_by(CognitiveDistortionLog.timestamp.desc()).limit(limit).all()
            
            result = []
            for log in logs:
                # Convert comma-separated string back to list for display
                detected_types_list = log.detected_types.split(', ') if log.detected_types else []
                result.append({
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat(),
                    'input_text': log.input_text,
                    'detected_types': detected_types_list,
                    'severity_score': log.severity_score,
                    'recommendation': log.recommendation,
                    'related_emotion': log.related_emotion,
                    'related_goal': log.related_goal
                })
            
            session.close()
            return result
        except Exception as e:
            logger.error(f"[{self.name}] Failed to get distortion logs: {e}")
            return []
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process message and analyze for cognitive distortions.
        
        Args:
            message (str): The message to analyze
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing distortion analysis
        """
        try:
            # Analyze the message for cognitive distortions
            analysis = self.analyze_distortion(message)
            
            # Format response
            detected_types = analysis['detected_types']
            severity = analysis['severity_score']
            recommendation = analysis['recommendation']
            related_emotion = analysis['related_emotion']
            related_goal = analysis['related_goal']
            confidence = analysis['confidence']
            
            # Create visual severity bar
            severity_bar = "█" * int(severity * 5) + "░" * (5 - int(severity * 5))
            
            if detected_types:
                distortion_names = []
                for dt in detected_types:
                    persian_name = self.distortion_patterns.get(dt, {}).get('persian_name', dt)
                    distortion_names.append(persian_name)
                
                distortion_text = ", ".join(distortion_names)
            else:
                distortion_text = "هیچ تحریف شناختی شناسایی نشد"
            
            # Build response content
            response_content = f"""🧠 **تحلیل تحریف‌های شناختی:**

**🔍 نتیجه تحلیل:**
• 🎯 **تحریف:** {distortion_text}
• 📊 **شدت:** {severity_bar} ({severity*100:.1f}%)
• 🤔 **اطمینان:** {confidence*100:.1f}%

**💡 پیشنهاد بازسازی شناختی:**
{recommendation}

**📋 شناسه:** {analysis['log_id']}"""
            
            return {
                'content': response_content,
                'analysis': analysis,
                'detected_types': detected_types,
                'severity_score': severity,
                'recommendation': recommendation,
                'related_emotion': related_emotion,
                'related_goal': related_goal,
                'confidence': confidence
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error in respond: {e}")
            return {
                'content': f"خطا در تحلیل تحریف‌های شناختی: {str(e)}",
                'analysis': None,
                'detected_types': [],
                'severity_score': 0.0,
                'recommendation': 'لطفاً دوباره تلاش کنید',
                'related_emotion': '',
                'related_goal': '',
                'confidence': 0.0
            }