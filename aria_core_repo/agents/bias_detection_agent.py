"""
BiasDetectionAgent - Cognitive bias detection and reflection agent.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from openai import OpenAI
from sqlalchemy import create_engine, Column, String, DateTime, Float, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BiasLog(Base):
    __tablename__ = 'bias_logs'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_text = Column(Text)
    bias_type = Column(Text)
    severity_score = Column(Float)
    suggestion = Column(Text)

# Create tables
Base.metadata.create_all(bind=engine)

class BiasDetectionAgent(BaseAgent):
    """
    Advanced cognitive bias detection agent with GPT-4o integration.
    Detects and analyzes cognitive biases in user decisions and beliefs.
    """
    
    def __init__(self):
        super().__init__("BiasDetectionAgent")
        self.description = "Cognitive bias detection and reflection agent"
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        # Supported bias types with patterns
        self.bias_patterns = {
            'confirmation_bias': {
                'keywords': ['confirms', 'belief', 'ignore', 'negative', 'support', 'view', 'proves', 'right', 'expected', 'only read', 'selective'],
                'phrases': ['confirms my belief', 'ignore negative information', 'support my view', 'proves I\'m right', 'as I expected', 'only read things that', 'selective reading'],
                'persian_name': 'سوگیری تأیید',
                'description': 'تمایل به جستجو، تفسیر و یادآوری اطلاعاتی که باورهای موجود را تأیید می‌کند'
            },
            'availability_bias': {
                'keywords': ['recently', 'heard', 'saw', 'news', 'remember', 'recall', 'comes to mind', 'just', 'lately'],
                'phrases': ['I recently heard', 'I saw on news', 'comes to mind', 'I remember', 'just heard about', 'recent example'],
                'persian_name': 'سوگیری دسترسی',
                'description': 'تمایل به ارزیابی احتمال بر اساس نمونه‌هایی که به راحتی به یاد می‌آیند'
            },
            'overconfidence': {
                'keywords': ['certain', 'definitely', 'absolutely', 'sure', 'doubt', 'guaranteed', 'predict', 'always', 'never', 'perfect'],
                'phrases': ['absolutely certain', 'definitely will', 'no doubt', 'I know for sure', 'guaranteed', 'I can predict', 'always right', 'never wrong'],
                'persian_name': 'اعتماد بیش از حد',
                'description': 'اعتماد بیش از حد به قضاوت‌ها و پیش‌بینی‌های شخصی'
            },
            'anchoring': {
                'keywords': ['first', 'initial', 'starting', 'original', 'baseline', 'anchor', 'impression', 'beginning'],
                'phrases': ['first impression', 'initial price', 'starting point', 'based on first', 'original estimate', 'initial thought'],
                'persian_name': 'سوگیری لنگر',
                'description': 'تأثیر بیش از حد اطلاعات اولیه در تصمیم‌گیری'
            },
            'sunk_cost_fallacy': {
                'keywords': ['already', 'invested', 'spent', 'waste', 'continue', 'paid', 'money', 'time', 'much'],
                'phrases': ['already invested', 'already spent', 'can\'t waste', 'have to continue', 'already paid', 'invested too much', 'waste money'],
                'persian_name': 'مغالطه هزینه فرورفته',
                'description': 'ادامه یک رفتار یا تلاش صرفاً به دلیل سرمایه‌گذاری قبلی'
            },
            'negativity_bias': {
                'keywords': ['everything', 'always', 'never', 'worst', 'bad', 'terrible', 'disaster', 'hopeless', 'doomed'],
                'phrases': ['everything is bad', 'always fails', 'never works', 'worst case', 'terrible', 'hopeless', 'doomed'],
                'persian_name': 'سوگیری منفی',
                'description': 'تمایل به توجه بیشتر به اطلاعات منفی نسبت به مثبت'
            },
            'framing_effect': {
                'keywords': ['depends', 'perspective', 'way', 'look', 'angle', 'side', 'frame', 'reframe', 'half'],
                'phrases': ['depends how you', 'matter of perspective', 'way to look at it', 'different angle', 'positive side', 'negative side', 'glass half'],
                'persian_name': 'اثر قاب‌بندی',
                'description': 'تأثیر شیوه ارائه اطلاعات بر تصمیم‌گیری'
            }
        }
        
        logger.info(f"[{self.name}] Bias detection patterns and analysis framework initialized")
        
        # Initialize database
        self._init_database()
        
        logger.info(f"[{self.name}] OpenAI GPT integration ready for bias analysis")
        logger.info(f"[{self.name}] Initialized with PostgreSQL database integration for bias tracking")
    
    def _init_database(self):
        """Initialize database tables for bias logging"""
        try:
            # Create tables if they don't exist
            Base.metadata.create_all(bind=engine)
            logger.info(f"[{self.name}] Bias logs table ready")
        except Exception as e:
            logger.error(f"[{self.name}] Database initialization failed: {e}")
    
    def _detect_bias_patterns(self, text: str) -> Dict[str, Any]:
        """
        Detect cognitive biases using pattern matching.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: Detected biases with scores
        """
        detected_biases = []
        severity_scores = []
        
        text_lower = text.lower()
        
        for bias_type, pattern_info in self.bias_patterns.items():
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
                    detected_biases.append(bias_type)
                    severity_scores.append(final_score)
        
        return {
            'detected_biases': detected_biases,
            'severity_scores': severity_scores,
            'method': 'pattern_matching'
        }
    
    def _analyze_bias_with_gpt(self, text: str) -> Dict[str, Any]:
        """
        Analyze cognitive biases using OpenAI GPT-4o.
        
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
                        "content": """شما یک تحلیلگر تخصصی سوگیری‌های شناختی هستید. متن ورودی را تحلیل کنید و سوگیری‌های احتمالی را شناسایی کنید.

سوگیری‌های قابل تشخیص:
- confirmation_bias: سوگیری تأیید
- availability_bias: سوگیری دسترسی  
- overconfidence: اعتماد بیش از حد
- anchoring: سوگیری لنگر
- sunk_cost_fallacy: مغالطه هزینه فرورفته
- negativity_bias: سوگیری منفی
- framing_effect: اثر قاب‌بندی

پاسخ را در قالب JSON ارائه دهید:
{
  "bias_detected": true/false,
  "bias_types": ["bias1", "bias2", ...],
  "severity_score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "reasoning": "دلیل تشخیص",
  "suggestion": "پیشنهاد تأملی برای کاربر"
}"""
                    },
                    {
                        "role": "user",
                        "content": f"متن برای تحلیل: {text}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=800,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['method'] = 'gpt_analysis'
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] GPT analysis failed: {e}")
            return None
    
    def _generate_reflection_suggestion(self, bias_types: List[str], severity: float) -> str:
        """
        Generate a reflective suggestion based on detected biases.
        
        Args:
            bias_types (List[str]): List of detected bias types
            severity (float): Severity score
            
        Returns:
            str: Reflection suggestion
        """
        if not bias_types:
            return "تحلیل شما متعادل به نظر می‌رسد. ادامه دهید!"
        
        primary_bias = bias_types[0]
        bias_info = self.bias_patterns.get(primary_bias, {})
        bias_name = bias_info.get('persian_name', primary_bias)
        
        suggestions = {
            'confirmation_bias': "آیا ممکن است شواهد مخالف را نادیده گرفته باشید؟ سعی کنید دیدگاه‌های مختلف را بررسی کنید.",
            'availability_bias': "آیا این تصمیم بر اساس تجربه‌های اخیر گرفته شده؟ سعی کنید داده‌های کلی‌تر را در نظر بگیرید.",
            'overconfidence': "آیا احتمال اشتباه بودن را در نظر گرفته‌اید؟ ممکن است کمی محتاط‌تر عمل کنید.",
            'anchoring': "آیا اطلاعات اولیه بر تصمیم شما تأثیر گذاشته؟ سعی کنید گزینه‌های مختلف را بررسی کنید.",
            'sunk_cost_fallacy': "آیا فقط به دلیل سرمایه‌گذاری قبلی ادامه می‌دهید؟ گاهی ترک کردن بهترین راه است.",
            'negativity_bias': "آیا روی جنبه‌های منفی تمرکز کرده‌اید؟ سعی کنید نکات مثبت را نیز ببینید.",
            'framing_effect': "آیا شیوه ارائه اطلاعات بر نظر شما تأثیر گذاشته؟ سعی کنید از زوایای مختلف نگاه کنید."
        }
        
        base_suggestion = suggestions.get(primary_bias, "در نظر گیری دیدگاه‌های مختلف می‌تواند مفید باشد.")
        
        if severity >= 0.7:
            return f"⚠️ **سوگیری {bias_name}** احتمالاً تأثیر قابل توجهی دارد. {base_suggestion}"
        elif severity >= 0.5:
            return f"📝 **سوگیری {bias_name}** ممکن است وجود داشته باشد. {base_suggestion}"
        else:
            return f"ℹ️ **سوگیری {bias_name}** نشانه‌های خفیفی دارد. {base_suggestion}"
    
    def analyze_bias(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for cognitive biases using hybrid approach.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: Bias analysis results
        """
        self.remember(f"Bias analysis for: {text[:50]}...")
        
        # Start with pattern-based analysis
        pattern_result = self._detect_bias_patterns(text)
        
        # Try GPT analysis as primary method
        gpt_result = self._analyze_bias_with_gpt(text)
        
        # Combine results
        if gpt_result and gpt_result.get('bias_detected'):
            # Use GPT results as primary
            bias_types = gpt_result.get('bias_types', [])
            severity = gpt_result.get('severity_score', 0.0)
            confidence = gpt_result.get('confidence', 0.0)
            method = 'gpt_analysis'
            reasoning = gpt_result.get('reasoning', '')
            
            # Convert bias types to Persian names
            persian_bias_names = []
            for bias in bias_types:
                bias_info = self.bias_patterns.get(bias, {})
                persian_name = bias_info.get('persian_name', bias)
                persian_bias_names.append(persian_name)
            
        elif pattern_result['detected_biases']:
            # Fallback to pattern matching
            bias_types = pattern_result['detected_biases']
            severity = max(pattern_result['severity_scores']) if pattern_result['severity_scores'] else 0.0
            confidence = 0.6  # Pattern matching confidence
            method = 'pattern_matching'
            reasoning = f"تشخیص بر اساس کلمات و عبارات کلیدی مرتبط با سوگیری"
            
            # Convert bias types to Persian names
            persian_bias_names = []
            for bias in bias_types:
                bias_info = self.bias_patterns.get(bias, {})
                persian_name = bias_info.get('persian_name', bias)
                persian_bias_names.append(persian_name)
                
        else:
            # No bias detected
            bias_types = []
            persian_bias_names = []
            severity = 0.0
            confidence = 0.8
            method = 'no_bias_detected'
            reasoning = "هیچ سوگیری قابل توجهی شناسایی نشد"
        
        # Generate reflection suggestion
        suggestion = self._generate_reflection_suggestion(bias_types, severity)
        
        # Save to database
        bias_log_id = str(uuid.uuid4())
        # Convert list to comma-separated string for database storage
        bias_types_str = ', '.join(bias_types) if bias_types else ''
        
        # Only save if there are actual biases detected or if severity > 0
        if bias_types_str or severity > 0:
            self._save_bias_log(bias_log_id, text, bias_types_str, severity, suggestion)
        
        self.remember(f"Bias analysis completed: {len(bias_types)} biases detected with {severity:.2f} severity")
        
        return {
            'bias_detected': len(bias_types) > 0,
            'bias_type': persian_bias_names,
            'severity_score': severity,
            'confidence': confidence,
            'suggestion': suggestion,
            'method': method,
            'reasoning': reasoning,
            'log_id': bias_log_id
        }
    
    def _save_bias_log(self, log_id: str, input_text: str, bias_types_str: str, severity: float, suggestion: str):
        """Save bias analysis to database"""
        try:
            session = SessionLocal()
            
            bias_log = BiasLog(
                id=log_id,
                timestamp=datetime.utcnow(),
                input_text=input_text,
                bias_type=bias_types_str,
                severity_score=severity,
                suggestion=suggestion
            )
            
            session.add(bias_log)
            session.commit()
            session.close()
            
            logger.info(f"[{self.name}] Bias log saved with ID: {log_id}")
            
        except Exception as e:
            logger.error(f"[{self.name}] Failed to save bias log: {e}")
    
    def get_bias_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent bias analysis logs.
        
        Args:
            limit (int): Number of logs to retrieve
            
        Returns:
            List[Dict]: Recent bias logs
        """
        try:
            session = SessionLocal()
            
            logs = session.query(BiasLog).order_by(BiasLog.timestamp.desc()).limit(limit).all()
            
            result = []
            for log in logs:
                # Convert comma-separated string back to list for display
                bias_types_list = log.bias_type.split(', ') if log.bias_type and log.bias_type != 'None' else []
                result.append({
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat(),
                    'input_text': log.input_text,
                    'bias_type': bias_types_list,
                    'severity_score': log.severity_score,
                    'suggestion': log.suggestion
                })
            
            session.close()
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Failed to retrieve bias logs: {e}")
            return []
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process message and analyze for cognitive biases.
        
        Args:
            message (str): The message to analyze
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing bias analysis
        """
        try:
            # Analyze for cognitive biases
            analysis = self.analyze_bias(message)
            
            # Format response
            if analysis['bias_detected']:
                bias_names = ', '.join(analysis['bias_type'])
                severity_bar = '█' * int(analysis['severity_score'] * 5) + '░' * (5 - int(analysis['severity_score'] * 5))
                
                response = f"""🧠 **تحلیل سوگیری شناختی:**

```json
{json.dumps(analysis, ensure_ascii=False, indent=2)}
```

**🔍 نتیجه تحلیل:**
• 🎯 **سوگیری شناسایی شده:** {bias_names}
• 📊 **شدت:** {severity_bar} ({analysis['severity_score']:.1%})
• 🤔 **اطمینان:** {analysis['confidence']:.1%}
• 🔬 **روش تشخیص:** {analysis['method']}

**💡 پیشنهاد تأملی:**
{analysis['suggestion']}

**📋 شناسه لاگ:** {analysis['log_id']}"""
                
            else:
                response = f"""🧠 **تحلیل سوگیری شناختی:**

```json
{json.dumps(analysis, ensure_ascii=False, indent=2)}
```

**✅ نتیجه تحلیل:**
• 🎯 **وضعیت:** هیچ سوگیری قابل توجهی شناسایی نشد
• 🤔 **اطمینان:** {analysis['confidence']:.1%}
• 💡 **پیشنهاد:** {analysis['suggestion']}

**📋 شناسه لاگ:** {analysis['log_id']}"""
            
            return {
                'success': True,
                'analysis': analysis,
                'response': response
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error in respond: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"خطا در تحلیل سوگیری: {e}"
            }