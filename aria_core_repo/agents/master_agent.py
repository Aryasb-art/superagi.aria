"""
Master Agent for coordinating and managing other AI agents.
"""

from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
import json
import asyncio


class MasterAgent(BaseAgent):
    """
    Central coordination agent that manages communication between different sub-agents.
    Acts as a router and orchestrator for the multi-agent system.
    """
    
    def __init__(self):
        super().__init__(
            name="MasterAgent",
            description="Central coordinator for managing and routing messages between AI agents"
        )
        self.sub_agents: Dict[str, BaseAgent] = {}
        self.routing_rules: Dict[str, str] = {}
        self.default_responses = {
            "greeting": "سلام! من MasterAgent هستم. چطور می‌تونم کمکتون کنم؟",
            "status": "سیستم آماده است. تمام ایجنت‌ها فعال هستند.",
            "help": "می‌تونم پیام‌هاتون رو به ایجنت‌های مناسب ارجاع بدم یا مستقیماً پاسخ بدم.",
            "error": "متأسفم، مشکلی پیش آمده. لطفاً دوباره تلاش کنید."
        }
        
        # Initialize sub-agents
        self._initialize_utility_agent()
        self._initialize_tool_agent()
        self._initialize_summary_agent()
        self._initialize_longterm_memory_agent()
        self._initialize_conceptual_memory_agent()
        self._initialize_repetitive_learning_agent()
        self._initialize_knowledge_graph_agent()
        self._initialize_auto_suggester_agent()
        self._initialize_goal_inference_agent()
        self._initialize_emotion_regulation_agent()
        self._initialize_decision_support_agent()
        self._initialize_self_awareness_agent()
        self._initialize_interactive_security_check_agent()
        self._initialize_reward_agent()
        self._initialize_bias_detection_agent()
        self._initialize_cognitive_distortion_agent()
        self._initialize_ethical_reasoning_agent()
        self._initialize_simulated_consensus_agent()
        self._initialize_advanced_memory_manager_agent()
    
    def register_agent(self, agent: BaseAgent, keywords: Optional[List[str]] = None) -> None:
        """
        Register a sub-agent with the master agent.
        
        Args:
            agent (BaseAgent): The agent to register
            keywords (List[str]): Keywords that route messages to this agent
        """
        self.sub_agents[agent.name] = agent
        
        if keywords:
            for keyword in keywords:
                self.routing_rules[keyword.lower()] = agent.name
        
        self.log(f"Registered sub-agent: {agent.name}")
    
    def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister a sub-agent.
        
        Args:
            agent_name (str): Name of the agent to unregister
            
        Returns:
            bool: True if successful, False if agent not found
        """
        if agent_name in self.sub_agents:
            del self.sub_agents[agent_name]
            
            # Remove routing rules for this agent
            rules_to_remove = [k for k, v in self.routing_rules.items() if v == agent_name]
            for rule in rules_to_remove:
                del self.routing_rules[rule]
            
            self.log(f"Unregistered sub-agent: {agent_name}")
            return True
        
        return False
    
    def route_message(self, message: str) -> Optional[str]:
        """
        Determine which agent should handle the message based on content.
        
        Args:
            message (str): The message to route
            
        Returns:
            Optional[str]: Name of the target agent, or None for master agent
        """
        message_lower = message.lower()
        
        # Check routing rules for keyword matches
        for keyword, agent_name in self.routing_rules.items():
            if keyword in message_lower:
                return agent_name
        
        # If no specific routing rule matches, handle by master agent
        return None
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process message and generate appropriate response.
        
        Args:
            message (str): The message to respond to
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the agent's reply
        """
        try:
            # Receive the message first
            received_msg = self.receive(message, context.get("sender", "user") if context else "user")
            
            # Remember the message in short-term memory
            self.remember(f"User: {message}")
            
            # Determine routing
            target_agent = self.route_message(message)
            
            if target_agent and target_agent in self.sub_agents:
                # Route to sub-agent
                sub_agent = self.sub_agents[target_agent]
                if sub_agent.is_active:
                    self.log(f"Routing message to {target_agent}")
                    sub_response = sub_agent.respond(message, context)
                    
                    response = {
                        "response_id": received_msg["message_id"],
                        "content": sub_response.get("content", "پاسخی دریافت نشد"),
                        "handled_by": target_agent,
                        "timestamp": received_msg["timestamp"],
                        "success": True
                    }
                else:
                    response = {
                        "response_id": received_msg["message_id"],
                        "content": f"ایجنت {target_agent} در دسترس نیست.",
                        "handled_by": self.name,
                        "timestamp": received_msg["timestamp"],
                        "success": False
                    }
            else:
                # Handle by master agent
                response_content = self._generate_master_response(message)
                response = {
                    "response_id": received_msg["message_id"],
                    "content": response_content,
                    "handled_by": self.name,
                    "timestamp": received_msg["timestamp"],
                    "success": True
                }
            
            self.log(f"Generated response: {response['content'][:100]}...")
            return response
            
        except Exception as e:
            self.log(f"Error processing message: {str(e)}", "error")
            return {
                "response_id": received_msg.get("message_id", "unknown"),
                "content": self.default_responses["error"],
                "handled_by": self.name,
                "timestamp": received_msg.get("timestamp", ""),
                "success": False,
                "error": str(e)
            }
    
    def _generate_master_response(self, message: str) -> str:
        """
        Generate a response from the master agent itself.
        
        Args:
            message (str): The message to respond to
            
        Returns:
            str: Generated response
        """
        message_lower = message.lower()
        
        # Simple keyword-based responses
        if any(word in message_lower for word in ["سلام", "hello", "hi", "درود"]):
            return self.default_responses["greeting"]
        
        elif any(word in message_lower for word in ["وضعیت", "status", "حال"]):
            active_agents = [name for name, agent in self.sub_agents.items() if agent.is_active]
            return f"وضعیت سیستم: {len(active_agents)} ایجنت فعال - {', '.join(active_agents)}"
        
        elif any(word in message_lower for word in ["کمک", "help", "راهنما"]):
            return self.default_responses["help"]
        
        elif any(word in message_lower for word in ["لیست", "agents", "ایجنت"]):
            agent_list = list(self.sub_agents.keys())
            return f"ایجنت‌های موجود: {', '.join(agent_list) if agent_list else 'هیچ ایجنتی ثبت نشده'}"
        
        elif any(word in message_lower for word in ["show memory", "نمایش حافظه", "حافظه"]):
            recent_memories = self.recall(5)
            memory_status = self.get_memory_status()
            if recent_memories:
                memory_text = "\n".join([f"- {mem['content']}" for mem in recent_memories])
                return f"آخرین حافظه‌ها:\n{memory_text}\n\nوضعیت حافظه: {memory_status['total_entries']}/{memory_status['max_capacity']}"
            else:
                return "حافظه خالی است."
        
        elif any(word in message_lower for word in ["clear memory", "پاک کردن حافظه"]):
            self.clear_memory()
            return "حافظه کوتاه‌مدت پاک شد."
        
        else:
            # Remember the response in memory
            response_text = f"پیام شما دریافت شد: '{message}'. در حال پردازش..."
            self.remember(f"Agent: {response_text}")
            return response_text
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including all agents.
        
        Returns:
            Dict: Complete system status
        """
        agent_statuses = {}
        for name, agent in self.sub_agents.items():
            agent_statuses[name] = agent.get_status()
        
        return {
            "master_agent": self.get_status(),
            "sub_agents": agent_statuses,
            "routing_rules": self.routing_rules,
            "total_agents": len(self.sub_agents),
            "active_agents": len([a for a in self.sub_agents.values() if a.is_active])
        }
    
    async def broadcast_message(self, message: str, exclude_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send a message to all active sub-agents.
        
        Args:
            message (str): Message to broadcast
            exclude_agents (List[str]): Agents to exclude from broadcast
            
        Returns:
            Dict: Responses from all agents
        """
        exclude_agents = exclude_agents or []
        responses = {}
        
        for name, agent in self.sub_agents.items():
            if agent.is_active and name not in exclude_agents:
                try:
                    response = agent.respond(message)
                    responses[name] = response
                except Exception as e:
                    responses[name] = {"error": str(e)}
        
        self.log(f"Broadcasted message to {len(responses)} agents")
        return responses
    
    def _initialize_utility_agent(self) -> None:
        """Initialize and register the UtilityAgent."""
        try:
            from .utility_agent import UtilityAgent
            utility_agent = UtilityAgent()
            self.register_agent(utility_agent, utility_agent.keywords)
            self.log("UtilityAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize UtilityAgent: {e}", level="error")
    
    def _initialize_tool_agent(self) -> None:
        """Initialize and register the ToolAgent."""
        try:
            from .tool_agent import ToolAgent
            tool_agent = ToolAgent()
            self.register_agent(tool_agent, tool_agent.keywords)
            self.log("ToolAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize ToolAgent: {e}", level="error")
    
    def _initialize_summary_agent(self) -> None:
        """Initialize and register the SummaryAgent."""
        try:
            from .summary_agent import SummaryAgent
            summary_agent = SummaryAgent()
            self.register_agent(summary_agent, keywords=[
                'خلاصه', 'summary', 'summarize', 'خلاصه‌سازی', 'خلاصه کن',
                'مختصر', 'brief', 'فشرده', 'compress'
            ])
            self.log("SummaryAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize SummaryAgent: {e}", level="error")
    
    def _initialize_longterm_memory_agent(self) -> None:
        """Initialize and register the LongTermMemoryAgent."""
        try:
            from .longterm_memory_agent import LongTermMemoryAgent
            longterm_memory_agent = LongTermMemoryAgent()
            self.register_agent(longterm_memory_agent, keywords=[
                'حافظه', 'memory', 'ذخیره', 'save', 'یادداشت', 'note',
                'یاد بگیر', 'remember', 'یادآوری', 'remind', 'جستجو', 'search',
                'نشان بده', 'show', 'لیست', 'list', 'آخرین', 'recent'
            ])
            self.log("LongTermMemoryAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize LongTermMemoryAgent: {e}", level="error")
    
    def _initialize_conceptual_memory_agent(self) -> None:
        """Initialize and register the ConceptualMemoryAgent."""
        try:
            from .conceptual_memory_agent import ConceptualMemoryAgent
            conceptual_memory_agent = ConceptualMemoryAgent()
            self.register_agent(conceptual_memory_agent, keywords=[
                'مفهوم', 'concept', 'تحلیل', 'analyze', 'معنی', 'meaning',
                'احساس', 'feeling', 'ارزش', 'value', 'هدف', 'goal',
                'انگیزه', 'motivation', 'الهام', 'inspiration', 'ترس', 'fear'
            ])
            self.log("ConceptualMemoryAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize ConceptualMemoryAgent: {e}", level="error")
    
    def _initialize_repetitive_learning_agent(self) -> None:
        """Initialize and register the RepetitiveLearningAgent."""
        try:
            from .repetitive_learning_agent import RepetitiveLearningAgent
            repetitive_learning_agent = RepetitiveLearningAgent()
            self.register_agent(repetitive_learning_agent, keywords=[
                'تکرار', 'repetitive', 'الگو', 'pattern', 'مکرر', 'repeated',
                'تحلیل', 'analyze', 'بررسی', 'observe', 'مشاهده', 'frequent',
                'یادگیری', 'learning', 'عادت', 'habit'
            ])
            self.log("RepetitiveLearningAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize RepetitiveLearningAgent: {e}", level="error")
    
    def _initialize_knowledge_graph_agent(self) -> None:
        """Initialize and register the KnowledgeGraphAgent."""
        try:
            from .knowledge_graph_agent import KnowledgeGraphAgent
            knowledge_graph_agent = KnowledgeGraphAgent()
            self.register_agent(knowledge_graph_agent, keywords=[
                'گراف', 'graph', 'مفهوم', 'concept', 'رابطه', 'relationship',
                'دانش', 'knowledge', 'استخراج', 'extract', 'ساختار', 'structure',
                'تحلیل', 'analyze', 'شبکه', 'network', 'نقشه', 'map'
            ])
            self.log("KnowledgeGraphAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize KnowledgeGraphAgent: {e}", level="error")
    
    def _initialize_auto_suggester_agent(self) -> None:
        """Initialize and register the AutoSuggesterAgent."""
        try:
            from .auto_suggester_agent import AutoSuggesterAgent
            auto_suggester_agent = AutoSuggesterAgent()
            self.register_agent(auto_suggester_agent, keywords=[
                'پیشنهاد', 'suggestion', 'راهنما', 'hint', 'ادامه', 'continue',
                'کمک', 'help', 'نظر', 'opinion', 'توصیه', 'recommend',
                'بعدی', 'next', 'قدم', 'step', 'اقدام', 'action'
            ])
            self.log("AutoSuggesterAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize AutoSuggesterAgent: {e}", level="error")
    
    def _initialize_goal_inference_agent(self) -> None:
        """Initialize and register the GoalInferenceAgent."""
        try:
            from .goal_inference_agent import GoalInferenceAgent
            goal_inference_agent = GoalInferenceAgent()
            self.register_agent(goal_inference_agent, keywords=[
                'هدف', 'goal', 'نیت', 'intent', 'قصد', 'intention',
                'تشخیص', 'detect', 'تحلیل', 'analyze', 'بررسی', 'examine',
                'چرا', 'why', 'چی', 'what', 'منظور', 'meaning'
            ])
            self.log("GoalInferenceAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize GoalInferenceAgent: {e}", level="error")
    
    def _initialize_emotion_regulation_agent(self) -> None:
        """Initialize and register the EmotionRegulationAgent."""
        try:
            from .emotion_regulation_agent import EmotionRegulationAgent
            emotion_agent = EmotionRegulationAgent()
            self.register_agent(emotion_agent, keywords=[
                'هیجان', 'emotion', 'احساس', 'feeling', 'خشم', 'anger',
                'اضطراب', 'anxiety', 'غم', 'sadness', 'خوشحال', 'happy',
                'ناراحت', 'upset', 'عصبانی', 'angry', 'استرس', 'stress',
                'تنظیم', 'regulate', 'آرام', 'calm', 'کنترل', 'control'
            ])
            self.log("EmotionRegulationAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize EmotionRegulationAgent: {e}", level="error")
    
    def _initialize_decision_support_agent(self) -> None:
        """Initialize and register the DecisionSupportAgent."""
        try:
            from .decision_support_agent import DecisionSupportAgent
            decision_agent = DecisionSupportAgent()
            # Set reference to master for inter-agent communication
            decision_agent._master_agent = self
            self.register_agent(decision_agent, keywords=[
                'تصمیم', 'decision', 'انتخاب', 'choice', 'چه کار', 'what to do',
                'مشاوره', 'advice', 'راهنمایی', 'guidance', 'پیشنهاد', 'suggest',
                'تردید', 'doubt', 'دودلی', 'uncertain', 'کمک', 'help',
                'چی کار', 'نظر', 'opinion', 'راه حل', 'solution'
            ])
            self.log("DecisionSupportAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize DecisionSupportAgent: {e}", level="error")
    
    def _initialize_self_awareness_agent(self) -> None:
        """Initialize and register the SelfAwarenessAgent."""
        try:
            from .self_awareness_agent import SelfAwarenessAgent
            awareness_agent = SelfAwarenessAgent()
            self.register_agent(awareness_agent, keywords=[
                'خودآگاهی', 'self-awareness', 'وضعیت ذهنی', 'mental state',
                'خستگی', 'fatigue', 'بی‌انگیزگی', 'unmotivated', 'گم شدن', 'lost',
                'سردرگمی', 'confusion', 'تمرکز', 'focus', 'انگیزه', 'motivation',
                'احساس خستگی دارم', 'نمی‌دونم دارم چی کار می‌کنم', 'هدفی که داشتم چی بود؟',
                'انگیزه‌ام از بین رفته', 'گیج شدم', 'راه گم کردم', 'feel tired',
                'don\'t know what I\'m doing', 'lost motivation', 'confused'
            ])
            self.log("SelfAwarenessAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize SelfAwarenessAgent: {e}", level="error")

    def _initialize_interactive_security_check_agent(self) -> None:
        """Initialize and register the InteractiveSecurityCheckAgent."""
        try:
            from .interactive_security_check_agent import InteractiveSecurityCheckAgent
            security_agent = InteractiveSecurityCheckAgent()
            self.register_agent(security_agent, keywords=[
                'امنیت', 'security', 'بررسی امنیت', 'security check',
                'تهدید', 'threat', 'خطر', 'risk', 'ریسک',
                'احتیاط', 'caution', 'هشدار', 'alert', 'warning',
                'ایمنی', 'safety', 'محافظت', 'protection',
                'تحلیل امنیت', 'security analysis', 'بررسی خطر', 'risk assessment',
                'فرسودگی', 'burnout', 'استرس', 'stress', 'فشار', 'pressure',
                'عجله', 'impulsive', 'تکانشی', 'رفتار خطرناک', 'dangerous behavior'
            ])
            self.log("InteractiveSecurityCheckAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize InteractiveSecurityCheckAgent: {e}", level="error")

    def _initialize_reward_agent(self) -> None:
        """Initialize and register the RewardAgent."""
        try:
            from .reward_agent import RewardAgent
            reward_agent = RewardAgent()
            self.register_agent(reward_agent, keywords=[
                'پاداش', 'reward', 'تشویق', 'encouragement', 'انگیزه', 'motivation',
                'پیشرفت', 'progress', 'موفقیت', 'success', 'دستاورد', 'achievement',
                'بهبود', 'improvement', 'پیشرفت مثبت', 'positive progress',
                'تبریک', 'congratulations', 'عالی', 'excellent', 'خوب کردم', 'well done',
                'بهتر شدم', 'got better', 'پیش رفتم', 'made progress',
                'موفق شدم', 'succeeded', 'کار خوبی کردم', 'did good work'
            ])
            self.log("RewardAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize RewardAgent: {e}", level="error")

    def _initialize_bias_detection_agent(self) -> None:
        """Initialize and register the BiasDetectionAgent."""
        try:
            from .bias_detection_agent import BiasDetectionAgent
            bias_detection_agent = BiasDetectionAgent()
            self.register_agent(bias_detection_agent, keywords=[
                'سوگیری', 'bias', 'cognitive', 'thinking', 'decision', 'judgment', 
                'تفکر', 'تصمیم', 'قضاوت', 'تحلیل', 'analysis', 'بررسی',
                'confirmation', 'availability', 'overconfidence', 'anchoring',
                'sunk cost', 'negativity', 'framing', 'تأیید', 'دسترسی',
                'اعتماد', 'لنگر', 'هزینه', 'منفی', 'قاب‌بندی'
            ])
            self.log("BiasDetectionAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize BiasDetectionAgent: {e}", level="error")
    
    def _initialize_cognitive_distortion_agent(self) -> None:
        """Initialize and register the CognitiveDistortionAgent."""
        try:
            from .cognitive_distortion_agent import CognitiveDistortionAgent
            cognitive_distortion_agent = CognitiveDistortionAgent()
            self.register_agent(cognitive_distortion_agent, keywords=[
                'تحریف', 'distortion', 'شناختی', 'cognitive', 'فکر', 'thinking',
                'تفکر', 'thought', 'منطق', 'logic', 'استدلال', 'reasoning',
                'تعمیم', 'generalization', 'فاجعه', 'catastrophe', 'برچسب', 'label',
                'شخصی‌سازی', 'personalization', 'ذهن‌خوانی', 'mind reading',
                'عاطفی', 'emotional', 'فیلتر', 'filter', 'سرزنش', 'blame',
                'پیشگویی', 'fortune telling', 'همه یا هیچ', 'all or nothing',
                'تحریف شناختی', 'cognitive distortion', 'بازسازی شناختی', 'cognitive reframing'
            ])
            self.log(f"CognitiveDistortionAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize CognitiveDistortionAgent: {e}", level="error")

    def _initialize_ethical_reasoning_agent(self) -> None:
        """Initialize and register the EthicalReasoningAgent."""
        try:
            from .ethical_reasoning_agent import EthicalReasoningAgent
            ethical_reasoning_agent = EthicalReasoningAgent()
            self.register_agent(ethical_reasoning_agent, keywords=[
                'اخلاق', 'ethics', 'اخلاقی', 'ethical', 'ارزش', 'values', 'value',
                'اخلاقیات', 'morality', 'moral', 'استدلال اخلاقی', 'ethical reasoning',
                'مسئولیت', 'responsibility', 'وظیفه', 'duty', 'obligation', 'تکلیف',
                'عدالت', 'justice', 'fairness', 'انصاف', 'integrity', 'صداقت',
                'فایده‌گرایی', 'utilitarianism', 'utilitarian', 'consequentialism',
                'deontology', 'categorical imperative', 'virtue ethics', 'فضیلت',
                'care ethics', 'مراقبت', 'inaction', 'negligence', 'غفلت',
                'تضاد منافع', 'conflict of interest', 'تبعیض', 'discrimination',
                'سوءاستفاده', 'abuse', 'exploitation', 'بهره‌کشی', 'corruption',
                'فساد', 'harm', 'آسیب', 'بی‌عدالتی', 'injustice', 'unfair'
            ])
            self.log(f"EthicalReasoningAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize EthicalReasoningAgent: {e}", level="error")

    def _initialize_simulated_consensus_agent(self) -> None:
        """Initialize and register the SimulatedConsensusAgent."""
        try:
            from .simulated_consensus_agent import SimulatedConsensusAgent
            simulated_consensus_agent = SimulatedConsensusAgent()
            self.register_agent(simulated_consensus_agent, keywords=[
                'تصمیم گروهی', 'group decision', 'consensus', 'اجماع', 'گروه', 'group',
                'مشاوره', 'consultation', 'نظرسنجی', 'survey', 'رای', 'vote',
                'تصمیم‌گیری', 'decision making', 'collaborative', 'همکاری', 'cooperation',
                'نظرات', 'opinions', 'دیدگاه', 'perspective', 'نقطه نظر', 'point of view',
                'شبیه‌سازی', 'simulation', 'virtual', 'مجازی', 'agents', 'ایجنت',
                'بحث', 'discussion', 'مناقشه', 'debate', 'تبادل نظر', 'exchange',
                'تعامل', 'interaction', 'مذاکره', 'negotiation', 'توافق', 'agreement',
                'رأی‌گیری', 'voting', 'انتخاب', 'selection', 'گزینش', 'choice'
            ])
            self.log(f"SimulatedConsensusAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize SimulatedConsensusAgent: {e}", level="error")

    def _initialize_advanced_memory_manager_agent(self) -> None:
        """Initialize and register the AdvancedMemoryManagerAgent."""
        try:
            from .advanced_memory_manager_agent import AdvancedMemoryManagerAgent
            advanced_memory_manager_agent = AdvancedMemoryManagerAgent()
            self.register_agent(advanced_memory_manager_agent, keywords=[
                'حافظه', 'memory', 'مدیریت حافظه', 'memory management', 'ذخیره', 'storage',
                'بازیابی', 'retrieval', 'خلاصه', 'summary', 'summarize', 'خلاصه‌سازی',
                'حافظه کوتاه‌مدت', 'short-term', 'حافظه بلندمدت', 'long-term', 'حافظه‌بازتابی', 'reflective',
                'حافظه ماموریت', 'mission-specific', 'درجه اهمیت', 'importance', 'آمار حافظه', 'memory statistics',
                'پاکسازی', 'purge', 'مدیریت', 'management', 'تجزیه', 'analysis', 'طبقه‌بندی', 'classification',
                'نگهداری', 'store', 'جستجو', 'search', 'یادآوری', 'recall', 'فراموش', 'forget',
                'حافظه پیشرفته', 'advanced memory', 'مدیر حافظه', 'memory manager'
            ])
            self.log(f"AdvancedMemoryManagerAgent initialized and registered")
        except Exception as e:
            self.log(f"Failed to initialize AdvancedMemoryManagerAgent: {e}", level="error")


# Global instance for easy access
master_agent = MasterAgent()