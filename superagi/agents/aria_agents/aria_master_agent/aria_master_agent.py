
from typing import Dict, Any, List
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.llms.base_llm import BaseLlm


class AriaMasterAgent(BaseAriaAgent):
    """
    Aria Master Agent for orchestrating other agents
    """
    
    def __init__(self, llm: BaseLlm, **kwargs):
        super().__init__(llm=llm, **kwargs)
        self.agent_type = "master"
        self.sub_agents = {}
    
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute master orchestration task
        """
        try:
            prompt = f"""
            As a master agent, analyze the following task and determine the best approach:
            
            Task: {task}
            Context: {context or {}}
            
            Provide your analysis and action plan:
            """
            
            response = self.llm.chat_completion([{"role": "user", "content": prompt}])
            
            return {
                "success": True,
                "analysis": response,
                "agent_type": self.agent_type,
                "action_plan": "Task analyzed and plan generated"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": self.agent_type
            }
    
    def delegate_task(self, task: str, agent_type: str) -> Dict[str, Any]:
        """
        Delegate task to sub-agent
        """
        if agent_type in self.sub_agents:
            return self.sub_agents[agent_type].execute(task)
        else:
            return {
                "success": False,
                "error": f"Agent type {agent_type} not available",
                "agent_type": self.agent_type
            }
    
    def get_capabilities(self) -> List[str]:
        """
        Return agent capabilities
        """
        return [
            "task_orchestration",
            "agent_coordination",
            "workflow_management",
            "decision_making"
        ]
    
    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """
        Return agent configuration
        """
        return {
            "name": "AriaMasterAgent",
            "description": "Master agent for orchestrating and coordinating other agents",
            "capabilities": ["task_orchestration", "agent_coordination"],
            "version": "1.0.0"
        }
