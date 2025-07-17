"""
Patient agents with realistic healthcare-seeking behaviors
"""
from .base_agent import BaseHealthcareAgent, AgentState
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


class VeteranPatientAgent(BaseHealthcareAgent):
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
        self.arrival_time = model.time
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
        
    def step(self):
        """Execute one step of patient behavior"""
        self.log_action(f"Step in state {self.patient_state.value}")
        
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
        
        total_time = self.model.time - self.arrival_time
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