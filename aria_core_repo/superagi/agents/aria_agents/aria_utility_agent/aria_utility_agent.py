"""
Aria Utility Agent for text processing, summarization, and translation using OpenAI GPT.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from openai import OpenAI
from ..base_agent import BaseAgent


class AriaUtilityAgent(BaseAgent):
    """
    Agent for text processing, summarization, and translation using OpenAI GPT.
    Supports Persian-English translation and text improvement.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "agent_config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            agent_config = yaml.safe_load(f)
        
        super().__init__(
            name="AriaUtilityAgent",
            description="Agent for text processing, summarization, and translation using OpenAI GPT",
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
                self.log("OpenAI GPT integration ready for text processing")
            else:
                self.log("OpenAI API key not found, using fallback responses", "warning")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}", "error")
            self.openai_available = False
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response for text processing tasks.
        
        Args:
            message (str): The message to process
            context (Dict): Optional context information
            
        Returns:
            Dict: Response with processed text
        """
        try:
            # Store in memory
            self.remember(f"User: {message}")
            
            # Detect task type
            task_type = self._detect_task_type(message)
            
            if task_type == "translation":
                result = self._translate_text(message)
            elif task_type == "summarization":
                result = self._summarize_text(message)
            elif task_type == "improvement":
                result = self._improve_text(message)
            else:
                result = self._general_processing(message)
            
            response = {
                "response_id": f"{self.agent_id}_{hash(message) % 100000}",
                "content": result,
                "task_type": task_type,
                "handled_by": self.name,
                "timestamp": self.created_at.isoformat(),
                "success": True,
                "openai_used": self.openai_available,
                "error": None
            }
            
            self.remember(f"Agent: {result}")
            self.log(f"Processed {task_type} task: {result[:100]}...")
            
            return response
            
        except Exception as e:
            error_response = {
                "response_id": f"error_{hash(str(e)) % 100000}",
                "content": f"خطا در پردازش متن: {str(e)}",
                "task_type": "error",
                "handled_by": self.name,
                "timestamp": self.created_at.isoformat(),
                "success": False,
                "openai_used": False,
                "error": str(e)
            }
            
            self.log(f"Error processing text: {e}", "error")
            return error_response
    
    def _detect_task_type(self, message: str) -> str:
        """Detect the type of text processing task"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['translate', 'ترجمه', 'translation']):
            return "translation"
        elif any(word in message_lower for word in ['summarize', 'خلاصه', 'summary']):
            return "summarization"
        elif any(word in message_lower for word in ['improve', 'بهبود', 'correction']):
            return "improvement"
        else:
            return "general"
    
    def _translate_text(self, text: str) -> str:
        """Translate text between Persian and English"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a skilled translator. If the text is in Persian, translate it to English. If it's in English, translate it to Persian. Maintain the original meaning and tone."
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 500),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI translation error: {e}", "error")
                return f"خطا در ترجمه: {str(e)}"
        else:
            return "سرویس ترجمه در دسترس نیست. لطفاً دوباره تلاش کنید."
    
    def _summarize_text(self, text: str) -> str:
        """Summarize text content"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a skilled summarizer. Provide a concise summary of the text while maintaining key points. Respond in Persian."
                        },
                        {
                            "role": "user",
                            "content": f"خلاصه کن: {text}"
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 500),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI summarization error: {e}", "error")
                return f"خطا در خلاصه‌سازی: {str(e)}"
        else:
            return "سرویس خلاصه‌سازی در دسترس نیست. لطفاً دوباره تلاش کنید."
    
    def _improve_text(self, text: str) -> str:
        """Improve text quality and structure"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a skilled text editor. Improve the given text by fixing grammar, enhancing clarity, and maintaining the original meaning. Respond in the same language as the input."
                        },
                        {
                            "role": "user",
                            "content": f"بهبود بده: {text}"
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 500),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI improvement error: {e}", "error")
                return f"خطا در بهبود متن: {str(e)}"
        else:
            return "سرویس بهبود متن در دسترس نیست. لطفاً دوباره تلاش کنید."
    
    def _general_processing(self, text: str) -> str:
        """General text processing"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful text processing assistant. Process the given text and provide a useful response in Persian."
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 500),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI processing error: {e}", "error")
                return f"خطا در پردازش: {str(e)}"
        else:
            return f"متن دریافت شد: '{text}'. سرویس پردازش در دسترس نیست."
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "supported_tasks": [
                "translation",
                "summarization", 
                "improvement",
                "general_processing"
            ],
            "languages": ["persian", "english"],
            "openai_available": self.openai_available,
            "model": self.config.get("openai", {}).get("model", "gpt-4o")
        }