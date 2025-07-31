
"""
Aria Agent Pool - Advanced agent management for scalability
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading
import time
from queue import Queue, PriorityQueue
from dataclasses import dataclass
from enum import Enum
import uuid

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy" 
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class AgentInstance:
    id: str
    agent_type: str
    agent: Any
    status: AgentStatus
    last_used: datetime
    task_count: int = 0
    error_count: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class TaskRequest:
    id: str
    message: str
    context: Dict[str, Any]
    priority: int = 1
    max_retries: int = 3
    timeout: int = 30
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def __lt__(self, other):
        return self.priority > other.priority  # Higher priority first

class AriaAgentPool:
    """
    Advanced agent pool management for high-scale deployments
    """
    
    def __init__(self, max_agents_per_type: int = 10):
        self.max_agents_per_type = max_agents_per_type
        self.agent_pools: Dict[str, List[AgentInstance]] = {}
        self.task_queue = PriorityQueue()
        self.active_tasks: Dict[str, TaskRequest] = {}
        
        # Performance metrics
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_response_time": 0,
            "agent_utilization": {}
        }
        
        # Background worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.running = True
        self.worker_thread.start()
        
        # Cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def submit_task(self, message: str, context: Dict[str, Any], 
                   priority: int = 1, agent_type: str = None) -> str:
        """
        Submit task to agent pool with priority
        """
        task_id = str(uuid.uuid4())
        
        # Auto-determine agent type if not specified
        if not agent_type:
            agent_type = self._determine_best_agent_type(message, context)
        
        task = TaskRequest(
            id=task_id,
            message=message,
            context={**context, "preferred_agent_type": agent_type},
            priority=priority
        )
        
        self.task_queue.put(task)
        self.metrics["total_tasks"] += 1
        
        return task_id
    
    def _determine_best_agent_type(self, message: str, context: Dict[str, Any]) -> str:
        """
        Intelligent agent type determination based on load balancing
        """
        # Use master agent's analysis but consider current load
        message_lower = message.lower()
        
        agent_preferences = []
        
        # Keyword-based preferences
        if any(word in message_lower for word in ["tool", "search", "file"]):
            agent_preferences.append("AriaToolAgent")
        elif any(word in message_lower for word in ["memory", "remember", "recall"]):
            agent_preferences.append("AriaMemoryAgent")
        elif any(word in message_lower for word in ["summary", "summarize", "brief"]):
            agent_preferences.append("AriaSummaryAgent")
        elif any(word in message_lower for word in ["goal", "plan", "strategy"]):
            agent_preferences.append("AriaGoalAgent")
        elif any(word in message_lower for word in ["emotion", "feeling", "sentiment"]):
            agent_preferences.append("AriaEmotionAgent")
        else:
            agent_preferences.append("AriaUtilityAgent")
        
        # Consider current load
        for agent_type in agent_preferences:
            current_load = self._get_agent_load(agent_type)
            if current_load < 0.8:  # Less than 80% utilized
                return agent_type
        
        # Return least loaded agent type
        return self._get_least_loaded_agent_type()
    
    def _get_agent_load(self, agent_type: str) -> float:
        """Calculate current load for agent type"""
        if agent_type not in self.agent_pools:
            return 0.0
        
        total_agents = len(self.agent_pools[agent_type])
        busy_agents = len([a for a in self.agent_pools[agent_type] if a.status == AgentStatus.BUSY])
        
        return busy_agents / max(total_agents, 1)
    
    def _get_least_loaded_agent_type(self) -> str:
        """Get the least loaded agent type"""
        agent_types = ["AriaUtilityAgent", "AriaToolAgent", "AriaMemoryAgent", 
                      "AriaSummaryAgent", "AriaGoalAgent", "AriaEmotionAgent"]
        
        min_load = float('inf')
        best_type = "AriaUtilityAgent"
        
        for agent_type in agent_types:
            load = self._get_agent_load(agent_type)
            if load < min_load:
                min_load = load
                best_type = agent_type
        
        return best_type
    
    def _get_or_create_agent(self, agent_type: str) -> Optional[AgentInstance]:
        """Get available agent or create new one"""
        if agent_type not in self.agent_pools:
            self.agent_pools[agent_type] = []
        
        # Find idle agent
        for agent_instance in self.agent_pools[agent_type]:
            if agent_instance.status == AgentStatus.IDLE:
                return agent_instance
        
        # Create new agent if under limit
        if len(self.agent_pools[agent_type]) < self.max_agents_per_type:
            try:
                from superagi.agents.aria_agents.aria_agent_factory import AriaAgentFactory
                agent = AriaAgentFactory.create_agent(None, f"{agent_type}-{len(self.agent_pools[agent_type])}", agent_type)
                
                agent_instance = AgentInstance(
                    id=f"{agent_type}-{uuid.uuid4().hex[:8]}",
                    agent_type=agent_type,  
                    agent=agent,
                    status=AgentStatus.IDLE,
                    last_used=datetime.now()
                )
                
                self.agent_pools[agent_type].append(agent_instance)
                return agent_instance
                
            except Exception as e:
                print(f"Failed to create agent {agent_type}: {e}")
                return None
        
        # All agents busy, wait for one to become available
        return None
    
    def _worker_loop(self):
        """Background worker to process tasks"""
        while self.running:
            try:
                # Get task with timeout
                task = self.task_queue.get(timeout=1)
                
                preferred_agent_type = task.context.get("preferred_agent_type", "AriaUtilityAgent")
                agent_instance = self._get_or_create_agent(preferred_agent_type)
                
                if agent_instance:
                    self._execute_task(agent_instance, task)
                else:
                    # Requeue with lower priority if no agents available
                    task.priority = max(task.priority - 1, 0)
                    self.task_queue.put(task)
                    time.sleep(0.1)  # Brief pause to prevent busy waiting
                    
            except Exception as e:
                if self.running:  # Only log if not shutting down
                    print(f"Worker loop error: {e}")
                time.sleep(0.1)
    
    def _execute_task(self, agent_instance: AgentInstance, task: TaskRequest):
        """Execute task with specific agent"""
        try:
            agent_instance.status = AgentStatus.BUSY
            agent_instance.last_used = datetime.now()
            self.active_tasks[task.id] = task
            
            start_time = datetime.now()
            
            # Execute task
            result = agent_instance.agent.respond(task.message, task.context)
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(agent_instance.agent_type, execution_time, True)
            
            agent_instance.task_count += 1
            agent_instance.status = AgentStatus.IDLE
            
            self.metrics["completed_tasks"] += 1
            
        except Exception as e:
            print(f"Task execution failed: {e}")
            agent_instance.error_count += 1
            agent_instance.status = AgentStatus.ERROR
            self.metrics["failed_tasks"] += 1
            
        finally:
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
    
    def _update_metrics(self, agent_type: str, execution_time: float, success: bool):
        """Update performance metrics"""
        if agent_type not in self.metrics["agent_utilization"]:
            self.metrics["agent_utilization"][agent_type] = {
                "total_tasks": 0,
                "avg_time": 0,
                "success_rate": 1.0
            }
        
        util = self.metrics["agent_utilization"][agent_type]
        util["total_tasks"] += 1
        
        # Rolling average
        util["avg_time"] = (util["avg_time"] * 0.9) + (execution_time * 0.1)
        
        if success:
            util["success_rate"] = (util["success_rate"] * 0.95) + (1.0 * 0.05)
        else:
            util["success_rate"] = (util["success_rate"] * 0.95) + (0.0 * 0.05)
    
    def _cleanup_loop(self):
        """Cleanup idle agents and reset error states"""
        while self.running:
            try:
                time.sleep(60)  # Run every minute
                
                current_time = datetime.now()
                for agent_type, agents in self.agent_pools.items():
                    # Remove old idle agents
                    agents_to_remove = []
                    for agent in agents:
                        if (agent.status == AgentStatus.IDLE and 
                            current_time - agent.last_used > timedelta(minutes=10) and
                            len(agents) > 1):  # Keep at least one agent
                            agents_to_remove.append(agent)
                        
                        # Reset error agents after 5 minutes
                        elif (agent.status == AgentStatus.ERROR and
                              current_time - agent.last_used > timedelta(minutes=5)):
                            agent.status = AgentStatus.IDLE
                            agent.error_count = 0
                    
                    for agent in agents_to_remove:
                        agents.remove(agent)
                        
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status"""
        status = {
            "total_agents": sum(len(agents) for agents in self.agent_pools.values()),
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "metrics": self.metrics,
            "agent_pools": {}
        }
        
        for agent_type, agents in self.agent_pools.items():
            status["agent_pools"][agent_type] = {
                "total": len(agents),
                "idle": len([a for a in agents if a.status == AgentStatus.IDLE]),
                "busy": len([a for a in agents if a.status == AgentStatus.BUSY]),
                "error": len([a for a in agents if a.status == AgentStatus.ERROR]),
                "load": self._get_agent_load(agent_type)
            }
        
        return status
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        self.worker_thread.join(timeout=5)
        self.cleanup_thread.join(timeout=5)
