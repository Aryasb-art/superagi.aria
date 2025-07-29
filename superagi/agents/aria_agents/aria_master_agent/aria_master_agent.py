from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from typing import Dict, Any, Optional
import logging

class AriaMasterAgent(BaseAriaAgent):
    """
    Master Agent - Central coordination and decision-making agent
    Manages overall task flow and delegates to specialized agents
    """

    def __init__(self, session, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(session, agent_id, config)
        self.name = "AriaMasterAgent"
        self.description = "Central coordination and decision-making agent"
        self.capabilities = [
            "task_coordination",
            "agent_delegation", 
            "decision_making",
            "workflow_management"
        ]

    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate coordinated response by analyzing task and delegating to appropriate agents
        """
        self.log(f"Master agent processing: {message[:100]}...")

        # Analyze task complexity and requirements
        task_analysis = self._analyze_task(message, context)

        # Determine required agents and coordination strategy
        coordination_plan = self._create_coordination_plan(task_analysis)

        # Execute coordination plan
        response = self._execute_coordination(coordination_plan, message, context)

        return {
            "agent": self.name,
            "response": response,
            "task_analysis": task_analysis,
            "coordination_plan": coordination_plan,
            "timestamp": self._get_timestamp(),
            "metadata": {
                "complexity": task_analysis.get("complexity", "medium"),
                "agents_involved": coordination_plan.get("agents", []),
                "execution_strategy": coordination_plan.get("strategy", "sequential")
            }
        }

    def _analyze_task(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze task complexity and requirements with weighted scoring"""
        
        # Agent scoring system
        agent_scores = {
            "AriaUtilityAgent": 0,
            "AriaToolAgent": 0,
            "AriaMemoryAgent": 0,
            "AriaSummaryAgent": 0,
            "AriaGoalAgent": 0,
            "AriaEmotionAgent": 0
        }
        
        # Keyword weights and mappings
        keyword_weights = {
            # Tool Agent keywords
            "tool": {"AriaToolAgent": 5, "AriaUtilityAgent": 2},
            "search": {"AriaToolAgent": 4, "AriaUtilityAgent": 1},
            "file": {"AriaToolAgent": 4},
            "email": {"AriaToolAgent": 3},
            "download": {"AriaToolAgent": 4},
            
            # Memory Agent keywords
            "remember": {"AriaMemoryAgent": 5},
            "recall": {"AriaMemoryAgent": 5},
            "memory": {"AriaMemoryAgent": 4},
            "previous": {"AriaMemoryAgent": 3},
            "history": {"AriaMemoryAgent": 3},
            
            # Summary Agent keywords
            "summarize": {"AriaSummaryAgent": 5},
            "summary": {"AriaSummaryAgent": 5},
            "brief": {"AriaSummaryAgent": 4},
            "overview": {"AriaSummaryAgent": 3},
            "analyze": {"AriaSummaryAgent": 2, "AriaUtilityAgent": 2},
            
            # Goal Agent keywords
            "goal": {"AriaGoalAgent": 5},
            "plan": {"AriaGoalAgent": 4},
            "strategy": {"AriaGoalAgent": 3},
            "objective": {"AriaGoalAgent": 4},
            
            # Emotion Agent keywords
            "emotion": {"AriaEmotionAgent": 5},
            "feeling": {"AriaEmotionAgent": 4},
            "sentiment": {"AriaEmotionAgent": 4},
            "mood": {"AriaEmotionAgent": 3}
        }
        
        # Calculate scores based on keywords
        message_lower = message.lower()
        for keyword, agents_weights in keyword_weights.items():
            if keyword in message_lower:
                for agent, weight in agents_weights.items():
                    agent_scores[agent] += weight
        
        # Default utility agent gets base score
        if sum(agent_scores.values()) == 0:
            agent_scores["AriaUtilityAgent"] = 3
        
        # Determine primary and secondary agents
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        primary_agent = sorted_agents[0][0] if sorted_agents[0][1] > 0 else "AriaUtilityAgent"
        
        # Complexity analysis
        complexity = "medium"
        if any(word in message_lower for word in ["complex", "multiple", "analyze", "research"]):
            complexity = "high"
        elif any(word in message_lower for word in ["simple", "quick", "basic"]):
            complexity = "low"
        
        analysis = {
            "complexity": complexity,
            "primary_agent": primary_agent,
            "agent_scores": agent_scores,
            "sorted_agents": sorted_agents,
            "requires_tools": agent_scores["AriaToolAgent"] > 0,
            "requires_memory": agent_scores["AriaMemoryAgent"] > 0,
            "requires_summary": agent_scores["AriaSummaryAgent"] > 0,
            "task_type": self._determine_task_type(message_lower)
        }
        
        return analysis
    
    def _determine_task_type(self, message_lower: str) -> str:
        """Determine task type based on content"""
        if any(word in message_lower for word in ["question", "what", "how", "why"]):
            return "question"
        elif any(word in message_lower for word in ["create", "generate", "make"]):
            return "creation"
        elif any(word in message_lower for word in ["find", "search", "lookup"]):
            return "search"
        elif any(word in message_lower for word in ["analyze", "review", "examine"]):
            return "analysis"
        else:
            return "general"

    def _create_coordination_plan(self, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create coordination plan based on task analysis"""
        plan = {
            "strategy": "sequential",
            "agents": ["AriaUtilityAgent"],
            "steps": []
        }

        # Determine which agents to involve
        if task_analysis["requires_tools"]:
            plan["agents"].append("AriaToolAgent")

        if task_analysis["requires_memory"]:
            plan["agents"].append("AriaMemoryAgent")

        if task_analysis["requires_summary"]:
            plan["agents"].append("AriaSummaryAgent")

        # Create execution steps
        for i, agent in enumerate(plan["agents"]):
            plan["steps"].append({
                "step": i + 1,
                "agent": agent,
                "action": "process_task"
            })

        return plan

    def _execute_coordination(self, plan: Dict[str, Any], message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute coordination plan with error handling and fallback"""
        results = []
        failed_agents = []
        
        for step in plan["steps"]:
            agent_name = step["agent"]
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    self.log(f"Delegating to {agent_name} (attempt {retry_count + 1})")
                    
                    # Try to execute with specific agent
                    result = self._execute_agent_task(agent_name, message, context)
                    
                    if result.get("success"):
                        results.append(f"✅ {agent_name}: {result.get('response', 'Task completed')}")
                        break
                    else:
                        raise Exception(result.get("error", "Unknown error"))
                        
                except Exception as e:
                    retry_count += 1
                    self.log(f"❌ {agent_name} failed (attempt {retry_count}): {str(e)}")
                    
                    if retry_count >= max_retries:
                        failed_agents.append(agent_name)
                        # Try fallback agent
                        fallback_result = self._try_fallback_agent(agent_name, message, context)
                        if fallback_result:
                            results.append(f"🔄 Fallback for {agent_name}: {fallback_result}")
                        else:
                            results.append(f"❌ {agent_name}: Failed after {max_retries} attempts")
        
        # Generate final response with error summary
        response_parts = [
            "Master Agent Coordination Report:",
            *results
        ]
        
        if failed_agents:
            response_parts.extend([
                "",
                f"⚠️  Failed agents: {', '.join(failed_agents)}",
                "✅ Fallback mechanisms were activated where possible"
            ])
        
        return "\n".join(response_parts)
    
    def _execute_agent_task(self, agent_name: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with specific agent"""
        try:
            # Simulate agent execution with potential for failure
            import random
            if random.random() < 0.1:  # 10% chance of failure for simulation
                return {
                    "success": False,
                    "error": f"Simulated failure in {agent_name}"
                }
            
            return {
                "success": True,
                "response": f"Task processed successfully by {agent_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _try_fallback_agent(self, failed_agent: str, message: str, context: Dict[str, Any]) -> str:
        """Try fallback agent when primary agent fails"""
        
        fallback_mapping = {
            "AriaToolAgent": "AriaUtilityAgent",
            "AriaMemoryAgent": "AriaUtilityAgent", 
            "AriaSummaryAgent": "AriaUtilityAgent",
            "AriaGoalAgent": "AriaUtilityAgent",
            "AriaEmotionAgent": "AriaUtilityAgent",
            "AriaUtilityAgent": "AriaMasterAgent"  # Last resort
        }
        
        fallback_agent = fallback_mapping.get(failed_agent)
        if fallback_agent and fallback_agent != failed_agent:
            try:
                self.log(f"Trying fallback: {fallback_agent} for {failed_agent}")
                result = self._execute_agent_task(fallback_agent, message, context)
                if result.get("success"):
                    return f"Handled by {fallback_agent} (fallback)"
            except Exception as e:
                self.log(f"Fallback also failed: {str(e)}")
        
        return None

    def execute(self, *args, **kwargs):
        """Execute master agent functionality"""
        if args:
            message = args[0]
            context = kwargs.get('context')
            return self.respond(message, context)
        return {"status": "executed", "agent": self.name}

    def get_agent_type(self) -> str:
        """Return the agent type"""
        return "AriaMasterAgent"

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "can_coordinate": True,
            "can_delegate": True,
            "coordination_strategies": ["sequential", "parallel", "hierarchical"]
        }