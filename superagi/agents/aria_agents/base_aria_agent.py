
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.lib.logger import logger

class BaseAriaAgent(ABC):
    """
    Base class for all Aria Robot agents in SuperAGI
    """
    
    def __init__(self, session, agent_id: int):
        self.session = session
        self.agent_id = agent_id
        self.agent = Agent.get_agent_from_id(session, agent_id)
        self.config = Agent.fetch_configuration(session, agent_id)
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capability keywords this agent handles"""
        pass
        
    @abstractmethod
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the agent's main functionality"""
        pass
        
    @abstractmethod
    def get_agent_type(self) -> str:
        """Return the agent type identifier"""
        pass
        
    def log_info(self, message: str):
        """Log info message with agent context"""
        logger.info(f"[{self.get_agent_type()}][Agent-{self.agent_id}] {message}")
        
    def log_error(self, message: str):
        """Log error message with agent context"""
        logger.error(f"[{self.get_agent_type()}][Agent-{self.agent_id}] {message}")
