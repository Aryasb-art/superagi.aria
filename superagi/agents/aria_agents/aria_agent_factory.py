
from typing import Optional
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.agents.aria_agents.aria_agent_registry import AriaAgentRegistry
from superagi.lib.logger import logger

class AriaAgentFactory:
    """
    Factory for creating Aria Robot agents
    """
    
    @staticmethod
    def create_agent(session, agent_id: int, agent_type: str) -> Optional[BaseAriaAgent]:
        """
        Create an Aria agent instance
        
        Args:
            session: Database session
            agent_id: Agent ID
            agent_type: Type of agent to create
            
        Returns:
            BaseAriaAgent instance or None if not found
        """
        try:
            agent_class = AriaAgentRegistry.get_agent_by_type(agent_type)
            if agent_class:
                return agent_class(session, agent_id)
            else:
                logger.error(f"Unknown Aria agent type: {agent_type}")
                return None
        except Exception as e:
            logger.error(f"Error creating Aria agent {agent_type}: {str(e)}")
            return None
    
    @staticmethod
    def create_agent_by_capability(session, agent_id: int, capability: str) -> Optional[BaseAriaAgent]:
        """
        Create an agent that handles a specific capability
        
        Args:
            session: Database session
            agent_id: Agent ID
            capability: Required capability
            
        Returns:
            BaseAriaAgent instance or None if not found
        """
        try:
            agents = AriaAgentRegistry.get_agents_by_capability(capability)
            if agents:
                # Return the first available agent for the capability
                agent_class = agents[0]
                return agent_class(session, agent_id)
            else:
                logger.error(f"No Aria agent found for capability: {capability}")
                return None
        except Exception as e:
            logger.error(f"Error creating Aria agent for capability {capability}: {str(e)}")
            return None
    
    @staticmethod
    def get_available_agent_types() -> list:
        """Get list of all available Aria agent types"""
        return list(AriaAgentRegistry.get_all_agents().keys())
    
    @staticmethod
    def get_available_capabilities() -> list:
        """Get list of all available capabilities"""
        return AriaAgentRegistry.get_all_capabilities()
