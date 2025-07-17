"""
Base agent class with common functionality
"""
from mesa import Agent
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Common agent states"""
    IDLE = "idle"
    ACTIVE = "active"
    WAITING = "waiting"
    COMPLETED = "completed"


class BaseHealthcareAgent(Agent, ABC):
    """Base class for all healthcare agents"""
    
    def __init__(self, unique_id: str, model, agent_type: str):
        super().__init__(unique_id, model)
        self.agent_type = agent_type
        self.state = AgentState.IDLE
        self.history = []
        self.metrics = {}
        
    @abstractmethod
    def step(self):
        """Execute one simulation step"""
        pass
        
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log agent actions for analysis"""
        event = {
            'time': self.model.time,
            'agent_id': self.unique_id,
            'action': action,
            'details': details or {}
        }
        self.history.append(event)
        logger.debug(f"{self.agent_type} {self.unique_id}: {action}")
        
    def get_state_vector(self) -> list:
        """Return numerical state representation for ML"""
        return []