"""
Tool Agent for comprehensive task processing and analysis using OpenAI GPT API.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from openai import OpenAI
from datetime import datetime
from textblob import TextBlob
from .base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolAgent(BaseAgent):
    """
    Tool Agent that handles various text processing tasks with detailed logging.
    Uses OpenAI GPT API for task analysis and execution.
    """
    
    def __init__(self):
        super().__init__(
            name="ToolAgent",
            description="Comprehensive tool agent for task processing, analysis, and execution using OpenAI GPT"
        )
        
        # Initialize OpenAI client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Keywords for routing messages to this agent
        self.keywords = [
            "تحلیل", "analysis", "آنالیز", "analyze",
            "پردازش", "process", "processing",
            "استخراج", "extract", "extraction",
            "ابزار", "tool", "tools", "تول",
            "عملکرد", "operation", "کار", "work",
            "انجام", "execute", "اجرا", "run",
            "احساس", "احساسات", "sentiment", "emotion"
        ]
        
        # Task types mapping
        self.task_types = {
            "summary": ["خلاصه", "خلاصه‌سازی", "summary", "summarize"],
            "translation": ["ترجمه", "translate", "translation", "تبدیل"],
            "extraction": ["استخراج", "extract", "extraction", "بیرون کشیدن"],
            "analysis": ["تحلیل", "analyze", "analysis", "آنالیز"],
            "improvement": ["بهبود", "improve", "improvement", "تصحیح", "correct"],
            "conversion": ["تبدیل", "convert", "conversion", "تغییر"],
            "generation": ["تولید", "generate", "generation", "ایجاد", "create"],
            "sentiment": ["احساس", "احساسات", "sentiment", "emotion", "تحلیل احساس"]
        }
        
        logger.info(f"[{self.name}] Initialized with OpenAI GPT integration and task processing capabilities")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process message and generate appropriate response using OpenAI GPT.
        
        Args:
            message (str): The message to respond to
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the agent's reply
        """
        start_time = datetime.now()
        
        try:
            # Log the incoming message
            self.log(f"Processing task: {message[:100]}...")
            
            # Remember the user message
            self.remember(f"User: {message}")
            
            # Process the task
            task_result = self.process_task(message)
            
            # Create response
            response = {
                "response_id": f"tool_{hash(message + str(context)) % 100000}",
                "content": task_result["content"],
                "handled_by": self.name,
                "timestamp": self._get_current_timestamp(),
                "success": task_result["success"],
                "task_type": task_result["task_type"],
                "processing_time": task_result.get("processing_time", 0),
                "error": task_result.get("error")
            }
            
            # Remember the agent response
            self.remember(f"Agent: {task_result['content'][:100]}...")
            
            # Log completion
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            self.log(f"Task completed: {task_result['task_type']} in {processing_time:.2f}s - Success: {task_result['success']}")
            
            return response
            
        except Exception as e:
            error_message = f"Error processing task: {str(e)}"
            self.log(error_message, level="error")
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                "response_id": f"tool_error_{hash(message) % 100000}",
                "content": f"متأسفانه در پردازش وظیفه شما مشکلی پیش آمد: {str(e)}",
                "handled_by": self.name,
                "timestamp": self._get_current_timestamp(),
                "success": False,
                "processing_time": processing_time,
                "error": error_message
            }
    
    def process_task(self, message: str) -> Dict[str, Any]:
        """
        Process the task based on message content and return detailed results.
        
        Args:
            message (str): The input message containing the task
            
        Returns:
            Dict: Task processing results
        """
        start_time = datetime.now()
        
        try:
            # Determine task type
            task_type, confidence = self._analyze_task_type(message)
            
            self.log(f"Task type identified: {task_type} (confidence: {confidence:.2f})")
            
            # Extract content from message
            content = self._extract_task_content(message, task_type)
            
            # Execute the task based on type
            if task_type == "summary":
                result = self._execute_summary_task(content)
            elif task_type == "translation":
                result = self._execute_translation_task(content)
            elif task_type == "extraction":
                result = self._execute_extraction_task(content)
            elif task_type == "analysis":
                result = self._execute_analysis_task(content)
            elif task_type == "improvement":
                result = self._execute_improvement_task(content)
            elif task_type == "conversion":
                result = self._execute_conversion_task(content)
            elif task_type == "generation":
                result = self._execute_generation_task(content)
            elif task_type == "sentiment":
                result = self._execute_sentiment_task(content)
            else:
                result = self._execute_general_task(message)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                "content": result,
                "success": True,
                "task_type": task_type,
                "confidence": confidence,
                "processing_time": processing_time,
                "error": None
            }
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            self.log(f"Task processing failed: {str(e)}", level="error")
            
            return {
                "content": f"خطا در انجام وظیفه: {str(e)}",
                "success": False,
                "task_type": "unknown",
                "confidence": 0.0,
                "processing_time": processing_time,
                "error": str(e)
            }
    
    def _analyze_task_type(self, message: str) -> Tuple[str, float]:
        """
        Analyze message to determine task type and confidence level.
        
        Args:
            message (str): Input message
            
        Returns:
            Tuple[str, float]: Task type and confidence score
        """
        message_lower = message.lower()
        
        # Check each task type for keyword matches
        best_match = "general"
        best_score = 0.0
        
        for task_type, keywords in self.task_types.items():
            score = 0.0
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1.0
            
            # Normalize score by number of keywords
            normalized_score = score / len(keywords) if keywords else 0.0
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_match = task_type
        
        return best_match, best_score
    
    def _extract_task_content(self, message: str, task_type: str) -> str:
        """
        Extract the main content for processing from the message.
        
        Args:
            message (str): Original message
            task_type (str): Identified task type
            
        Returns:
            str: Extracted content
        """
        # Remove task-specific command words
        content = message
        
        # Get keywords for the identified task type
        if task_type in self.task_types:
            for keyword in self.task_types[task_type]:
                content = content.replace(keyword, "").strip()
        
        # Remove common separators
        content = content.replace(":", "").replace("کن", "").strip()
        
        return content if content else message
    
    def _execute_summary_task(self, content: str) -> str:
        """Execute summarization task."""
        try:
            prompt = f"""
            لطفاً متن زیر را به صورت خلاصه و مفید خلاصه کنید:
            - نکات کلیدی را حفظ کنید
            - واضح و مفهوم باشد
            - به زبان فارسی پاسخ دهید
            
            متن: {content}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            return f"📝 **خلاصه متن:**\n\n{result}"
            
        except Exception as e:
            return f"خطا در خلاصه‌سازی: {str(e)}"
    
    def _execute_translation_task(self, content: str) -> str:
        """Execute translation task."""
        try:
            prompt = f"""
            لطفاً متن زیر را ترجمه کنید:
            - اگر فارسی است، به انگلیسی ترجمه کنید
            - اگر انگلیسی است، به فارسی ترجمه کنید
            - اگر زبان دیگری است، به فارسی ترجمه کنید
            
            متن: {content}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return f"🌐 **ترجمه:**\n\n{result}"
            
        except Exception as e:
            return f"خطا در ترجمه: {str(e)}"
    
    def _execute_extraction_task(self, content: str) -> str:
        """Execute information extraction task."""
        try:
            prompt = f"""
            لطفاً از متن زیر اطلاعات مهم را استخراج کنید:
            - نام‌ها، تاریخ‌ها، اعداد
            - نکات کلیدی و مفاهیم اصلی
            - به صورت فهرست ارائه دهید
            
            متن: {content}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.5
            )
            
            result = response.choices[0].message.content
            return f"🔍 **اطلاعات استخراج شده:**\n\n{result}"
            
        except Exception as e:
            return f"خطا در استخراج اطلاعات: {str(e)}"
    
    def _execute_analysis_task(self, content: str) -> str:
        """Execute analysis task."""
        try:
            prompt = f"""
            لطفاً متن زیر را تحلیل کنید:
            - موضوع اصلی و زیرموضوعات
            - نقاط قوت و ضعف
            - نتیجه‌گیری و پیشنهادات
            
            متن: {content}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.6
            )
            
            result = response.choices[0].message.content
            return f"📊 **تحلیل متن:**\n\n{result}"
            
        except Exception as e:
            return f"خطا در تحلیل: {str(e)}"
    
    def _execute_improvement_task(self, content: str) -> str:
        """Execute text improvement task."""
        try:
            prompt = f"""
            لطفاً متن زیر را بهبود دهید:
            - املا و گرامر را تصحیح کنید
            - ساختار جملات را بهبود دهید
            - وضوح و خوانایی را افزایش دهید
            
            متن: {content}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.4
            )
            
            result = response.choices[0].message.content
            return f"✨ **متن بهبود یافته:**\n\n{result}"
            
        except Exception as e:
            return f"خطا در بهبود متن: {str(e)}"
    
    def _execute_conversion_task(self, content: str) -> str:
        """Execute conversion task."""
        try:
            prompt = f"""
            لطفاً متن زیر را بر اساس درخواست تبدیل کنید:
            - فرمت، ساختار یا نوع محتوا را تغییر دهید
            - حفظ معنا و مفهوم اصلی
            
            متن: {content}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.5
            )
            
            result = response.choices[0].message.content
            return f"🔄 **متن تبدیل شده:**\n\n{result}"
            
        except Exception as e:
            return f"خطا در تبدیل: {str(e)}"
    
    def _execute_generation_task(self, content: str) -> str:
        """Execute content generation task."""
        try:
            prompt = f"""
            بر اساس موضوع زیر، محتوای مفید و کاربردی تولید کنید:
            - خلاقانه و مفید باشد
            - ساختار مناسب داشته باشد
            - به زبان فارسی باشد
            
            موضوع: {content}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=900,
                temperature=0.8
            )
            
            result = response.choices[0].message.content
            return f"🎯 **محتوای تولید شده:**\n\n{result}"
            
        except Exception as e:
            return f"خطا در تولید محتوا: {str(e)}"
    
    def _execute_sentiment_task(self, content: str) -> str:
        """Execute sentiment analysis task using TextBlob."""
        try:
            # Analyze sentiment using TextBlob
            sentiment_result = self.analyze_sentiment(content)
            
            # Create detailed response
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Create emoji based on sentiment
            sentiment_emoji = {
                "مثبت": "😊",
                "منفی": "😞", 
                "خنثی": "😐"
            }
            
            result = f"""**تحلیل احساسات متن:**

