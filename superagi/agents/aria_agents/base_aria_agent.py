"""Fix constructor signature and add missing abstract methods"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import deque
import logging
import uuid


class BaseAriaAgent(ABC):
    """
    Abstract base class for all SuperAGI Aria agents.
    Provides core functionality including message handling, logging, and state management.
    """

    def __init__(self, session, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize base aria agent"""
        self.session = session
        self.agent_id = agent_id
        self.config = config or {}
        self.name = "BaseAriaAgent"
        self.description = "Base class for all Aria agents"
        self.capabilities = []
        self.logger = logger

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute agent functionality"""
        pass

    @abstractmethod
    def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response to a message"""
        pass

    @abstractmethod
    def get_agent_type(self) -> str:
        """Return the agent type"""
        pass

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
`