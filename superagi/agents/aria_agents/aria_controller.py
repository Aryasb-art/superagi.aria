
"""
Aria Robot Central Controller
Central orchestration system for managing and coordinating all Aria agents
"""

from typing import Dict, Any, List, Optional
from superagi.agents.aria_agents.aria_agent_factory import AriaAgentFactory
from superagi.agents.aria_agents.aria_agent_registry import AriaAgentRegistry
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.lib.logger import logger
import json
import uuid
from datetime import datetime


class AriaController:
    """
    Central controller for managing all Aria Robot agents
    """
    
    def __init__(self, session):
        """
        Initialize the Aria Controller
        
        Args:
            session: Database session
        """
        self.session = session
        self.controller_id = str(uuid.uuid4())
        self.active_agents: Dict[str, BaseAriaAgent] = {}
        self.created_at = datetime.utcnow()
        
        # Initialize logger
        self.logger = logger
        self.logger.info(f"Aria Controller initialized with ID: {self.controller_id}")
    
    def get_available_agents(self) -> List[str]:
        """Get list of all available agent types"""
        return AriaAgentFactory.get_available_agent_types()
    
    def get_available_capabilities(self) -> List[str]:
        """Get list of all available capabilities"""
        return AriaAgentFactory.get_available_capabilities()
    
    def create_agent(self, agent_type: str, agent_id: int = None) -> Optional[BaseAriaAgent]:
        """
        Create and register an agent instance
        
        Args:
            agent_type: Type of agent to create
            agent_id: Optional agent ID (defaults to generated ID)
            
        Returns:
            BaseAriaAgent instance or None
        """
        if agent_id is None:
            agent_id = len(self.active_agents) + 1
            
        try:
            agent = AriaAgentFactory.create_agent(self.session, agent_id, agent_type)
            if agent:
                agent_key = f"{agent_type}_{agent_id}"
                self.active_agents[agent_key] = agent
                self.logger.info(f"Agent created: {agent_key}")
                return agent
            else:
                self.logger.error(f"Failed to create agent: {agent_type}")
                return None
        except Exception as e:
            self.logger.error(f"Error creating agent {agent_type}: {str(e)}")
            return None
    
    def get_agent(self, agent_key: str) -> Optional[BaseAriaAgent]:
        """Get an active agent by key"""
        return self.active_agents.get(agent_key)
    
    def execute_task(self, task: str, agent_type: str = None, agent_key: str = None, 
                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task using the most appropriate agent
        
        Args:
            task: Task description
            agent_type: Specific agent type to use (optional)
            agent_key: Specific agent instance to use (optional)
            context: Task context
            
        Returns:
            Dict containing execution result
        """
        try:
            # Determine which agent to use
            agent = None
            
            if agent_key and agent_key in self.active_agents:
                agent = self.active_agents[agent_key]
            elif agent_type:
                # Create agent if not exists
                agent = self.create_agent(agent_type)
            else:
                # Use master agent for coordination
                master_key = None
                for key, active_agent in self.active_agents.items():
                    if isinstance(active_agent.__class__.__name__, str) and "Master" in active_agent.__class__.__name__:
                        master_key = key
                        break
                
                if not master_key:
                    # Create master agent
                    agent = self.create_agent("AriaMasterAgent")
                else:
                    agent = self.active_agents[master_key]
            
            if not agent:
                return {
                    "success": False,
                    "error": "No suitable agent found or could be created",
                    "task": task
                }
            
            # Execute the task
            result = agent.execute(task, context)
            
            return {
                "success": True,
                "result": result,
                "agent_type": agent.get_agent_type(),
                "agent_id": agent.agent_id,
                "task": task,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task": task,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        agent_statuses = {}
        for key, agent in self.active_agents.items():
            try:
                agent_statuses[key] = agent.get_status()
            except Exception as e:
                agent_statuses[key] = {"error": str(e)}
        
        return {
            "controller_id": self.controller_id,
            "created_at": self.created_at.isoformat(),
            "active_agents_count": len(self.active_agents),
            "available_agent_types": self.get_available_agents(),
            "available_capabilities": self.get_available_capabilities(),
            "active_agents": agent_statuses,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def broadcast_message(self, message: str, sender: str = "controller") -> Dict[str, Any]:
        """
        Broadcast a message to all active agents
        
        Args:
            message: Message to broadcast
            sender: Sender identifier
            
        Returns:
            Dict with broadcast results
        """
        results = {}
        
        for key, agent in self.active_agents.items():
            try:
                result = agent.receive(message, sender)
                results[key] = result
            except Exception as e:
                results[key] = {"error": str(e)}
        
        return {
            "broadcast_id": str(uuid.uuid4()),
            "message": message,
            "sender": sender,
            "recipients": len(self.active_agents),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def shutdown_agent(self, agent_key: str) -> bool:
        """Shutdown and remove an agent"""
        if agent_key in self.active_agents:
            try:
                agent = self.active_agents[agent_key]
                agent.deactivate()
                del self.active_agents[agent_key]
                self.logger.info(f"Agent shutdown: {agent_key}")
                return True
            except Exception as e:
                self.logger.error(f"Error shutting down agent {agent_key}: {str(e)}")
                return False
        return False
    
    def shutdown_all(self) -> Dict[str, bool]:
        """Shutdown all active agents"""
        results = {}
        agent_keys = list(self.active_agents.keys())
        
        for key in agent_keys:
            results[key] = self.shutdown_agent(key)
        
        return results
