"""
Interactive Security Check Agent for analyzing mental/cognitive safety signals 
and providing personalized security advice or alerts.
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from uuid import uuid4, UUID
from sqlalchemy import Column, String, Float, DateTime, Text, Enum as SQLEnum, create_engine
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from openai import OpenAI
from .base_agent import BaseAgent

# Database setup
Base = declarative_base()

class ThreatType(Enum):
    BURNOUT = "burnout"
    EMOTIONAL_OVERLOAD = "emotional_overload"
    IMPULSIVITY = "impulsivity"
    COGNITIVE_FATIGUE = "cognitive_fatigue"
    STRESS_OVERLOAD = "stress_overload"
    DECISION_PARALYSIS = "decision_paralysis"
    ANXIETY_SPIRAL = "anxiety_spiral"
    NONE = "none"

class AlertLevel(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"

class SecurityCheck(Base):
    """Database model for storing security check results and analysis."""
    __tablename__ = "security_checks"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    input_text = Column(Text, nullable=False)
    detected_threat_type = Column(SQLEnum(ThreatType), nullable=False, default=ThreatType.NONE)
    alert_level = Column(SQLEnum(AlertLevel), nullable=False, default=AlertLevel.GREEN)
    risk_score = Column(Float, nullable=False, default=0.0)
    recommendation = Column(Text, nullable=False)
    analysis_data = Column(Text, nullable=True)  # JSON string for additional analysis details
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InteractiveSecurityCheckAgent(BaseAgent):
    """
    Interactive Security Check Agent for analyzing mental/cognitive safety signals.
    Provides personalized security advice and risk assessments.
    """
    
    def __init__(self):
        super().__init__("InteractiveSecurityCheckAgent")
        self.logger = logging.getLogger("agent.InteractiveSecurityCheckAgent")
        
        # Database setup
        self.db_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self._create_security_checks_table()
        
        # Initialize OpenAI
        self._initialize_openai()
        
        # Initialize threat detection patterns
        self._initialize_threat_patterns()
        
        self.logger.info("[InteractiveSecurityCheckAgent] Initialized with PostgreSQL database integration for security analysis")

    def _create_security_checks_table(self):
        """Create security_checks table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("[InteractiveSecurityCheckAgent] Security checks table ready")
        except Exception as e:
            self.logger.error(f"[InteractiveSecurityCheckAgent] Error creating security checks table: {e}")

    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available."""
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
                self.logger.info("[InteractiveSecurityCheckAgent] OpenAI GPT integration ready for security analysis")
            else:
                self.openai_client = None
                self.logger.warning("[InteractiveSecurityCheckAgent] OpenAI API key not found, using pattern-based analysis only")
        except Exception as e:
            self.openai_client = None
            self.logger.error(f"[InteractiveSecurityCheckAgent] Error initializing OpenAI: {e}")

    def _initialize_threat_patterns(self):
        """Initialize threat detection patterns and security recommendations."""
        self.threat_patterns = {
            ThreatType.BURNOUT: {
                'keywords': ['خسته', 'کسل', 'انگیزه', 'تمام شد', 'دیگه نمیتونم', 'burnt out', 'exhausted', 'tired', 'motivation'],
                'phrases': ['انگیزه ندارم', 'خیلی خسته ام', 'دیگه نمی تونم', 'تمومش کن'],
                'recommendation': '🔋 استراحت کوتاه یا تغییر فعالیت پیشنهاد می‌شود'
            },
            ThreatType.EMOTIONAL_OVERLOAD: {
                'keywords': ['استرس', 'اضطراب', 'نگران', 'ترس', 'overwhelmed', 'stressed', 'anxious', 'worried'],
                'phrases': ['خیلی استرس دارم', 'نگرانم', 'اضطراب دارم', 'غرق شدم'],
                'recommendation': '🧘 تکنیک‌های تنفس عمیق یا مدیتیشن کوتاه انجام دهید'
            },
            ThreatType.IMPULSIVITY: {
                'keywords': ['الان', 'فوری', 'سریع', 'باید', 'حتما', 'immediately', 'urgent', 'must', 'right now'],
                'phrases': ['همین الان باید', 'فوری باشه', 'سریع باشه', 'حتما الان'],
                'recommendation': '⏸️ قبل از عمل، چند دقیقه فکر کنید و گزینه‌ها را بررسی کنید'
            },
            ThreatType.COGNITIVE_FATIGUE: {
                'keywords': ['فکر', 'تمرکز', 'ذهن', 'حواس', 'یادگیری', 'focus', 'concentration', 'thinking', 'mental'],
                'phrases': ['نمی تونم فکر کنم', 'حواسم پرته', 'تمرکز ندارم', 'ذهنم خسته'],
                'recommendation': '🧠 چند دقیقه استراحت ذهنی یا تمرین ساده تمرکز انجام دهید'
            },
            ThreatType.STRESS_OVERLOAD: {
                'keywords': ['فشار', 'استرس', 'تنش', 'pressure', 'stress', 'tension', 'burden'],
                'phrases': ['تحت فشارم', 'استرس زیاد', 'فشار کاری', 'تنش دارم'],
                'recommendation': '💪 از تکنیک‌های کاهش استرس استفاده کنید یا با متخصص صحبت کنید'
            },
            ThreatType.DECISION_PARALYSIS: {
                'keywords': ['تصمیم', 'انتخاب', 'نمیدونم', 'مردد', 'decision', 'choice', 'confused', 'undecided'],
                'phrases': ['نمی دونم چی کار کنم', 'مردد هستم', 'تصمیم نمی تونم بگیرم'],
                'recommendation': '🎯 گزینه‌ها را لیست کنید و مزایا/معایب هر کدام را بنویسید'
            },
            ThreatType.ANXIETY_SPIRAL: {
                'keywords': ['اضطراب', 'ترس', 'وحشت', 'پانیک', 'anxiety', 'fear', 'panic', 'worried'],
                'phrases': ['اضطراب دارم', 'می ترسم', 'پانیک', 'وحشت کردم'],
                'recommendation': '🌸 تکنیک‌های آرامش‌بخش یا تماس با حمایت روانی'
            }
        }
        
        self.logger.info("[InteractiveSecurityCheckAgent] Threat detection patterns and security recommendations initialized")

    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process security check requests and generate comprehensive analysis.
        
        Args:
            message (str): The message to analyze for security threats
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing security analysis and recommendations
        """
        try:
            self.remember(f"User: {message[:50]}...")
            
            # Analyze security threats
            analysis_result = self._analyze_security_threats(message, context or {})
            
            # Save to database
            security_check_id = self._save_security_check(
                input_text=message,
                threat_type=analysis_result['threat_type'],
                alert_level=analysis_result['alert_level'],
                risk_score=analysis_result['risk_score'],
                recommendation=analysis_result['recommendation'],
                analysis_data=analysis_result.get('analysis_data', {})
            )
            
            # Format response
            response_content = self._format_security_response(analysis_result, security_check_id)
            
            # Remember the analysis
            self.remember(f"Security analysis: {analysis_result['alert_level'].value} (risk: {analysis_result['risk_score']:.1f})...")
            
            return {
                'response_id': f"security_{security_check_id}",
                'content': response_content,
                'handled_by': self.name,
                'timestamp': self._get_current_timestamp(),
                'success': True,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"[InteractiveSecurityCheckAgent] Error in respond: {e}")
            return {
                'response_id': f"security_error_{self._get_current_timestamp()}",
                'content': f"خطا در تحلیل امنیت ذهنی: {str(e)}",
                'handled_by': self.name,
                'timestamp': self._get_current_timestamp(),
                'success': False,
                'error': str(e)
            }

    def _analyze_security_threats(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text for cognitive/emotional security threats."""
        try:
            # First try pattern-based analysis
            pattern_result = self._pattern_based_threat_detection(message)
            
            # If OpenAI is available and pattern confidence is low, use GPT analysis
            if self.openai_client and pattern_result['confidence'] < 0.7:
                try:
                    gpt_result = self._gpt_threat_analysis(message, context)
                    # Combine pattern and GPT results
                    return self._combine_analysis_results(pattern_result, gpt_result)
                except Exception as e:
                    self.logger.warning(f"[InteractiveSecurityCheckAgent] GPT analysis failed: {e}")
                    return pattern_result
            
            return pattern_result
            
        except Exception as e:
            self.logger.error(f"[InteractiveSecurityCheckAgent] Error in threat analysis: {e}")
            return {
                'threat_type': ThreatType.NONE,
                'alert_level': AlertLevel.GREEN,
                'risk_score': 0.0,
                'recommendation': 'تحلیل امنیت انجام نشد',
                'confidence': 0.0,
                'analysis_data': {'error': str(e)}
            }

    def _pattern_based_threat_detection(self, message: str) -> Dict[str, Any]:
        """Detect threats using pattern matching."""
        message_lower = message.lower()
        detected_threats = []
        total_score = 0.0
        
        for threat_type, patterns in self.threat_patterns.items():
            threat_score = 0.0
            matches = []
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in message_lower:
                    threat_score += 0.3
                    matches.append(f"keyword: {keyword}")
            
            # Check phrases
            for phrase in patterns['phrases']:
                if phrase in message_lower:
                    threat_score += 0.5
                    matches.append(f"phrase: {phrase}")
            
            if threat_score > 0:
                detected_threats.append({
                    'type': threat_type,
                    'score': min(threat_score, 1.0),
                    'matches': matches,
                    'recommendation': patterns['recommendation']
                })
                total_score += threat_score
        
        # Determine primary threat
        if detected_threats:
            primary_threat = max(detected_threats, key=lambda x: x['score'])
            risk_score = min(total_score / 2, 1.0)  # Normalize
            
            # Determine alert level
            if risk_score >= 0.7:
                alert_level = AlertLevel.RED
            elif risk_score >= 0.4:
                alert_level = AlertLevel.YELLOW
            else:
                alert_level = AlertLevel.GREEN
                
            return {
                'threat_type': primary_threat['type'],
                'alert_level': alert_level,
                'risk_score': risk_score,
                'recommendation': primary_threat['recommendation'],
                'confidence': min(primary_threat['score'], 0.8),
                'analysis_data': {
                    'detected_threats': detected_threats,
                    'analysis_method': 'pattern_based'
                }
            }
        
        # No threats detected
        return {
            'threat_type': ThreatType.NONE,
            'alert_level': AlertLevel.GREEN,
            'risk_score': 0.0,
            'recommendation': '✅ وضعیت ذهنی شما مناسب به نظر می‌رسد',
            'confidence': 0.6,
            'analysis_data': {'analysis_method': 'pattern_based', 'threats_found': 0}
        }

    def _gpt_threat_analysis(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI GPT for advanced threat analysis."""
        try:
            system_prompt = """تو یک متخصص امنیت ذهنی و روان‌شناس هستی. متن کاربر را تحلیل کن و تهدیدات احتمالی برای سلامت ذهنی/عاطفی او را شناسایی کن.

انواع تهدیدات:
- burnout: فرسودگی و خستگی
- emotional_overload: بار عاطفی زیاد
- impulsivity: تصمیم‌گیری عجولانه
- cognitive_fatigue: خستگی ذهنی
- stress_overload: استرس مفرط
- decision_paralysis: عدم توانایی تصمیم‌گیری
- anxiety_spiral: مارپیچ اضطراب
- none: بدون تهدید

سطوح هشدار:
- green: امن
- yellow: احتیاط
- red: خطر

پاسخ را در فرمت JSON ارائه کن:
{
  "threat_type": "نوع تهدید",
  "alert_level": "سطح هشدار",
  "risk_score": امتیاز خطر (0.0-1.0),
  "recommendation": "توصیه مناسب به فارسی",
  "confidence": اطمینان (0.0-1.0)
}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"تحلیل امنیت ذهنی: {message}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'threat_type': ThreatType(result.get('threat_type', 'none')),
                'alert_level': AlertLevel(result.get('alert_level', 'green')),
                'risk_score': float(result.get('risk_score', 0.0)),
                'recommendation': result.get('recommendation', 'تحلیل امنیت انجام شد'),
                'confidence': float(result.get('confidence', 0.5)),
                'analysis_data': {
                    'analysis_method': 'gpt_powered',
                    'gpt_response': result
                }
            }
            
        except Exception as e:
            self.logger.error(f"[InteractiveSecurityCheckAgent] GPT analysis failed: {e}")
            raise e

    def _combine_analysis_results(self, pattern_result: Dict, gpt_result: Dict) -> Dict[str, Any]:
        """Combine pattern-based and GPT analysis results."""
        # Use GPT result if it has higher confidence, otherwise combine
        if gpt_result['confidence'] > pattern_result['confidence']:
            return {
                **gpt_result,
                'analysis_data': {
                    'analysis_method': 'hybrid',
                    'pattern_result': pattern_result['analysis_data'],
                    'gpt_result': gpt_result['analysis_data']
                }
            }
        else:
            # Use pattern result but enhance with GPT insights
            return {
                **pattern_result,
                'recommendation': gpt_result.get('recommendation', pattern_result['recommendation']),
                'analysis_data': {
                    'analysis_method': 'hybrid',
                    'primary': 'pattern_based',
                    'pattern_result': pattern_result['analysis_data'],
                    'gpt_result': gpt_result['analysis_data']
                }
            }

    def _save_security_check(self, input_text: str, threat_type: ThreatType, alert_level: AlertLevel,
                           risk_score: float, recommendation: str, analysis_data: Dict[str, Any]) -> str:
        """Save security check analysis to database."""
        try:
            db = self.SessionLocal()
            
            security_check = SecurityCheck(
                input_text=input_text,
                detected_threat_type=threat_type,
                alert_level=alert_level,
                risk_score=risk_score,
                recommendation=recommendation,
                analysis_data=json.dumps(analysis_data, ensure_ascii=False)
            )
            
            db.add(security_check)
            db.commit()
            db.refresh(security_check)
            
            security_check_id = str(security_check.id)
            db.close()
            
            self.logger.info(f"[InteractiveSecurityCheckAgent] Security check saved with ID: {security_check_id}")
            return security_check_id
            
        except Exception as e:
            self.logger.error(f"[InteractiveSecurityCheckAgent] Error saving security check: {e}")
            return "error"

    def _format_security_response(self, analysis_result: Dict[str, Any], security_check_id: str) -> str:
        """Format security analysis response for display."""
        threat_type = analysis_result['threat_type']
        alert_level = analysis_result['alert_level']
        risk_score = analysis_result['risk_score']
        recommendation = analysis_result['recommendation']
        confidence = analysis_result['confidence']
        
        # Get emoji for alert level
        alert_emoji = {
            AlertLevel.GREEN: '🟢',
            AlertLevel.YELLOW: '🟡',
            AlertLevel.RED: '🔴'
        }
        
        # Get threat type in Persian
        threat_persian = {
            ThreatType.BURNOUT: 'فرسودگی',
            ThreatType.EMOTIONAL_OVERLOAD: 'بار عاطفی زیاد',
            ThreatType.IMPULSIVITY: 'عجله و تکانشگری',
            ThreatType.COGNITIVE_FATIGUE: 'خستگی ذهنی',
            ThreatType.STRESS_OVERLOAD: 'استرس مفرط',
            ThreatType.DECISION_PARALYSIS: 'عدم توانایی تصمیم‌گیری',
            ThreatType.ANXIETY_SPIRAL: 'مارپیچ اضطراب',
            ThreatType.NONE: 'تهدید خاصی شناسایی نشد'
        }
        
        response = f"""🛡️ **بررسی امنیت ذهنی:**

```json
{{
  "threat_type": "{threat_type.value}",
  "alert_level": "{alert_level.value}",
  "risk_score": {risk_score:.1f},
  "recommendation": "{recommendation}"
}}
```

**📊 نتایج تحلیل:**
• {alert_emoji[alert_level]} **سطح هشدار:** {alert_level.value}
• 🔍 **نوع تهدید:** {threat_persian[threat_type]}
• ⚡ **امتیاز خطر:** {'█' * int(risk_score * 5)}{'░' * (5 - int(risk_score * 5))} ({risk_score * 100:.1f}%)
• 📈 **اطمینان:** {'█' * int(confidence * 5)}{'░' * (5 - int(confidence * 5))} ({confidence * 100:.1f}%)

**🎯 توصیه امنیتی:**
{recommendation}

🛡️ **نکته:** این تحلیل بر اساس الگوهای امنیت ذهنی و سیگنال‌های شناختی انجام شده است."""

        return response

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "تحلیل امنیت ذهنی",
            "شناسایی تهدیدات شناختی",
            "ارزیابی خطر عاطفی",
            "توصیه‌های امنیتی شخصی",
            "نظارت بر سلامت روان",
            "هشدار امنیت ذهنی",
            "پشتیبانی تصمیم‌گیری امن"
        ]

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for security checks."""
        try:
            db = self.SessionLocal()
            
            total_checks = db.query(SecurityCheck).count()
            
            # Count by alert level
            green_count = db.query(SecurityCheck).filter(SecurityCheck.alert_level == AlertLevel.GREEN).count()
            yellow_count = db.query(SecurityCheck).filter(SecurityCheck.alert_level == AlertLevel.YELLOW).count()
            red_count = db.query(SecurityCheck).filter(SecurityCheck.alert_level == AlertLevel.RED).count()
            
            # Count by threat type
            threat_counts = {}
            for threat_type in ThreatType:
                count = db.query(SecurityCheck).filter(SecurityCheck.detected_threat_type == threat_type).count()
                threat_counts[threat_type.value] = count
            
            db.close()
            
            return {
                'total_security_checks': total_checks,
                'alert_levels': {
                    'green': green_count,
                    'yellow': yellow_count,
                    'red': red_count
                },
                'threat_types': threat_counts,
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"[InteractiveSecurityCheckAgent] Error getting database stats: {e}")
            return {'error': str(e)}

    def list_recent_security_checks(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent security check analyses."""
        try:
            db = self.SessionLocal()
            
            security_checks = db.query(SecurityCheck).order_by(
                SecurityCheck.created_at.desc()
            ).limit(limit).all()
            
            checks_data = []
            for check in security_checks:
                checks_data.append({
                    'id': str(check.id),
                    'input_text': check.input_text,
                    'detected_threat_type': check.detected_threat_type.value,
                    'alert_level': check.alert_level.value,
                    'risk_score': check.risk_score,
                    'recommendation': check.recommendation,
                    'created_at': check.created_at.isoformat()
                })
            
            db.close()
            
            return {
                'security_checks': checks_data,
                'count': len(checks_data),
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"[InteractiveSecurityCheckAgent] Error listing security checks: {e}")
            return {'error': str(e), 'security_checks': [], 'count': 0}