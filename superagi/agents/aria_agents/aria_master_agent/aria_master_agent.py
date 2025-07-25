"""
AriaMasterAgent - Central coordination system for managing and orchestrating multiple specialized agents
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.lib.logger import logger

class AriaMasterAgent(BaseAriaAgent):
    """
    AriaMasterAgent serves as the central coordination system that:
    - Manages and orchestrates multiple specialized agents
    - Routes tasks to appropriate agents based on capabilities
    - Coordinates complex multi-agent workflows
    - Monitors agent performance and health
    - Handles inter-agent communication and data sharing
    """

    def __init__(self, llm, agent_id: int, agent_execution_id: int = None):
        super().__init__(llm, agent_id, agent_execution_id)
        self.agent_name = "AriaMasterAgent"
        self.registered_agents = {}
        self.agent_capabilities = {}
        self.task_queue = []
        self.active_workflows = {}
        self.agent_health_status = {}
        self.coordination_history = []

    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent.

        Returns:
            List[str]: List of capability strings
        """
        return [
            "agent_coordination",
            "workflow_orchestration",
            "task_delegation",
            "multi_agent_communication",
            "system_monitoring"
        ]

    def get_agent_type(self) -> str:
        """
        Get the type identifier for this agent.

        Returns:
            str: Agent type identifier
        """
        return "AriaMasterAgent"

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute master coordination tasks

        Args:
            task: Dictionary containing task information

        Returns:
            Dictionary containing execution results
        """
        try:
            task_type = task.get('type', 'coordinate')

            if task_type == 'register_agent':
                return self._register_agent(task)
            elif task_type == 'route_task':
                return self._route_task(task)
            elif task_type == 'orchestrate_workflow':
                return self._orchestrate_workflow(task)
            elif task_type == 'monitor_agents':
                return self._monitor_agents(task)
            elif task_type == 'coordinate_communication':
                return self._coordinate_communication(task)
            elif task_type == 'get_system_status':
                return self._get_system_status(task)
            else:
                return self._coordinate_general_task(task)

        except Exception as e:
            logger.error(f"AriaMasterAgent execution error: {str(e)}")
            return {
                "status": "error",
                "message": f"Master coordination failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _register_agent(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent with the master coordination system"""
        try:
            agent_info = task.get('agent_info', {})
            agent_id = agent_info.get('id')
            agent_name = agent_info.get('name')
            capabilities = agent_info.get('capabilities', [])

            if not agent_id or not agent_name:
                return {
                    "status": "error",
                    "message": "Agent ID and name are required for registration"
                }

            # Register the agent
            self.registered_agents[agent_id] = {
                'name': agent_name,
                'capabilities': capabilities,
                'status': 'active',
                'registered_at': datetime.now().isoformat(),
                'last_task_time': None,
                'task_count': 0,
                'success_rate': 1.0
            }

            # Update capability mapping
            for capability in capabilities:
                if capability not in self.agent_capabilities:
                    self.agent_capabilities[capability] = []
                if agent_id not in self.agent_capabilities[capability]:
                    self.agent_capabilities[capability].append(agent_id)

            # Initialize health status
            self.agent_health_status[agent_id] = {
                'status': 'healthy',
                'last_check': datetime.now().isoformat(),
                'response_time': 0.0,
                'error_count': 0
            }

            logger.info(f"Agent registered successfully: {agent_name} ({agent_id})")

            return {
                "status": "success",
                "message": f"Agent {agent_name} registered successfully",
                "agent_id": agent_id,
                "capabilities": capabilities,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Agent registration error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to register agent: {str(e)}"
            }

    def _route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route a task to the most appropriate agent"""
        try:
            task_requirements = task.get('requirements', [])
            task_priority = task.get('priority', 0.5)
            task_data = task.get('task_data', {})

            # Find suitable agents
            suitable_agents = self._find_suitable_agents(task_requirements)

            if not suitable_agents:
                return {
                    "status": "error",
                    "message": "No suitable agents found for task requirements",
                    "requirements": task_requirements
                }

            # Select the best agent based on availability and performance
            selected_agent = self._select_best_agent(suitable_agents, task_priority)

            # Create task assignment
            task_assignment = {
                'task_id': f"task_{int(time.time() * 1000)}",
                'assigned_agent': selected_agent,
                'task_data': task_data,
                'priority': task_priority,
                'assigned_at': datetime.now().isoformat(),
                'status': 'assigned'
            }

            # Add to task queue
            self.task_queue.append(task_assignment)

            # Update agent task count
            if selected_agent in self.registered_agents:
                self.registered_agents[selected_agent]['task_count'] += 1
                self.registered_agents[selected_agent]['last_task_time'] = datetime.now().isoformat()

            logger.info(f"Task routed to agent: {selected_agent}")

            return {
                "status": "success",
                "message": "Task routed successfully",
                "task_id": task_assignment['task_id'],
                "assigned_agent": selected_agent,
                "agent_name": self.registered_agents.get(selected_agent, {}).get('name', 'Unknown'),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Task routing error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to route task: {str(e)}"
            }

    def _orchestrate_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a complex multi-agent workflow"""
        try:
            workflow_definition = task.get('workflow', {})
            workflow_id = workflow_definition.get('id', f"workflow_{int(time.time() * 1000)}")
            steps = workflow_definition.get('steps', [])

            if not steps:
                return {
                    "status": "error",
                    "message": "Workflow must contain at least one step"
                }

            # Create workflow instance
            workflow_instance = {
                'id': workflow_id,
                'steps': steps,
                'current_step': 0,
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'results': {},
                'step_history': []
            }

            # Add to active workflows
            self.active_workflows[workflow_id] = workflow_instance

            # Execute first step
            first_step_result = self._execute_workflow_step(workflow_instance, 0)

            return {
                "status": "success",
                "message": "Workflow orchestration started",
                "workflow_id": workflow_id,
                "total_steps": len(steps),
                "first_step_result": first_step_result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Workflow orchestration error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to orchestrate workflow: {str(e)}"
            }

    def _monitor_agents(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor the health and performance of registered agents"""
        try:
            detailed_report = task.get('detailed', False)

            agent_reports = {}

            for agent_id, agent_info in self.registered_agents.items():
                health_info = self.agent_health_status.get(agent_id, {})

                basic_report = {
                    'name': agent_info['name'],
                    'status': agent_info['status'],
                    'health': health_info.get('status', 'unknown'),
                    'task_count': agent_info['task_count'],
                    'success_rate': agent_info['success_rate']
                }

                if detailed_report:
                    basic_report.update({
                        'capabilities': agent_info['capabilities'],
                        'registered_at': agent_info['registered_at'],
                        'last_task_time': agent_info['last_task_time'],
                        'response_time': health_info.get('response_time', 0.0),
                        'error_count': health_info.get('error_count', 0),
                        'last_health_check': health_info.get('last_check')
                    })

                agent_reports[agent_id] = basic_report

            # Calculate system statistics
            total_agents = len(self.registered_agents)
            active_agents = sum(1 for info in self.registered_agents.values() if info['status'] == 'active')
            healthy_agents = sum(1 for info in self.agent_health_status.values() if info['status'] == 'healthy')

            return {
                "status": "success",
                "message": "Agent monitoring completed",
                "system_stats": {
                    "total_agents": total_agents,
                    "active_agents": active_agents,
                    "healthy_agents": healthy_agents,
                    "system_health": healthy_agents / max(total_agents, 1)
                },
                "agents": agent_reports,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Agent monitoring error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to monitor agents: {str(e)}"
            }

    def _coordinate_communication(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate communication between agents"""
        try:
            communication_type = task.get('communication_type', 'broadcast')
            sender_agent = task.get('sender')
            target_agents = task.get('targets', [])
            message = task.get('message', {})

            if communication_type == 'broadcast':
                # Send message to all registered agents
                target_agents = list(self.registered_agents.keys())
            elif communication_type == 'targeted' and not target_agents:
                return {
                    "status": "error",
                    "message": "Target agents required for targeted communication"
                }

            # Prepare communication record
            communication_record = {
                'id': f"comm_{int(time.time() * 1000)}",
                'type': communication_type,
                'sender': sender_agent,
                'targets': target_agents,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'delivery_status': {}
            }

            # Simulate message delivery
            successful_deliveries = 0
            for target in target_agents:
                if target in self.registered_agents and self.registered_agents[target]['status'] == 'active':
                    communication_record['delivery_status'][target] = 'delivered'
                    successful_deliveries += 1
                else:
                    communication_record['delivery_status'][target] = 'failed'

            # Add to coordination history
            self.coordination_history.append(communication_record)

            return {
                "status": "success",
                "message": "Communication coordinated successfully",
                "communication_id": communication_record['id'],
                "targets_count": len(target_agents),
                "successful_deliveries": successful_deliveries,
                "delivery_rate": successful_deliveries / max(len(target_agents), 1),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Communication coordination error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to coordinate communication: {str(e)}"
            }

    def _get_system_status(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            include_history = task.get('include_history', False)

            system_status = {
                "master_agent": {
                    "name": self.agent_name,
                    "status": "active",
                    "uptime": datetime.now().isoformat()
                },
                "registered_agents": len(self.registered_agents),
                "active_workflows": len(self.active_workflows),
                "pending_tasks": len(self.task_queue),
                "capabilities_coverage": len(self.agent_capabilities),
                "system_health": self._calculate_system_health()
            }

            if include_history:
                system_status["recent_communications"] = self.coordination_history[-10:]  # Last 10
                system_status["completed_workflows"] = [
                    wf for wf in self.active_workflows.values() 
                    if wf['status'] == 'completed'
                ]

            return {
                "status": "success",
                "message": "System status retrieved successfully",
                "system_status": system_status,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"System status error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get system status: {str(e)}"
            }

    def _coordinate_general_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general coordination tasks"""
        try:
            # Analyze the task and determine coordination strategy
            task_analysis = {
                "complexity": self._analyze_task_complexity(task),
                "required_capabilities": self._extract_capabilities(task),
                "estimated_duration": self._estimate_task_duration(task),
                "resource_requirements": self._assess_resource_requirements(task)
            }

            return {
                "status": "success",
                "message": "General coordination task processed",
                "task_analysis": task_analysis,
                "coordination_recommendation": self._generate_coordination_recommendation(task_analysis),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"General coordination error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to coordinate general task: {str(e)}"
            }

    def _find_suitable_agents(self, requirements: List[str]) -> List[str]:
        """Find agents that meet the task requirements"""
        suitable_agents = []

        for requirement in requirements:
            if requirement in self.agent_capabilities:
                suitable_agents.extend(self.agent_capabilities[requirement])

        # Remove duplicates and filter active agents
        suitable_agents = list(set(suitable_agents))
        suitable_agents = [
            agent_id for agent_id in suitable_agents
            if agent_id in self.registered_agents and 
               self.registered_agents[agent_id]['status'] == 'active'
        ]

        return suitable_agents

    def _select_best_agent(self, suitable_agents: List[str], task_priority: float) -> str:
        """Select the best agent from suitable candidates"""
        if not suitable_agents:
            return None

        # Score agents based on performance metrics
        agent_scores = {}

        for agent_id in suitable_agents:
            agent_info = self.registered_agents[agent_id]
            health_info = self.agent_health_status.get(agent_id, {})

            score = 0.0

            # Success rate weight (40%)
            score += agent_info['success_rate'] * 0.4

            # Health status weight (30%)
            if health_info.get('status') == 'healthy':
                score += 0.3

            # Response time weight (20%) - lower is better
            response_time = health_info.get('response_time', 1.0)
            score += max(0, (1.0 - response_time)) * 0.2

            # Task load weight (10%) - lower load is better
            task_count = agent_info['task_count']
            if task_count == 0:
                score += 0.1
            else:
                score += max(0, (1.0 - min(task_count / 10.0, 1.0))) * 0.1

            agent_scores[agent_id] = score

        # Return agent with highest score
        return max(agent_scores.keys(), key=lambda k: agent_scores[k])

    def _execute_workflow_step(self, workflow: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            if step_index >= len(workflow['steps']):
                workflow['status'] = 'completed'
                return {"status": "completed", "message": "Workflow completed"}

            step = workflow['steps'][step_index]
            step_type = step.get('type', 'task')

            # Record step execution
            step_record = {
                'step_index': step_index,
                'step_type': step_type,
                'started_at': datetime.now().isoformat(),
                'status': 'running'
            }

            workflow['step_history'].append(step_record)

            # Execute step based on type
            if step_type == 'task':
                result = self._route_task(step)
            elif step_type == 'parallel':
                result = self._execute_parallel_steps(step.get('parallel_steps', []))
            elif step_type == 'condition':
                result = self._evaluate_condition_step(step)
            else:
                result = {"status": "error", "message": f"Unknown step type: {step_type}"}

            # Update step record
            step_record['completed_at'] = datetime.now().isoformat()
            step_record['status'] = result['status']
            step_record['result'] = result

            # Store result
            workflow['results'][f'step_{step_index}'] = result

            # Move to next step if successful
            if result['status'] == 'success':
                workflow['current_step'] = step_index + 1
                if workflow['current_step'] < len(workflow['steps']):
                    # Continue with next step
                    return self._execute_workflow_step(workflow, workflow['current_step'])
                else:
                    # Workflow completed
                    workflow['status'] = 'completed'
                    workflow['completed_at'] = datetime.now().isoformat()
            else:
                # Step failed
                workflow['status'] = 'failed'
                workflow['failed_at'] = datetime.now().isoformat()
                workflow['failure_reason'] = result.get('message', 'Step execution failed')

            return result

        except Exception as e:
            logger.error(f"Workflow step execution error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to execute workflow step: {str(e)}"
            }

    def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        if not self.registered_agents:
            return 0.0

        total_score = 0.0
        total_agents = len(self.registered_agents)

        for agent_id, agent_info in self.registered_agents.items():
            health_info = self.agent_health_status.get(agent_id, {})

            agent_score = 0.0

            # Agent status (50%)
            if agent_info['status'] == 'active':
                agent_score += 0.5

            # Health status (30%)
            if health_info.get('status') == 'healthy':
                agent_score += 0.3

            # Success rate (20%)
            agent_score += agent_info['success_rate'] * 0.2

            total_score += agent_score

        return total_score / total_agents

    def _analyze_task_complexity(self, task: Dict[str, Any]) -> str:
        """Analyze task complexity"""
        requirements = task.get('requirements', [])
        data_size = len(json.dumps(task.get('task_data', {})))

        if len(requirements) > 3 or data_size > 10000:
            return "high"
        elif len(requirements) > 1 or data_size > 1000:
            return "medium"
        else:
            return "low"

    def _extract_capabilities(self, task: Dict[str, Any]) -> List[str]:
        """Extract required capabilities from task"""
        return task.get('requirements', [])

    def _estimate_task_duration(self, task: Dict[str, Any]) -> int:
        """Estimate task duration in seconds"""
        complexity = self._analyze_task_complexity(task)

        if complexity == "high":
            return 300  # 5 minutes
        elif complexity == "medium":
            return 120  # 2 minutes
        else:
            return 60   # 1 minute

    def _assess_resource_requirements(self, task: Dict[str, Any]) -> Dict[str, str]:
        """Assess resource requirements for task"""
        complexity = self._analyze_task_complexity(task)

        return {
            "cpu": "high" if complexity == "high" else "medium",
            "memory": "high" if complexity == "high" else "low",
            "network": "medium",
            "storage": "low"
        }

    def _generate_coordination_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate coordination recommendation based on analysis"""
        complexity = analysis['complexity']
        capabilities = analysis['required_capabilities']

        if complexity == "high" or len(capabilities) > 2:
            return {
                "strategy": "multi_agent_workflow",
                "recommended_agents": len(capabilities),
                "parallel_execution": True,
                "monitoring_level": "detailed"
            }
        else:
            return {
                "strategy": "single_agent_routing",
                "recommended_agents": 1,
                "parallel_execution": False,
                "monitoring_level": "basic"
            }

    def _execute_parallel_steps(self, parallel_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple steps in parallel"""
        # This is a simplified implementation
        # In a real system, this would involve actual parallel execution
        results = []

        for step in parallel_steps:
            result = self._route_task(step)
            results.append(result)

        success_count = sum(1 for r in results if r['status'] == 'success')

        return {
            "status": "success" if success_count == len(results) else "partial_success",
            "message": f"Parallel execution completed: {success_count}/{len(results)} successful",
            "results": results,
            "success_rate": success_count / len(results)
        }

    def _evaluate_condition_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a conditional workflow step"""
        condition = step.get('condition', {})
        condition_type = condition.get('type', 'always_true')

        # Simple condition evaluation
        if condition_type == 'always_true':
            condition_met = True
        elif condition_type == 'agent_available':
            required_agent = condition.get('agent_id')
            condition_met = (required_agent in self.registered_agents and 
                           self.registered_agents[required_agent]['status'] == 'active')
        else:
            condition_met = False

        return {
            "status": "success",
            "condition_met": condition_met,
            "message": f"Condition '{condition_type}' evaluated to {condition_met}"
        }

    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get coordination statistics"""
        return {
            "registered_agents": len(self.registered_agents),
            "active_workflows": len(self.active_workflows),
            "pending_tasks": len(self.task_queue),
            "total_capabilities": len(self.agent_capabilities),
            "system_health": self._calculate_system_health(),
            "communication_history_count": len(self.coordination_history)
        }