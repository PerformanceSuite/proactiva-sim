"""
Modernized base agent class with Mesa 3.0 compatibility and error handling
"""
from mesa import Agent
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from enum import Enum
import logging

from ..utils.error_handler import (
    handle_simulation_errors, 
    safe_agent_operation, 
    AgentError,
    simulation_logger
)


class AgentState(Enum):
    """Base agent states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TERMINATED = "terminated"


class ModernizedBaseAgent(Agent, ABC):
    """
    Modernized base agent class with Mesa 3.0 best practices
    
    Features:
    - Proper Mesa 3.0 Agent inheritance
    - Centralized error handling
    - Performance monitoring
    - Structured logging
    - Memory-efficient state management
    """
    
    def __init__(self, unique_id: Union[int, str], model, agent_type: str):
        # Mesa 3.0 initialization
        super().__init__(unique_id, model)
        
        # Agent identification
        self.agent_type = agent_type
        self.creation_time = getattr(model, 'time', 0) if model else 0
        
        # State management
        self.state = AgentState.ACTIVE
        self.last_action = None
        self.action_history = []
        
        # Performance tracking
        self.performance_metrics = {
            'actions_taken': 0,
            'errors_encountered': 0,
            'last_action_time': 0,
            'total_execution_time': 0.0
        }
        
        # Error handling
        self.error_count = 0
        self.last_error = None
        
        simulation_logger.log_agent_action(
            str(self.unique_id), 
            "created", 
            {"agent_type": agent_type, "creation_time": self.creation_time}
        )
    
    @handle_simulation_errors()
    def step(self):
        """Execute one step of agent behavior with error handling"""
        if self.state != AgentState.ACTIVE:
            return
        
        try:
            step_start_time = self.get_current_time()
            
            # Execute agent-specific behavior
            self.agent_step()
            
            # Update performance metrics
            self.performance_metrics['actions_taken'] += 1
            self.performance_metrics['last_action_time'] = step_start_time
            
            # Limit action history to prevent memory growth
            if len(self.action_history) > 100:
                self.action_history = self.action_history[-50:]  # Keep last 50 actions
                
        except Exception as e:
            self.handle_error(e)
    
    @abstractmethod
    def agent_step(self):
        """Agent-specific step behavior - to be implemented by subclasses"""
        pass
    
    def handle_error(self, error: Exception):
        """Handle agent errors"""
        self.error_count += 1
        self.last_error = str(error)
        self.performance_metrics['errors_encountered'] += 1
        
        # Log the error
        simulation_logger.log_error(
            AgentError(f"Agent {self.unique_id} error: {str(error)}", agent_id=str(self.unique_id)),
            context={
                'agent_type': self.agent_type,
                'state': self.state.value,
                'error_count': self.error_count
            }
        )
        
        # Decide recovery strategy based on error count
        if self.error_count >= 5:
            self.state = AgentState.ERROR
            simulation_logger.logger.warning(f"Agent {self.unique_id} disabled due to repeated errors")
        elif self.error_count >= 3:
            # Temporary deactivation
            self.state = AgentState.INACTIVE
            simulation_logger.logger.warning(f"Agent {self.unique_id} temporarily deactivated")
    
    def get_current_time(self) -> int:
        """Safely get current simulation time"""
        return getattr(self.model, 'time', 0) if self.model else 0
    
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log agent actions with error handling"""
        try:
            self.last_action = action
            action_entry = {
                'action': action,
                'time': self.get_current_time(),
                'details': details or {}
            }
            self.action_history.append(action_entry)
            
            simulation_logger.log_agent_action(str(self.unique_id), action, details)
            
        except Exception as e:
            # Don't let logging errors break the agent
            simulation_logger.log_error(
                AgentError(f"Logging failed for agent {self.unique_id}: {str(e)}")
            )
    
    def safe_move(self, new_position):
        """Safely move agent to new position"""
        return safe_agent_operation(
            self, 
            "move", 
            self._execute_move, 
            new_position
        )
    
    def _execute_move(self, new_position):
        """Execute the actual move operation"""
        if self.model and hasattr(self.model, 'grid') and self.model.grid:
            try:
                self.model.grid.move_agent(self, new_position)
                self.log_action("moved", {"new_position": new_position})
                return True
            except Exception as e:
                raise AgentError(f"Move failed: {str(e)}", agent_id=str(self.unique_id))
        return False
    
    def safe_place(self, position):
        """Safely place agent at position"""
        return safe_agent_operation(
            self,
            "place",
            self._execute_place,
            position
        )
    
    def _execute_place(self, position):
        """Execute the actual place operation"""
        if self.model and hasattr(self.model, 'grid') and self.model.grid:
            try:
                self.model.grid.place_agent(self, position)
                self.log_action("placed", {"position": position})
                return True
            except Exception as e:
                raise AgentError(f"Placement failed: {str(e)}", agent_id=str(self.unique_id))
        return False
    
    def get_neighbors(self, radius: int = 1):
        """Safely get neighboring agents"""
        try:
            if self.model and hasattr(self.model, 'grid') and self.model.grid:
                if hasattr(self, 'pos') and self.pos:
                    return self.model.grid.get_neighbors(self.pos, include_center=False, radius=radius)
            return []
        except Exception as e:
            self.log_action("get_neighbors_failed", {"error": str(e)})
            return []
    
    def interact_with_agent(self, other_agent, interaction_type: str, data: Dict[str, Any] = None):
        """Safely interact with another agent"""
        try:
            if not other_agent or other_agent.state != AgentState.ACTIVE:
                return False
            
            # Log the interaction
            self.log_action(f"interact_{interaction_type}", {
                "target_agent": str(other_agent.unique_id),
                "target_type": getattr(other_agent, 'agent_type', 'unknown'),
                "data": data or {}
            })
            
            return self._execute_interaction(other_agent, interaction_type, data)
            
        except Exception as e:
            self.handle_error(e)
            return False
    
    def _execute_interaction(self, other_agent, interaction_type: str, data: Dict[str, Any] = None):
        """Execute specific interaction - to be overridden by subclasses"""
        return True
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get comprehensive agent state information"""
        try:
            return {
                'unique_id': str(self.unique_id),
                'agent_type': self.agent_type,
                'state': self.state.value,
                'position': getattr(self, 'pos', None),
                'creation_time': self.creation_time,
                'current_time': self.get_current_time(),
                'last_action': self.last_action,
                'performance': self.performance_metrics.copy(),
                'error_count': self.error_count,
                'actions_history_count': len(self.action_history)
            }
        except Exception as e:
            simulation_logger.log_error(
                AgentError(f"Failed to get state info for agent {self.unique_id}: {str(e)}")
            )
            return {'unique_id': str(self.unique_id), 'error': str(e)}
    
    def cleanup(self):
        """Clean up agent resources"""
        try:
            self.state = AgentState.TERMINATED
            self.action_history.clear()
            self.log_action("cleanup", {"final_metrics": self.performance_metrics})
            
            simulation_logger.logger.info(f"Agent {self.unique_id} cleaned up successfully")
            
        except Exception as e:
            simulation_logger.log_error(
                AgentError(f"Cleanup failed for agent {self.unique_id}: {str(e)}")
            )
    
    def reset_errors(self):
        """Reset error state for recovery"""
        self.error_count = 0
        self.last_error = None
        if self.state == AgentState.INACTIVE:
            self.state = AgentState.ACTIVE
        self.log_action("error_reset")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring"""
        current_time = self.get_current_time()
        lifetime = max(1, current_time - self.creation_time)
        
        return {
            'agent_id': str(self.unique_id),
            'agent_type': self.agent_type,
            'lifetime': lifetime,
            'actions_per_time': self.performance_metrics['actions_taken'] / lifetime,
            'error_rate': self.error_count / max(1, self.performance_metrics['actions_taken']),
            'current_state': self.state.value,
            'last_action': self.last_action
        }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.unique_id}, type={self.agent_type}, state={self.state.value})"