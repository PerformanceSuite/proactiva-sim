"""
Performance optimization utilities for large-scale simulations
"""
import time
import psutil
import gc
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import deque

from .error_handler import performance_monitor, simulation_logger, PerformanceError


@dataclass
class PerformanceThresholds:
    """Performance thresholds for monitoring"""
    max_step_duration: float = 1.0  # seconds
    max_memory_usage: float = 1024.0  # MB
    max_agent_count: int = 10000
    max_error_rate: float = 0.05  # 5%
    min_fps: int = 10  # steps per second


class AgentBatchProcessor:
    """Optimize agent processing by batching operations"""
    
    def __init__(self, batch_size: int = 100, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.processing_stats = {
            'batches_processed': 0,
            'total_agents_processed': 0,
            'average_batch_time': 0.0,
            'errors': 0
        }
    
    def process_agents_in_batches(self, agents: List, process_func: Callable) -> Dict[str, Any]:
        """Process agents in optimized batches"""
        start_time = time.time()
        total_agents = len(agents)
        
        if total_agents == 0:
            return self.processing_stats
        
        # Determine optimal batch size based on agent count
        optimal_batch_size = min(self.batch_size, max(10, total_agents // self.max_workers))
        
        try:
            # Single-threaded for small agent counts
            if total_agents < 50:
                self._process_single_threaded(agents, process_func)
            else:
                self._process_multi_threaded(agents, process_func, optimal_batch_size)
            
            # Update statistics
            duration = time.time() - start_time
            self.processing_stats.update({
                'batches_processed': self.processing_stats['batches_processed'] + 1,
                'total_agents_processed': self.processing_stats['total_agents_processed'] + total_agents,
                'average_batch_time': (self.processing_stats['average_batch_time'] + duration) / 2
            })
            
            performance_monitor.record_metric('batch_processing_time', duration)
            performance_monitor.record_metric('agents_per_batch', total_agents)
            
        except Exception as e:
            self.processing_stats['errors'] += 1
            simulation_logger.log_error(
                PerformanceError(f"Batch processing failed: {str(e)}"),
                context={'agent_count': total_agents, 'batch_size': optimal_batch_size}
            )
        
        return self.processing_stats
    
    def _process_single_threaded(self, agents: List, process_func: Callable):
        """Process agents in single thread for small counts"""
        for agent in agents:
            try:
                process_func(agent)
            except Exception as e:
                simulation_logger.log_error(
                    PerformanceError(f"Agent processing failed: {str(e)}"),
                    context={'agent_id': getattr(agent, 'unique_id', 'unknown')}
                )
    
    def _process_multi_threaded(self, agents: List, process_func: Callable, batch_size: int):
        """Process agents using thread pool for large counts"""
        batches = [agents[i:i + batch_size] for i in range(0, len(agents), batch_size)]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_batch = {
                executor.submit(self._process_batch, batch, process_func): batch 
                for batch in batches
            }
            
            for future in as_completed(future_to_batch):
                try:
                    future.result()
                except Exception as e:
                    batch = future_to_batch[future]
                    simulation_logger.log_error(
                        PerformanceError(f"Batch thread failed: {str(e)}"),
                        context={'batch_size': len(batch)}
                    )
    
    def _process_batch(self, batch: List, process_func: Callable):
        """Process a single batch of agents"""
        for agent in batch:
            try:
                process_func(agent)
            except Exception as e:
                simulation_logger.log_error(
                    PerformanceError(f"Agent in batch failed: {str(e)}"),
                    context={'agent_id': getattr(agent, 'unique_id', 'unknown')}
                )


class MemoryManager:
    """Manage memory usage and cleanup"""
    
    def __init__(self, threshold_mb: float = 1024.0):
        self.threshold_mb = threshold_mb
        self.cleanup_stats = {
            'cleanups_performed': 0,
            'memory_freed_mb': 0.0,
            'last_cleanup_time': 0
        }
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    def check_and_cleanup(self) -> bool:
        """Check memory usage and cleanup if needed"""
        current_memory = self.get_memory_usage()
        performance_monitor.record_metric('memory_usage_mb', current_memory)
        
        if current_memory > self.threshold_mb:
            return self.perform_cleanup()
        return False
    
    def perform_cleanup(self) -> bool:
        """Perform memory cleanup"""
        try:
            memory_before = self.get_memory_usage()
            
            # Force garbage collection
            gc.collect()
            
            memory_after = self.get_memory_usage()
            memory_freed = max(0, memory_before - memory_after)
            
            self.cleanup_stats.update({
                'cleanups_performed': self.cleanup_stats['cleanups_performed'] + 1,
                'memory_freed_mb': self.cleanup_stats['memory_freed_mb'] + memory_freed,
                'last_cleanup_time': time.time()
            })
            
            simulation_logger.logger.info(f"Memory cleanup: freed {memory_freed:.2f} MB")
            performance_monitor.record_metric('memory_cleanup_freed_mb', memory_freed)
            
            return memory_freed > 0
            
        except Exception as e:
            simulation_logger.log_error(
                PerformanceError(f"Memory cleanup failed: {str(e)}")
            )
            return False


class SimulationProfiler:
    """Profile simulation performance"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.step_times = deque(maxlen=window_size)
        self.agent_counts = deque(maxlen=window_size)
        self.memory_usage = deque(maxlen=window_size)
        self.start_time = time.time()
        self.total_steps = 0
    
    def record_step(self, step_duration: float, agent_count: int, memory_mb: float):
        """Record metrics for a simulation step"""
        self.step_times.append(step_duration)
        self.agent_counts.append(agent_count)
        self.memory_usage.append(memory_mb)
        self.total_steps += 1
        
        # Record to performance monitor
        performance_monitor.record_metric('step_duration', step_duration)
        performance_monitor.record_metric('agent_count', agent_count)
        performance_monitor.record_metric('memory_usage', memory_mb)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.step_times:
            return {'status': 'no_data'}
        
        import statistics
        
        try:
            return {
                'simulation_runtime': time.time() - self.start_time,
                'total_steps': self.total_steps,
                'average_step_time': statistics.mean(self.step_times),
                'max_step_time': max(self.step_times),
                'min_step_time': min(self.step_times),
                'step_time_std': statistics.stdev(self.step_times) if len(self.step_times) > 1 else 0,
                'current_fps': 1.0 / self.step_times[-1] if self.step_times[-1] > 0 else 0,
                'average_agent_count': statistics.mean(self.agent_counts),
                'max_agent_count': max(self.agent_counts),
                'current_memory_mb': self.memory_usage[-1] if self.memory_usage else 0,
                'max_memory_mb': max(self.memory_usage) if self.memory_usage else 0,
                'memory_trend': self._calculate_trend(list(self.memory_usage)),
                'performance_score': self._calculate_performance_score()
            }
        except Exception as e:
            simulation_logger.log_error(
                PerformanceError(f"Performance summary calculation failed: {str(e)}")
            )
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a metric"""
        if len(values) < 2:
            return 'stable'
        
        recent_avg = sum(values[-10:]) / min(10, len(values))
        older_avg = sum(values[:-10]) / max(1, len(values) - 10)
        
        if recent_avg > older_avg * 1.1:
            return 'increasing'
        elif recent_avg < older_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            # Base score components
            step_time_score = min(100, 100 / max(0.1, statistics.mean(self.step_times)))
            memory_score = max(0, 100 - (max(self.memory_usage) / 10))  # Penalize high memory
            stability_score = max(0, 100 - (statistics.stdev(self.step_times) * 100)) if len(self.step_times) > 1 else 100
            
            # Weighted average
            return (step_time_score * 0.4 + memory_score * 0.3 + stability_score * 0.3)
        except Exception:
            return 50.0  # Default middle score


class AdaptivePerformanceManager:
    """Adaptively manage simulation performance"""
    
    def __init__(self, thresholds: PerformanceThresholds = None):
        self.thresholds = thresholds or PerformanceThresholds()
        self.batch_processor = AgentBatchProcessor()
        self.memory_manager = MemoryManager(self.thresholds.max_memory_usage)
        self.profiler = SimulationProfiler()
        
        self.adaptive_settings = {
            'batch_size': 100,
            'update_frequency': 1,
            'memory_check_frequency': 10,
            'performance_mode': 'balanced'  # 'speed', 'memory', 'balanced'
        }
        
        self.optimization_history = deque(maxlen=50)
    
    def optimize_step(self, model) -> Dict[str, Any]:
        """Optimize a single simulation step"""
        step_start_time = time.time()
        
        try:
            # Get current metrics
            agent_count = model.schedule.get_agent_count() if hasattr(model, 'schedule') else 0
            memory_usage = self.memory_manager.get_memory_usage()
            
            # Adaptive optimizations
            self._adapt_to_load(agent_count, memory_usage)
            
            # Memory management
            if model.step_count % self.adaptive_settings['memory_check_frequency'] == 0:
                self.memory_manager.check_and_cleanup()
            
            # Process agents with optimizations
            if hasattr(model, 'schedule') and model.schedule:
                agents = list(model.schedule.agents)
                if self.adaptive_settings['performance_mode'] == 'speed' and len(agents) > 200:
                    # Use batch processing for large agent counts
                    self.batch_processor.process_agents_in_batches(
                        agents, 
                        lambda agent: agent.step()
                    )
                else:
                    # Standard Mesa step
                    model.schedule.step()
            
            # Record performance
            step_duration = time.time() - step_start_time
            self.profiler.record_step(step_duration, agent_count, memory_usage)
            
            # Check for performance issues
            self._check_performance_thresholds(step_duration, agent_count, memory_usage)
            
            return {
                'step_duration': step_duration,
                'agent_count': agent_count,
                'memory_usage': memory_usage,
                'optimizations_applied': self.adaptive_settings.copy()
            }
            
        except Exception as e:
            simulation_logger.log_error(
                PerformanceError(f"Performance optimization failed: {str(e)}")
            )
            return {'error': str(e)}
    
    def _adapt_to_load(self, agent_count: int, memory_usage: float):
        """Adapt settings based on current load"""
        # Adjust batch size based on agent count
        if agent_count > 1000:
            self.adaptive_settings['batch_size'] = min(200, agent_count // 10)
            self.adaptive_settings['performance_mode'] = 'speed'
        elif agent_count > 500:
            self.adaptive_settings['batch_size'] = 100
            self.adaptive_settings['performance_mode'] = 'balanced'
        else:
            self.adaptive_settings['batch_size'] = 50
            self.adaptive_settings['performance_mode'] = 'memory'
        
        # Adjust memory check frequency based on memory pressure
        if memory_usage > self.thresholds.max_memory_usage * 0.8:
            self.adaptive_settings['memory_check_frequency'] = 5
        else:
            self.adaptive_settings['memory_check_frequency'] = 10
    
    def _check_performance_thresholds(self, step_duration: float, agent_count: int, memory_usage: float):
        """Check if performance thresholds are exceeded"""
        if step_duration > self.thresholds.max_step_duration:
            simulation_logger.log_error(
                PerformanceError(f"Step duration threshold exceeded: {step_duration:.3f}s"),
                context={'threshold': self.thresholds.max_step_duration, 'agent_count': agent_count}
            )
        
        if memory_usage > self.thresholds.max_memory_usage:
            simulation_logger.log_error(
                PerformanceError(f"Memory usage threshold exceeded: {memory_usage:.1f}MB"),
                context={'threshold': self.thresholds.max_memory_usage, 'agent_count': agent_count}
            )
        
        if agent_count > self.thresholds.max_agent_count:
            simulation_logger.log_error(
                PerformanceError(f"Agent count threshold exceeded: {agent_count}"),
                context={'threshold': self.thresholds.max_agent_count}
            )
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        return {
            'profiler_summary': self.profiler.get_performance_summary(),
            'memory_stats': self.memory_manager.cleanup_stats,
            'batch_processing_stats': self.batch_processor.processing_stats,
            'current_settings': self.adaptive_settings.copy(),
            'thresholds': {
                'max_step_duration': self.thresholds.max_step_duration,
                'max_memory_usage': self.thresholds.max_memory_usage,
                'max_agent_count': self.thresholds.max_agent_count,
                'max_error_rate': self.thresholds.max_error_rate
            }
        }