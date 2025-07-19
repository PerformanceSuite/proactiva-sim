"""
Patient agents with realistic healthcare-seeking behaviors
"""
from .modernized_base_agent import ModernizedBaseAgent, AgentState
from enum import Enum
import random
import numpy as np
from typing import Optional, Dict, Any


class PatientCondition(Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent" 
    ROUTINE = "routine"
    MENTAL_HEALTH = "mental_health"
    CHRONIC = "chronic"
    PREVENTIVE = "preventive"


class PatientState(Enum):
    ARRIVAL = "arrival"
    CHECK_IN = "check_in"
    WAITING = "waiting"
    TRIAGE = "triage"
    TREATMENT = "treatment"
    DISCHARGED = "discharged"
    LEFT_WITHOUT_TREATMENT = "left_without_treatment"


class VeteranPatientAgent(ModernizedBaseAgent):
    """Veteran patient with specific characteristics and behaviors"""
    
    def __init__(self, unique_id: str, model, **kwargs):
        super().__init__(unique_id, model, "veteran_patient")
        
        # Demographics
        self.age = kwargs.get('age', random.randint(25, 85))
        self.service_era = kwargs.get('service_era', random.choice([
            "Vietnam", "Gulf War", "OEF/OIF", "Korea", "Peacetime"
        ]))
        self.disability_rating = kwargs.get('disability_rating', 
                                          random.choices([0, 30, 50, 70, 100], 
                                                       weights=[0.3, 0.2, 0.2, 0.2, 0.1])[0])
        
        # Medical condition
        self.condition = kwargs.get('condition', self._determine_condition())
        self.urgency = self._calculate_urgency()
        self.comorbidities = self._generate_comorbidities()
        
        # State and metrics
        self.patient_state = PatientState.ARRIVAL
        self.arrival_time = getattr(model, 'time', 0) if model else 0
        self.wait_time = 0
        self.satisfaction = 50
        self.pain_level = random.randint(0, 10) if self.condition != PatientCondition.PREVENTIVE else 0
        
        # Treatment preferences
        self.tech_comfort = self._calculate_tech_comfort()
        self.vr_willingness = self.tech_comfort > 60 and self.condition == PatientCondition.MENTAL_HEALTH
        self.telehealth_preference = self.tech_comfort > 50
        
        # Social network
        self.social_connections = []
        self.influence_strength = random.uniform(0.1, 1.0)
        
        # Location and movement
        self.current_location = "entrance"
        self.destination = None
        self.path = []
        
        # Grid position for animation (x, y coordinates)
        self.position = {"x": 1, "y": 1}  # Start at entrance
        self.target_position = {"x": 1, "y": 1}
        self.movement_speed = 0.2  # Grid cells per step
        self.is_moving = False
        self.movement_progress = 0.0
        self.movement_trail = []  # Track movement history for trails
    
    # Hospital area positions (matching frontend grid layout)
    AREA_POSITIONS = {
        'entrance': {'x': 1, 'y': 1},
        'reception': {'x': 3, 'y': 3},
        'waiting_room': {'x': 4, 'y': 6},
        'triage': {'x': 12, 'y': 3},
        'emergency': {'x': 2, 'y': 10},
        'primary_care': {'x': 6, 'y': 10},
        'mental_health': {'x': 10, 'y': 10},
        'specialist': {'x': 14, 'y': 10},
        'vr_therapy_suite': {'x': 15, 'y': 10},
        'telehealth_center': {'x': 16, 'y': 4},
        'pharmacy': {'x': 3, 'y': 16},
        'lab': {'x': 8, 'y': 16},
        'imaging': {'x': 12, 'y': 16},
        'discharge': {'x': 16, 'y': 16}
    }
        
    def _determine_condition(self) -> PatientCondition:
        """Determine patient condition based on veteran demographics"""
        # Veterans have higher rates of certain conditions
        if self.service_era in ["Vietnam", "OEF/OIF"]:
            weights = [0.1, 0.15, 0.35, 0.25, 0.1, 0.05]  # Higher mental health
        else:
            weights = [0.1, 0.2, 0.4, 0.15, 0.1, 0.05]
            
        return random.choices(list(PatientCondition), weights=weights)[0]
        
    def _calculate_urgency(self) -> int:
        """Calculate triage urgency (1=most urgent, 5=least)"""
        urgency_map = {
            PatientCondition.EMERGENCY: 1,
            PatientCondition.URGENT: random.randint(2, 3),
            PatientCondition.MENTAL_HEALTH: random.randint(2, 4),
            PatientCondition.CHRONIC: random.randint(3, 4),
            PatientCondition.ROUTINE: random.randint(4, 5),
            PatientCondition.PREVENTIVE: 5
        }
        return urgency_map[self.condition]
        
    def _generate_comorbidities(self) -> list:
        """Generate realistic comorbidities"""
        possible_comorbidities = [
            "PTSD", "Depression", "Anxiety", "Chronic Pain", 
            "Diabetes", "Hypertension", "Substance Use", "TBI"
        ]
        
        # More comorbidities with age and disability rating
        num_comorbidities = min(
            int(self.age / 20) + int(self.disability_rating / 30),
            len(possible_comorbidities)
        )
        
        return random.sample(possible_comorbidities, num_comorbidities)
        
    def _calculate_tech_comfort(self) -> int:
        """Calculate technology comfort based on age and era"""
        base_comfort = 100 - self.age
        
        era_modifiers = {
            "OEF/OIF": 20,
            "Gulf War": 10,
            "Peacetime": 5,
            "Vietnam": -10,
            "Korea": -20
        }
        
        return max(0, min(100, base_comfort + era_modifiers.get(self.service_era, 0)))
    
    def update_position(self):
        """Update agent position for smooth movement animation"""
        if self.current_location in self.AREA_POSITIONS:
            self.target_position = self.AREA_POSITIONS[self.current_location].copy()
            
            # Smooth movement towards target
            dx = self.target_position['x'] - self.position['x']
            dy = self.target_position['y'] - self.position['y']
            
            if abs(dx) > 0.1 or abs(dy) > 0.1:
                self.position['x'] += dx * self.movement_speed
                self.position['y'] += dy * self.movement_speed
                self.is_moving = True
            else:
                self.position = self.target_position.copy()
                self.is_moving = False
        
    def agent_step(self):
        """Execute one step of patient behavior - implements abstract method"""
        self.log_action(f"Step in state {self.patient_state.value}")
        
        # Update position for smooth movement animation
        self.update_position()
        
        if self.patient_state == PatientState.ARRIVAL:
            self.arrive_at_facility()
        elif self.patient_state == PatientState.CHECK_IN:
            self.check_in()
        elif self.patient_state == PatientState.WAITING:
            self.wait_for_care()
        elif self.patient_state == PatientState.TRIAGE:
            self.undergo_triage()
        elif self.patient_state == PatientState.TREATMENT:
            self.receive_treatment()
            
    def arrive_at_facility(self):
        """Patient arrives at healthcare facility"""
        self.log_action("Arrived at facility", {
            "condition": self.condition.value,
            "urgency": self.urgency,
            "pain_level": self.pain_level
        })
        
        # Move to check-in
        self.current_location = "entrance"
        self.destination = "reception"
        self.patient_state = PatientState.CHECK_IN
        
        # Notify model of arrival
        self.model.patient_arrivals += 1
        
    def check_in(self):
        """Check in at reception"""
        # Check if reception is available
        if self.model.reception_available():
            self.log_action("Checking in at reception")
            self.current_location = "reception"
            self.patient_state = PatientState.WAITING
            self.model.waiting_room.append(self)
            
            # AI triage possibility
            if self.model.ai_triage_enabled:
                self.ai_triage_assessment()
        else:
            # Wait at reception
            self.wait_time += 1
            
    def wait_for_care(self):
        """Wait for treatment"""
        self.wait_time += 1
        
        # Update satisfaction based on wait time
        if self.wait_time > 30:
            self.satisfaction -= 1
        if self.wait_time > 60:
            self.satisfaction -= 2
            
        # Check if patient leaves
        if self.should_leave_without_treatment():
            self.leave_without_treatment()
            return
            
        # Check for available provider
        if self.model.provider_available_for(self):
            self.patient_state = PatientState.TREATMENT
            
    def should_leave_without_treatment(self) -> bool:
        """Determine if patient leaves due to wait"""
        if self.urgency >= 4 and self.wait_time > 120:  # Non-urgent, 2+ hours
            leave_probability = (self.wait_time - 120) / 240  # Increases over time
            return random.random() < leave_probability
        return False
        
    def leave_without_treatment(self):
        """Patient leaves without being seen"""
        self.log_action("Left without treatment", {
            "wait_time": self.wait_time,
            "satisfaction": self.satisfaction
        })
        
        self.patient_state = PatientState.LEFT_WITHOUT_TREATMENT
        self.satisfaction = max(0, self.satisfaction - 20)
        self.model.patients_left_without_treatment += 1
        
        # Negative word of mouth
        self.spread_experience(negative=True)
        
    def receive_treatment(self):
        """Receive medical treatment"""
        treatment_type = self.determine_treatment_type()
        
        self.log_action(f"Receiving {treatment_type} treatment")
        
        if treatment_type == "vr_therapy":
            self.receive_vr_therapy()
        elif treatment_type == "telehealth":
            self.receive_telehealth()
        else:
            self.receive_traditional_treatment()
    
    def receive_telehealth(self):
        """Receive telehealth consultation"""
        # Move to telehealth center
        self.move_to_area("telehealth_center")
        
        consultation_quality = random.uniform(0.6, 0.9)
        
        # Update satisfaction (telehealth generally well-received)
        satisfaction_change = (consultation_quality - 0.6) * 25
        self.satisfaction = max(0, min(100, self.satisfaction + satisfaction_change))
        
        # Update pain (limited physical intervention)
        self.pain_level = max(0, self.pain_level - 1)
        
        if hasattr(self.model, 'telehealth_sessions_completed'):
            self.model.telehealth_sessions_completed += 1
        
        self.complete_treatment()
            
    def determine_treatment_type(self) -> str:
        """Determine which treatment modality to use"""
        if self.condition == PatientCondition.MENTAL_HEALTH:
            if self.vr_willingness and self.model.vr_stations_available > 0:
                return "vr_therapy"
            elif self.telehealth_preference and self.model.telehealth_available():
                return "telehealth"
                
        elif self.condition in [PatientCondition.ROUTINE, PatientCondition.CHRONIC]:
            if self.telehealth_preference and self.model.telehealth_available():
                return "telehealth"
                
        return "traditional"
        
    def receive_vr_therapy(self):
        """Experience VR therapy session"""
        self.model.vr_stations_available -= 1
        session_quality = random.uniform(0.7, 1.0)  # VR tends to be effective
        
        # Update satisfaction
        satisfaction_boost = session_quality * 30
        self.satisfaction = min(100, self.satisfaction + satisfaction_boost)
        
        # Update metrics
        self.pain_level = max(0, self.pain_level - 3)
        self.model.vr_sessions_completed += 1
        
        # Positive experience influences others
        if self.satisfaction > 80:
            self.spread_experience(positive=True, modality="vr")
            
        self.complete_treatment()
        
    def undergo_triage(self):
        """Undergo triage assessment"""
        self.log_action("Undergoing triage", {
            "urgency": self.urgency,
            "condition": self.condition.value
        })
        
        # Move to appropriate treatment area based on condition
        treatment_area = self._determine_treatment_area()
        self.move_to_area(treatment_area)
        self.patient_state = PatientState.TREATMENT
    
    def _determine_treatment_area(self) -> str:
        """Determine which treatment area patient should go to"""
        if self.condition == PatientCondition.EMERGENCY:
            return "emergency"
        elif self.condition == PatientCondition.MENTAL_HEALTH:
            return "mental_health"
        elif self.condition in [PatientCondition.ROUTINE, PatientCondition.CHRONIC, PatientCondition.PREVENTIVE]:
            return "primary_care"
        else:
            return "specialist"
    
    def receive_traditional_treatment(self):
        """Receive traditional in-person treatment"""
        treatment_quality = random.uniform(0.5, 0.9)
        
        # Update satisfaction
        satisfaction_change = (treatment_quality - 0.7) * 20
        self.satisfaction = max(0, min(100, self.satisfaction + satisfaction_change))
        
        # Update pain
        self.pain_level = max(0, self.pain_level - 2)
        
        self.complete_treatment()
        
    def complete_treatment(self):
        """Complete treatment and prepare for discharge"""
        self.patient_state = PatientState.DISCHARGED
        self.model.patients_treated += 1
        
        current_time = getattr(self.model, 'time', 0) if self.model else 0
        total_time = current_time - self.arrival_time
        self.log_action("Treatment completed", {
            "total_time": total_time,
            "wait_time": self.wait_time,
            "final_satisfaction": self.satisfaction
        })
        
    def spread_experience(self, positive=False, negative=False, modality=None):
        """Share experience with social network"""
        if not self.social_connections:
            return
            
        influence_range = int(self.influence_strength * len(self.social_connections))
        influenced = random.sample(self.social_connections, 
                                 min(influence_range, len(self.social_connections)))
        
        for connection in influenced:
            if positive and modality == "vr":
                connection.vr_willingness = True
                connection.tech_comfort = min(100, connection.tech_comfort + 10)
            elif negative:
                connection.satisfaction = max(0, connection.satisfaction - 5)
                
    def get_state_vector(self) -> list:
        """Return numerical representation for ML models"""
        state_encoding = {
            PatientState.ARRIVAL: 0,
            PatientState.CHECK_IN: 1,
            PatientState.WAITING: 2,
            PatientState.TRIAGE: 3,
            PatientState.TREATMENT: 4,
            PatientState.DISCHARGED: 5,
            PatientState.LEFT_WITHOUT_TREATMENT: 6
        }
        
        condition_encoding = {
            PatientCondition.EMERGENCY: 0,
            PatientCondition.URGENT: 1,
            PatientCondition.ROUTINE: 2,
            PatientCondition.MENTAL_HEALTH: 3,
            PatientCondition.CHRONIC: 4,
            PatientCondition.PREVENTIVE: 5
        }
        
        return [
            self.age / 100,
            self.disability_rating / 100,
            condition_encoding[self.condition] / 5,
            self.urgency / 5,
            self.wait_time / 120,  # Normalize to 2 hours
            self.satisfaction / 100,
            self.pain_level / 10,
            self.tech_comfort / 100,
            int(self.vr_willingness),
            int(self.telehealth_preference),
            state_encoding[self.patient_state] / 6
        ]
    
    def ai_triage_assessment(self):
        """Perform AI-powered triage assessment"""
        # Simulate AI triage assessment with improved accuracy
        ai_accuracy = 0.85  # 85% accuracy for AI triage
        
        # Generate AI assessment score based on patient data
        assessment_factors = [
            self.urgency / 5,  # Clinical urgency
            self.pain_level / 10,  # Pain level
            len(self.comorbidities) / 8,  # Comorbidity burden
            (100 - self.age) / 100,  # Younger patients score higher
            1 if self.condition == PatientCondition.EMERGENCY else 0  # Emergency condition
        ]
        
        ai_score = sum(assessment_factors) / len(assessment_factors)
        
        # Add some randomness to simulate AI uncertainty
        ai_score += random.uniform(-0.1, 0.1)
        ai_score = max(0, min(1, ai_score))  # Clamp between 0 and 1
        
        # Determine if AI assessment is accurate
        is_accurate = random.random() < ai_accuracy
        
        if is_accurate:
            # Correct assessment - prioritize appropriately
            if ai_score > 0.7:
                self.urgency = min(self.urgency, 2)  # High priority
                self.log_action("AI Triage: High priority detected")
            elif ai_score > 0.4:
                self.urgency = max(2, min(self.urgency, 3))  # Medium priority
                self.log_action("AI Triage: Medium priority assigned")
            else:
                self.urgency = max(3, self.urgency)  # Lower priority
                self.log_action("AI Triage: Standard priority assigned")
        else:
            # Incorrect assessment - simulate AI error
            error_adjustment = random.choice([-1, 1])
            self.urgency = max(1, min(5, self.urgency + error_adjustment))
            self.log_action("AI Triage: Assessment completed (potential misclassification)")
        
        # Slight satisfaction boost from efficient AI process
        self.satisfaction += random.randint(2, 5)
        self.satisfaction = min(100, self.satisfaction)
        
        # Record AI triage usage for metrics
        if hasattr(self.model, 'ai_triage_assessments'):
            self.model.ai_triage_assessments += 1
        else:
            self.model.ai_triage_assessments = 1
    
    def move_to_area(self, area_name: str):
        """Start movement to a new hospital area"""
        if area_name in self.AREA_POSITIONS:
            self.target_position = self.AREA_POSITIONS[area_name].copy()
            self.destination = area_name
            self.is_moving = True
            self.movement_progress = 0.0
            
            # Log the movement
            self.log_action("started_movement", {
                "from": self.current_location,
                "to": area_name,
                "from_pos": self.position.copy(),
                "to_pos": self.target_position.copy()
            })
    
    def update_position(self):
        """Update agent position with smooth movement"""
        if not self.is_moving:
            return
        
        # Calculate movement delta
        dx = self.target_position['x'] - self.position['x']
        dy = self.target_position['y'] - self.position['y']
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 0.1:  # Close enough to target
            # Snap to target
            self.position = self.target_position.copy()
            self.is_moving = False
            self.movement_progress = 1.0
            self.current_location = self.destination
            
            # Add to movement trail
            self.add_to_trail(self.position.copy())
            
            self.log_action("completed_movement", {
                "arrived_at": self.current_location,
                "position": self.position.copy()
            })
        else:
            # Move toward target
            move_distance = min(self.movement_speed, distance)
            move_ratio = move_distance / distance
            
            self.position['x'] += dx * move_ratio
            self.position['y'] += dy * move_ratio
            self.movement_progress = min(1.0, self.movement_progress + move_ratio)
            
            # Add to trail periodically
            if len(self.movement_trail) == 0 or distance > 1.0:
                self.add_to_trail(self.position.copy())
    
    def add_to_trail(self, position: dict):
        """Add position to movement trail"""
        self.movement_trail.append({
            'x': position['x'],
            'y': position['y'],
            'timestamp': getattr(self.model, 'time', 0) if self.model else 0
        })
        
        # Keep trail length manageable
        if len(self.movement_trail) > 10:
            self.movement_trail = self.movement_trail[-5:]  # Keep last 5 positions
    
    def get_animation_data(self) -> dict:
        """Get data needed for frontend animation"""
        return {
            'unique_id': self.unique_id,
            'agent_type': self.agent_type,
            'position': self.position.copy(),
            'target_position': self.target_position.copy() if self.is_moving else None,
            'current_location': self.current_location,
            'destination': self.destination,
            'is_moving': self.is_moving,
            'movement_progress': self.movement_progress,
            'state': self.patient_state.value if hasattr(self, 'patient_state') else 'unknown',
            'condition': self.condition.value if hasattr(self, 'condition') else 'unknown',
            'wait_time': getattr(self, 'wait_time', 0),
            'satisfaction': getattr(self, 'satisfaction', 50),
            'movement_trail': self.movement_trail[-3:] if self.movement_trail else []  # Last 3 positions
        }