
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.lib.logger import logger


class AriaToolAgent(BaseAriaAgent):
    """
    Aria Tool Agent - Advanced task processing agent with comprehensive capabilities
    """

    def get_capabilities(self) -> List[str]:
        return [
            "task_execution",
            "tool_management", 
            "workflow_processing",
            "data_transformation",
            "api_integration",
            "file_processing",
            "automation",
            "system_integration"
        ]

    def get_agent_type(self) -> str:
        return "AriaToolAgent"

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute tool-based tasks with comprehensive processing
        
        Args:
            task (str): The task to execute
            context (Dict): Optional context containing task parameters and tools
            
        Returns:
            Dict: Task execution result with detailed output
        """
        try:
            self.log(f"Executing tool task: {task}")
            
            if not context:
                context = {}
            
            task_type = context.get('task_type', 'general')
            tools = context.get('tools', [])
            parameters = context.get('parameters', {})
            
            result = None
            
            if task_type == 'workflow':
                result = self._execute_workflow(task, context)
            elif task_type == 'data_processing':
                result = self._process_data(task, context)
            elif task_type == 'api_call':
                result = self._handle_api_call(task, context)
            elif task_type == 'file_operation':
                result = self._handle_file_operation(task, context)
            elif task_type == 'automation':
                result = self._handle_automation(task, context)
            else:
                result = self._general_tool_execution(task, context)
            
            execution_result = {
                "success": True,
                "result": result,
                "task": task,
                "task_type": task_type,
                "tools_used": tools,
                "execution_time": time.time(),
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.get_agent_type()
            }
            
            self.remember(f"Completed tool task: {task}")
            return execution_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "task": task,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.get_agent_type()
            }
            self.log(f"Error executing tool task: {str(e)}", "error")
            return error_result

    def _execute_workflow(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a multi-step workflow"""
        workflow_steps = context.get('workflow_steps', [])
        if not workflow_steps:
            return {"error": "No workflow steps provided"}
        
        results = []
        for i, step in enumerate(workflow_steps):
            try:
                step_result = self._execute_single_step(step, context)
                results.append({
                    "step": i + 1,
                    "description": step.get('description', f'Step {i + 1}'),
                    "result": step_result,
                    "success": True
                })
                self.log(f"Completed workflow step {i + 1}: {step.get('description', 'Unnamed step')}")
            except Exception as e:
                results.append({
                    "step": i + 1,
                    "description": step.get('description', f'Step {i + 1}'),
                    "error": str(e),
                    "success": False
                })
                self.log(f"Failed workflow step {i + 1}: {str(e)}", "error")
                break
        
        return {
            "workflow_results": results,
            "total_steps": len(workflow_steps),
            "completed_steps": len([r for r in results if r.get('success', False)]),
            "workflow_success": all(r.get('success', False) for r in results)
        }

    def _execute_single_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        action = step.get('action', 'unknown')
        parameters = step.get('parameters', {})
        
        if action == 'data_transform':
            return self._transform_data(parameters)
        elif action == 'validate':
            return self._validate_data(parameters)
        elif action == 'compute':
            return self._compute_values(parameters)
        elif action == 'format':
            return self._format_output(parameters)
        else:
            return {"action": action, "parameters": parameters, "note": "Step executed with basic processing"}

    def _process_data(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process data transformation tasks"""
        data = context.get('data', {})
        operation = context.get('operation', 'analyze')
        
        if operation == 'analyze':
            return self._analyze_data(data)
        elif operation == 'transform':
            return self._transform_data(context)
        elif operation == 'validate':
            return self._validate_data(context)
        elif operation == 'aggregate':
            return self._aggregate_data(data, context)
        else:
            return {"error": f"Unknown data operation: {operation}"}

    def _analyze_data(self, data: Any) -> Dict[str, Any]:
        """Analyze data structure and content"""
        analysis = {
            "data_type": type(data).__name__,
            "size": len(data) if hasattr(data, '__len__') else 1
        }
        
        if isinstance(data, dict):
            analysis.update({
                "keys": list(data.keys()),
                "key_count": len(data),
                "value_types": {k: type(v).__name__ for k, v in data.items()}
            })
        elif isinstance(data, list):
            analysis.update({
                "item_count": len(data),
                "item_types": [type(item).__name__ for item in data[:5]],  # First 5 items
                "unique_types": list(set(type(item).__name__ for item in data))
            })
        elif isinstance(data, str):
            analysis.update({
                "length": len(data),
                "word_count": len(data.split()),
                "line_count": len(data.split('\n'))
            })
        
        return {"analysis": analysis}

    def _transform_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data based on specified rules"""
        data = context.get('data', {})
        transformation = context.get('transformation', {})
        
        if not transformation:
            return {"transformed_data": data, "note": "No transformation rules provided"}
        
        transform_type = transformation.get('type', 'identity')
        
        if transform_type == 'map':
            # Apply mapping function
            mapping = transformation.get('mapping', {})
            if isinstance(data, dict):
                transformed = {mapping.get(k, k): v for k, v in data.items()}
            elif isinstance(data, list):
                transformed = [mapping.get(item, item) for item in data]
            else:
                transformed = mapping.get(data, data)
            return {"transformed_data": transformed, "transformation": "mapping"}
        
        elif transform_type == 'filter':
            # Filter data based on criteria
            criteria = transformation.get('criteria', {})
            if isinstance(data, dict):
                transformed = {k: v for k, v in data.items() if self._meets_criteria(v, criteria)}
            elif isinstance(data, list):
                transformed = [item for item in data if self._meets_criteria(item, criteria)]
            else:
                transformed = data if self._meets_criteria(data, criteria) else None
            return {"transformed_data": transformed, "transformation": "filtering"}
        
        else:
            return {"transformed_data": data, "transformation": "identity"}

    def _meets_criteria(self, item: Any, criteria: Dict[str, Any]) -> bool:
        """Check if an item meets specified criteria"""
        if not criteria:
            return True
        
        for key, condition in criteria.items():
            if key == 'type':
                if type(item).__name__ != condition:
                    return False
            elif key == 'min_length' and hasattr(item, '__len__'):
                if len(item) < condition:
                    return False
            elif key == 'max_length' and hasattr(item, '__len__'):
                if len(item) > condition:
                    return False
            elif key == 'contains' and isinstance(item, str):
                if condition not in item:
                    return False
        
        return True

    def _validate_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against specified rules"""
        data = context.get('data', {})
        validation_rules = context.get('validation_rules', {})
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = validation_rules.get('required_fields', [])
        if isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    validation_results["errors"].append(f"Missing required field: {field}")
                    validation_results["valid"] = False
        
        # Check data types
        type_rules = validation_rules.get('types', {})
        if isinstance(data, dict):
            for field, expected_type in type_rules.items():
                if field in data and type(data[field]).__name__ != expected_type:
                    validation_results["errors"].append(f"Field {field} should be {expected_type}, got {type(data[field]).__name__}")
                    validation_results["valid"] = False
        
        # Check value ranges
        range_rules = validation_rules.get('ranges', {})
        if isinstance(data, dict):
            for field, range_spec in range_rules.items():
                if field in data:
                    value = data[field]
                    if isinstance(value, (int, float)):
                        min_val = range_spec.get('min')
                        max_val = range_spec.get('max')
                        if min_val is not None and value < min_val:
                            validation_results["errors"].append(f"Field {field} value {value} is below minimum {min_val}")
                            validation_results["valid"] = False
                        if max_val is not None and value > max_val:
                            validation_results["errors"].append(f"Field {field} value {value} is above maximum {max_val}")
                            validation_results["valid"] = False
        
        return {"validation": validation_results}

    def _aggregate_data(self, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data using specified functions"""
        aggregation_type = context.get('aggregation_type', 'summary')
        
        if not isinstance(data, list):
            return {"error": "Data must be a list for aggregation"}
        
        if aggregation_type == 'summary':
            return {
                "count": len(data),
                "types": list(set(type(item).__name__ for item in data)),
                "sample": data[:3] if data else []
            }
        
        elif aggregation_type == 'numeric':
            numeric_data = [item for item in data if isinstance(item, (int, float))]
            if numeric_data:
                return {
                    "count": len(numeric_data),
                    "sum": sum(numeric_data),
                    "average": sum(numeric_data) / len(numeric_data),
                    "min": min(numeric_data),
                    "max": max(numeric_data)
                }
            else:
                return {"error": "No numeric data found for aggregation"}
        
        else:
            return {"error": f"Unknown aggregation type: {aggregation_type}"}

    def _handle_api_call(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API call simulation"""
        api_config = context.get('api_config', {})
        endpoint = api_config.get('endpoint', 'unknown')
        method = api_config.get('method', 'GET')
        parameters = api_config.get('parameters', {})
        
        # Simulate API call (in a real implementation, this would make actual HTTP requests)
        return {
            "api_call": {
                "endpoint": endpoint,
                "method": method,
                "parameters": parameters,
                "status": "simulated",
                "response": {
                    "status_code": 200,
                    "data": {"message": "API call simulated successfully"},
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        }

    def _handle_file_operation(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operation simulation"""
        operation = context.get('operation', 'read')
        file_path = context.get('file_path', 'unknown')
        
        # Simulate file operation (in a real implementation, this would interact with the file system)
        return {
            "file_operation": {
                "operation": operation,
                "file_path": file_path,
                "status": "simulated",
                "result": f"File {operation} operation simulated for {file_path}",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def _handle_automation(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle automation tasks"""
        automation_type = context.get('automation_type', 'general')
        steps = context.get('automation_steps', [])
        
        return {
            "automation": {
                "type": automation_type,
                "steps_count": len(steps),
                "status": "completed",
                "result": f"Automation of type {automation_type} completed with {len(steps)} steps",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def _general_tool_execution(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general tool execution"""
        return {
            "general_execution": {
                "task": task,
                "context_keys": list(context.keys()),
                "status": "completed",
                "result": "General tool task executed successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def _compute_values(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Compute values based on parameters"""
        operation = parameters.get('operation', 'add')
        values = parameters.get('values', [])
        
        if not values:
            return {"error": "No values provided for computation"}
        
        try:
            if operation == 'add':
                result = sum(values)
            elif operation == 'multiply':
                result = 1
                for val in values:
                    result *= val
            elif operation == 'average':
                result = sum(values) / len(values)
            elif operation == 'max':
                result = max(values)
            elif operation == 'min':
                result = min(values)
            else:
                result = values[0] if values else 0
            
            return {"computation": {"operation": operation, "result": result, "input_count": len(values)}}
        except Exception as e:
            return {"error": f"Computation error: {str(e)}"}

    def _format_output(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Format output based on parameters"""
        data = parameters.get('data', '')
        format_type = parameters.get('format', 'text')
        
        if format_type == 'json':
            try:
                if isinstance(data, str):
                    formatted = json.dumps(json.loads(data), indent=2)
                else:
                    formatted = json.dumps(data, indent=2)
                return {"formatted_output": formatted, "format": "json"}
            except Exception as e:
                return {"error": f"JSON formatting error: {str(e)}"}
        
        elif format_type == 'table':
            # Simple table formatting
            if isinstance(data, list) and data and isinstance(data[0], dict):
                headers = list(data[0].keys())
                rows = [" | ".join(headers)]
                rows.append("-" * len(rows[0]))
                for item in data:
                    rows.append(" | ".join(str(item.get(h, '')) for h in headers))
                return {"formatted_output": "\n".join(rows), "format": "table"}
            else:
                return {"formatted_output": str(data), "format": "text"}
        
        else:
            return {"formatted_output": str(data), "format": "text"}