📝 **متن:** {content}

{sentiment_emoji.get(sentiment_result, "🤔")} **نتیجه:** {sentiment_result}

📊 **جزئیات تحلیل:**
• میزان احساس (Polarity): {polarity:.3f} (از -1 تا +1)
• میزان ذهنی‌بودن (Subjectivity): {subjectivity:.3f} (از 0 تا 1)

📋 **توضیح:**
• مثبت: احساس خوشحالی، رضایت یا مطلوبیت
• منفی: احساس ناراحتی، نارضایتی یا نامطلوبیت  
• خنثی: احساس معمولی بدون گرایش خاص"""
            
            return result
            
        except Exception as e:
            return f"خطا در تحلیل احساسات: {str(e)}"
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text using TextBlob.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            str: Sentiment label in Persian ("مثبت", "منفی", "خنثی")
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return "مثبت"
            elif polarity < -0.1:
                return "منفی"
            else:
                return "خنثی"
                
        except Exception as e:
            self.log(f"Error in sentiment analysis: {e}", level="error")
            return "خنثی"
    
    def _execute_general_task(self, message: str) -> str:
        """Execute general task when specific type is not identified."""
        try:
            prompt = f"""
            شما یک دستیار هوشمند و ابزار پردازش متن هستید.
            لطفاً به درخواست زیر پاسخ مفید و کاربردی دهید:
            
            {message}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            return f"🔧 **پاسخ ابزار:**\n\n{result}"
            
        except Exception as e:
            return f"خطا در پردازش عمومی: {str(e)}"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return [
            "خلاصه‌سازی متن",
            "ترجمه چندزبانه", 
            "استخراج اطلاعات",
            "تحلیل محتوا",
            "بهبود متن",
            "تبدیل فرمت",
            "تولید محتوا",
            "تحلیل احساسات",
            "پردازش عمومی"
        ]
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about processed tasks."""
        # This could be enhanced to track actual statistics
        return {
            "supported_tasks": len(self.task_types),
            "total_capabilities": len(self.get_capabilities()),
            "language_support": ["فارسی", "English"],
            "processing_modes": ["خلاصه", "ترجمه", "تحلیل", "بهبود", "تبدیل", "تولید", "احساسات"]
        }