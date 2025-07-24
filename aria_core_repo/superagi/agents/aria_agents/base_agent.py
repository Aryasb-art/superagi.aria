"""
Base Agent class providing core functionality for all SuperAGI Aria agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import deque
import logging
import uuid


class BaseAgent(ABC):
    """
    Abstract base class for all SuperAGI Aria agents.
    Provides core functionality including message handling, logging, and state management.
    """
    
    def __init__(self, name: str, description: str = "", config: Dict[str, Any] = None):
        """
        Initialize the base agent.
        
        Args:
            name (str): Unique name identifier for the agent
            description (str): Optional description of the agent's purpose
            config (Dict): Configuration parameters for the agent
        """
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.config = config or {}
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.message_history: List[Dict[str, Any]] = []
        
        # Short-term memory system - independent per agent
        self.short_term_memory: deque = deque(maxlen=10)  # Store last 10 messages
        
        # Setup logging
        self.logger = logging.getLogger(f"superagi.aria.{self.name}")
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
            Dict: Response with content and metadata
        """
        pass
    
    def log(self, message: str, level: str = "info") -> None:
        """
        Log a message with the agent's logger.
        
        Args:
            message (str): Message to log
            level (str): Log level (debug, info, warning, error, critical)
        """
        getattr(self.logger, level)(f"[{self.name}] {message}")
    
    def remember(self, message: str) -> None:
        """
        Store a message in short-term memory.
        
        Args:
            message (str): Message to remember
        """
        memory_entry = {
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name
        }
        self.short_term_memory.append(memory_entry)
        self.log(f"Remembered: {message[:100]}...")
    
    def recall(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve messages from short-term memory.
        
        Args:
            query (str): Optional search query to filter memories
            
        Returns:
            List[Dict]: List of memory entries
        """
        if not query:
            return list(self.short_term_memory)
        
        # Simple keyword search
        filtered_memories = []
        for memory in self.short_term_memory:
            if query.lower() in memory["content"].lower():
                filtered_memories.append(memory)
        
        return filtered_memories
    
    def clear_memory(self) -> None:
        """Clear all short-term memory."""
        self.short_term_memory.clear()
        self.log("Short-term memory cleared")
    
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
            "memory_size": len(self.short_term_memory),
            "last_activity": self.message_history[-1]["timestamp"] if self.message_history else None
        }
    
    def activate(self) -> None:
        """Activate the agent."""
        self.is_active = True
        self.log("Agent activated")
    
    def deactivate(self) -> None:
        """Deactivate the agent."""
        self.is_active = False
        self.log("Agent deactivated")
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update agent configuration.
        
        Args:
            config (Dict): New configuration parameters
        """
        self.config.update(config)
        self.log(f"Configuration updated: {config}")