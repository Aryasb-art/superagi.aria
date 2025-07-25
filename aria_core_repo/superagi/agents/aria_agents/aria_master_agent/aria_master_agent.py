"""
Aria Master Agent for coordinating and managing other AI agents.
"""

from typing import Dict, Any, Optional, List
from ..base_agent import BaseAgent
import json
import yaml
import os


class AriaMasterAgent(BaseAgent):
    """
    Central coordination agent that manages communication between different sub-agents.
    Acts as a router and orchestrator for the multi-agent system.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "agent_config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            agent_config = yaml.safe_load(f)
        
        super().__init__(
            name="AriaMasterAgent",
            description="Central coordinator for managing and routing messages between AI agents",
            config=config or agent_config
        )
        
        self.sub_agents: Dict[str, BaseAgent] = {}
        self.routing_rules: Dict[str, str] = {}
        self.default_responses = {
            "greeting": "سلام! من AriaMasterAgent هستم. چطور می‌تونم کمکتون کنم؟",
            "status": "سیستم آماده است. تمام ایجنت‌ها فعال هستند.",
            "help": "می‌تونم پیام‌هاتون رو به ایجنت‌های مناسب ارجاع بدم یا مستقیماً پاسخ بدم.",
            "error": "متأسفم، مشکلی پیش آمده. لطفاً دوباره تلاش کنید."
        }
        
        # Initialize routing capabilities
        self._setup_routing_rules()
    
    def _setup_routing_rules(self):
        """Setup routing rules based on configuration"""
        if "routing_keywords" in self.config.get("agent_config", {}):
            for keyword in self.config["agent_config"]["routing_keywords"]:
                self.routing_rules[keyword.lower()] = "AriaMasterAgent"
    
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
            bool: True if successful, False otherwise
        """
        if agent_name in self.sub_agents:
            del self.sub_agents[agent_name]
            
            # Remove routing rules
            rules_to_remove = []
            for keyword, routed_agent in self.routing_rules.items():
                if routed_agent == agent_name:
                    rules_to_remove.append(keyword)
            
            for rule in rules_to_remove:
                del self.routing_rules[rule]
            
            self.log(f"Unregistered sub-agent: {agent_name}")
            return True
        
        return False
    
    def route_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Route a message to the appropriate agent based on keywords.
        
        Args:
            message (str): The message to route
            context (Dict): Optional context information
            
        Returns:
            Optional[str]: Name of the agent to route to, or None for master agent
        """
        message_lower = message.lower()
        
        # Check routing rules
        for keyword, agent_name in self.routing_rules.items():
            if keyword in message_lower:
                if agent_name in self.sub_agents:
                    return agent_name
        
        # Default to master agent
        return None
    
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response to a received message.
        
        Args:
            message (str): The message to respond to
            context (Dict): Optional context information
            
        Returns:
            Dict: Response with content and metadata
        """
        try:
            # Store in memory
            self.remember(f"User: {message}")
            
            # Route message
            target_agent = self.route_message(message, context)
            
            if target_agent and target_agent in self.sub_agents:
                # Forward to sub-agent
                response = self.sub_agents[target_agent].respond(message, context)
                self.remember(f"Routed to {target_agent}: {response.get('content', '')[:100]}...")
                return response
            
            # Handle directly
            response_content = self._generate_direct_response(message, context)
            
            response = {
                "response_id": f"{self.agent_id}_{hash(message) % 100000}",
                "content": response_content,
                "handled_by": self.name,
                "timestamp": self.created_at.isoformat(),
                "success": True,
                "error": None
            }
            
            self.remember(f"Agent: {response_content}")
            self.log(f"Generated response: {response_content[:100]}...")
            
            return response
            
        except Exception as e:
            error_response = {
                "response_id": f"error_{hash(str(e)) % 100000}",
                "content": f"خطا در پردازش پیام: {str(e)}",
                "handled_by": self.name,
                "timestamp": self.created_at.isoformat(),
                "success": False,
                "error": str(e)
            }
            
            self.log(f"Error processing message: {e}", "error")
            return error_response
    
    def _generate_direct_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a direct response from the master agent.
        
        Args:
            message (str): The message to respond to
            context (Dict): Optional context information
            
        Returns:
            str: Response content
        """
        message_lower = message.lower()
        
        # Check for specific commands
        if any(word in message_lower for word in ['سلام', 'hello', 'hi', 'greeting']):
            return self.default_responses["greeting"]
        elif any(word in message_lower for word in ['وضعیت', 'status', 'system']):
            return self._get_system_status_response()
        elif any(word in message_lower for word in ['کمک', 'help', 'راهنما']):
            return self.default_responses["help"]
        else:
            # Default response with system info
            return f"پیام شما دریافت شد: '{message}'. در حال پردازش..."
    
    def _get_system_status_response(self) -> str:
        """Get system status response"""
        active_agents = len(self.sub_agents)
        agent_names = list(self.sub_agents.keys())
        
        if active_agents == 0:
            return "هیچ ایجنت فرعی فعال نیست."
        
        return f"وضعیت سیستم: {active_agents} ایجنت فعال - {', '.join(agent_names)}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dict: System status information
        """
        sub_agent_status = {}
        for name, agent in self.sub_agents.items():
            sub_agent_status[name] = agent.get_status()
        
        return {
            "master_agent": self.get_status(),
            "sub_agents": sub_agent_status,
            "routing_rules": self.routing_rules,
            "total_agents": len(self.sub_agents),
            "active_agents": len([a for a in self.sub_agents.values() if a.is_active])
        }
    
    def broadcast_message(self, message: str, sender: str = "master") -> Dict[str, Any]:
        """
        Broadcast a message to all active sub-agents.
        
        Args:
            message (str): Message to broadcast
            sender (str): Sender identifier
            
        Returns:
            Dict: Broadcast results
        """
        results = {}
        
        for name, agent in self.sub_agents.items():
            if agent.is_active:
                try:
                    response = agent.respond(message, {"sender": sender, "broadcast": True})
                    results[name] = {
                        "success": True,
                        "response": response
                    }
                except Exception as e:
                    results[name] = {
                        "success": False,
                        "error": str(e)
                    }
        
        self.log(f"Broadcast message to {len(results)} agents")
        return results
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """
        Get capabilities of all registered agents.
        
        Returns:
            Dict: Agent capabilities mapping
        """
        capabilities = {
            self.name: self.config.get("agent_config", {}).get("capabilities", [])
        }
        
        for name, agent in self.sub_agents.items():
            if hasattr(agent, 'config') and agent.config:
                capabilities[name] = agent.config.get("agent_config", {}).get("capabilities", [])
            else:
                capabilities[name] = ["basic_response"]
        
        return capabilities