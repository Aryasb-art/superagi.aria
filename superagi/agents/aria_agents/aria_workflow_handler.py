
from typing import Dict, Any, List
from superagi.agents.aria_agents.aria_agent_factory import AriaAgentFactory
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.lib.logger import logger

class AriaWorkflowHandler:
    """
    Handles workflow execution for Aria Robot agents
    """
    
    def __init__(self, session, agent_id: int):
        self.session = session
        self.agent_id = agent_id
    
    def execute_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow using appropriate Aria agents
        
        Args:
            workflow_data: Workflow configuration and data
            
        Returns:
            Workflow execution results
        """
        try:
            task = workflow_data.get('task', '')
            capability = workflow_data.get('capability', '')
            agent_type = workflow_data.get('agent_type', '')
            context = workflow_data.get('context', {})
            
            # Create agent based on type or capability
            agent = None
            if agent_type:
                agent = AriaAgentFactory.create_agent(self.session, self.agent_id, agent_type)
            elif capability:
                agent = AriaAgentFactory.create_agent_by_capability(self.session, self.agent_id, capability)
            
            if not agent:
                return {
                    "status": "error",
                    "error": f"No suitable Aria agent found for task: {task}"
                }
            
            # Execute the task
            result = agent.execute(task, context)
            
            logger.info(f"Workflow executed successfully with {agent.get_agent_type()}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing Aria workflow: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def execute_multi_agent_workflow(self, workflow_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a multi-step workflow using multiple Aria agents
        
        Args:
            workflow_steps: List of workflow steps
            
        Returns:
            List of execution results for each step
        """
        results = []
        
        for i, step in enumerate(workflow_steps):
            logger.info(f"Executing workflow step {i+1}/{len(workflow_steps)}")
            
            # Add previous results to context
            step_context = step.get('context', {})
            step_context['previous_results'] = results
            step['context'] = step_context
            
            result = self.execute_workflow(step)
            results.append(result)
            
            # Stop on error if configured
            if result.get('status') == 'error' and step.get('stop_on_error', True):
                logger.error(f"Stopping workflow execution at step {i+1} due to error")
                break
        
        return results
