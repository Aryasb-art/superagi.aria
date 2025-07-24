"""
Aria Goal Agent - Advanced goal and intent detection agent with hybrid analysis.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
from database import get_db
from sqlalchemy.orm import Session
from ..base_agent import BaseAgent
from sqlalchemy import text


class AriaGoalAgent(BaseAgent):
    """
    Advanced goal and intent detection agent with hybrid analysis.
    Combines pattern recognition with OpenAI GPT for comprehensive goal inference.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "agent_config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            agent_config = yaml.safe_load(f)
        
        super().__init__(
            name="AriaGoalAgent",
            description="Advanced goal and intent detection agent with hybrid analysis",
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
                self.log("OpenAI GPT integration ready for goal inference")
            else:
                self.log("OpenAI API key not found, using pattern-based analysis", "warning")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}", "error")
            self.openai_available = False
        
        # Initialize database
        self._initialize_database()
        
        # Load configuration
        self.intent_categories = self.config.get("intent_categories", [])
        self.confidence_levels = self.config.get("confidence_levels", [])
        
        # Pattern-based detection keywords
        self.goal_patterns = {
            "action/initiation": ["want to", "going to", "plan to", "می‌خواهم", "قصد دارم", "برنامه دارم"],
            "decision/choice": ["should I", "which one", "better", "باید", "کدام", "بهتر"],
            "concern/worry": ["worried", "concerned", "anxious", "نگران", "نگرانی", "مضطرب"],
            "motivation/energy": ["motivated", "energy", "drive", "انگیزه", "انرژی", "پشتکار"],
            "confusion/help": ["confused", "help", "don't know", "گیج", "کمک", "نمی‌دانم"],
            "planning/organization": ["plan", "organize", "schedule", "برنامه", "سازماندهی", "زمان‌بندی"],
            "learning/knowledge": ["learn", "study", "understand", "یاد بگیرم", "مطالعه", "درک"],
            "health/wellness": ["health", "exercise", "wellness", "سلامتی", "ورزش", "تندرستی"],
            "relationship/social": ["relationship", "social", "friend", "رابطه", "اجتماعی", "دوست"],
            "career/work": ["career", "work", "job", "شغل", "کار", "حرفه"],
            "general/other": ["general", "other", "misc", "عمومی", "سایر", "متفرقه"]
        }
        
        self.log("Goal inference agent initialized with hybrid analysis")
    
    def _initialize_database(self):
        """Initialize database table for goal inferences"""
        try:
            db = next(get_db())
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS goal_inferences (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER DEFAULT 1,
                    input_text TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    intent_category VARCHAR(50),
                    confidence VARCHAR(20),
                    detected_by VARCHAR(20),
                    context_data JSONB,
                    analysis_details JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
            self.log("Goal inferences table ready")
        except Exception as e:
            self.log(f"Database initialization error: {e}", "error")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze message for goal and intent detection.
        
        Args:
            message (str): The message to analyze
            context (Dict): Optional context information
            
        Returns:
            Dict: Response with goal analysis results
        """
        try:
            # Store in memory
            self.remember(f"User: {message}")
            
            # Perform hybrid analysis
            analysis_result = self._analyze_goal_and_intent(message, context)
            
            # Store in database
            self._store_goal_inference(message, analysis_result, context)
            
            # Format response
            response_content = self._format_goal_response(analysis_result)
            
            response = {
                "response_id": f"{self.agent_id}_{hash(message) % 100000}",
                "content": response_content,
                "goal_analysis": analysis_result,
                "handled_by": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "openai_used": self.openai_available,
                "error": None
            }
            
            self.remember(f"Agent: {response_content}")
            self.log(f"Goal analysis completed with {analysis_result['confidence']} confidence")
            
            return response
            
        except Exception as e:
            error_response = {
                "response_id": f"error_{hash(str(e)) % 100000}",
                "content": f"خطا در تشخیص هدف: {str(e)}",
                "handled_by": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "openai_used": False,
                "error": str(e)
            }
            
            self.log(f"Error in goal analysis: {e}", "error")
            return error_response
    
    def _analyze_goal_and_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Hybrid goal and intent analysis"""
        # Try pattern-based analysis first
        pattern_result = self._pattern_based_analysis(message)
        
        # If high confidence from patterns, use that
        if pattern_result['confidence'] >= 0.8:
            return {
                **pattern_result,
                "detected_by": "pattern",
                "analysis_method": "pattern_based",
                "context_data": context or {}
            }
        
        # Otherwise, use OpenAI analysis
        if self.openai_available:
            openai_result = self._openai_analysis(message, context)
            return {
                **openai_result,
                "detected_by": "openai",
                "analysis_method": "gpt_powered",
                "context_data": context or {}
            }
        
        # Fallback to pattern result
        return {
            **pattern_result,
            "detected_by": "pattern",
            "analysis_method": "pattern_fallback",
            "context_data": context or {}
        }
    
    def _pattern_based_analysis(self, message: str) -> Dict[str, Any]:
        """Pattern-based goal detection"""
        message_lower = message.lower()
        
        # Score each intent category
        category_scores = {}
        for category, patterns in self.goal_patterns.items():
            score = sum(1 for pattern in patterns if pattern in message_lower)
            if score > 0:
                category_scores[category] = score / len(patterns)
        
        if category_scores:
            # Get best category
            best_category = max(category_scores, key=category_scores.get)
            confidence_score = category_scores[best_category]
            
            # Determine confidence level
            if confidence_score >= 0.7:
                confidence = "high"
            elif confidence_score >= 0.4:
                confidence = "medium"
            else:
                confidence = "low"
            
            # Generate simple goal statement
            goal = self._generate_simple_goal(message, best_category)
            
            return {
                "goal": goal,
                "intent_category": best_category,
                "confidence": confidence,
                "confidence_score": confidence_score,
                "category_scores": category_scores
            }
        
        return {
            "goal": "عمومی - نیاز به بررسی بیشتر",
            "intent_category": "general/other",
            "confidence": "low",
            "confidence_score": 0.3,
            "category_scores": {}
        }
    
    def _openai_analysis(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """OpenAI-powered goal analysis"""
        try:
            system_prompt = f"""
            You are an expert in goal and intent detection. Analyze the user's message and provide:
            1. A clear goal statement
            2. Intent category from: {', '.join(self.intent_categories)}
            3. Confidence level (high/medium/low)
            
            Respond in JSON format with Persian goal statement:
            {{
                "goal": "goal in Persian",
                "intent_category": "category",
                "confidence": "level",
                "reasoning": "brief explanation"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.config.get("openai", {}).get("model", "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=self.config.get("openai", {}).get("max_tokens", 500),
                temperature=self.config.get("openai", {}).get("temperature", 0.3),
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "goal": result.get("goal", "هدف مشخص نشد"),
                "intent_category": result.get("intent_category", "general/other"),
                "confidence": result.get("confidence", "medium"),
                "reasoning": result.get("reasoning", ""),
                "confidence_score": self._confidence_to_score(result.get("confidence", "medium"))
            }
            
        except Exception as e:
            self.log(f"OpenAI analysis error: {e}", "error")
            return self._pattern_based_analysis(message)
    
    def _generate_simple_goal(self, message: str, category: str) -> str:
        """Generate simple goal statement based on category"""
        category_goals = {
            "action/initiation": f"اقدام و شروع: {message[:50]}",
            "decision/choice": f"تصمیم‌گیری: {message[:50]}",
            "concern/worry": f"نگرانی: {message[:50]}",
            "motivation/energy": f"انگیزه و انرژی: {message[:50]}",
            "confusion/help": f"کمک و راهنمایی: {message[:50]}",
            "planning/organization": f"برنامه‌ریزی: {message[:50]}",
            "learning/knowledge": f"یادگیری: {message[:50]}",
            "health/wellness": f"سلامتی: {message[:50]}",
            "relationship/social": f"روابط اجتماعی: {message[:50]}",
            "career/work": f"شغل و کار: {message[:50]}",
            "general/other": f"عمومی: {message[:50]}"
        }
        
        return category_goals.get(category, f"هدف: {message[:50]}")
    
    def _confidence_to_score(self, confidence: str) -> float:
        """Convert confidence level to numerical score"""
        mapping = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        return mapping.get(confidence, 0.5)
    
    def _store_goal_inference(self, message: str, analysis: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        """Store goal inference in database"""
        try:
            user_id = context.get("user_id", 1) if context else 1
            
            db = next(get_db())
            db.execute(text("""
                INSERT INTO goal_inferences (
                    user_id, input_text, goal, intent_category, confidence, 
                    detected_by, context_data, analysis_details, created_at
                ) VALUES (
                    :user_id, :input_text, :goal, :intent_category, :confidence,
                    :detected_by, :context_data, :analysis_details, :created_at
                )
            """), {
                "user_id": user_id,
                "input_text": message,
                "goal": analysis.get("goal", ""),
                "intent_category": analysis.get("intent_category", ""),
                "confidence": analysis.get("confidence", ""),
                "detected_by": analysis.get("detected_by", ""),
                "context_data": json.dumps(context or {}),
                "analysis_details": json.dumps(analysis),
                "created_at": datetime.utcnow()
            })
            db.commit()
            
            self.log("Goal inference stored in database")
            
        except Exception as e:
            self.log(f"Database storage error: {e}", "error")
    
    def _format_goal_response(self, analysis: Dict[str, Any]) -> str:
        """Format goal analysis response"""
        confidence_emoji = {
            "high": "✅",
            "medium": "⚠️",
            "low": "❓"
        }
        
        emoji = confidence_emoji.get(analysis.get("confidence", "medium"), "⚠️")
        
        response = f"🎯 **تشخیص هدف و قصد**\n\n"
        response += f"**🎯 هدف:** {analysis.get('goal', 'نامشخص')}\n"
        response += f"**📋 دسته:** {analysis.get('intent_category', 'عمومی')}\n"
        response += f"**{emoji} اطمینان:** {analysis.get('confidence', 'متوسط')}\n"
        response += f"**🔍 روش تشخیص:** {analysis.get('detected_by', 'نامشخص')}\n"
        
        if analysis.get("reasoning"):
            response += f"**💭 دلیل:** {analysis['reasoning']}\n"
        
        return response
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "supported_analysis": ["goal_inference", "intent_detection"],
            "intent_categories": self.intent_categories,
            "confidence_levels": self.confidence_levels,
            "analysis_methods": ["pattern_based", "openai_powered"],
            "openai_available": self.openai_available,
            "database_storage": True
        }