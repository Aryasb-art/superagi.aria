"""
EthicalReasoningAgent - Ethical reasoning and value alignment analysis agent.

This agent analyzes decisions, strategies, or statements based on ethical reasoning frameworks,
detecting potential ethical misalignments, value conflicts, and integrity risks.
"""

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import Column, String, DateTime, Float, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from agents.base_agent import BaseAgent
from config import settings
from openai import OpenAI
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class EthicalLog(Base):
    """Database model for ethical reasoning logs."""
    __tablename__ = 'ethical_logs'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_text = Column(Text)
    status = Column(String)  # ok, warning, alert
    confidence = Column(Float)
    framework_flags = Column(Text)  # JSON string of triggered frameworks
    guidance = Column(Text)
    analysis_data = Column(Text)  # JSON string of full analysis


class EthicalReasoningAgent(BaseAgent):
    """
    Advanced ethical reasoning and value alignment analysis agent.
    Analyzes decisions and statements based on major ethical frameworks.
    """
    
    def __init__(self):
        super().__init__("EthicalReasoningAgent")
        self.openai_client = None
        self.session = None
        self._init_database()
        self._init_openai()
        self._init_ethical_frameworks()
        logger.info(f"[{self.name}] Initialized with PostgreSQL database integration for ethical reasoning analysis")
    
    def _init_database(self):
        """Initialize database connection and create tables."""
        try:
            engine = create_engine(settings.DATABASE_URL)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()
            logger.info(f"[{self.name}] Ethical logs table ready")
        except Exception as e:
            logger.error(f"[{self.name}] Database initialization failed: {e}")
            self.session = None
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                logger.info(f"[{self.name}] OpenAI GPT integration ready for ethical reasoning analysis")
            else:
                logger.warning(f"[{self.name}] OpenAI API key not found, using pattern-based analysis only")
        except Exception as e:
            logger.error(f"[{self.name}] OpenAI initialization failed: {e}")
            self.openai_client = None
    
    def _init_ethical_frameworks(self):
        """Initialize ethical frameworks and pattern detection."""
        # Ethical framework patterns for detection
        self.ethical_patterns = {
            'utilitarianism': {
                'keywords': ['greatest good', 'greatest happiness', 'utility', 'consequence', 'outcome', 'benefit most people', 'maximum welfare', 'cost-benefit'],
                'persian_keywords': ['بیشترین خیر', 'بیشترین سود', 'نفع عمومی', 'رفاه جامعه', 'نتیجه', 'پیامد', 'بیشترین منفعت'],
                'concerns': ['ends justify means', 'individual sacrifice', 'minority rights ignored']
            },
            'deontology': {
                'keywords': ['duty', 'obligation', 'categorical imperative', 'universal law', 'inherent right', 'moral rule', 'principle'],
                'persian_keywords': ['وظیفه', 'تکلیف', 'اصل اخلاقی', 'قانون کلی', 'حق ذاتی', 'قاعده اخلاقی', 'اصل'],
                'concerns': ['rigid rules', 'inflexible', 'ignores consequences']
            },
            'virtue_ethics': {
                'keywords': ['character', 'virtue', 'integrity', 'honesty', 'courage', 'compassion', 'wisdom', 'temperance'],
                'persian_keywords': ['شخصیت', 'فضیلت', 'صداقت', 'شجاعت', 'دلسوزی', 'حکمت', 'اعتدال', 'درستکاری'],
                'concerns': ['cultural relativism', 'vague guidance', 'subjective virtues']
            },
            'care_ethics': {
                'keywords': ['care', 'relationship', 'responsibility', 'empathy', 'nurturing', 'interdependence', 'context'],
                'persian_keywords': ['مراقبت', 'رابطه', 'مسئولیت', 'همدلی', 'پرورش', 'وابستگی متقابل', 'بافت'],
                'concerns': ['partiality', 'limited scope', 'gender bias']
            }
        }
        
        # Ethical risk indicators
        self.risk_indicators = {
            'high_risk': [
                'harm others', 'deception', 'exploitation', 'discrimination', 'manipulation',
                'violence', 'fraud', 'corruption', 'abuse', 'injustice',
                'آسیب به دیگران', 'فریب', 'بهره‌کشی', 'تبعیض', 'دستکاری',
                'خشونت', 'کلاهبرداری', 'فساد', 'سوءاستفاده', 'بی‌عدالتی'
            ],
            'medium_risk': [
                'unfair advantage', 'bias', 'conflict of interest', 'privacy violation',
                'breach of trust', 'negligence', 'irresponsibility',
                'مزیت ناعادلانه', 'تعصب', 'تضاد منافع', 'نقض حریم خصوصی',
                'شکست اعتماد', 'غفلت', 'بی‌مسئولیتی'
            ],
            'inaction_risks': [
                'failing to act', 'ignoring', 'negligence', 'turning blind eye',
                'avoiding responsibility', 'passive acceptance',
                'عدم اقدام', 'نادیده گرفتن', 'غفلت', 'چشم بستن',
                'فرار از مسئولیت', 'پذیرش منفعلانه'
            ]
        }
        
        logger.info(f"[{self.name}] Ethical frameworks and risk patterns initialized")
    
    def _detect_ethical_patterns(self, text: str) -> Dict[str, Any]:
        """
        Detect ethical frameworks and risks using pattern matching.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: Detected ethical patterns with scores
        """
        text_lower = text.lower()
        
        # Detect ethical frameworks
        framework_scores = {}
        triggered_frameworks = []
        
        for framework, patterns in self.ethical_patterns.items():
            score = 0
            all_keywords = patterns['keywords'] + patterns['persian_keywords']
            
            for keyword in all_keywords:
                if keyword.lower() in text_lower:
                    score += 1
            
            if score > 0:
                framework_scores[framework] = score / len(all_keywords)
                triggered_frameworks.append(framework)
        
        # Detect risk levels
        risk_score = 0.0
        risk_indicators = []
        
        # High risk indicators
        for indicator in self.risk_indicators['high_risk']:
            if indicator.lower() in text_lower:
                risk_score += 0.3
                risk_indicators.append(f"High risk: {indicator}")
        
        # Medium risk indicators
        for indicator in self.risk_indicators['medium_risk']:
            if indicator.lower() in text_lower:
                risk_score += 0.2
                risk_indicators.append(f"Medium risk: {indicator}")
        
        # Inaction risks
        for indicator in self.risk_indicators['inaction_risks']:
            if indicator.lower() in text_lower:
                risk_score += 0.15
                risk_indicators.append(f"Inaction risk: {indicator}")
        
        # Normalize risk score
        risk_score = min(1.0, risk_score)
        
        # Determine status
        if risk_score >= 0.7:
            status = "alert"
        elif risk_score >= 0.4:
            status = "warning"
        else:
            status = "ok"
        
        return {
            'frameworks': triggered_frameworks,
            'framework_scores': framework_scores,
            'risk_score': risk_score,
            'risk_indicators': risk_indicators,
            'status': status,
            'confidence': 0.7 if triggered_frameworks else 0.4,
            'detection_method': 'pattern_based'
        }
    
    def _analyze_ethics_with_gpt(self, text: str) -> Dict[str, Any]:
        """
        Analyze ethical reasoning using OpenAI GPT-4o.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: GPT analysis results
        """
        if not self.openai_client:
            return self._detect_ethical_patterns(text)
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert ethical reasoning analyst. Analyze the given text for ethical implications based on major ethical frameworks:

