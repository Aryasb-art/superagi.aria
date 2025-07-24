"""
SimulatedConsensusAgent - Collaborative decision-making simulation agent.

This agent simulates a collaborative decision-making process among multiple virtual agents 
with different perspectives to help evaluate complex decisions with nuance.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
from agents.base_agent import BaseAgent

Base = declarative_base()

class ConsensusLog(Base):
    """Database model for consensus decision logs."""
    __tablename__ = 'consensus_logs'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_text = Column(Text)
    virtual_agents = Column(Text)  # JSON string of virtual agent perspectives
    consensus_result = Column(Text)
    final_decision = Column(Text)
    confidence_score = Column(Float)
    primary_contributor = Column(String)  # Which virtual agent contributed most
    decision_data = Column(Text)  # JSON string of full decision process


class SimulatedConsensusAgent(BaseAgent):
    """
    Advanced collaborative decision-making simulation agent.
    Simulates multiple virtual agents with different perspectives for complex decisions.
    """
    
    def __init__(self):
        super().__init__("SimulatedConsensusAgent")
        self._init_database()
        self._init_openai()
        self._init_virtual_agents()
        self.logger.info("[SimulatedConsensusAgent] Initialized with PostgreSQL database integration for consensus tracking")
    
    def _init_database(self):
        """Initialize database connection and create tables."""
        try:
            DATABASE_URL = os.environ.get('DATABASE_URL')
            if not DATABASE_URL:
                raise ValueError("DATABASE_URL environment variable is not set")
            
            self.engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            self.logger.info("[SimulatedConsensusAgent] Consensus logs table ready")
        except Exception as e:
            self.logger.error(f"[SimulatedConsensusAgent] Database initialization failed: {e}")
            raise
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            self.openai_client = OpenAI(api_key=api_key)
            self.logger.info("[SimulatedConsensusAgent] OpenAI GPT integration ready for consensus simulation")
        except Exception as e:
            self.logger.error(f"[SimulatedConsensusAgent] OpenAI initialization failed: {e}")
            self.openai_client = None
    
    def _init_virtual_agents(self):
        """Initialize virtual agent personas and characteristics."""
        self.virtual_agents = {
            "risk_averse": {
                "name": "محافظه‌کار",
                "name_en": "Risk-Averse Agent",
                "perspective": "focuses on minimizing risks and potential negative outcomes",
                "bias": "tends to overestimate risks and prefer safer options",
                "priority": "safety and security",
                "keywords": ["خطر", "امنیت", "محافظه", "احتیاط", "ریسک"]
            },
            "optimistic": {
                "name": "خوش‌بین",
                "name_en": "Optimistic Agent", 
                "perspective": "focuses on opportunities and positive outcomes",
                "bias": "tends to underestimate risks and overestimate benefits",
                "priority": "growth and opportunity",
                "keywords": ["فرصت", "امید", "مثبت", "رشد", "موفقیت"]
            },
            "data_driven": {
                "name": "تحلیل‌گر",
                "name_en": "Data-Driven Agent",
                "perspective": "relies on facts, statistics, and logical analysis",
                "bias": "may undervalue emotional or intuitive factors",
                "priority": "accuracy and evidence",
                "keywords": ["داده", "تحلیل", "منطق", "آمار", "واقعیت"]
            },
            "ethical": {
                "name": "اخلاق‌مدار",
                "name_en": "Ethical Agent",
                "perspective": "evaluates decisions based on moral principles and fairness",
                "bias": "may prioritize ethical considerations over practical outcomes",
                "priority": "moral integrity and fairness",
                "keywords": ["اخلاق", "عدالت", "انصاف", "اصول", "ارزش"]
            },
            "pragmatic": {
                "name": "عملگرا",
                "name_en": "Pragmatic Agent",
                "perspective": "focuses on practical implementation and realistic outcomes",
                "bias": "may undervalue idealistic or long-term considerations",
                "priority": "feasibility and practicality",
                "keywords": ["عملی", "واقعی", "اجرایی", "ممکن", "کاربردی"]
            }
        }
        
        self.logger.info("[SimulatedConsensusAgent] Virtual agent personas and decision frameworks initialized")
    
    def _simulate_agent_perspective(self, agent_key: str, decision_text: str, language: str = "fa") -> Dict[str, Any]:
        """
        Simulate a single virtual agent's perspective on a decision.
        
        Args:
            agent_key (str): Key for the virtual agent
            decision_text (str): The decision to evaluate
            language (str): Response language (fa/en)
            
        Returns:
            Dict: Virtual agent's perspective and reasoning
        """
        agent = self.virtual_agents[agent_key]
        
        if self.openai_client:
            try:
                prompt = f"""
                You are a virtual agent named {agent['name']} ({agent['name_en']}).
                Your perspective: {agent['perspective']}
                Your cognitive bias: {agent['bias']}
                Your priority: {agent['priority']}
                
                Analyze this decision/dilemma: "{decision_text}"
                
                Provide your analysis in {'Persian' if language == 'fa' else 'English'} with:
                1. Your main argument (2-3 sentences)
                2. Key concerns or opportunities you see
                3. Your recommended action
                4. Confidence level (0-1)
                
                Respond in JSON format:
                {{
                    "agent_name": "{agent['name'] if language == 'fa' else agent['name_en']}",
                    "argument": "your main argument here",
                    "concerns": ["concern1", "concern2"],
                    "opportunities": ["opportunity1", "opportunity2"],
                    "recommendation": "your recommended action",
                    "confidence": 0.8,
                    "reasoning": "brief explanation of your reasoning"
                }}
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
                
                return json.loads(response.choices[0].message.content)
                
            except Exception as e:
                self.logger.error(f"[SimulatedConsensusAgent] OpenAI simulation failed for {agent_key}: {e}")
                return self._fallback_perspective(agent_key, decision_text, language)
        
        return self._fallback_perspective(agent_key, decision_text, language)
    
    def _fallback_perspective(self, agent_key: str, decision_text: str, language: str = "fa") -> Dict[str, Any]:
        """
        Fallback method for generating agent perspectives without OpenAI.
        
        Args:
            agent_key (str): Key for the virtual agent
            decision_text (str): The decision to evaluate
            language (str): Response language (fa/en)
            
        Returns:
            Dict: Virtual agent's perspective
        """
        agent = self.virtual_agents[agent_key]
        
        # Simple rule-based perspective generation
        if language == "fa":
            perspectives = {
                "risk_averse": {
                    "argument": "این تصمیم ممکن است خطرات پنهانی داشته باشد که باید بررسی شود.",
                    "concerns": ["خطرات احتمالی", "عدم قطعیت", "پیامدهای منفی"],
                    "opportunities": ["امنیت بیشتر", "کاهش ریسک"],
                    "recommendation": "تحقیق بیشتر و بررسی دقیق‌تر پیش از تصمیم‌گیری",
                    "confidence": 0.6
                },
                "optimistic": {
                    "argument": "این فرصت مناسبی برای رشد و پیشرفت است.",
                    "concerns": ["زمان‌بندی", "منابع"],
                    "opportunities": ["رشد شخصی", "تجربه جدید", "موفقیت"],
                    "recommendation": "اقدام سریع و بهره‌گیری از فرصت",
                    "confidence": 0.8
                },
                "data_driven": {
                    "argument": "نیاز به تحلیل دقیق‌تر داده‌ها و اطلاعات موجود است.",
                    "concerns": ["کمبود داده", "تحلیل ناکافی"],
                    "opportunities": ["تصمیم‌گیری بر اساس واقعیات", "دقت بالا"],
                    "recommendation": "جمع‌آوری و تحلیل اطلاعات بیشتر",
                    "confidence": 0.7
                },
                "ethical": {
                    "argument": "باید اصول اخلاقی و تأثیر بر دیگران در نظر گرفته شود.",
                    "concerns": ["تأثیر بر دیگران", "اصول اخلاقی"],
                    "opportunities": ["عمل صحیح", "رضایت وجدان"],
                    "recommendation": "بررسی جنبه‌های اخلاقی تصمیم",
                    "confidence": 0.75
                },
                "pragmatic": {
                    "argument": "باید عملی بودن و قابلیت اجرا را در نظر گرفت.",
                    "concerns": ["پیچیدگی اجرا", "منابع لازم"],
                    "opportunities": ["نتایج قابل دستیابی", "حل مسئله"],
                    "recommendation": "تمرکز بر راه‌حل‌های عملی و قابل اجرا",
                    "confidence": 0.65
                }
            }
        else:
            perspectives = {
                "risk_averse": {
                    "argument": "This decision may have hidden risks that need careful evaluation.",
                    "concerns": ["Potential risks", "Uncertainty", "Negative consequences"],
                    "opportunities": ["Greater security", "Risk reduction"],
                    "recommendation": "More research and thorough evaluation before deciding",
                    "confidence": 0.6
                },
                "optimistic": {
                    "argument": "This is a good opportunity for growth and advancement.",
                    "concerns": ["Timing", "Resources"],
                    "opportunities": ["Personal growth", "New experience", "Success"],
                    "recommendation": "Quick action and seize the opportunity",
                    "confidence": 0.8
                },
                "data_driven": {
                    "argument": "More detailed analysis of available data and information is needed.",
                    "concerns": ["Data shortage", "Insufficient analysis"],
                    "opportunities": ["Fact-based decisions", "High accuracy"],
                    "recommendation": "Gather and analyze more information",
                    "confidence": 0.7
                },
                "ethical": {
                    "argument": "Moral principles and impact on others should be considered.",
                    "concerns": ["Impact on others", "Moral principles"],
                    "opportunities": ["Right action", "Peace of mind"],
                    "recommendation": "Review ethical aspects of the decision",
                    "confidence": 0.75
                },
                "pragmatic": {
                    "argument": "Practicality and feasibility should be considered.",
                    "concerns": ["Implementation complexity", "Required resources"],
                    "opportunities": ["Achievable results", "Problem solving"],
                    "recommendation": "Focus on practical and feasible solutions",
                    "confidence": 0.65
                }
            }
        
        perspective = perspectives.get(agent_key, perspectives["pragmatic"])
        perspective["agent_name"] = agent['name'] if language == 'fa' else agent['name_en']
        perspective["reasoning"] = f"تحلیل بر اساس {agent['priority']}" if language == 'fa' else f"Analysis based on {agent['priority']}"
        
        return perspective
    
    def simulate_consensus(self, decision_text: str, language: str = "fa") -> Dict[str, Any]:
        """
        Simulate a consensus decision-making process among virtual agents.
        
        Args:
            decision_text (str): The decision to evaluate
            language (str): Response language (fa/en)
            
        Returns:
            Dict: Consensus results with all agent perspectives
        """
        consensus_id = str(uuid.uuid4())
        
        # Simulate 3-5 virtual agents
        selected_agents = ["risk_averse", "optimistic", "data_driven", "ethical", "pragmatic"]
        
        agent_perspectives = {}
        total_confidence = 0
        
        for agent_key in selected_agents:
            perspective = self._simulate_agent_perspective(agent_key, decision_text, language)
            agent_perspectives[agent_key] = perspective
            total_confidence += perspective.get("confidence", 0.5)
        
        # Calculate weighted consensus
        avg_confidence = total_confidence / len(selected_agents)
        primary_contributor = max(agent_perspectives.keys(), 
                                key=lambda x: agent_perspectives[x].get("confidence", 0))
        
        # Generate final consensus
        final_consensus = self._generate_consensus_summary(agent_perspectives, decision_text, language)
        
        # Save to database
        self._save_consensus_log(
            consensus_id, decision_text, json.dumps(agent_perspectives, ensure_ascii=False),
            final_consensus, avg_confidence, primary_contributor
        )
        
        return {
            "consensus_id": consensus_id,
            "virtual_agents": agent_perspectives,
            "final_consensus": final_consensus,
            "confidence_score": avg_confidence,
            "primary_contributor": agent_perspectives[primary_contributor]["agent_name"],
            "decision_summary": self._format_decision_summary(agent_perspectives, final_consensus, language)
        }
    
    def _generate_consensus_summary(self, perspectives: Dict[str, Dict], decision_text: str, language: str) -> str:
        """
        Generate a consensus summary from virtual agent perspectives.
        
        Args:
            perspectives (Dict): All agent perspectives
            decision_text (str): Original decision text
            language (str): Response language
            
        Returns:
            str: Consensus summary
        """
        if self.openai_client:
            try:
                perspectives_text = json.dumps(perspectives, ensure_ascii=False, indent=2)
                
                prompt = f"""
                Based on these virtual agent perspectives about the decision "{decision_text}":

                {perspectives_text}

                Generate a balanced consensus summary in {'Persian' if language == 'fa' else 'English'} that:
                1. Acknowledges the main concerns raised
                2. Highlights the opportunities identified
                3. Provides a balanced recommendation
                4. Considers the weight of each perspective

                Keep the summary concise (3-4 sentences) and actionable.
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                self.logger.error(f"[SimulatedConsensusAgent] Consensus generation failed: {e}")
                return self._fallback_consensus_summary(perspectives, language)
        
        return self._fallback_consensus_summary(perspectives, language)
    
    def _fallback_consensus_summary(self, perspectives: Dict[str, Dict], language: str) -> str:
        """Generate a fallback consensus summary."""
        if language == "fa":
            return "بر اساس تحلیل گروهی، این تصمیم نیازمند بررسی همه جنبه‌های مطرح شده است. توصیه می‌شود با در نظر گیری خطرات، فرصت‌ها و جنبه‌های اخلاقی، تصمیم متعادلی اتخاذ شود."
        else:
            return "Based on group analysis, this decision requires consideration of all aspects raised. It is recommended to make a balanced decision considering risks, opportunities, and ethical aspects."
    
    def _format_decision_summary(self, perspectives: Dict[str, Dict], consensus: str, language: str) -> str:
        """Format the complete decision summary for display."""
        if language == "fa":
            summary = f"🤝 **خلاصه تصمیم‌گیری گروهی**\n\n"
            
            for agent_key, perspective in perspectives.items():
                summary += f"👤 **{perspective['agent_name']}**\n"
                summary += f"💭 نظر: {perspective['argument']}\n"
                summary += f"📊 اطمینان: {perspective['confidence']:.0%}\n"
                summary += f"💡 توصیه: {perspective['recommendation']}\n\n"
            
            summary += f"🎯 **نتیجه گیری نهایی:**\n{consensus}\n"
            
        else:
            summary = f"🤝 **Group Decision Summary**\n\n"
            
            for agent_key, perspective in perspectives.items():
                summary += f"👤 **{perspective['agent_name']}**\n"
                summary += f"💭 Opinion: {perspective['argument']}\n"
                summary += f"📊 Confidence: {perspective['confidence']:.0%}\n"
                summary += f"💡 Recommendation: {perspective['recommendation']}\n\n"
            
            summary += f"🎯 **Final Conclusion:**\n{consensus}\n"
        
        return summary
    
    def _save_consensus_log(self, consensus_id: str, input_text: str, virtual_agents: str, 
                           consensus_result: str, confidence_score: float, primary_contributor: str):
        """Save consensus decision to database."""
        try:
            decision_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "agent_count": 5,
                "consensus_method": "weighted_average",
                "confidence_score": confidence_score
            }
            
            log_entry = ConsensusLog(
                id=consensus_id,
                input_text=input_text,
                virtual_agents=virtual_agents,
                consensus_result=consensus_result,
                confidence_score=confidence_score,
                primary_contributor=primary_contributor,
                decision_data=json.dumps(decision_data, ensure_ascii=False)
            )
            
            self.session.add(log_entry)
            self.session.commit()
            
        except Exception as e:
            self.logger.error(f"[SimulatedConsensusAgent] Failed to save consensus log: {e}")
            self.session.rollback()
    
    def get_consensus_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent consensus decision logs.
        
        Args:
            limit (int): Number of logs to retrieve
            
        Returns:
            List[Dict]: Recent consensus logs
        """
        try:
            logs = self.session.query(ConsensusLog)\
                              .order_by(ConsensusLog.timestamp.desc())\
                              .limit(limit)\
                              .all()
            
            result = []
            for log in logs:
                result.append({
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "input_text": log.input_text,
                    "consensus_result": log.consensus_result,
                    "confidence_score": log.confidence_score,
                    "primary_contributor": log.primary_contributor
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"[SimulatedConsensusAgent] Failed to get consensus logs: {e}")
            return []
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process message and simulate consensus decision-making.
        
        Args:
            message (str): The decision or dilemma to evaluate
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing consensus analysis
        """
        try:
            # Detect language
            language = "fa" if any(ord(char) > 127 for char in message) else "en"
            
            # Simulate consensus
            consensus_result = self.simulate_consensus(message, language)
            
            # Format response
            response_content = consensus_result["decision_summary"]
            
            # Store in short-term memory
            self.remember(f"تصمیم گروهی: {message}", "consensus_decision")
            
            return {
                "agent": self.name,
                "response": response_content,
                "consensus_data": consensus_result,
                "timestamp": datetime.utcnow().isoformat(),
                "language": language
            }
            
        except Exception as e:
            self.logger.error(f"[SimulatedConsensusAgent] Error in respond: {e}")
            error_msg = "خطا در شبیه‌سازی تصمیم‌گیری گروهی" if "fa" in message else "Error in group decision simulation"
            return {
                "agent": self.name,
                "response": error_msg,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }