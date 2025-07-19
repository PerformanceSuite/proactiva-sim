"""
Centralized error handling and logging system for the simulation
"""
import logging
import traceback
import functools
from typing import Any, Callable, Dict, Optional, Union
from datetime import datetime
import json


class SimulationError(Exception):
    """Base exception for simulation-specific errors"""
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "SIMULATION_ERROR"
        self.context = context or {}
        self.timestamp = datetime.now()


class AgentError(SimulationError):
    """Errors related to agent operations"""
    def __init__(self, message: str, agent_id: str = None, **kwargs):
        super().__init__(message, error_code="AGENT_ERROR", **kwargs)
        self.agent_id = agent_id


class ModelError(SimulationError):
    """Errors related to model operations"""
    def __init__(self, message: str, model_id: str = None, **kwargs):
        super().__init__(message, error_code="MODEL_ERROR", **kwargs)
        self.model_id = model_id


class NetworkError(SimulationError):
    """Errors related to network/grid operations"""
    def __init__(self, message: str, node: str = None, **kwargs):
        super().__init__(message, error_code="NETWORK_ERROR", **kwargs)
        self.node = node


class PerformanceError(SimulationError):
    """Errors related to performance issues"""
    def __init__(self, message: str, metric: str = None, **kwargs):
        super().__init__(message, error_code="PERFORMANCE_ERROR", **kwargs)
        self.metric = metric


class SimulationLogger:
    """Centralized logging system with structured logging"""
    
    def __init__(self, name: str = "simulation", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Error statistics
        self.error_stats = {
            'total_errors': 0,
            'error_types': {},
            'last_error': None
        }
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log an error with context"""
        context = context or {}
        
        error_info = {
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        if hasattr(error, 'error_code'):
            error_info['error_code'] = error.error_code
        
        # Add traceback for debugging
        if self.logger.level <= logging.DEBUG:
            error_info['traceback'] = traceback.format_exc()
        
        self.logger.error(json.dumps(error_info, indent=2))
        
        # Update statistics
        self.error_stats['total_errors'] += 1
        error_type = type(error).__name__
        self.error_stats['error_types'][error_type] = self.error_stats['error_types'].get(error_type, 0) + 1
        self.error_stats['last_error'] = error_info
    
    def log_performance(self, metric: str, value: Union[int, float], context: Dict[str, Any] = None):
        """Log performance metrics"""
        perf_info = {
            'metric': metric,
            'value': value,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        self.logger.info(f"PERFORMANCE: {json.dumps(perf_info)}")
    
    def log_agent_action(self, agent_id: str, action: str, details: Dict[str, Any] = None):
        """Log agent actions for debugging"""
        action_info = {
            'agent_id': agent_id,
            'action': action,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.logger.debug(f"AGENT_ACTION: {json.dumps(action_info)}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error statistics summary"""
        return self.error_stats.copy()


# Global logger instance
simulation_logger = SimulationLogger()


def handle_simulation_errors(logger: SimulationLogger = None):
    """Decorator for handling simulation errors"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            error_logger = logger or simulation_logger
            try:
                return func(*args, **kwargs)
            except SimulationError as e:
                context = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                error_logger.log_error(e, context)
                raise
            except Exception as e:
                # Convert generic exceptions to SimulationError
                context = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys()),
                    'original_error': str(e)
                }
                simulation_error = SimulationError(
                    f"Unexpected error in {func.__name__}: {str(e)}",
                    context=context
                )
                error_logger.log_error(simulation_error, context)
                raise simulation_error
        return wrapper
    return decorator


def safe_execute(func: Callable, default_return=None, context: Dict[str, Any] = None):
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        simulation_logger.log_error(e, context)
        return default_return


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self, logger: SimulationLogger = None):
        self.logger = logger or simulation_logger
        self.metrics = {}
        self.thresholds = {
            'step_duration': 1.0,  # seconds
            'memory_usage': 100.0,  # MB
            'agent_count': 10000,
            'error_rate': 0.05  # 5%
        }
    
    def record_metric(self, name: str, value: Union[int, float], context: Dict[str, Any] = None):
        """Record a performance metric"""
        self.metrics[name] = {
            'value': value,
            'timestamp': datetime.now(),
            'context': context or {}
        }
        
        # Check thresholds
        if name in self.thresholds and value > self.thresholds[name]:
            self.logger.log_error(
                PerformanceError(f"Performance threshold exceeded: {name} = {value}"),
                context={'metric': name, 'value': value, 'threshold': self.thresholds[name]}
            )
        
        self.logger.log_performance(name, value, context)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recorded metrics"""
        return {
            name: {
                'value': data['value'],
                'timestamp': data['timestamp'].isoformat()
            }
            for name, data in self.metrics.items()
        }


# Global performance monitor
performance_monitor = PerformanceMonitor()


class ErrorRecoveryManager:
    """Manage error recovery strategies"""
    
    def __init__(self):
        self.recovery_strategies = {}
        self.recovery_attempts = {}
    
    def register_recovery_strategy(self, error_type: type, strategy: Callable):
        """Register a recovery strategy for an error type"""
        self.recovery_strategies[error_type] = strategy
    
    def attempt_recovery(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Attempt to recover from an error"""
        error_type = type(error)
        
        if error_type not in self.recovery_strategies:
            return False
        
        # Track recovery attempts
        error_key = f"{error_type.__name__}_{str(error)}"
        attempts = self.recovery_attempts.get(error_key, 0)
        
        if attempts >= 3:  # Max 3 recovery attempts
            simulation_logger.log_error(
                SimulationError(f"Max recovery attempts exceeded for {error_type.__name__}"),
                context={'original_error': str(error), 'attempts': attempts}
            )
            return False
        
        try:
            self.recovery_attempts[error_key] = attempts + 1
            strategy = self.recovery_strategies[error_type]
            result = strategy(error, context)
            
            if result:
                simulation_logger.logger.info(f"Successfully recovered from {error_type.__name__}")
                # Reset attempt counter on successful recovery
                self.recovery_attempts[error_key] = 0
            
            return result
            
        except Exception as recovery_error:
            simulation_logger.log_error(
                SimulationError(f"Recovery strategy failed: {str(recovery_error)}"),
                context={'original_error': str(error), 'recovery_error': str(recovery_error)}
            )
            return False


# Global error recovery manager
error_recovery_manager = ErrorRecoveryManager()


# Utility functions for common error scenarios
def safe_agent_operation(agent, operation: str, func: Callable, *args, **kwargs):
    """Safely execute an agent operation"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = {
            'agent_id': getattr(agent, 'unique_id', 'unknown'),
            'agent_type': getattr(agent, 'agent_type', 'unknown'),
            'operation': operation
        }
        raise AgentError(f"Agent operation failed: {operation}", context=context) from e


def safe_model_operation(model, operation: str, func: Callable, *args, **kwargs):
    """Safely execute a model operation"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = {
            'model_type': type(model).__name__,
            'operation': operation,
            'time': getattr(model, 'time', 'unknown')
        }
        raise ModelError(f"Model operation failed: {operation}", context=context) from e


def safe_network_operation(grid, operation: str, func: Callable, *args, **kwargs):
    """Safely execute a network/grid operation"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = {
            'operation': operation,
            'grid_type': type(grid).__name__ if grid else 'None'
        }
        raise NetworkError(f"Network operation failed: {operation}", context=context) from e