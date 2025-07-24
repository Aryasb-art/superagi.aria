
"""
AriaMemoryAgent - Advanced memory management system for comprehensive data handling
"""

import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from superagi.lib.logger import logger

class AriaMemoryAgent(BaseAriaAgent):
    """
    AriaMemoryAgent handles comprehensive memory management including:
    - Short-term memory operations
    - Long-term memory storage and retrieval
    - Memory compression and optimization
    - Context-aware memory access
    - Memory prioritization and cleanup
    """
    
    def __init__(self, llm, agent_id: int, agent_execution_id: int = None):
        super().__init__(llm, agent_id, agent_execution_id)
        self.agent_name = "AriaMemoryAgent"
        self.short_term_memory = []
        self.long_term_memory = {}
        self.memory_index = {}
        self.memory_priorities = {}
        self.max_short_term_size = 100
        self.max_long_term_size = 1000
        self.compression_threshold = 0.8
        
    def get_capabilities(self) -> List[str]:
        """Return the capabilities of this agent"""
        return [
            "memory_management",
            "data_storage",
            "information_retrieval",
            "context_management",
            "memory_optimization"
        ]
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute memory-related tasks
        
        Args:
            task: Dictionary containing task information
            
        Returns:
            Dictionary containing execution results
        """
        try:
            task_type = task.get('type', 'general_memory')
            
            if task_type == 'store_memory':
                return self._store_memory(task)
            elif task_type == 'retrieve_memory':
                return self._retrieve_memory(task)
            elif task_type == 'search_memory':
                return self._search_memory(task)
            elif task_type == 'compress_memory':
                return self._compress_memory(task)
            elif task_type == 'cleanup_memory':
                return self._cleanup_memory(task)
            else:
                return self._general_memory_task(task)
                
        except Exception as e:
            logger.error(f"AriaMemoryAgent execution error: {str(e)}")
            return {
                "status": "error",
                "message": f"Memory operation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _store_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Store information in memory"""
        try:
            data = task.get('data', {})
            memory_type = task.get('memory_type', 'short_term')
            priority = task.get('priority', 0.5)
            
            memory_entry = {
                'id': f"mem_{int(time.time() * 1000)}",
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'priority': priority,
                'access_count': 0,
                'last_accessed': datetime.now().isoformat()
            }
            
            if memory_type == 'short_term':
                self._add_to_short_term(memory_entry)
            else:
                self._add_to_long_term(memory_entry)
            
            logger.info(f"Memory stored successfully: {memory_entry['id']}")
            
            return {
                "status": "success",
                "message": "Memory stored successfully",
                "memory_id": memory_entry['id'],
                "memory_type": memory_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Memory storage error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to store memory: {str(e)}"
            }
    
    def _retrieve_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve specific memory by ID"""
        try:
            memory_id = task.get('memory_id')
            if not memory_id:
                return {
                    "status": "error",
                    "message": "Memory ID required for retrieval"
                }
            
            # Search in short-term memory
            for entry in self.short_term_memory:
                if entry['id'] == memory_id:
                    entry['access_count'] += 1
                    entry['last_accessed'] = datetime.now().isoformat()
                    return {
                        "status": "success",
                        "memory": entry,
                        "source": "short_term"
                    }
            
            # Search in long-term memory
            if memory_id in self.long_term_memory:
                entry = self.long_term_memory[memory_id]
                entry['access_count'] += 1
                entry['last_accessed'] = datetime.now().isoformat()
                return {
                    "status": "success",
                    "memory": entry,
                    "source": "long_term"
                }
            
            return {
                "status": "error",
                "message": f"Memory with ID {memory_id} not found"
            }
            
        except Exception as e:
            logger.error(f"Memory retrieval error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve memory: {str(e)}"
            }
    
    def _search_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Search memory based on criteria"""
        try:
            query = task.get('query', '')
            max_results = task.get('max_results', 10)
            search_type = task.get('search_type', 'content')
            
            results = []
            
            # Search short-term memory
            for entry in self.short_term_memory:
                if self._matches_query(entry, query, search_type):
                    results.append({
                        **entry,
                        'source': 'short_term',
                        'relevance_score': self._calculate_relevance(entry, query)
                    })
            
            # Search long-term memory
            for memory_id, entry in self.long_term_memory.items():
                if self._matches_query(entry, query, search_type):
                    results.append({
                        **entry,
                        'source': 'long_term',
                        'relevance_score': self._calculate_relevance(entry, query)
                    })
            
            # Sort by relevance and limit results
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            results = results[:max_results]
            
            return {
                "status": "success",
                "results": results,
                "total_found": len(results),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Memory search error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to search memory: {str(e)}"
            }
    
    def _compress_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Compress and optimize memory storage"""
        try:
            compression_ratio = task.get('compression_ratio', 0.5)
            
            # Identify low-priority memories for compression
            candidates = []
            
            # Check short-term memory
            for entry in self.short_term_memory:
                if entry['priority'] < compression_ratio:
                    candidates.append(('short_term', entry))
            
            # Check long-term memory
            for memory_id, entry in self.long_term_memory.items():
                if entry['priority'] < compression_ratio:
                    candidates.append(('long_term', entry))
            
            # Compress candidates
            compressed_count = 0
            for source, entry in candidates:
                compressed_data = self._compress_entry(entry)
                if compressed_data:
                    if source == 'short_term':
                        # Update in short-term
                        for i, mem in enumerate(self.short_term_memory):
                            if mem['id'] == entry['id']:
                                self.short_term_memory[i] = compressed_data
                                break
                    else:
                        # Update in long-term
                        self.long_term_memory[entry['id']] = compressed_data
                    
                    compressed_count += 1
            
            return {
                "status": "success",
                "message": f"Compressed {compressed_count} memory entries",
                "compressed_count": compressed_count,
                "total_candidates": len(candidates)
            }
            
        except Exception as e:
            logger.error(f"Memory compression error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to compress memory: {str(e)}"
            }
    
    def _cleanup_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up old or unused memories"""
        try:
            max_age_days = task.get('max_age_days', 30)
            min_access_count = task.get('min_access_count', 1)
            
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            removed_count = 0
            
            # Clean short-term memory
            self.short_term_memory = [
                entry for entry in self.short_term_memory
                if not self._should_remove_entry(entry, cutoff_date, min_access_count)
            ]
            
            # Clean long-term memory
            to_remove = []
            for memory_id, entry in self.long_term_memory.items():
                if self._should_remove_entry(entry, cutoff_date, min_access_count):
                    to_remove.append(memory_id)
            
            for memory_id in to_remove:
                del self.long_term_memory[memory_id]
                removed_count += 1
            
            return {
                "status": "success",
                "message": f"Cleaned up {removed_count} memory entries",
                "removed_count": removed_count,
                "remaining_short_term": len(self.short_term_memory),
                "remaining_long_term": len(self.long_term_memory)
            }
            
        except Exception as e:
            logger.error(f"Memory cleanup error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to cleanup memory: {str(e)}"
            }
    
    def _general_memory_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general memory-related tasks"""
        try:
            # Analyze current memory state
            memory_stats = {
                "short_term_count": len(self.short_term_memory),
                "long_term_count": len(self.long_term_memory),
                "total_memories": len(self.short_term_memory) + len(self.long_term_memory),
                "memory_utilization": {
                    "short_term": len(self.short_term_memory) / self.max_short_term_size,
                    "long_term": len(self.long_term_memory) / self.max_long_term_size
                }
            }
            
            # Check if compression is needed
            if memory_stats["memory_utilization"]["short_term"] > self.compression_threshold:
                self._auto_compress_short_term()
            
            return {
                "status": "success",
                "message": "Memory analysis completed",
                "memory_stats": memory_stats,
                "task_processed": task.get('description', 'General memory task'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"General memory task error: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process memory task: {str(e)}"
            }
    
    def _add_to_short_term(self, entry: Dict[str, Any]):
        """Add entry to short-term memory"""
        if len(self.short_term_memory) >= self.max_short_term_size:
            # Remove oldest entry
            self.short_term_memory.pop(0)
        
        self.short_term_memory.append(entry)
    
    def _add_to_long_term(self, entry: Dict[str, Any]):
        """Add entry to long-term memory"""
        if len(self.long_term_memory) >= self.max_long_term_size:
            # Remove lowest priority entry
            min_priority_id = min(self.long_term_memory.keys(), 
                                key=lambda k: self.long_term_memory[k]['priority'])
            del self.long_term_memory[min_priority_id]
        
        self.long_term_memory[entry['id']] = entry
    
    def _matches_query(self, entry: Dict[str, Any], query: str, search_type: str) -> bool:
        """Check if entry matches search query"""
        query_lower = query.lower()
        
        if search_type == 'content':
            content = json.dumps(entry['data']).lower()
            return query_lower in content
        elif search_type == 'id':
            return query_lower in entry['id'].lower()
        elif search_type == 'priority':
            try:
                target_priority = float(query)
                return abs(entry['priority'] - target_priority) < 0.1
            except ValueError:
                return False
        
        return False
    
    def _calculate_relevance(self, entry: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for search results"""
        score = 0.0
        query_lower = query.lower()
        content = json.dumps(entry['data']).lower()
        
        # Content match score
        if query_lower in content:
            score += 0.5
        
        # Priority bonus
        score += entry['priority'] * 0.3
        
        # Access frequency bonus
        score += min(entry['access_count'] * 0.01, 0.2)
        
        return score
    
    def _compress_entry(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Compress a memory entry"""
        try:
            # Simple compression: summarize data if it's too large
            data_str = json.dumps(entry['data'])
            if len(data_str) > 1000:  # Compress if over 1KB
                compressed_entry = entry.copy()
                compressed_entry['data'] = {
                    'summary': data_str[:500] + '...[compressed]',
                    'original_size': len(data_str),
                    'compressed': True
                }
                compressed_entry['priority'] *= 0.8  # Reduce priority
                return compressed_entry
            
            return entry
            
        except Exception as e:
            logger.error(f"Entry compression error: {str(e)}")
            return None
    
    def _should_remove_entry(self, entry: Dict[str, Any], cutoff_date: datetime, min_access_count: int) -> bool:
        """Determine if entry should be removed during cleanup"""
        try:
            entry_date = datetime.fromisoformat(entry['timestamp'])
            return (entry_date < cutoff_date and 
                   entry['access_count'] < min_access_count and 
                   entry['priority'] < 0.3)
        except Exception:
            return False
    
    def _auto_compress_short_term(self):
        """Automatically compress short-term memory when needed"""
        # Move high-priority items to long-term memory
        to_move = []
        for i, entry in enumerate(self.short_term_memory):
            if entry['priority'] > 0.7 or entry['access_count'] > 5:
                to_move.append(i)
        
        # Move entries from short-term to long-term (in reverse order to maintain indices)
        for i in reversed(to_move):
            entry = self.short_term_memory.pop(i)
            self._add_to_long_term(entry)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        return {
            "short_term_memory": {
                "count": len(self.short_term_memory),
                "capacity": self.max_short_term_size,
                "utilization": len(self.short_term_memory) / self.max_short_term_size
            },
            "long_term_memory": {
                "count": len(self.long_term_memory),
                "capacity": self.max_long_term_size,
                "utilization": len(self.long_term_memory) / self.max_long_term_size
            },
            "total_memories": len(self.short_term_memory) + len(self.long_term_memory)
        }
