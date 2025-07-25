"""
Base Agent class providing core functionality for all AI agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import deque
import logging
import uuid


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the system.
    Provides core functionality including message handling, logging, and state management.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the base agent.
        
        Args:
            name (str): Unique name identifier for the agent
            description (str): Optional description of the agent's purpose
        """
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.message_history: List[Dict[str, Any]] = []
        
        # Short-term memory system - independent per agent
        self.short_term_memory: deque = deque(maxlen=10)  # Store last 10 messages
        
        # Setup logging
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.logger.setLevel(logging.INFO)
        
        # Create console handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def receive(self, message: str, sender: str = "user", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Receive and process an incoming message.
        
        Args:
            message (str): The incoming message content
            sender (str): Identifier of the message sender
            metadata (Dict): Optional metadata about the message
            
        Returns:
            Dict: Processed message with timestamp and ID
        """
        received_message = {
            "message_id": str(uuid.uuid4()),
            "content": message,
            "sender": sender,
            "receiver": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.message_history.append(received_message)
        self.log(f"Received message from {sender}: {message[:100]}...")
        
        return received_message
    
    @abstractmethod
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response to a received message.
        
        Args:
            message (str): The message to respond to
            context (Dict): Optional context information
            
        Returns:
            Dict: Response containing the agent's reply
        """
        pass
    
    def log(self, message: str, level: str = "info") -> None:
        """
        Log a message with the specified level.
        
        Args:
            message (str): Message to log
            level (str): Log level (debug, info, warning, error, critical)
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[{self.name}] {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dict: Agent status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "total_messages": len(self.message_history),
            "last_activity": self.message_history[-1]["timestamp"] if self.message_history else None
        }
    
    def get_message_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the agent's message history.
        
        Args:
            limit (int): Optional limit on number of messages to return
            
        Returns:
            List: Recent message history
        """
        if limit:
            return self.message_history[-limit:]
        return self.message_history
    
    def activate(self) -> None:
        """Activate the agent."""
        self.is_active = True
        self.log("Agent activated")
    
    def deactivate(self) -> None:
        """Deactivate the agent."""
        self.is_active = False
        self.log("Agent deactivated")
    
    def reset_history(self) -> None:
        """Clear the agent's message history."""
        self.message_history.clear()
        self.log("Message history cleared")
    
    def remember(self, message: str) -> None:
        """
        Add a message to short-term memory.
        
        Args:
            message (str): Message to remember
        """
        memory_entry = {
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name
        }
        self.short_term_memory.append(memory_entry)
        self.log(f"Remembered: {message[:50]}...")
    
    def recall(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the last n messages from short-term memory.
        
        Args:
            n (int): Number of recent messages to retrieve (default: 5)
            
        Returns:
            List[Dict]: Recent messages from memory
        """
        if n <= 0:
            return []
        
        # Get last n messages, but don't exceed available memory
        memory_list = list(self.short_term_memory)
        return memory_list[-n:] if len(memory_list) >= n else memory_list
    
    def clear_memory(self) -> None:
        """Clear all short-term memory."""
        self.short_term_memory.clear()
        self.log("Short-term memory cleared")
    
    def get_memory_status(self) -> Dict[str, Any]:
        """
        Get current memory status.
        
        Returns:
            Dict: Memory statistics and information
        """
        return {
            "total_entries": len(self.short_term_memory),
            "max_capacity": self.short_term_memory.maxlen,
            "available_space": self.short_term_memory.maxlen - len(self.short_term_memory),
            "oldest_entry": self.short_term_memory[0]["timestamp"] if self.short_term_memory else None,
            "newest_entry": self.short_term_memory[-1]["timestamp"] if self.short_term_memory else None
        }