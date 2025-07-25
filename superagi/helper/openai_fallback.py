
import openai
import logging
import time
from typing import Dict, Any, Optional, List
import random

class OpenAIFallbackManager:
    """
    OpenAI Fallback Manager - Handle API failures and implement backup strategies
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Fallback configuration
        self.max_retries = self.config.get("max_retries", 3)
        self.base_delay = self.config.get("base_delay", 1)
        self.max_delay = self.config.get("max_delay", 60)
        self.fallback_models = self.config.get("fallback_models", [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "text-davinci-003"
        ])
        
        # Error tracking
        self.error_counts = {}
        self.last_success = {}
        
    def make_request_with_fallback(self, request_func, *args, **kwargs) -> Any:
        """
        Make OpenAI request with automatic fallback and retry logic
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Try primary request
                result = request_func(*args, **kwargs)
                self._record_success(request_func.__name__)
                return result
                
            except openai.RateLimitError as e:
                self.logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
                last_exception = e
                self._handle_rate_limit(attempt)
                
            except openai.APIError as e:
                self.logger.error(f"API error on attempt {attempt + 1}: {e}")
                last_exception = e
                self._handle_api_error(e, attempt)
                
            except openai.AuthenticationError as e:
                self.logger.error(f"Authentication error: {e}")
                raise e  # Don't retry auth errors
                
            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                last_exception = e
                if attempt < self.max_retries - 1:
                    self._exponential_backoff(attempt)
        
        # All retries failed, try fallback strategies
        return self._try_fallback_strategies(request_func, last_exception, *args, **kwargs)
    
    def _handle_rate_limit(self, attempt: int):
        """Handle rate limit errors with exponential backoff"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        jitter = random.uniform(0, 0.1) * delay
        total_delay = delay + jitter
        
        self.logger.info(f"Rate limited. Waiting {total_delay:.2f} seconds...")
        time.sleep(total_delay)
    
    def _handle_api_error(self, error: openai.APIError, attempt: int):
        """Handle API errors with appropriate delays"""
        if "server_error" in str(error).lower():
            # Server errors - exponential backoff
            self._exponential_backoff(attempt)
        else:
            # Other API errors - shorter delay
            time.sleep(self.base_delay)
    
    def _exponential_backoff(self, attempt: int):
        """Implement exponential backoff with jitter"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        jitter = random.uniform(0, 0.1) * delay
        time.sleep(delay + jitter)
    
    def _try_fallback_strategies(self, request_func, last_exception, *args, **kwargs) -> Any:
        """Try fallback strategies when primary requests fail"""
        self.logger.warning("Primary requests failed, trying fallback strategies...")
        
        # Strategy 1: Try different models
        if "model" in kwargs:
            original_model = kwargs["model"]
            for fallback_model in self.fallback_models:
                if fallback_model != original_model:
                    try:
                        self.logger.info(f"Trying fallback model: {fallback_model}")
                        kwargs["model"] = fallback_model
                        result = request_func(*args, **kwargs)
                        self._record_fallback_success(fallback_model)
                        return result
                    except Exception as e:
                        self.logger.warning(f"Fallback model {fallback_model} failed: {e}")
                        continue
        
        # Strategy 2: Reduce request complexity
        simplified_result = self._try_simplified_request(request_func, *args, **kwargs)
        if simplified_result:
            return simplified_result
        
        # Strategy 3: Return cached or default response
        cached_result = self._get_cached_response(request_func, *args, **kwargs)
        if cached_result:
            return cached_result
        
        # All fallback strategies failed
        self.logger.error("All fallback strategies failed")
        raise last_exception
    
    def _try_simplified_request(self, request_func, *args, **kwargs) -> Optional[Any]:
        """Try a simplified version of the request"""
        try:
            # Reduce max_tokens if present
            if "max_tokens" in kwargs and kwargs["max_tokens"] > 100:
                original_max_tokens = kwargs["max_tokens"]
                kwargs["max_tokens"] = min(100, original_max_tokens // 2)
                self.logger.info(f"Trying simplified request with max_tokens={kwargs['max_tokens']}")
                result = request_func(*args, **kwargs)
                self._record_simplified_success()
                return result
        except Exception as e:
            self.logger.warning(f"Simplified request failed: {e}")
        
        return None
    
    def _get_cached_response(self, request_func, *args, **kwargs) -> Optional[Any]:
        """Get cached response or generate default response"""
        # In a real implementation, this would check a cache
        # For now, return a simple default response structure
        
        if "chat" in request_func.__name__.lower():
            return self._get_default_chat_response()
        elif "completion" in request_func.__name__.lower():
            return self._get_default_completion_response()
        
        return None
    
    def _get_default_chat_response(self) -> Dict[str, Any]:
        """Get default chat completion response"""
        return {
            "id": "fallback-response",
            "object": "chat.completion",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "I apologize, but I'm experiencing technical difficulties. Please try your request again."
                },
                "finish_reason": "fallback"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 15,
                "total_tokens": 15
            }
        }
    
    def _get_default_completion_response(self) -> Dict[str, Any]:
        """Get default text completion response"""
        return {
            "id": "fallback-response",
            "object": "text_completion",
            "choices": [{
                "text": "I apologize, but I'm experiencing technical difficulties. Please try your request again.",
                "finish_reason": "fallback"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 15,
                "total_tokens": 15
            }
        }
    
    def _record_success(self, function_name: str):
        """Record successful request"""
        self.last_success[function_name] = time.time()
        if function_name in self.error_counts:
            self.error_counts[function_name] = 0
    
    def _record_fallback_success(self, model: str):
        """Record successful fallback"""
        self.logger.info(f"Fallback successful with model: {model}")
    
    def _record_simplified_success(self):
        """Record successful simplified request"""
        self.logger.info("Simplified request successful")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of OpenAI integration"""
        current_time = time.time()
        status = {
            "status": "healthy",
            "last_success_times": {},
            "error_counts": self.error_counts.copy(),
            "fallback_models_available": len(self.fallback_models)
        }
        
        for func_name, last_success_time in self.last_success.items():
            time_since_success = current_time - last_success_time
            status["last_success_times"][func_name] = {
                "timestamp": last_success_time,
                "seconds_ago": int(time_since_success)
            }
            
            # Mark as unhealthy if no success in last 5 minutes and errors > 5
            if time_since_success > 300 and self.error_counts.get(func_name, 0) > 5:
                status["status"] = "degraded"
        
        return status

# Global fallback manager instance
fallback_manager = OpenAIFallbackManager()

def with_fallback(func):
    """Decorator to add fallback support to OpenAI functions"""
    def wrapper(*args, **kwargs):
        return fallback_manager.make_request_with_fallback(func, *args, **kwargs)
    return wrapper
