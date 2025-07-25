"""
Utility Agent for text processing, summarization, and translation using OpenAI GPT API.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from .base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UtilityAgent(BaseAgent):
    """
    Utility Agent that handles text processing tasks like summarization and translation.
    Uses OpenAI GPT API for advanced text processing capabilities.
    """
    
    def __init__(self):
        super().__init__(
            name="UtilityAgent",
            description="Agent for text processing, summarization, and translation using OpenAI GPT"
        )
        
        # Initialize OpenAI client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Keywords for routing messages to this agent
        self.keywords = [
            "خلاصه", "خلاصه‌سازی", "summari", "summary",
            "ترجمه", "translate", "translation",
            "تبدیل", "convert", "پردازش متن", "text processing",
            "تحلیل متن", "text analysis", "بهبود متن", "improve text"
        ]
        
        logger.info(f"[{self.name}] Initialized with OpenAI GPT integration")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process message and generate appropriate response using OpenAI GPT.
        
        Args:
            message (str): The message to respond to
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the agent's reply
        """
        try:
            # Log the incoming message
            self.log(f"Processing message: {message[:50]}...")
            
            # Remember the user message
            self.remember(f"User: {message}")
            
            # Determine the type of processing needed
            task_type = self._determine_task_type(message)
            
            # Process the message based on task type
            if task_type == "summarize":
                response_content = self._summarize_text(message)
            elif task_type == "translate":
                response_content = self._translate_text(message)
            elif task_type == "improve":
                response_content = self._improve_text(message)
            else:
                response_content = self._general_processing(message)
            
            # Create response
            response = {
                "response_id": f"util_{hash(message + str(context)) % 100000}",
                "content": response_content,
                "handled_by": self.name,
                "timestamp": self._get_current_timestamp(),
                "success": True,
                "task_type": task_type,
                "error": None
            }
            
            # Remember the agent response
            self.remember(f"Agent: {response_content[:100]}...")
            
            self.log(f"Generated response for {task_type} task")
            return response
            
        except Exception as e:
            error_message = f"Error processing message: {str(e)}"
            self.log(error_message, level="error")
            
            return {
                "response_id": f"util_error_{hash(message) % 100000}",
                "content": f"متأسفانه در پردازش پیام شما مشکلی پیش آمد: {str(e)}",
                "handled_by": self.name,
                "timestamp": self._get_current_timestamp(),
                "success": False,
                "error": error_message
            }
    
    def _determine_task_type(self, message: str) -> str:
        """
        Determine the type of task based on message content.
        
        Args:
            message (str): The input message
            
        Returns:
            str: Task type (summarize, translate, improve, general)
        """
        message_lower = message.lower()
        
        # Check for summarization keywords
        if any(keyword in message_lower for keyword in ["خلاصه", "summari", "summary"]):
            return "summarize"
        
        # Check for translation keywords
        if any(keyword in message_lower for keyword in ["ترجمه", "translate", "translation"]):
            return "translate"
        
        # Check for text improvement keywords
        if any(keyword in message_lower for keyword in ["بهبود", "improve", "تصحیح", "correct"]):
            return "improve"
        
        return "general"
    
    def _summarize_text(self, message: str) -> str:
        """
        Summarize the given text using OpenAI GPT.
        
        Args:
            message (str): Text to summarize
            
        Returns:
            str: Summarized text
        """
        try:
            # Extract text to summarize (remove command words)
            text_to_summarize = self._extract_content_from_message(message)
            
            prompt = f"""
            لطفاً متن زیر را به صورت خلاصه و مفید خلاصه کنید. خلاصه باید:
            - نکات کلیدی را شامل شود
            - واضح و مفهوم باشد
            - به زبان فارسی باشد
            
            متن:
            {text_to_summarize}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content
            return f"📝 **خلاصه متن:**\n\n{summary}"
            
        except Exception as e:
            return f"متأسفانه در خلاصه‌سازی متن مشکلی پیش آمد: {str(e)}"
    
    def _translate_text(self, message: str) -> str:
        """
        Translate the given text using OpenAI GPT.
        
        Args:
            message (str): Text to translate
            
        Returns:
            str: Translated text
        """
        try:
            # Extract text to translate
            text_to_translate = self._extract_content_from_message(message)
            
            # Detect language and translate accordingly
            prompt = f"""
            لطفاً متن زیر را تشخیص دهید و ترجمه کنید:
            - اگر متن فارسی است، به انگلیسی ترجمه کنید
            - اگر متن انگلیسی است، به فارسی ترجمه کنید
            - اگر زبان دیگری است، به فارسی ترجمه کنید
            
            فقط ترجمه را برگردانید، بدون توضیح اضافی.
            
            متن:
            {text_to_translate}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            translation = response.choices[0].message.content
            return f"🌐 **ترجمه:**\n\n{translation}"
            
        except Exception as e:
            return f"متأسفانه در ترجمه متن مشکلی پیش آمد: {str(e)}"
    
    def _improve_text(self, message: str) -> str:
        """
        Improve the given text using OpenAI GPT.
        
        Args:
            message (str): Text to improve
            
        Returns:
            str: Improved text
        """
        try:
            text_to_improve = self._extract_content_from_message(message)
            
            prompt = f"""
            لطفاً متن زیر را بهبود دهید:
            - املا و گرامر را تصحیح کنید
            - جملات را روان‌تر کنید
            - ساختار را بهبود دهید
            - وضوح و خوانایی را افزایش دهید
            
            متن اصلی:
            {text_to_improve}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.5
            )
            
            improved_text = response.choices[0].message.content
            return f"✨ **متن بهبود یافته:**\n\n{improved_text}"
            
        except Exception as e:
            return f"متأسفانه در بهبود متن مشکلی پیش آمد: {str(e)}"
    
    def _general_processing(self, message: str) -> str:
        """
        General text processing using OpenAI GPT.
        
        Args:
            message (str): Message to process
            
        Returns:
            str: Processed response
        """
        try:
            prompt = f"""
            شما یک دستیار هوشمند برای پردازش متن هستید. 
            لطفاً به پیام زیر پاسخ مفید و کاربردی دهید:
            
            {message}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"متأسفانه در پردازش پیام مشکلی پیش آمد: {str(e)}"
    
    def _extract_content_from_message(self, message: str) -> str:
        """
        Extract the main content from a message by removing command words.
        
        Args:
            message (str): Original message
            
        Returns:
            str: Extracted content
        """
        # Remove common command words
        command_words = [
            "خلاصه کن", "خلاصه‌سازی", "summarize", "summary",
            "ترجمه کن", "translate", "translation",
            "بهبود بده", "improve", "تصحیح کن", "correct"
        ]
        
        content = message
        for word in command_words:
            content = content.replace(word, "").strip()
        
        # Remove extra whitespace
        content = " ".join(content.split())
        
        return content if content else message
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            str: Current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities.
        
        Returns:
            List[str]: List of capabilities
        """
        return [
            "خلاصه‌سازی متن",
            "ترجمه متن",
            "بهبود متن",
            "تحلیل متن",
            "پردازش زبان طبیعی"
        ]