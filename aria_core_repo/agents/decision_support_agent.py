"""
Decision Support Agent for multi-dimensional decision analysis with goal, emotion, memory, and risk assessment.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON, Float
from sqlalchemy.orm import sessionmaker

from .base_agent import BaseAgent
from database import Base, engine, SessionLocal


class DecisionSupport(Base):
    """Database model for storing decision support analysis and recommendations."""
    __tablename__ = "decision_support"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for anonymous users
    decision_text = Column(Text, nullable=False)  # Original decision text
    goal_alignment = Column(Text, nullable=False)  # Goal alignment analysis
    emotional_state = Column(Text, nullable=False)  # Emotional state analysis
    risk_level = Column(String(20), nullable=False)  # low/medium/high
    confidence_score = Column(Float, nullable=False)  # 0.0-1.0
    recommendation = Column(Text, nullable=False)  # Final recommendation
    analysis_data = Column(JSON, nullable=False)  # Complete analysis data
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DecisionSupportAgent(BaseAgent):
    """
    Decision Support Agent that provides comprehensive multi-dimensional analysis
    for decision-making using goal, emotion, memory, and risk assessment.
    """
    
    def __init__(self):
        super().__init__("DecisionSupportAgent", "ایجنت پشتیبانی تصمیم‌گیری")
        self.log("Initialized with PostgreSQL database integration for decision support storage")
        
        # Create table if it doesn't exist
        self._create_decision_support_table()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        self._initialize_openai()
        
        # Decision keywords for pattern matching
        self.decision_keywords = [
            "تصمیم", "انتخاب", "چه کار", "چی کار", "راه حل", "مشاوره",
            "کمک", "پیشنهاد", "نظر", "راهنمایی", "تردید", "دودلی",
            "decide", "choice", "help", "advice", "suggest", "opinion",
            "باید", "should", "کنم", "بکنم", "؟", "سرمایه‌گذاری", "investment",
            "شغل", "job", "ازدواج", "marriage", "خرید", "buy", "بخرم", "purchase",
            "یا نه", "or not", "ترک", "quit", "استعفا", "resign"
        ]
        
        # Risk indicators for pattern-based analysis
        self.risk_indicators = {
            "high": [
                "همه پولم", "تمام دارایی", "وام", "قرض", "کار رها",
                "استعفا", "ترک تحصیل", "طلاق", "قطع رابطه", "فروش خانه",
                "all money", "quit job", "divorce", "drop out", "sell house"
            ],
            "medium": [
                "سرمایه‌گذاری", "تغییر شغل", "نقل مکان", "ازدواج", "شروع کسب‌وکار",
                "investment", "job change", "move", "marriage", "start business"
            ],
            "low": [
                "خرید", "سفر", "دوره", "کلاس", "هبی", "تفریح",
                "purchase", "travel", "course", "hobby", "entertainment"
            ]
        }
        
        # Recommendation patterns based on analysis
        self.recommendation_patterns = {
            "proceed": {
                "conditions": ["positive_emotion", "goal_aligned", "low_risk"],
                "message": "پیش برو - شرایط مناسب است",
                "color": "green"
            },
            "caution": {
                "conditions": ["medium_risk", "partial_alignment"],
                "message": "احتیاط کن - بیشتر بررسی کن",
                "color": "yellow"
            },
            "stop": {
                "conditions": ["negative_emotion", "high_risk", "goal_misaligned"],
                "message": "متوقف شو - شرایط مناسب نیست",
                "color": "red"
            }
        }
        
        self.log("Decision support patterns and analysis framework initialized")
    
    def _create_decision_support_table(self):
        """Create decision_support table if it doesn't exist."""
        try:
            Base.metadata.create_all(bind=engine)
            self.log("Decision support table ready")
        except Exception as e:
            self.log(f"Error creating decision support table: {e}", level="error")
    
    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available."""
        try:
            import openai
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.log("OpenAI GPT integration ready for decision analysis")
            else:
                self.log("OpenAI API key not found, using pattern-based decision analysis only")
        except ImportError:
            self.log("OpenAI library not available, using pattern-based decision analysis only")
        except Exception as e:
            self.log(f"OpenAI initialization error: {e}, using pattern-based decision analysis only")
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process decision support requests and generate comprehensive analysis.
        
        Args:
            message (str): The decision request message
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing decision analysis and recommendations
        """
        try:
            self.log(f"Processing decision support request: {message[:100]}...")
            
            # Remember the user message
            self.remember(message)
            
            # Detect if this is a decision request
            if not self._is_decision_request(message):
                return {"response": "این پیام به نظر درخواست تصمیم‌گیری نیست. لطفاً تصمیمی که در مورد آن تردید دارید را بیان کنید."}
            
            # Perform comprehensive decision analysis
            result = self._analyze_decision_comprehensively(message, context)
            
            # Save to database if analysis successful
            if result.get("success", False):
                self._save_decision_analysis(
                    context.get("user_id") if context else None,
                    message,
                    result["analysis"]
                )
            
            return {"response": result.get("response", "")}
                
        except Exception as e:
            self.log(f"Error processing decision support request: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل تصمیم:** {str(e)}"
            }
    
    def _is_decision_request(self, message: str) -> bool:
        """Check if the message is a decision request."""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.decision_keywords)
    
    def _analyze_decision_comprehensively(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform comprehensive multi-dimensional decision analysis."""
        try:
            user_id = context.get("user_id") if context else None
            
            # Step 1: Goal alignment analysis using GoalInferenceAgent
            goal_analysis = self._analyze_goal_alignment(message)
            
            # Step 2: Emotional state analysis using EmotionRegulationAgent
            emotion_analysis = self._analyze_emotional_state(message)
            
            # Step 3: Memory context analysis using LongTermMemory
            memory_analysis = self._analyze_memory_context(message)
            
            # Step 4: Risk assessment
            risk_analysis = self._assess_decision_risk(message, goal_analysis, emotion_analysis)
            
            # Step 5: Generate comprehensive recommendation
            final_recommendation = self._generate_comprehensive_recommendation(
                goal_analysis, emotion_analysis, memory_analysis, risk_analysis, message
            )
            
            # Step 6: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                goal_analysis, emotion_analysis, risk_analysis
            )
            
            # Prepare final analysis
            analysis_result = {
                "goal_alignment": goal_analysis.get("summary", "نامشخص"),
                "emotional_state": emotion_analysis.get("summary", "نامشخص"),
                "risk_level": risk_analysis.get("level", "medium"),
                "confidence_score": confidence_score,
                "recommendation": final_recommendation["message"],
                "recommendation_color": final_recommendation["color"],
                "analysis_details": {
                    "goal": goal_analysis,
                    "emotion": emotion_analysis,
                    "memory": memory_analysis,
                    "risk": risk_analysis
                }
            }
            
            # Format response
            response = self._format_decision_support_response(analysis_result, message)
            
            return {
                "response": response,
                "analysis": analysis_result,
                "success": True,
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.log(f"Error in comprehensive decision analysis: {e}", level="error")
            return {
                "response": f"❌ **خطا در تحلیل تصمیم:** {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _analyze_goal_alignment(self, message: str) -> Dict[str, Any]:
        """Analyze goal alignment using GoalInferenceAgent integration."""
        try:
            # Try to get goal analysis from GoalInferenceAgent if available
            from .master_agent import MasterAgent
            master = getattr(self, '_master_agent', None)
            
            if master and hasattr(master, 'sub_agents'):
                goal_agent = master.sub_agents.get("GoalInferenceAgent")
                if goal_agent:
                    goal_response = goal_agent.respond(message)
                    goal_content = goal_response.get("response", "")
                    
                    # Extract goal from response (simple parsing)
                    if "goal" in goal_content.lower():
                        return {
                            "detected": True,
                            "goal": self._extract_goal_from_response(goal_content),
                            "alignment": "مطابق با اهداف",
                            "summary": "هدف مشخص شناسایی شد",
                            "confidence": "high"
                        }
            
            # Fallback pattern-based goal analysis
            return self._pattern_based_goal_analysis(message)
            
        except Exception as e:
            self.log(f"Goal analysis error: {e}")
            return self._pattern_based_goal_analysis(message)
    
    def _pattern_based_goal_analysis(self, message: str) -> Dict[str, Any]:
        """Pattern-based goal analysis fallback."""
        goal_keywords = {
            "career": ["شغل", "کار", "حرفه", "career", "job"],
            "education": ["تحصیل", "دانشگاه", "دوره", "education", "study"],
            "financial": ["پول", "سرمایه", "مالی", "money", "financial"],
            "personal": ["زندگی", "شخصی", "خانواده", "personal", "life"],
            "health": ["سلامت", "ورزش", "رژیم", "health", "fitness"]
        }
        
        message_lower = message.lower()
        detected_goals = []
        
        for category, keywords in goal_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_goals.append(category)
        
        if detected_goals:
            return {
                "detected": True,
                "goal": detected_goals[0],
                "alignment": "احتمالاً مطابق با اهداف",
                "summary": f"هدف در حوزه {detected_goals[0]} شناسایی شد",
                "confidence": "medium"
            }
        else:
            return {
                "detected": False,
                "goal": "نامشخص",
                "alignment": "نامشخص",
                "summary": "هدف مشخصی شناسایی نشد",
                "confidence": "low"
            }
    
    def _analyze_emotional_state(self, message: str) -> Dict[str, Any]:
        """Analyze emotional state using EmotionRegulationAgent integration."""
        try:
            # Try to get emotion analysis from EmotionRegulationAgent if available
            from .master_agent import MasterAgent
            master = getattr(self, '_master_agent', None)
            
            if master and hasattr(master, 'sub_agents'):
                emotion_agent = master.sub_agents.get("EmotionRegulationAgent")
                if emotion_agent:
                    emotion_response = emotion_agent.respond(message)
                    emotion_content = emotion_response.get("response", "")
                    
                    # Extract emotion from response (simple parsing)
                    if "emotion" in emotion_content.lower():
                        return {
                            "detected": True,
                            "emotion": self._extract_emotion_from_response(emotion_content),
                            "state": "احساس مشخص شناسایی شد",
                            "summary": "وضعیت احساسی تحلیل شد",
                            "confidence": "high"
                        }
            
            # Fallback pattern-based emotion analysis
            return self._pattern_based_emotion_analysis(message)
            
        except Exception as e:
            self.log(f"Emotion analysis error: {e}")
            return self._pattern_based_emotion_analysis(message)
    
    def _pattern_based_emotion_analysis(self, message: str) -> Dict[str, Any]:
        """Pattern-based emotion analysis fallback."""
        emotion_patterns = {
            "positive": ["خوشحال", "راضی", "امیدوار", "happy", "excited", "hopeful"],
            "negative": ["نگران", "ناراحت", "عصبانی", "worried", "sad", "angry"],
            "neutral": ["عادی", "معمولی", "normal", "okay"]
        }
        
        message_lower = message.lower()
        
        for state, keywords in emotion_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return {
                    "detected": True,
                    "emotion": state,
                    "state": f"احساس {state}",
                    "summary": f"وضعیت احساسی {state} تشخیص داده شد",
                    "confidence": "medium"
                }
        
        return {
            "detected": False,
            "emotion": "نامشخص",
            "state": "وضعیت احساسی نامشخص",
            "summary": "احساس خاصی تشخیص داده نشد",
            "confidence": "low"
        }
    
    def _analyze_memory_context(self, message: str) -> Dict[str, Any]:
        """Analyze memory context for similar past decisions."""
        try:
            # Analyze short-term memory
            memory_insights = []
            if hasattr(self, 'memory') and self.memory:
                recent_messages = list(self.memory)[-5:]
                
                # Look for decision patterns
                decision_count = sum(1 for msg in recent_messages 
                                   if any(keyword in msg.lower() for keyword in self.decision_keywords))
                
                if decision_count > 1:
                    memory_insights.append("چندین تصمیم اخیر - ممکن است نیاز به تمرکز بیشتر باشد")
                
                # Look for emotional patterns
                negative_emotions = ["نگران", "ناراحت", "عصبانی", "استرس"]
                emotional_stress = sum(1 for msg in recent_messages 
                                     for emotion in negative_emotions 
                                     if emotion in msg.lower())
                
                if emotional_stress > 0:
                    memory_insights.append("نشانه‌هایی از استرس احساسی در تعاملات اخیر")
            
            return {
                "insights": memory_insights,
                "pattern_count": len(memory_insights),
                "summary": "تحلیل حافظه کوتاه‌مدت انجام شد" if memory_insights else "الگوی خاصی در حافظه یافت نشد"
            }
            
        except Exception as e:
            self.log(f"Memory analysis error: {e}")
            return {
                "insights": [],
                "pattern_count": 0,
                "summary": "خطا در تحلیل حافظه"
            }
    
    def _assess_decision_risk(self, message: str, goal_analysis: Dict, emotion_analysis: Dict) -> Dict[str, Any]:
        """Assess decision risk level based on content and analysis."""
        try:
            message_lower = message.lower()
            risk_score = 0
            risk_factors = []
            
            # Pattern-based risk assessment
            for level, indicators in self.risk_indicators.items():
                for indicator in indicators:
                    if indicator in message_lower:
                        if level == "high":
                            risk_score += 3
                            risk_factors.append(f"مؤلفه پرخطر: {indicator}")
                        elif level == "medium":
                            risk_score += 2
                            risk_factors.append(f"مؤلفه متوسط: {indicator}")
                        else:  # low
                            risk_score += 1
                            risk_factors.append(f"مؤلفه کم‌خطر: {indicator}")
            
            # Emotional state risk adjustment
            if emotion_analysis.get("emotion") == "negative":
                risk_score += 1
                risk_factors.append("وضعیت احساسی منفی")
            
            # Goal alignment risk adjustment
            if goal_analysis.get("alignment") == "نامشخص":
                risk_score += 1
                risk_factors.append("عدم وضوح هدف")
            
            # Determine final risk level
            if risk_score >= 4:
                risk_level = "high"
            elif risk_score >= 2:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # GPT-based risk assessment if available
            gpt_risk = None
            if self.openai_client and risk_score >= 2:
                gpt_risk = self._gpt_risk_assessment(message, goal_analysis, emotion_analysis)
            
            return {
                "level": gpt_risk.get("level", risk_level) if gpt_risk else risk_level,
                "score": risk_score,
                "factors": risk_factors,
                "gpt_analysis": gpt_risk,
                "summary": f"سطح ریسک: {risk_level}"
            }
            
        except Exception as e:
            self.log(f"Risk assessment error: {e}")
            return {
                "level": "medium",
                "score": 2,
                "factors": ["خطا در تحلیل ریسک"],
                "summary": "ریسک متوسط (به دلیل عدم قطعیت)"
            }
    
    def _gpt_risk_assessment(self, message: str, goal_analysis: Dict, emotion_analysis: Dict) -> Dict[str, Any]:
        """GPT-based risk assessment for complex decisions."""
        try:
            prompt = f"""
            تحلیل ریسک این تصمیم:
            
            متن تصمیم: "{message}"
            تحلیل هدف: {goal_analysis.get('summary', 'نامشخص')}
            وضعیت احساسی: {emotion_analysis.get('summary', 'نامشخص')}
            
            لطفاً سطح ریسک (low/medium/high) و دلایل آن را مشخص کن.
            
            پاسخ را فقط در قالب JSON برگردان:
            {{
                "level": "low/medium/high",
                "reasoning": "دلیل تحلیل ریسک",
                "key_risks": ["ریسک‌های کلیدی"],
                "confidence": "high/medium/low"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            self.log(f"GPT risk assessment completed: {result.get('level', 'unknown')}")
            return result
            
        except Exception as e:
            self.log(f"GPT risk assessment failed: {e}")
            return None
    
    def _generate_comprehensive_recommendation(self, goal_analysis: Dict, emotion_analysis: Dict, 
                                             memory_analysis: Dict, risk_analysis: Dict, message: str) -> Dict[str, Any]:
        """Generate comprehensive recommendation based on all analysis."""
        
        # Determine recommendation based on analysis
        risk_level = risk_analysis.get("level", "medium")
        emotion_state = emotion_analysis.get("emotion", "نامشخص")
        goal_aligned = goal_analysis.get("detected", False)
        
        # Decision logic
        if risk_level == "high" or emotion_state == "negative":
            recommendation = {
                "message": "🔴 متوقف شو - شرایط مناسب نیست. بیشتر فکر کن.",
                "color": "red",
                "action": "stop"
            }
        elif risk_level == "medium" or not goal_aligned:
            recommendation = {
                "message": "🟡 احتیاط کن - بیشتر بررسی کن قبل از تصمیم.",
                "color": "yellow", 
                "action": "caution"
            }
        else:
            recommendation = {
                "message": "🟢 پیش برو - شرایط مناسب است.",
                "color": "green",
                "action": "proceed"
            }
        
        # Add memory context warnings
        if memory_analysis.get("pattern_count", 0) > 0:
            recommendation["message"] += f" توجه: {memory_analysis['insights'][0]}"
        
        return recommendation
    
    def _calculate_confidence_score(self, goal_analysis: Dict, emotion_analysis: Dict, risk_analysis: Dict) -> float:
        """Calculate confidence score for the decision analysis."""
        score = 0.0
        
        # Goal analysis confidence
        goal_conf = goal_analysis.get("confidence", "low")
        if goal_conf == "high":
            score += 0.4
        elif goal_conf == "medium":
            score += 0.2
        
        # Emotion analysis confidence
        emotion_conf = emotion_analysis.get("confidence", "low")
        if emotion_conf == "high":
            score += 0.3
        elif emotion_conf == "medium":
            score += 0.15
        
        # Risk assessment confidence
        risk_factors = len(risk_analysis.get("factors", []))
        if risk_factors >= 2:
            score += 0.3
        elif risk_factors == 1:
            score += 0.15
        
        return min(1.0, max(0.0, score))
    
    def _extract_goal_from_response(self, response: str) -> str:
        """Extract goal from GoalInferenceAgent response."""
        # Simple extraction - could be improved
        if "شروع" in response or "action" in response.lower():
            return "شروع/اقدام"
        elif "تصمیم" in response or "decision" in response.lower():
            return "تصمیم‌گیری"
        else:
            return "عمومی"
    
    def _extract_emotion_from_response(self, response: str) -> str:
        """Extract emotion from EmotionRegulationAgent response."""
        # Simple extraction - could be improved
        if "خشم" in response or "anger" in response.lower():
            return "خشم"
        elif "اضطراب" in response or "anxiety" in response.lower():
            return "اضطراب"
        elif "خوشحال" in response or "happy" in response.lower():
            return "خوشحالی"
        else:
            return "نامشخص"
    
    def _format_decision_support_response(self, analysis: Dict[str, Any], original_message: str) -> str:
        """Format the decision support analysis response."""
        
        goal_alignment = analysis.get("goal_alignment", "نامشخص")
        emotional_state = analysis.get("emotional_state", "نامشخص")
        risk_level = analysis.get("risk_level", "medium")
        confidence_score = analysis.get("confidence_score", 0.0)
        recommendation = analysis.get("recommendation", "احتیاط کن")
        color = analysis.get("recommendation_color", "yellow")
        
        # Color emojis
        color_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(color, "🟡")
        
        # Risk level emojis
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "🟡")
        
        # Confidence bar
        conf_bars = int(confidence_score * 5)
        confidence_bar = "█" * conf_bars + "░" * (5 - conf_bars)
        
        response = f"🎯 **تحلیل پشتیبانی تصمیم:**\n\n"
        
        # Main recommendation with JSON format
        json_result = {
            "goal_alignment": goal_alignment,
            "emotion": emotional_state,
            "risk_level": risk_level,
            "suggestion": recommendation
        }
        
        response += f"```json\n{json.dumps(json_result, ensure_ascii=False, indent=2)}\n```\n\n"
        
        # Detailed analysis
        response += f"**📊 تحلیل چندبعدی:**\n"
        response += f"• 🎯 **تراز هدف:** {goal_alignment}\n"
        response += f"• 💝 **وضعیت احساسی:** {emotional_state}\n"
        response += f"• {risk_emoji} **سطح ریسک:** {risk_level}\n"
        response += f"• 📈 **اعتماد تحلیل:** {confidence_bar} ({confidence_score:.1%})\n\n"
        
        # Main recommendation
        response += f"**🎯 توصیه نهایی:**\n"
        response += f"{color_emoji} {recommendation}\n\n"
        
        # Risk factors if available
        risk_factors = analysis.get("analysis_details", {}).get("risk", {}).get("factors", [])
        if risk_factors:
            response += f"**⚠️ عوامل ریسک شناسایی شده:**\n"
            for factor in risk_factors[:3]:  # Show top 3
                response += f"• {factor}\n"
            response += "\n"
        
        # Memory insights if available
        memory_insights = analysis.get("analysis_details", {}).get("memory", {}).get("insights", [])
        if memory_insights:
            response += f"**🧠 تحلیل حافظه:**\n"
            for insight in memory_insights[:2]:  # Show top 2
                response += f"• {insight}\n"
            response += "\n"
        
        response += "🎯 **نکته:** این تحلیل بر اساس هدف، احساس، حافظه و ریسک انجام شده است."
        
        return response
    
    def _save_decision_analysis(self, user_id: Optional[int], decision_text: str, analysis: Dict[str, Any]) -> int:
        """Save decision analysis to database."""
        try:
            db = SessionLocal()
            
            decision_support = DecisionSupport(
                user_id=user_id,
                decision_text=decision_text,
                goal_alignment=analysis.get("goal_alignment", "نامشخص"),
                emotional_state=analysis.get("emotional_state", "نامشخص"),
                risk_level=analysis.get("risk_level", "medium"),
                confidence_score=analysis.get("confidence_score", 0.0),
                recommendation=analysis.get("recommendation", "احتیاط کن"),
                analysis_data=analysis.get("analysis_details", {})
            )
            
            db.add(decision_support)
            db.commit()
            db.refresh(decision_support)
            
            decision_id = decision_support.id
            self.log(f"Decision analysis saved with ID: {decision_id}")
            
            db.close()
            return decision_id
            
        except Exception as e:
            self.log(f"Error saving decision analysis: {e}", level="error")
            return 0
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decision analyses from database."""
        try:
            db = SessionLocal()
            
            decisions = db.query(DecisionSupport).order_by(
                DecisionSupport.created_at.desc()
            ).limit(limit).all()
            
            result = []
            for decision in decisions:
                result.append({
                    "id": decision.id,
                    "decision_text": decision.decision_text[:100] + "..." if len(decision.decision_text) > 100 else decision.decision_text,
                    "goal_alignment": decision.goal_alignment,
                    "emotional_state": decision.emotional_state,
                    "risk_level": decision.risk_level,
                    "confidence_score": decision.confidence_score,
                    "recommendation": decision.recommendation,
                    "created_at": decision.created_at.isoformat()
                })
            
            db.close()
            return result
            
        except Exception as e:
            self.log(f"Error getting recent decisions: {e}", level="error")
            return []
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> list:
        """Get list of agent capabilities."""
        return [
            "تحلیل چندبعدی تصمیم",
            "ارزیابی تراز هدف",
            "تحلیل وضعیت احساسی",
            "بررسی زمینه حافظه",
            "ارزیابی ریسک",
            "محاسبه اعتماد تحلیل",
            "توصیه نهایی رنگی",
            "ذخیره تصمیمات",
            "تحلیل الگوهای تصمیم",
            "اتصال به ایجنت‌های دیگر"
        ]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for decision support."""
        try:
            db = SessionLocal()
            
            total_decisions = db.query(DecisionSupport).count()
            recent_decisions = db.query(DecisionSupport).filter(
                DecisionSupport.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
            ).count()
            
            # Count by risk level
            risk_counts = {}
            for level in ["low", "medium", "high"]:
                count = db.query(DecisionSupport).filter(DecisionSupport.risk_level == level).count()
                risk_counts[level] = count
            
            # Average confidence score
            avg_confidence = db.query(func.avg(DecisionSupport.confidence_score)).scalar() or 0.0
            
            db.close()
            
            return {
                "total_decisions": total_decisions,
                "recent_decisions": recent_decisions,
                "risk_distribution": risk_counts,
                "average_confidence": round(float(avg_confidence), 2),
                "table_name": "decision_support"
            }
            
        except Exception as e:
            self.log(f"Error getting database stats: {e}", level="error")
            return {
                "total_decisions": 0,
                "recent_decisions": 0,
                "risk_distribution": {"low": 0, "medium": 0, "high": 0},
                "average_confidence": 0.0,
                "error": str(e)
            }