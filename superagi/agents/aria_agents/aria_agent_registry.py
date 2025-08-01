from typing import Dict, Type, List
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.agents.aria_agents.aria_utility_agent.aria_utility_agent import AriaUtilityAgent
from superagi.agents.aria_agents.aria_tool_agent.aria_tool_agent import AriaToolAgent
from superagi.agents.aria_agents.aria_memory_agent.aria_memory_agent import AriaMemoryAgent
from superagi.agents.aria_agents.aria_summary_agent.aria_summary_agent import AriaSummaryAgent
from superagi.agents.aria_agents.aria_master_agent.aria_master_agent import AriaMasterAgent
from superagi.agents.aria_agents.aria_emotion_agent.aria_emotion_agent import AriaEmotionAgent
from superagi.agents.aria_agents.aria_goal_agent.aria_goal_agent import AriaGoalAgent
from superagi.lib.logger import logger

class AriaAgentRegistry:
    """
    Registry for all Aria Robot agents in SuperAGI
    """

    _agents: Dict[str, Type[BaseAriaAgent]] = {
        "AriaUtilityAgent": AriaUtilityAgent,
        "AriaToolAgent": AriaToolAgent,
        "AriaMemoryAgent": AriaMemoryAgent,
        "AriaSummaryAgent": AriaSummaryAgent,
        "AriaMasterAgent": AriaMasterAgent,
        "AriaEmotionAgent": AriaEmotionAgent,
        "AriaGoalAgent": AriaGoalAgent,
    }

    _capability_map: Dict[str, List[str]] = {}

    @classmethod
    def register_agent(cls, agent_class: Type[BaseAriaAgent]):
        """Register a new Aria agent"""
        agent_type = agent_class.__name__
        cls._agents[agent_type] = agent_class

        # Create temporary instance to get capabilities
        temp_instance = agent_class(None, 0, {})
        capabilities = temp_instance.get_capabilities()

        for capability in capabilities:
            if capability not in cls._capability_map:
                cls._capability_map[capability] = []
            cls._capability_map[capability].append(agent_type)

        logger.info(f"Registered Aria agent: {agent_type} with capabilities: {capabilities}")

    @classmethod
    def get_agent_by_type(cls, agent_type: str) -> Type[BaseAriaAgent]:
        """Get agent class by type"""
        return cls._agents.get(agent_type)

    @classmethod
    def get_agents_by_capability(cls, capability: str) -> List[Type[BaseAriaAgent]]:
        """Get all agents that handle a specific capability"""
        agent_types = cls._capability_map.get(capability, [])
        return [cls._agents[agent_type] for agent_type in agent_types if agent_type in cls._agents]

    @classmethod
    def get_all_agents(cls) -> Dict[str, Type[BaseAriaAgent]]:
        """Get all registered agents"""
        return cls._agents.copy()

    @classmethod
    def get_all_capabilities(cls) -> List[str]:
        """Get all available capabilities"""
        return list(cls._capability_map.keys())

    @classmethod
    def initialize_registry(cls):
        """Initialize the registry with all agents"""
        for agent_class in cls._agents.values():
            try:
                temp_instance = agent_class(None, 0, {})
                capabilities = temp_instance.get_capabilities()

                for capability in capabilities:
                    if capability not in cls._capability_map:
                        cls._capability_map[capability] = []
                    if agent_class.__name__ not in cls._capability_map[capability]:
                        cls._capability_map[capability].append(agent_class.__name__)
            except Exception as e:
                logger.error(f"Error initializing agent {agent_class.__name__}: {str(e)}")

# Initialize the registry
AriaAgentRegistry.initialize_registry()