
from superagi.agents.aria_agents.base_aria_agent import BaseAriaAgent
from typing import Dict, Any, Optional, List
import json
from datetime import datetime, timedelta
from collections import defaultdict
import re

class AriaAdvancedMemoryAgent(BaseAriaAgent):
    """
    Advanced Memory Agent - Sophisticated memory management with classification and retrieval
    Handles different memory types: short_term, long_term, mission_specific, reflective
    """
    
    def __init__(self, session, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(session, agent_id, config)
        self.name = "AriaAdvancedMemoryAgent"
        self.description = "Advanced memory management with intelligent classification"
        self.capabilities = [
            "memory_classification",
            "importance_scoring",
            "context_retrieval",
            "memory_clustering",
            "retention_policies"
        ]
        
        # Memory storage by type
        self.memory_types = {
            "short_term": [],      # Recent interactions (1-10 items)
            "long_term": [],       # Important persistent memories
            "mission_specific": [], # Task/goal related memories
            "reflective": []       # Self-awareness and learning memories
        }
        
        # Configuration
        self.max_short_term = config.get("max_short_term", 10) if config else 10
        self.max_long_term = config.get("max_long_term", 100) if config else 100
        self.importance_threshold = config.get("importance_threshold", 7) if config else 7
        
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process memory-related requests"""
        self.log(f"Advanced memory processing: {message[:100]}...")
        
        # Determine memory operation type
        operation = self._identify_operation(message)
        
        if operation == "store":
            result = self._store_memory(message, context)
        elif operation == "retrieve":
            result = self._retrieve_memory(message, context)
        elif operation == "analyze":
            result = self._analyze_memory(message, context)
        elif operation == "summarize":
            result = self._summarize_memory(message, context)
        elif operation == "statistics":
            result = self._get_memory_statistics()
        else:
            result = self._general_memory_response(message, context)
        
        return {
            "agent": self.name,
            "response": result,
            "operation": operation,
            "timestamp": self._get_timestamp(),
            "memory_stats": self._get_basic_stats()
        }
    
    def _identify_operation(self, message: str) -> str:
        """Identify the type of memory operation requested"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["store", "save", "remember", "record"]):
            return "store"
        elif any(word in message_lower for word in ["retrieve", "recall", "find", "search"]):
            return "retrieve"
        elif any(word in message_lower for word in ["analyze", "classification", "importance"]):
            return "analyze"
        elif any(word in message_lower for word in ["summarize", "summary", "overview"]):
            return "summarize"
        elif any(word in message_lower for word in ["statistics", "stats", "metrics"]):
            return "statistics"
        else:
            return "general"
    
    def _store_memory(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Store memory with intelligent classification"""
        # Create memory entry
        memory_entry = {
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "importance": self._calculate_importance(content, context),
            "context": context or {},
            "memory_id": f"mem_{len(self._get_all_memories())}_{datetime.now().timestamp()}"
        }
        
        # Classify memory type
        memory_type = self._classify_memory_type(content, context)
        memory_entry["type"] = memory_type
        
        # Store in appropriate memory type
        self.memory_types[memory_type].append(memory_entry)
        
        # Apply retention policies
        self._apply_retention_policies()
        
        self.log(f"Stored memory of type '{memory_type}' with importance {memory_entry['importance']}")
        
        return f"Memory stored successfully:\n- Type: {memory_type}\n- Importance: {memory_entry['importance']}/10\n- ID: {memory_entry['memory_id']}"
    
    def _retrieve_memory(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Retrieve memories based on query and context"""
        # Extract memory type from query if specified
        memory_type = self._extract_memory_type_from_query(query)
        
        # Get relevant memories
        if memory_type and memory_type in self.memory_types:
            memories = self.memory_types[memory_type]
        else:
            memories = self._get_all_memories()
        
        # Search and rank memories
        relevant_memories = self._search_memories(query, memories)
        
        if not relevant_memories:
            return "No relevant memories found for your query."
        
        # Format results
        results = []
        for memory in relevant_memories[:5]:  # Top 5 results
            results.append(f"- [{memory['type']}] {memory['content'][:100]}... (Importance: {memory['importance']}/10)")
        
        return f"Found {len(relevant_memories)} relevant memories:\n" + "\n".join(results)
    
    def _analyze_memory(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Analyze and classify memory content"""
        importance = self._calculate_importance(content, context)
        memory_type = self._classify_memory_type(content, context)
        
        # Additional analysis
        keywords = self._extract_keywords(content)
        sentiment = self._analyze_sentiment(content)
        
        analysis_result = {
            "importance_score": importance,
            "classified_type": memory_type,
            "keywords": keywords,
            "sentiment": sentiment,
            "recommended_action": "store" if importance >= self.importance_threshold else "temporary"
        }
        
        return f"Memory Analysis:\n" + json.dumps(analysis_result, indent=2)
    
    def _summarize_memory(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Summarize memories of specific type or all memories"""
        memory_type = self._extract_memory_type_from_query(query)
        
        if memory_type and memory_type in self.memory_types:
            memories = self.memory_types[memory_type]
            title = f"Summary of {memory_type} memories"
        else:
            memories = self._get_all_memories()
            title = "Summary of all memories"
        
        if not memories:
            return f"No memories found for summarization."
        
        # Create summary
        total_memories = len(memories)
        high_importance = len([m for m in memories if m.get("importance", 0) >= 8])
        recent_memories = len([m for m in memories if self._is_recent(m.get("timestamp", ""))])
        
        summary = f"{title}:\n"
        summary += f"- Total memories: {total_memories}\n"
        summary += f"- High importance memories: {high_importance}\n"
        summary += f"- Recent memories (last 24h): {recent_memories}\n"
        
        # Add recent high-importance memories
        important_recent = [m for m in memories 
                          if m.get("importance", 0) >= 7 and self._is_recent(m.get("timestamp", ""))]
        
        if important_recent:
            summary += "\nRecent important memories:\n"
            for memory in important_recent[:3]:
                summary += f"- {memory['content'][:80]}...\n"
        
        return summary
    
    def _get_memory_statistics(self) -> str:
        """Get comprehensive memory statistics"""
        stats = {}
        total_memories = 0
        
        for mem_type, memories in self.memory_types.items():
            count = len(memories)
            total_memories += count
            avg_importance = sum(m.get("importance", 0) for m in memories) / max(count, 1)
            
            stats[mem_type] = {
                "count": count,
                "average_importance": round(avg_importance, 2)
            }
        
        stats["total_memories"] = total_memories
        stats["memory_efficiency"] = f"{(total_memories / (sum(self.memory_types.values(), [].__len__() or 1)) * 100):.1f}%"
        
        return f"Memory Statistics:\n" + json.dumps(stats, indent=2)
    
    def _classify_memory_type(self, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Classify memory into appropriate type"""
        content_lower = content.lower()
        
        # Mission-specific keywords
        if any(word in content_lower for word in ["goal", "task", "mission", "objective", "target"]):
            return "mission_specific"
        
        # Reflective keywords
        if any(word in content_lower for word in ["learned", "realized", "reflection", "insight", "understanding"]):
            return "reflective"
        
        # High importance for long-term
        importance = self._calculate_importance(content, context)
        if importance >= 8:
            return "long_term"
        
        # Default to short-term
        return "short_term"
    
    def _calculate_importance(self, content: str, context: Optional[Dict[str, Any]] = None) -> int:
        """Calculate importance score (1-10)"""
        score = 5  # Base score
        
        # Content-based scoring
        if any(word in content.lower() for word in ["critical", "important", "urgent", "error", "failure"]):
            score += 3
        if any(word in content.lower() for word in ["success", "achievement", "completed", "resolved"]):
            score += 2
        if any(word in content.lower() for word in ["user", "request", "feedback", "question"]):
            score += 1
        
        # Context-based scoring
        if context:
            if context.get("priority") == "high":
                score += 2
            if context.get("source") == "user":
                score += 1
        
        return min(10, max(1, score))
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        # Filter common words
        common_words = {"this", "that", "with", "have", "will", "from", "they", "been", "were", "said"}
        keywords = [word for word in set(words) if word not in common_words]
        return keywords[:10]  # Top 10 keywords
    
    def _analyze_sentiment(self, content: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ["good", "great", "excellent", "success", "completed", "resolved", "happy"]
        negative_words = ["bad", "error", "failure", "problem", "issue", "wrong", "failed"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _search_memories(self, query: str, memories: List[Dict]) -> List[Dict]:
        """Search memories and rank by relevance"""
        query_words = set(query.lower().split())
        scored_memories = []
        
        for memory in memories:
            content_words = set(memory["content"].lower().split())
            relevance = len(query_words.intersection(content_words))
            
            if relevance > 0:
                # Boost score with importance and recency
                score = relevance * memory.get("importance", 1)
                if self._is_recent(memory.get("timestamp", "")):
                    score *= 1.5
                
                scored_memories.append((score, memory))
        
        # Sort by score and return memories
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in scored_memories]
    
    def _extract_memory_type_from_query(self, query: str) -> Optional[str]:
        """Extract memory type from query"""
        query_lower = query.lower()
        for mem_type in self.memory_types.keys():
            if mem_type.replace("_", " ") in query_lower or mem_type in query_lower:
                return mem_type
        return None
    
    def _is_recent(self, timestamp_str: str) -> bool:
        """Check if timestamp is within last 24 hours"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return datetime.now() - timestamp < timedelta(hours=24)
        except:
            return False
    
    def _get_all_memories(self) -> List[Dict]:
        """Get all memories from all types"""
        all_memories = []
        for memories in self.memory_types.values():
            all_memories.extend(memories)
        return all_memories
    
    def _get_basic_stats(self) -> Dict[str, int]:
        """Get basic memory statistics"""
        return {mem_type: len(memories) for mem_type, memories in self.memory_types.items()}
    
    def _apply_retention_policies(self):
        """Apply retention policies to manage memory size"""
        # Short-term memory cleanup
        if len(self.memory_types["short_term"]) > self.max_short_term:
            # Keep most recent and most important
            sorted_memories = sorted(
                self.memory_types["short_term"],
                key=lambda x: (x.get("importance", 0), x.get("timestamp", "")),
                reverse=True
            )
            self.memory_types["short_term"] = sorted_memories[:self.max_short_term]
        
        # Long-term memory cleanup
        if len(self.memory_types["long_term"]) > self.max_long_term:
            # Keep most important
            sorted_memories = sorted(
                self.memory_types["long_term"],
                key=lambda x: x.get("importance", 0),
                reverse=True
            )
            self.memory_types["long_term"] = sorted_memories[:self.max_long_term]
    
    def _general_memory_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """General memory management response"""
        return f"Advanced Memory Agent ready. Available operations: store, retrieve, analyze, summarize, statistics. Current memory: {sum(len(memories) for memories in self.memory_types.values())} entries across {len(self.memory_types)} types."
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "memory_types": list(self.memory_types.keys()),
            "max_capacities": {
                "short_term": self.max_short_term,
                "long_term": self.max_long_term
            }
        }
