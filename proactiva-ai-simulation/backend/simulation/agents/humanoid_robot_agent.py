"""
Humanoid robot agents for patient assistance and healthcare support
"""
from .modernized_base_agent import ModernizedBaseAgent, AgentState
from enum import Enum
import random
import numpy as np
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class RobotTask(Enum):
    IDLE = "idle"
    PATIENT_GUIDANCE = "patient_guidance"
    VITAL_MONITORING = "vital_monitoring"
    MEDICATION_REMINDER = "medication_reminder"
    MOBILITY_ASSISTANCE = "mobility_assistance"
    COMPANIONSHIP = "companionship"
    EMERGENCY_RESPONSE = "emergency_response"
    CLEANING = "cleaning"
    DELIVERY = "delivery"
    PATIENT_EDUCATION = "patient_education"


class RobotCapability(Enum):
    NAVIGATION = "navigation"
    COMMUNICATION = "communication"
    VITAL_SENSING = "vital_sensing"
    PHYSICAL_SUPPORT = "physical_support"
    EMERGENCY_DETECTION = "emergency_detection"
    MEDICATION_MANAGEMENT = "medication_management"
    LANGUAGE_TRANSLATION = "language_translation"
    FALL_DETECTION = "fall_detection"


class HumanoidRobotAgent(ModernizedBaseAgent):
    """Advanced humanoid robot for healthcare assistance"""
    
    def __init__(self, unique_id: str, model, **kwargs):
        super().__init__(unique_id, model, "humanoid_robot")
        
        # Robot specifications
        self.model_name = kwargs.get('model_name', random.choice([
            "CareBot 3000", "MediAssist Pro", "HealthCompanion X", 
            "NurseBot Advanced", "PatientPal 2.0"
        ]))
        self.battery_level = 100.0  # Percentage
        self.battery_capacity = kwargs.get('battery_capacity', 8.0)  # Hours
        self.charging_time = kwargs.get('charging_time', 2.0)  # Hours
        
        # Capabilities
        self.capabilities = kwargs.get('capabilities', [
            RobotCapability.NAVIGATION,
            RobotCapability.COMMUNICATION,
            RobotCapability.VITAL_SENSING,
            RobotCapability.PHYSICAL_SUPPORT,
            RobotCapability.EMERGENCY_DETECTION,
            RobotCapability.MEDICATION_MANAGEMENT,
            RobotCapability.LANGUAGE_TRANSLATION,
            RobotCapability.FALL_DETECTION
        ])
        
        # Current task and assignment
        self.current_task = RobotTask.IDLE
        self.assigned_patient = None
        self.task_queue: List[Dict[str, Any]] = []
        self.task_completion_time = 0
        
        # Performance metrics
        self.tasks_completed = 0
        self.patient_interactions = 0
        self.emergency_responses = 0
        self.errors_encountered = 0
        self.patient_satisfaction_scores = []
        
        # Location and movement
        self.current_location = kwargs.get('initial_location', 'robot_dock')
        self.destination = None
        self.movement_speed = 1.5  # Faster than humans
        self.can_use_elevators = True
        
        # AI and learning
        self.ai_model_version = kwargs.get('ai_version', '2.5')
        self.learning_rate = 0.001
        self.interaction_history = []
        self.language_proficiency = {
            'english': 1.0,
            'spanish': 0.9,
            'vietnamese': 0.8,
            'tagalog': 0.7,
            'mandarin': 0.7
        }
        
        # Physical capabilities
        self.lifting_capacity = 50  # kg
        self.reach_height = 2.0  # meters
        self.grip_strength = 'adaptive'  # Adjusts to task
        
        # Safety features
        self.collision_avoidance = True
        self.emergency_stop = False
        self.sanitization_cycle = 0  # Minutes since last sanitization
        self.sanitization_interval = 60  # Minutes
        
        # Grid position for animation
        self.position = {"x": 5, "y": 5}  # Start at robot dock
        self.target_position = {"x": 5, "y": 5}
        
    def agent_step(self):
        """Mesa 3.x required method - delegates to step"""
        self.step()
        
    def step(self):
        """Execute one step of robot behavior"""
        if not self.is_active():
            return
            
        # Update battery
        self._update_battery()
        
        # Check if needs charging
        if self.battery_level < 20:
            self._return_to_charging_dock()
            return
            
        # Update sanitization cycle
        self.sanitization_cycle += 1
        if self.sanitization_cycle >= self.sanitization_interval:
            self._perform_sanitization()
            
        # Process current task
        if self.current_task != RobotTask.IDLE:
            self._process_current_task()
        else:
            # Look for new tasks
            self._find_new_task()
            
        # Update movement
        self._update_movement()
        
        # Log metrics
        self.track_metric('battery_level', self.battery_level)
        self.track_metric('tasks_completed', self.tasks_completed)
        self.track_metric('current_task', self.current_task.value)
        
    def _update_battery(self):
        """Update battery level based on activity"""
        if self.current_location == 'robot_dock' and self.current_task == RobotTask.IDLE:
            # Charging
            self.battery_level = min(100, self.battery_level + (100 / (self.charging_time * 60)))
        else:
            # Discharging based on task
            drain_rate = {
                RobotTask.IDLE: 0.5,
                RobotTask.PATIENT_GUIDANCE: 1.0,
                RobotTask.VITAL_MONITORING: 0.8,
                RobotTask.MOBILITY_ASSISTANCE: 2.0,
                RobotTask.EMERGENCY_RESPONSE: 3.0,
                RobotTask.CLEANING: 1.5,
                RobotTask.DELIVERY: 1.2
            }.get(self.current_task, 1.0)
            
            self.battery_level = max(0, self.battery_level - (drain_rate / (self.battery_capacity * 60)))
            
    def _find_new_task(self):
        """Find and assign new task based on priorities"""
        if not self.model:
            return
            
        # Check for emergencies first
        if self._check_for_emergencies():
            return
            
        # Check task queue
        if self.task_queue:
            task = self.task_queue.pop(0)
            self._start_task(task)
            return
            
        # Look for patients needing assistance
        patients_needing_help = []
        for agent in self.model.get_agents():
            if hasattr(agent, 'needs_assistance') and agent.needs_assistance:
                distance = self._calculate_distance(agent)
                patients_needing_help.append((agent, distance))
                
        if patients_needing_help:
            # Sort by distance and urgency
            patients_needing_help.sort(key=lambda x: (x[1], -getattr(x[0], 'urgency', 0)))
            patient, _ = patients_needing_help[0]
            
            # Determine appropriate task
            task_type = self._determine_task_for_patient(patient)
            self._start_task({
                'type': task_type,
                'patient': patient,
                'priority': 'normal'
            })
            
    def _determine_task_for_patient(self, patient) -> RobotTask:
        """Determine appropriate task based on patient needs"""
        if hasattr(patient, 'fallen') and patient.fallen:
            return RobotTask.EMERGENCY_RESPONSE
        elif hasattr(patient, 'needs_mobility_help') and patient.needs_mobility_help:
            return RobotTask.MOBILITY_ASSISTANCE
        elif hasattr(patient, 'needs_medication_reminder') and patient.needs_medication_reminder:
            return RobotTask.MEDICATION_REMINDER
        elif hasattr(patient, 'confused') and patient.confused:
            return RobotTask.PATIENT_GUIDANCE
        elif hasattr(patient, 'lonely') and patient.lonely:
            return RobotTask.COMPANIONSHIP
        else:
            return RobotTask.PATIENT_GUIDANCE
            
    def _start_task(self, task: Dict[str, Any]):
        """Start a new task"""
        self.current_task = task['type']
        self.assigned_patient = task.get('patient')
        self.task_completion_time = self._estimate_task_duration(task['type'])
        
        if self.assigned_patient:
            self.destination = getattr(self.assigned_patient, 'current_location', None)
            
        logger.info(f"Robot {self.unique_id} starting task {task['type'].value}")
        
    def _process_current_task(self):
        """Process the current task"""
        self.task_completion_time -= 1
        
        if self.task_completion_time <= 0:
            # Complete task
            self._complete_current_task()
            
    def _complete_current_task(self):
        """Complete the current task"""
        if self.current_task == RobotTask.VITAL_MONITORING and self.assigned_patient:
            # Record vitals
            vitals = self._measure_vitals(self.assigned_patient)
            self.interaction_history.append({
                'task': 'vital_monitoring',
                'patient': self.assigned_patient.unique_id,
                'vitals': vitals,
                'timestamp': self.model.time if self.model else 0
            })
            
        elif self.current_task == RobotTask.MEDICATION_REMINDER and self.assigned_patient:
            # Remind about medication
            if hasattr(self.assigned_patient, 'medication_taken'):
                self.assigned_patient.medication_taken = True
                
        elif self.current_task == RobotTask.MOBILITY_ASSISTANCE and self.assigned_patient:
            # Help with mobility
            if hasattr(self.assigned_patient, 'mobility_assisted'):
                self.assigned_patient.mobility_assisted = True
                
        # Update metrics
        self.tasks_completed += 1
        if self.assigned_patient:
            self.patient_interactions += 1
            # Simulate patient satisfaction
            satisfaction = random.uniform(0.7, 1.0) if random.random() > 0.1 else random.uniform(0.3, 0.7)
            self.patient_satisfaction_scores.append(satisfaction)
            
        # Reset task
        self.current_task = RobotTask.IDLE
        self.assigned_patient = None
        
    def _measure_vitals(self, patient) -> Dict[str, Any]:
        """Simulate vital signs measurement"""
        return {
            'heart_rate': random.randint(60, 100),
            'blood_pressure': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
            'temperature': round(random.uniform(97.0, 99.5), 1),
            'oxygen_saturation': random.randint(95, 100),
            'respiratory_rate': random.randint(12, 20)
        }
        
    def _check_for_emergencies(self) -> bool:
        """Check for emergency situations"""
        if not self.model:
            return False
            
        for agent in self.model.get_agents():
            if hasattr(agent, 'emergency_state') and agent.emergency_state:
                # Respond to emergency
                self._start_task({
                    'type': RobotTask.EMERGENCY_RESPONSE,
                    'patient': agent,
                    'priority': 'emergency'
                })
                self.emergency_responses += 1
                return True
                
        return False
        
    def _return_to_charging_dock(self):
        """Return to charging dock when battery is low"""
        self.current_task = RobotTask.IDLE
        self.destination = 'robot_dock'
        self.assigned_patient = None
        
    def _perform_sanitization(self):
        """Perform self-sanitization cycle"""
        self.sanitization_cycle = 0
        logger.info(f"Robot {self.unique_id} performing sanitization")
        
    def _estimate_task_duration(self, task_type: RobotTask) -> int:
        """Estimate duration for different tasks (in steps)"""
        durations = {
            RobotTask.IDLE: 0,
            RobotTask.PATIENT_GUIDANCE: 10,
            RobotTask.VITAL_MONITORING: 5,
            RobotTask.MEDICATION_REMINDER: 3,
            RobotTask.MOBILITY_ASSISTANCE: 15,
            RobotTask.COMPANIONSHIP: 20,
            RobotTask.EMERGENCY_RESPONSE: 8,
            RobotTask.CLEANING: 30,
            RobotTask.DELIVERY: 12,
            RobotTask.PATIENT_EDUCATION: 15
        }
        return durations.get(task_type, 10)
        
    def _update_movement(self):
        """Update robot movement with smooth animation"""
        if self.destination and self.destination != self.current_location:
            # Move towards destination
            self.is_moving = True
            
            # Update grid position for animation
            if self.position['x'] != self.target_position['x']:
                diff = self.target_position['x'] - self.position['x']
                self.position['x'] += min(max(diff * self.movement_speed * 0.1, -0.5), 0.5)
                
            if self.position['y'] != self.target_position['y']:
                diff = self.target_position['y'] - self.position['y']
                self.position['y'] += min(max(diff * self.movement_speed * 0.1, -0.5), 0.5)
                
            # Check if reached destination
            distance = abs(self.position['x'] - self.target_position['x']) + \
                      abs(self.position['y'] - self.target_position['y'])
            if distance < 0.1:
                self.current_location = self.destination
                self.is_moving = False
        else:
            self.is_moving = False
            
    def _calculate_distance(self, other_agent) -> float:
        """Calculate distance to another agent"""
        if hasattr(other_agent, 'position'):
            return abs(self.position['x'] - other_agent.position['x']) + \
                   abs(self.position['y'] - other_agent.position['y'])
        return float('inf')
        
    def can_perform_task(self, task_type: RobotTask) -> bool:
        """Check if robot can perform a specific task"""
        # Check battery
        if self.battery_level < 20:
            return False
            
        # Check capabilities
        required_capabilities = {
            RobotTask.VITAL_MONITORING: [RobotCapability.VITAL_SENSING],
            RobotTask.MOBILITY_ASSISTANCE: [RobotCapability.PHYSICAL_SUPPORT],
            RobotTask.EMERGENCY_RESPONSE: [RobotCapability.EMERGENCY_DETECTION],
            RobotTask.MEDICATION_REMINDER: [RobotCapability.MEDICATION_MANAGEMENT]
        }
        
        if task_type in required_capabilities:
            for cap in required_capabilities[task_type]:
                if cap not in self.capabilities:
                    return False
                    
        return True
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get robot performance metrics"""
        avg_satisfaction = np.mean(self.patient_satisfaction_scores) if self.patient_satisfaction_scores else 0
        
        return {
            'tasks_completed': self.tasks_completed,
            'patient_interactions': self.patient_interactions,
            'emergency_responses': self.emergency_responses,
            'average_satisfaction': avg_satisfaction,
            'battery_efficiency': self.battery_level / 100,
            'error_rate': self.errors_encountered / max(self.tasks_completed, 1),
            'utilization': 1.0 if self.current_task != RobotTask.IDLE else 0.0
        }