1. **Utilitarianism**: Greatest good for greatest number
2. **Deontology**: Duty-based ethics, universal principles
3. **Virtue Ethics**: Character-based ethics, virtues and vices
4. **Care Ethics**: Relationship-based ethics, care and responsibility

Analyze for:
- Ethical frameworks triggered
- Potential value conflicts
- Integrity risks
- Ethical negligence (inaction risks)
- Both actions and inactions

Respond with JSON in this exact format:
{
  "frameworks": ["list of triggered frameworks"],
  "risk_score": 0.0-1.0,
  "status": "ok/warning/alert",
  "confidence": 0.0-1.0,
  "reasoning_summary": "brief analysis in Persian",
  "ethical_guidance": "improvement suggestions in Persian",
  "inaction_risks": ["list of negligence risks"],
  "framework_analysis": {
    "utilitarianism": "brief assessment",
    "deontology": "brief assessment", 
    "virtue_ethics": "brief assessment",
    "care_ethics": "brief assessment"
  }
}"""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this text for ethical reasoning and potential risks:\n\n{text}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            result['detection_method'] = 'gpt_analysis'
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] GPT analysis failed: {e}")
            return self._detect_ethical_patterns(text)
    
    def _generate_ethical_guidance(self, frameworks: List[str], risk_score: float, 
                                  status: str, inaction_risks: List[str] = None) -> str:
        """
        Generate ethical guidance based on analysis results.
        
        Args:
            frameworks (List[str]): Triggered ethical frameworks
            risk_score (float): Risk score
            status (str): Status level
            inaction_risks (List[str]): Inaction risks detected
            
        Returns:
            str: Ethical guidance
        """
        guidance_parts = []
        
        # Status-based guidance
        if status == "alert":
            guidance_parts.append("⚠️ **هشدار اخلاقی بحرانی**: این تصمیم یا اقدام دارای خطرات اخلاقی جدی است.")
        elif status == "warning":
            guidance_parts.append("🟡 **توجه اخلاقی**: این موضوع نیازمند بررسی بیشتر اخلاقی است.")
        else:
            guidance_parts.append("✅ **وضعیت اخلاقی مطلوب**: تحلیل اولیه نشان‌دهنده عدم مشکل اخلاقی جدی است.")
        
        # Framework-specific guidance
        framework_guidance = {
            'utilitarianism': "از منظر فایده‌گرایی، بررسی کنید آیا این اقدام بیشترین سود را برای بیشترین تعداد افراد به همراه دارد.",
            'deontology': "از منظر اخلاق وظیفه‌محور، بررسی کنید آیا این اقدام با اصول اخلاقی کلی و وظایف اخلاقی سازگار است.",
            'virtue_ethics': "از منظر اخلاق فضیلت، بررسی کنید آیا این اقدام منعکس‌کننده فضایل اخلاقی مانند صداقت، شجاعت و عدالت است.",
            'care_ethics': "از منظر اخلاق مراقبت، بررسی کنید آیا این اقدام روابط و مسئولیت‌های مراقبتی را در نظر می‌گیرد."
        }
        
        for framework in frameworks:
            if framework in framework_guidance:
                guidance_parts.append(f"📚 **{framework}**: {framework_guidance[framework]}")
        
        # Risk-based guidance
        if risk_score >= 0.7:
            guidance_parts.append("🔴 **توصیه فوری**: این اقدام را متوقف کرده و مشاوره اخلاقی بگیرید.")
        elif risk_score >= 0.4:
            guidance_parts.append("🟠 **توصیه احتیاط**: قبل از ادامه، تبعات اخلاقی را بررسی کنید.")
        
        # Inaction risks
        if inaction_risks:
            guidance_parts.append("⚠️ **خطر غفلت اخلاقی**: عدم اقدام نیز می‌تواند دارای تبعات اخلاقی باشد.")
        
        # General guidance
        guidance_parts.extend([
            "🎯 **راهنمایی عملی**:",
            "• با افراد متأثر مشورت کنید",
            "• تبعات کوتاه‌مدت و بلندمدت را بررسی کنید",
            "• اصول اخلاقی سازمانی و شخصی را در نظر بگیرید",
            "• در صورت شک، از مشاوران اخلاقی کمک بگیرید"
        ])
        
        return "\n".join(guidance_parts)
    
    def analyze_ethics(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for ethical reasoning using hybrid approach.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: Ethical analysis results
        """
        if not text or len(text.strip()) < 10:
            return {
                'success': False,
                'error': 'متن ورودی برای تحلیل اخلاقی کافی نیست (حداقل 10 کاراکتر)'
            }
        
        try:
            # Try GPT analysis first, fallback to pattern-based
            if self.openai_client:
                analysis = self._analyze_ethics_with_gpt(text)
            else:
                analysis = self._detect_ethical_patterns(text)
            
            # Generate guidance
            guidance = self._generate_ethical_guidance(
                analysis.get('frameworks', []),
                analysis.get('risk_score', 0.0),
                analysis.get('status', 'ok'),
                analysis.get('inaction_risks', [])
            )
            
            # Prepare result
            result = {
                'status': analysis.get('status', 'ok'),
                'confidence': analysis.get('confidence', 0.5),
                'framework_flags': analysis.get('frameworks', []),
                'risk_score': analysis.get('risk_score', 0.0),
                'reasoning_summary': analysis.get('reasoning_summary', ''),
                'ethical_guidance': guidance,
                'inaction_risks': analysis.get('inaction_risks', []),
                'detection_method': analysis.get('detection_method', 'pattern_based'),
                'framework_analysis': analysis.get('framework_analysis', {}),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save to database
            log_id = str(uuid.uuid4())
            self._save_ethical_log(
                log_id=log_id,
                input_text=text,
                status=result['status'],
                confidence=result['confidence'],
                framework_flags=json.dumps(result['framework_flags']),
                guidance=guidance,
                analysis_data=json.dumps(result)
            )
            
            return {
                'success': True,
                'analysis': result,
                'log_id': log_id
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Ethical analysis failed: {e}")
            return {
                'success': False,
                'error': f'خطا در تحلیل اخلاقی: {str(e)}'
            }
    
    def _save_ethical_log(self, log_id: str, input_text: str, status: str, 
                         confidence: float, framework_flags: str, guidance: str,
                         analysis_data: str):
        """Save ethical analysis to database."""
        if not self.session:
            return
            
        try:
            log_entry = EthicalLog(
                id=log_id,
                timestamp=datetime.utcnow(),
                input_text=input_text,
                status=status,
                confidence=confidence,
                framework_flags=framework_flags,
                guidance=guidance,
                analysis_data=analysis_data
            )
            self.session.add(log_entry)
            self.session.commit()
        except Exception as e:
            logger.error(f"[{self.name}] Failed to save ethical log: {e}")
            if self.session:
                self.session.rollback()
    
    def get_ethical_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent ethical analysis logs.
        
        Args:
            limit (int): Number of logs to retrieve
            
        Returns:
            List[Dict]: Recent ethical logs
        """
        if not self.session:
            return []
            
        try:
            logs = self.session.query(EthicalLog).order_by(
                EthicalLog.timestamp.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat(),
                    'input_text': log.input_text,
                    'status': log.status,
                    'confidence': log.confidence,
                    'framework_flags': json.loads(log.framework_flags) if log.framework_flags else [],
                    'guidance': log.guidance,
                    'analysis_data': json.loads(log.analysis_data) if log.analysis_data else {}
                }
                for log in logs
            ]
        except Exception as e:
            logger.error(f"[{self.name}] Failed to retrieve ethical logs: {e}")
            return []
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process message and analyze for ethical reasoning.
        
        Args:
            message (str): The message to analyze
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing ethical analysis
        """
        if not message or not message.strip():
            return {
                'success': False,
                'content': 'لطفاً متن یا تصمیم خود را برای تحلیل اخلاقی وارد کنید'
            }
        
        # Analyze ethics
        analysis_result = self.analyze_ethics(message)
        
        if not analysis_result['success']:
            return {
                'success': False,
                'content': analysis_result['error']
            }
        
        analysis = analysis_result['analysis']
        
        # Format response
        response_parts = []
        
        # Status indicator
        status_emoji = {
            'ok': '✅',
            'warning': '🟡', 
            'alert': '🔴'
        }
        
        response_parts.append(f"{status_emoji.get(analysis['status'], '❓')} **وضعیت اخلاقی**: {analysis['status']}")
        
        # Confidence
        confidence_bar = '█' * int(analysis['confidence'] * 5) + '░' * (5 - int(analysis['confidence'] * 5))
        response_parts.append(f"📊 **اطمینان**: {confidence_bar} ({analysis['confidence']*100:.1f}%)")
        
        # Risk score
        if analysis['risk_score'] > 0:
            risk_bar = '█' * int(analysis['risk_score'] * 5) + '░' * (5 - int(analysis['risk_score'] * 5))
            response_parts.append(f"⚠️ **امتیاز خطر**: {risk_bar} ({analysis['risk_score']*100:.1f}%)")
        
        # Triggered frameworks
        if analysis['framework_flags']:
            frameworks_persian = {
                'utilitarianism': 'فایده‌گرایی',
                'deontology': 'اخلاق وظیفه‌محور',
                'virtue_ethics': 'اخلاق فضیلت',
                'care_ethics': 'اخلاق مراقبت'
            }
            framework_list = [frameworks_persian.get(f, f) for f in analysis['framework_flags']]
            response_parts.append(f"📚 **چارچوب‌های شناسایی شده**: {', '.join(framework_list)}")
        
        # Reasoning summary
        if analysis.get('reasoning_summary'):
            response_parts.append(f"🧠 **خلاصه تحلیل**: {analysis['reasoning_summary']}")
        
        # Inaction risks
        if analysis.get('inaction_risks'):
            response_parts.append(f"⚠️ **خطرات غفلت**: {len(analysis['inaction_risks'])} مورد شناسایی شد")
        
        # Guidance
        response_parts.append(f"\n{analysis['ethical_guidance']}")
        
        # Method used
        method_text = "تحلیل هوشمند GPT" if analysis['detection_method'] == 'gpt_analysis' else "تحلیل الگویی"
        response_parts.append(f"\n🔍 **روش تحلیل**: {method_text}")
        
        return {
            'success': True,
            'content': '\n'.join(response_parts),
            'analysis_data': analysis
        }