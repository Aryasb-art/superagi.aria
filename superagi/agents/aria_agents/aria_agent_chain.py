
"""
Aria Agent Chain
Pipeline execution system for chaining multiple Aria agents
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from superagi.agents.aria_agents.aria_controller import AriaController
from superagi.lib.logger import logger


class AriaAgentChain:
    """
    Chain system for executing agents in sequence with data flow
    """
    
    def __init__(self, session, chain_id: str = None):
        """Initialize agent chain"""
        self.session = session
        self.chain_id = chain_id or str(uuid.uuid4())
        self.controller = AriaController(session)
        self.logger = logger
        
        # Chain state
        self.chain_data: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.current_step = 0
        
        # Default chain definition
        self.default_chain = [
            {"agent": "AriaGoalAgent", "name": "goal_analysis"},
            {"agent": "AriaMemoryAgent", "name": "memory_processing"},
            {"agent": "AriaToolAgent", "name": "tool_execution"},
            {"agent": "AriaSummaryAgent", "name": "final_summary"}
        ]
    
    def execute_chain(self, initial_task: str, 
                     chain_config: Optional[List[Dict]] = None,
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the complete agent chain
        
        Args:
            initial_task: The initial task to process
            chain_config: Custom chain configuration
            context: Additional context
            
        Returns:
            Dict with chain execution results
        """
        try:
            # Use provided chain or default
            chain = chain_config or self.default_chain
            
            # Initialize chain data
            self.chain_data = {
                "initial_task": initial_task,
                "context": context or {},
                "chain_id": self.chain_id,
                "started_at": datetime.utcnow().isoformat()
            }
            
            current_input = initial_task
            
            self.logger.info(f"Starting chain execution: {self.chain_id}")
            
            # Execute each step in the chain
            for step_index, step_config in enumerate(chain):
                self.current_step = step_index
                
                step_result = self._execute_step(
                    step_config, 
                    current_input, 
                    step_index
                )
                
                if not step_result.get("success"):
                    return self._create_failure_result(
                        f"Chain failed at step {step_index + 1}: {step_config['name']}",
                        step_result.get("error")
                    )
                
                # Pass result to next step
                current_input = step_result.get("output", current_input)
                
                # Store step data for future steps
                self.chain_data[step_config["name"]] = step_result
            
            # Create final result
            return self._create_success_result(current_input)
            
        except Exception as e:
            self.logger.error(f"Chain execution error: {str(e)}")
            return self._create_failure_result("Chain execution failed", str(e))
    
    def _execute_step(self, step_config: Dict, input_data: str, 
                     step_index: int) -> Dict[str, Any]:
        """Execute a single step in the chain"""
        
        agent_type = step_config["agent"]
        step_name = step_config["name"]
        
        try:
            # Prepare enhanced context for agent
            enhanced_context = {
                "chain_id": self.chain_id,
                "step_index": step_index,
                "step_name": step_name,
                "previous_results": self._get_previous_results(),
                "chain_data": self.chain_data.copy()
            }
            
            self.logger.info(f"Executing step {step_index + 1}: {step_name} with {agent_type}")
            
            # Execute task with specific agent
            result = self.controller.execute_task(
                task=input_data,
                agent_type=agent_type,
                context=enhanced_context
            )
            
            if result.get("success"):
                # Extract output for next step
                agent_result = result.get("result", {})
                
                if isinstance(agent_result, dict):
                    output = agent_result.get("content", str(agent_result))
                else:
                    output = str(agent_result)
                
                step_result = {
                    "success": True,
                    "output": output,
                    "agent_type": agent_type,
                    "step_name": step_name,
                    "raw_result": result,
                    "executed_at": datetime.utcnow().isoformat()
                }
                
                # Add to execution history
                self.execution_history.append(step_result)
                
                return step_result
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "agent_type": agent_type,
                    "step_name": step_name
                }
                
        except Exception as e:
            self.logger.error(f"Step execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent_type,
                "step_name": step_name
            }
    
    def _get_previous_results(self) -> List[Dict[str, Any]]:
        """Get results from previous steps"""
        return [step for step in self.execution_history if step.get("success")]
    
    def _create_success_result(self, final_output: str) -> Dict[str, Any]:
        """Create successful chain result"""
        return {
            "success": True,
            "chain_id": self.chain_id,
            "final_output": final_output,
            "steps_completed": len(self.execution_history),
            "execution_history": self.execution_history,
            "chain_data": self.chain_data,
            "completed_at": datetime.utcnow().isoformat()
        }
    
    def _create_failure_result(self, error_msg: str, error_detail: str = None) -> Dict[str, Any]:
        """Create failed chain result"""
        return {
            "success": False,
            "chain_id": self.chain_id,
            "error": error_msg,
            "error_detail": error_detail,
            "steps_completed": len(self.execution_history),
            "execution_history": self.execution_history,
            "failed_at": datetime.utcnow().isoformat()
        }
    
    def get_chain_status(self) -> Dict[str, Any]:
        """Get current chain status"""
        return {
            "chain_id": self.chain_id,
            "current_step": self.current_step,
            "steps_completed": len(self.execution_history),
            "chain_data": self.chain_data,
            "execution_history": self.execution_history
        }
