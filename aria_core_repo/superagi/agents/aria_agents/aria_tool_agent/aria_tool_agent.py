"""
Aria Tool Agent for advanced task processing and analysis.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from openai import OpenAI
from textblob import TextBlob
from ..base_agent import BaseAgent


class AriaToolAgent(BaseAgent):
    """
    Advanced task processing agent with comprehensive capabilities.
    Supports task detection, sentiment analysis, and multi-task processing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "agent_config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            agent_config = yaml.safe_load(f)
        
        super().__init__(
            name="AriaToolAgent",
            description="Advanced task processing agent with comprehensive capabilities",
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
                self.log("OpenAI GPT integration ready for task processing")
            else:
                self.log("OpenAI API key not found, using fallback responses", "warning")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}", "error")
            self.openai_available = False
        
        # Initialize supported tasks
        self.supported_tasks = self.config.get("task_config", {}).get("supported_tasks", [])
        self.confidence_threshold = self.config.get("task_config", {}).get("confidence_threshold", 0.7)
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response for task processing.
        
        Args:
            message (str): The message to process
            context (Dict): Optional context information
            
        Returns:
            Dict: Response with processed task results
        """
        try:
            # Store in memory
            self.remember(f"User: {message}")
            
            # Detect task type and confidence
            task_detection = self._detect_task_type(message)
            task_type = task_detection.get("task_type", "general")
            confidence = task_detection.get("confidence", 0.5)
            
            # Process based on task type
            if task_type == "sentiment_analysis":
                result = self._analyze_sentiment(message)
            elif task_type == "summarization":
                result = self._summarize_text(message)
            elif task_type == "analysis":
                result = self._analyze_text(message)
            elif task_type == "extraction":
                result = self._extract_information(message)
            elif task_type == "improvement":
                result = self._improve_text(message)
            else:
                result = self._general_processing(message)
            
            response = {
                "response_id": f"{self.agent_id}_{hash(message) % 100000}",
                "content": result,
                "task_type": task_type,
                "confidence": confidence,
                "handled_by": self.name,
                "timestamp": self.created_at.isoformat(),
                "success": True,
                "openai_used": self.openai_available,
                "error": None
            }
            
            self.remember(f"Agent: {result}")
            self.log(f"Processed {task_type} task with confidence {confidence:.2f}")
            
            return response
            
        except Exception as e:
            error_response = {
                "response_id": f"error_{hash(str(e)) % 100000}",
                "content": f"خطا در پردازش وظیفه: {str(e)}",
                "task_type": "error",
                "confidence": 0.0,
                "handled_by": self.name,
                "timestamp": self.created_at.isoformat(),
                "success": False,
                "openai_used": False,
                "error": str(e)
            }
            
            self.log(f"Error processing task: {e}", "error")
            return error_response
    
    def _detect_task_type(self, message: str) -> Dict[str, Any]:
        """Detect the type of task with confidence scoring"""
        message_lower = message.lower()
        
        # Task detection patterns
        patterns = {
            "sentiment_analysis": ["sentiment", "احساس", "حال", "feel", "emotion"],
            "summarization": ["summarize", "خلاصه", "summary", "شرح"],
            "analysis": ["analyze", "تحلیل", "بررسی", "analysis"],
            "extraction": ["extract", "استخراج", "بیرون", "find"],
            "improvement": ["improve", "بهبود", "بهتر", "enhance"],
            "translation": ["translate", "ترجمه", "translation"],
            "conversion": ["convert", "تبدیل", "change"],
            "generation": ["generate", "تولید", "create"]
        }
        
        # Calculate confidence for each task type
        task_scores = {}
        for task_type, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                task_scores[task_type] = score / len(keywords)
        
        if task_scores:
            # Get the task with highest confidence
            best_task = max(task_scores, key=task_scores.get)
            confidence = task_scores[best_task]
            
            return {
                "task_type": best_task,
                "confidence": min(confidence, 1.0),
                "all_scores": task_scores
            }
        
        return {
            "task_type": "general",
            "confidence": 0.5,
            "all_scores": {}
        }
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment using TextBlob with Persian support"""
        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            
            # Convert to Persian labels
            if sentiment_score > 0.1:
                sentiment_label = "مثبت 😊"
            elif sentiment_score < -0.1:
                sentiment_label = "منفی 😞"
            else:
                sentiment_label = "خنثی 😐"
            
            return f"تحلیل احساسات: {sentiment_label} (امتیاز: {sentiment_score:.2f})"
            
        except Exception as e:
            self.log(f"Sentiment analysis error: {e}", "error")
            return f"خطا در تحلیل احساسات: {str(e)}"
    
    def _summarize_text(self, text: str) -> str:
        """Summarize text using OpenAI"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a skilled summarizer. Provide a concise summary in Persian."
                        },
                        {
                            "role": "user",
                            "content": f"خلاصه کن: {text}"
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 800),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI summarization error: {e}", "error")
                return f"خطا در خلاصه‌سازی: {str(e)}"
        else:
            return "سرویس خلاصه‌سازی در دسترس نیست."
    
    def _analyze_text(self, text: str) -> str:
        """Analyze text using OpenAI"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a skilled text analyst. Provide detailed analysis in Persian."
                        },
                        {
                            "role": "user",
                            "content": f"تحلیل کن: {text}"
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 800),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI analysis error: {e}", "error")
                return f"خطا در تحلیل: {str(e)}"
        else:
            return "سرویس تحلیل در دسترس نیست."
    
    def _extract_information(self, text: str) -> str:
        """Extract key information from text"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an information extraction expert. Extract key information and present it in Persian."
                        },
                        {
                            "role": "user",
                            "content": f"اطلاعات کلیدی را استخراج کن: {text}"
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 800),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI extraction error: {e}", "error")
                return f"خطا در استخراج: {str(e)}"
        else:
            return "سرویس استخراج در دسترس نیست."
    
    def _improve_text(self, text: str) -> str:
        """Improve text quality"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a text improvement expert. Enhance the given text while maintaining its meaning."
                        },
                        {
                            "role": "user",
                            "content": f"بهبود بده: {text}"
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 800),
                    temperature=self.config.get("openai", {}).get("temperature", 0.3)
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log(f"OpenAI improvement error: {e}", "error")
                return f"خطا در بهبود: {str(e)}"
        else:
            return "سرویس بهبود در دسترس نیست."
    
    def _general_processing(self, text: str) -> str:
        """General text processing"""
        if self.openai_available:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful processing assistant. Process the text and provide a useful response in Persian."
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ],
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 800),
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
            "supported_tasks": self.supported_tasks,
            "confidence_threshold": self.confidence_threshold,
            "openai_available": self.openai_available,
            "textblob_available": True,
            "model": self.config.get("openai", {}).get("model", "gpt-4o")
        }