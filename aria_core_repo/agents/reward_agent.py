"""
Reward Agent for detecting positive progress and providing motivational feedback.
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, Text, create_engine
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from openai import OpenAI
from .base_agent import BaseAgent

# Database setup
Base = declarative_base()

class TriggerType(Enum):
    EMOTIONAL_RECOVERY = "emotional_recovery"
    GOAL_ALIGNMENT = "goal_alignment"
    SECURITY_IMPROVEMENT = "security_improvement"
    STRESS_REDUCTION = "stress_reduction"
    POSITIVE_MINDSET = "positive_mindset"
    BREAKTHROUGH = "breakthrough"
    CONSISTENCY = "consistency"
    NONE = "none"

class RewardLog(Base):
    """Database model for storing reward feedback and logs."""
    __tablename__ = "reward_logs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    trigger_type = Column(Text, nullable=False)
    reward_message = Column(Text, nullable=False)
    emoji = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)

class RewardAgent(BaseAgent):
    """
    Reward Agent for detecting positive progress and providing motivational feedback.
    Automatically triggered by positive outputs from other agents.
    """
    
    def __init__(self):
        super().__init__("RewardAgent")
        self.logger = logging.getLogger("agent.RewardAgent")
        
        # Database setup
        self.db_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self._create_reward_logs_table()
        
        # Initialize OpenAI
        self._initialize_openai()
        
        # Initialize reward patterns and triggers
        self._initialize_reward_patterns()
        
        self.logger.info("[RewardAgent] Initialized with PostgreSQL database integration for reward tracking")

    def _create_reward_logs_table(self):
        """Create reward_logs table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("[RewardAgent] Reward logs table ready")
        except Exception as e:
            self.logger.error(f"[RewardAgent] Error creating reward logs table: {e}")

    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available."""
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
                self.logger.info("[RewardAgent] OpenAI GPT integration ready for reward generation")
            else:
                self.openai_client = None
                self.logger.warning("[RewardAgent] OpenAI API key not found, using pattern-based rewards only")
        except Exception as e:
            self.openai_client = None
            self.logger.error(f"[RewardAgent] Error initializing OpenAI: {e}")

    def _initialize_reward_patterns(self):
        """Initialize reward detection patterns and motivational messages."""
        self.reward_patterns = {
            TriggerType.EMOTIONAL_RECOVERY: {
                'keywords': ['بهتر', 'آرامش', 'خوب', 'مثبت', 'شاد', 'خوشحال', 'better', 'calm', 'positive', 'happy'],
                'phrases': ['حالم بهتر شد', 'آرامش پیدا کردم', 'احساس خوبی دارم', 'مثبت فکر می کنم'],
                'emojis': ['🌟', '💚', '🌈', '😊', '🎉'],
                'messages': [
                    'عالی! بهبود عاطفی شما قابل تحسین است',
                    'پیشرفت شما در مدیریت احساسات فوق‌العاده است',
                    'روحیه مثبت شما الهام‌بخش است',
                    'تبریک! به خوبی از چالش عاطفی عبور کردید'
                ]
            },
            TriggerType.GOAL_ALIGNMENT: {
                'keywords': ['هدف', 'موفقیت', 'پیشرفت', 'تحقق', 'دستیابی', 'goal', 'success', 'achievement', 'progress'],
                'phrases': ['هدفم را دنبال کردم', 'موفق شدم', 'پیشرفت کردم', 'به هدفم نزدیک شدم'],
                'emojis': ['🎯', '🏆', '⭐', '🚀', '💪'],
                'messages': [
                    'بسیار عالی! هماهنگی با اهدافتان فوق‌العاده است',
                    'تبریک! مسیر درستی را انتخاب کرده‌اید',
                    'پیشرفت شما در جهت اهداف قابل ستایش است',
                    'عالی! انگیزه و تمرکز شما بر اهداف چشمگیر است'
                ]
            },
            TriggerType.SECURITY_IMPROVEMENT: {
                'keywords': ['امن', 'محافظت', 'بهبود', 'کنترل', 'مدیریت', 'safe', 'secure', 'improvement', 'control'],
                'phrases': ['احساس امنیت می کنم', 'وضعیت تحت کنترل است', 'بهتر مدیریت می کنم'],
                'emojis': ['🛡️', '🔒', '✅', '🎖️', '💎'],
                'messages': [
                    'عالی! بهبود امنیت ذهنی شما قابل تقدیر است',
                    'تبریک! به خوبی خطرات را مدیریت کرده‌اید',
                    'پیشرفت شما در ایمن‌سازی فکر فوق‌العاده است',
                    'بسیار خوب! کنترل بهتری بر وضعیت دارید'
                ]
            },
            TriggerType.STRESS_REDUCTION: {
                'keywords': ['آرام', 'کاهش', 'تنش', 'استراحت', 'ریلکس', 'calm', 'relax', 'reduce', 'peace'],
                'phrases': ['استرسم کم شد', 'آرام شدم', 'تنشم کاهش پیدا کرد', 'احساس آرامش می کنم'],
                'emojis': ['🕯️', '🧘', '🌸', '☮️', '🍃'],
                'messages': [
                    'عالی! کاهش استرس شما قابل ستایش است',
                    'تبریک! به خوبی تنش را مدیریت کرده‌اید',
                    'آرامش یافته شما الهام‌بخش است',
                    'بسیار خوب! تکنیک‌های آرامش‌بخش عالی کار کرده'
                ]
            },
            TriggerType.POSITIVE_MINDSET: {
                'keywords': ['مثبت', 'امیدوار', 'خوشبین', 'انگیزه', 'انرژی', 'positive', 'optimistic', 'motivated'],
                'phrases': ['مثبت فکر می کنم', 'امیدوارم', 'انگیزه دارم', 'انرژی مثبت'],
                'emojis': ['☀️', '🌻', '💛', '🎈', '🔥'],
                'messages': [
                    'فوق‌العاده! تفکر مثبت شما شگفت‌انگیز است',
                    'عالی! نگرش امیدوارانه شما قابل تحسین است',
                    'تبریک! انرژی مثبت شما الهام‌بخش است',
                    'بسیار خوب! ذهنیت مثبت شما درخشان است'
                ]
            },
            TriggerType.BREAKTHROUGH: {
                'keywords': ['کشف', 'درک', 'فهمیدن', 'روشن', 'breakthrough', 'insight', 'understanding'],
                'phrases': ['فهمیدم', 'روشن شد', 'کشف کردم', 'درک پیدا کردم'],
                'emojis': ['💡', '🔍', '🎊', '🌟', '⚡'],
                'messages': [
                    'واو! کشف شما فوق‌العاده است',
                    'عالی! درک عمیق شما قابل تقدیر است',
                    'تبریک! بینش جدید شما شگفت‌انگیز است',
                    'بسیار خوب! روشن‌بینی شما الهام‌بخش است'
                ]
            }
        }
        
        self.logger.info("[RewardAgent] Reward patterns and motivational messages initialized")

    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze input for positive progress and generate reward feedback.
        
        Args:
            message (str): The message to analyze for positive patterns
            context (Dict): Optional context including analysis results from other agents
            
        Returns:
            Dict: Response containing reward feedback if positive progress detected
        """
        try:
            self.remember(f"Reward analysis for: {message[:50]}...")
            
            # Analyze for positive progress patterns
            reward_result = self._analyze_positive_progress(message, context or {})
            
            if reward_result['trigger_type'] != TriggerType.NONE:
                # Save reward log to database
                reward_id = self._save_reward_log(
                    trigger_type=reward_result['trigger_type'].value,
                    reward_message=reward_result['reward_message'],
                    emoji=reward_result['emoji'],
                    confidence=reward_result['confidence']
                )
                
                # Format response
                response_content = self._format_reward_response(reward_result, reward_id)
                
                # Remember the reward
                self.remember(f"Reward generated: {reward_result['trigger_type'].value} - {reward_result['emoji']}")
                
                return {
                    'response_id': f"reward_{reward_id}",
                    'content': response_content,
                    'handled_by': self.name,
                    'timestamp': self._get_current_timestamp(),
                    'success': True,
                    'error': None,
                    'reward_data': {
                        'reward_message': reward_result['reward_message'],
                        'emoji': reward_result['emoji'],
                        'confidence': reward_result['confidence'],
                        'trigger_type': reward_result['trigger_type'].value
                    }
                }
            else:
                # No reward triggered
                return {
                    'response_id': f"no_reward_{self._get_current_timestamp()}",
                    'content': 'هیچ پیشرفت قابل توجهی شناسایی نشد',
                    'handled_by': self.name,
                    'timestamp': self._get_current_timestamp(),
                    'success': True,
                    'error': None,
                    'reward_data': None
                }
            
        except Exception as e:
            self.logger.error(f"[RewardAgent] Error in respond: {e}")
            return {
                'response_id': f"reward_error_{self._get_current_timestamp()}",
                'content': f"خطا در تحلیل پیشرفت: {str(e)}",
                'handled_by': self.name,
                'timestamp': self._get_current_timestamp(),
                'success': False,
                'error': str(e)
            }

    def _analyze_positive_progress(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text for positive progress patterns."""
        try:
            # First try pattern-based analysis
            pattern_result = self._pattern_based_reward_detection(message, context)
            
            # If OpenAI is available and pattern confidence is low, use GPT analysis
            if self.openai_client and pattern_result['confidence'] < 0.7:
                try:
                    gpt_result = self._gpt_reward_analysis(message, context)
                    # Use GPT result if it has higher confidence
                    if gpt_result['confidence'] > pattern_result['confidence']:
                        return gpt_result
                except Exception as e:
                    self.logger.warning(f"[RewardAgent] GPT analysis failed: {e}")
            
            return pattern_result
            
        except Exception as e:
            self.logger.error(f"[RewardAgent] Error in progress analysis: {e}")
            return {
                'trigger_type': TriggerType.NONE,
                'reward_message': 'تحلیل پیشرفت انجام نشد',
                'emoji': '❓',
                'confidence': 0.0
            }

    def _pattern_based_reward_detection(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect positive patterns using keyword and phrase matching."""
        message_lower = message.lower()
        detected_triggers = []
        
        # Check context for positive indicators from other agents
        context_score = self._analyze_context_indicators(context)
        
        for trigger_type, patterns in self.reward_patterns.items():
            trigger_score = 0.0
            matches = []
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in message_lower:
                    trigger_score += 0.3
                    matches.append(f"keyword: {keyword}")
            
            # Check phrases
            for phrase in patterns['phrases']:
                if phrase in message_lower:
                    trigger_score += 0.5
                    matches.append(f"phrase: {phrase}")
            
            # Add context score
            trigger_score += context_score
            
            if trigger_score > 0:
                detected_triggers.append({
                    'type': trigger_type,
                    'score': min(trigger_score, 1.0),
                    'matches': matches,
                    'patterns': patterns
                })
        
        # Select the best trigger
        if detected_triggers:
            best_trigger = max(detected_triggers, key=lambda x: x['score'])
            confidence = min(best_trigger['score'], 0.9)
            
            # Select random message and emoji
            import random
            selected_emoji = random.choice(best_trigger['patterns']['emojis'])
            selected_message = random.choice(best_trigger['patterns']['messages'])
            
            return {
                'trigger_type': best_trigger['type'],
                'reward_message': selected_message,
                'emoji': selected_emoji,
                'confidence': confidence
            }
        
        # No positive progress detected
        return {
            'trigger_type': TriggerType.NONE,
            'reward_message': 'هیچ پیشرفت مثبتی شناسایی نشد',
            'emoji': '❓',
            'confidence': 0.0
        }

    def _analyze_context_indicators(self, context: Dict[str, Any]) -> float:
        """Analyze context for positive indicators from other agents."""
        context_score = 0.0
        
        # Check emotion regulation results
        if 'emotion_result' in context:
            emotion = context['emotion_result'].get('emotion', '').lower()
            if any(pos in emotion for pos in ['خوشحال', 'آرام', 'مثبت', 'happy', 'calm', 'positive']):
                context_score += 0.3
        
        # Check security check results
        if 'security_result' in context:
            alert_level = context['security_result'].get('alert_level', '').lower()
            if alert_level == 'green':
                context_score += 0.2
        
        # Check goal inference results
        if 'goal_result' in context:
            confidence = context['goal_result'].get('confidence', 0)
            if confidence > 0.7:
                context_score += 0.2
        
        return min(context_score, 0.5)

    def _gpt_reward_analysis(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI GPT for advanced reward analysis."""
        try:
            system_prompt = """تو یک متخصص انگیزه و روان‌شناس مثبت هستی. متن کاربر را تحلیل کن و ببین آیا نشانه‌ای از پیشرفت مثبت، بهبود احساسات، یا دستاورد وجود دارد.

انواع پیشرفت مثبت:
- emotional_recovery: بهبود عاطفی
- goal_alignment: هماهنگی با اهداف
- security_improvement: بهبود امنیت ذهنی
- stress_reduction: کاهش استرس
- positive_mindset: تفکر مثبت
- breakthrough: کشف یا درک جدید
- consistency: ثبات و پایداری
- none: بدون پیشرفت مثبت

اگر پیشرفت مثبتی شناسایی کردی، پیام تشویقی مناسب و یک ایموجی انتخاب کن.

پاسخ را در فرمت JSON ارائه کن:
{
  "trigger_type": "نوع پیشرفت",
  "reward_message": "پیام تشویقی به فارسی",
  "emoji": "ایموجی مناسب",
  "confidence": اطمینان (0.0-1.0)
}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"تحلیل پیشرفت مثبت: {message}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=400,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'trigger_type': TriggerType(result.get('trigger_type', 'none')),
                'reward_message': result.get('reward_message', 'پیشرفت خوبی داشته‌اید'),
                'emoji': result.get('emoji', '🌟'),
                'confidence': float(result.get('confidence', 0.5))
            }
            
        except Exception as e:
            self.logger.error(f"[RewardAgent] GPT analysis failed: {e}")
            raise e

    def _save_reward_log(self, trigger_type: str, reward_message: str, emoji: str, confidence: float) -> str:
        """Save reward log to database."""
        try:
            db = self.SessionLocal()
            
            reward_log = RewardLog(
                trigger_type=trigger_type,
                reward_message=reward_message,
                emoji=emoji,
                confidence=confidence
            )
            
            db.add(reward_log)
            db.commit()
            db.refresh(reward_log)
            
            reward_id = str(reward_log.id)
            db.close()
            
            self.logger.info(f"[RewardAgent] Reward log saved with ID: {reward_id}")
            return reward_id
            
        except Exception as e:
            self.logger.error(f"[RewardAgent] Error saving reward log: {e}")
            return "error"

    def _format_reward_response(self, reward_result: Dict[str, Any], reward_id: str) -> str:
        """Format reward response for display."""
        trigger_type = reward_result['trigger_type']
        reward_message = reward_result['reward_message']
        emoji = reward_result['emoji']
        confidence = reward_result['confidence']
        
        # Get trigger type in Persian
        trigger_persian = {
            TriggerType.EMOTIONAL_RECOVERY: 'بهبود عاطفی',
            TriggerType.GOAL_ALIGNMENT: 'هماهنگی با اهداف',
            TriggerType.SECURITY_IMPROVEMENT: 'بهبود امنیت ذهنی',
            TriggerType.STRESS_REDUCTION: 'کاهش استرس',
            TriggerType.POSITIVE_MINDSET: 'تفکر مثبت',
            TriggerType.BREAKTHROUGH: 'کشف جدید',
            TriggerType.CONSISTENCY: 'ثبات و پایداری',
            TriggerType.NONE: 'پیشرفت شناسایی نشد'
        }
        
        response = f"""🏆 **پاداش پیشرفت:**

```json
{{
  "trigger_type": "{trigger_type.value}",
  "reward_message": "{reward_message}",
  "emoji": "{emoji}",
  "confidence": {confidence:.1f}
}}
```

**🎉 تبریک!**
{emoji} **{reward_message}**

**📊 جزئیات پاداش:**
• 🎯 **نوع پیشرفت:** {trigger_persian[trigger_type]}
• 📈 **اطمینان:** {'█' * int(confidence * 5)}{'░' * (5 - int(confidence * 5))} ({confidence * 100:.1f}%)
• 🆔 **شناسه پاداش:** {reward_id[:8]}...

🌟 **پیام انگیزشی:** ادامه دهید! شما در حال پیشرفت هستید و این بسیار ارزشمند است."""

        return response

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "تشخیص پیشرفت مثبت",
            "تولید پیام‌های تشویقی",
            "ردیابی دستاوردها",
            "انگیزه‌بخشی",
            "پاداش‌دهی هوشمند",
            "تحلیل بهبود عملکرد",
            "ایجاد انگیزه مثبت"
        ]

    def get_reward_statistics(self) -> Dict[str, Any]:
        """Get reward statistics from database."""
        try:
            db = self.SessionLocal()
            
            total_rewards = db.query(RewardLog).count()
            
            # Count by trigger type
            trigger_counts = {}
            for trigger_type in TriggerType:
                if trigger_type != TriggerType.NONE:
                    count = db.query(RewardLog).filter(RewardLog.trigger_type == trigger_type.value).count()
                    trigger_counts[trigger_type.value] = count
            
            # Get average confidence
            avg_confidence = db.query(func.avg(RewardLog.confidence)).scalar() or 0.0
            
            db.close()
            
            return {
                'total_rewards': total_rewards,
                'trigger_types': trigger_counts,
                'average_confidence': round(float(avg_confidence), 2),
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"[RewardAgent] Error getting statistics: {e}")
            return {'error': str(e)}

    def list_recent_rewards(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent reward logs."""
        try:
            db = self.SessionLocal()
            
            rewards = db.query(RewardLog).order_by(
                RewardLog.timestamp.desc()
            ).limit(limit).all()
            
            rewards_data = []
            for reward in rewards:
                rewards_data.append({
                    'id': str(reward.id),
                    'timestamp': reward.timestamp.isoformat(),
                    'trigger_type': reward.trigger_type,
                    'reward_message': reward.reward_message,
                    'emoji': reward.emoji,
                    'confidence': reward.confidence
                })
            
            db.close()
            
            return {
                'rewards': rewards_data,
                'count': len(rewards_data),
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"[RewardAgent] Error listing rewards: {e}")
            return {'error': str(e), 'rewards': [], 'count': 0}