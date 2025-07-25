
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.lib.logger import logger


class AriaUtilityAgent(BaseAriaAgent):
    """
    Aria Utility Agent - Handles utility and helper tasks
    """

    def get_capabilities(self) -> List[str]:
        return [
            "text_processing",
            "data_formatting", 
            "string_manipulation",
            "list_operations",
            "dictionary_operations",
            "file_operations",
            "json_processing",
            "utility_functions"
        ]

    def get_agent_type(self) -> str:
        return "AriaUtilityAgent"

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute utility tasks
        
        Args:
            task (str): The utility task to perform
            context (Dict): Optional context containing task parameters
            
        Returns:
            Dict: Task execution result
        """
        try:
            self.log(f"Executing utility task: {task}")
            
            if not context:
                context = {}
            
            task_type = context.get('task_type', 'general')
            data = context.get('data', '')
            
            result = None
            
            if task_type == 'text_processing':
                result = self._process_text(task, data, context)
            elif task_type == 'data_formatting':
                result = self._format_data(task, data, context)
            elif task_type == 'json_processing':
                result = self._process_json(task, data, context)
            elif task_type == 'list_operations':
                result = self._process_list(task, data, context)
            elif task_type == 'dictionary_operations':
                result = self._process_dictionary(task, data, context)
            else:
                result = self._general_utility(task, data, context)
            
            execution_result = {
                "success": True,
                "result": result,
                "task": task,
                "task_type": task_type,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.get_agent_type()
            }
            
            self.remember(f"Completed utility task: {task}")
            return execution_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "task": task,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.get_agent_type()
            }
            self.log(f"Error executing utility task: {str(e)}", "error")
            return error_result

    def _process_text(self, task: str, data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process text-related utility tasks"""
        operation = context.get('operation', 'basic')
        
        if operation == 'clean':
            # Clean and normalize text
            cleaned = data.strip().replace('\n\n', '\n').replace('  ', ' ')
            return {"cleaned_text": cleaned, "original_length": len(data), "new_length": len(cleaned)}
        
        elif operation == 'split':
            delimiter = context.get('delimiter', ' ')
            parts = data.split(delimiter)
            return {"parts": parts, "count": len(parts)}
        
        elif operation == 'count':
            word_count = len(data.split())
            char_count = len(data)
            return {"word_count": word_count, "character_count": char_count}
        
        elif operation == 'extract':
            # Extract specific patterns or substrings
            pattern = context.get('pattern', '')
            if pattern:
                import re
                matches = re.findall(pattern, data)
                return {"matches": matches, "count": len(matches)}
            else:
                return {"error": "No pattern specified for extraction"}
        
        else:
            return {"processed_text": data, "operation": "basic"}

    def _format_data(self, task: str, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Format data according to specified format"""
        format_type = context.get('format', 'json')
        
        if format_type == 'json':
            try:
                if isinstance(data, str):
                    parsed = json.loads(data)
                    formatted = json.dumps(parsed, indent=2)
                else:
                    formatted = json.dumps(data, indent=2)
                return {"formatted_data": formatted, "format": "json"}
            except Exception as e:
                return {"error": f"JSON formatting error: {str(e)}"}
        
        elif format_type == 'csv':
            # Convert data to CSV format
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    csv_lines = [",".join(headers)]
                    for item in data:
                        csv_lines.append(",".join(str(item.get(h, '')) for h in headers))
                    return {"formatted_data": "\n".join(csv_lines), "format": "csv"}
            return {"error": "Data not suitable for CSV formatting"}
        
        elif format_type == 'table':
            # Format as simple table
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    table = [" | ".join(headers)]
                    table.append("-" * len(table[0]))
                    for item in data:
                        table.append(" | ".join(str(item.get(h, '')) for h in headers))
                    return {"formatted_data": "\n".join(table), "format": "table"}
            return {"error": "Data not suitable for table formatting"}
        
        else:
            return {"formatted_data": str(data), "format": "string"}

    def _process_json(self, task: str, data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process JSON data"""
        operation = context.get('operation', 'parse')
        
        try:
            if operation == 'parse':
                parsed = json.loads(data) if isinstance(data, str) else data
                return {"parsed_json": parsed, "type": type(parsed).__name__}
            
            elif operation == 'validate':
                json.loads(data) if isinstance(data, str) else json.dumps(data)
                return {"valid": True, "message": "Valid JSON"}
            
            elif operation == 'extract_keys':
                parsed = json.loads(data) if isinstance(data, str) else data
                if isinstance(parsed, dict):
                    return {"keys": list(parsed.keys()), "count": len(parsed)}
                else:
                    return {"error": "Not a JSON object"}
            
            elif operation == 'flatten':
                parsed = json.loads(data) if isinstance(data, str) else data
                flattened = self._flatten_dict(parsed) if isinstance(parsed, dict) else parsed
                return {"flattened": flattened}
            
            else:
                return {"error": f"Unknown JSON operation: {operation}"}
                
        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"Invalid JSON: {str(e)}"}

    def _process_list(self, task: str, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process list operations"""
        operation = context.get('operation', 'info')
        
        if not isinstance(data, list):
            try:
                data = list(data) if hasattr(data, '__iter__') else [data]
            except:
                return {"error": "Cannot convert data to list"}
        
        if operation == 'info':
            return {
                "length": len(data),
                "type": "list",
                "first_item": data[0] if data else None,
                "last_item": data[-1] if data else None
            }
        
        elif operation == 'sort':
            reverse = context.get('reverse', False)
            try:
                sorted_data = sorted(data, reverse=reverse)
                return {"sorted_list": sorted_data, "reverse": reverse}
            except Exception as e:
                return {"error": f"Cannot sort list: {str(e)}"}
        
        elif operation == 'unique':
            unique_data = list(set(data))
            return {"unique_list": unique_data, "original_count": len(data), "unique_count": len(unique_data)}
        
        elif operation == 'filter':
            condition = context.get('condition', 'non_empty')
            if condition == 'non_empty':
                filtered = [item for item in data if item]
                return {"filtered_list": filtered, "removed": len(data) - len(filtered)}
            else:
                return {"error": "Unsupported filter condition"}
        
        else:
            return {"error": f"Unknown list operation: {operation}"}

    def _process_dictionary(self, task: str, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process dictionary operations"""
        operation = context.get('operation', 'info')
        
        if not isinstance(data, dict):
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    return {"error": "Cannot convert string to dictionary"}
            else:
                return {"error": "Data is not a dictionary"}
        
        if operation == 'info':
            return {
                "key_count": len(data),
                "keys": list(data.keys()),
                "type": "dictionary"
            }
        
        elif operation == 'extract_value':
            key = context.get('key', '')
            if key in data:
                return {"key": key, "value": data[key], "found": True}
            else:
                return {"key": key, "value": None, "found": False}
        
        elif operation == 'merge':
            other_dict = context.get('other_dict', {})
            merged = {**data, **other_dict}
            return {"merged_dict": merged, "new_keys": len(merged) - len(data)}
        
        elif operation == 'flatten':
            flattened = self._flatten_dict(data)
            return {"flattened_dict": flattened}
        
        else:
            return {"error": f"Unknown dictionary operation: {operation}"}

    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """Flatten a nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _general_utility(self, task: str, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general utility tasks"""
        return {
            "message": "General utility task completed",
            "task": task,
            "data_type": type(data).__name__,
            "data_preview": str(data)[:100] if data else None
        }

    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response by executing utility task"""
        try:
            # Parse message to determine task type and context
            task_context = context or {}
            task_context.setdefault('task_type', 'text_processing')
            task_context.setdefault('data', message)
            
            # Execute utility task
            result = self.execute(message, task_context)
            
            return {
                "response": f"Utility task completed: {result.get('result', {}).get('message', 'Task processed successfully')}",
                "success": True,
                "agent": self.get_agent_type(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "response": f"Error processing utility task: {str(e)}",
                "success": False,
                "agent": self.get_agent_type(),
                "timestamp": datetime.utcnow().isoformat()
            }
