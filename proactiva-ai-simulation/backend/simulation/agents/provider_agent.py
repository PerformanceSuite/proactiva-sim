"""
Healthcare provider agents (doctors, nurses, therapists)
"""
from .base_agent import BaseHealthcareAgent, AgentState
from enum import Enum
import random
import numpy as np
from typing import Optional, List


class ProviderType(Enum):
    PHYSICIAN = "physician"
    NURSE_PRACTITIONER = "nurse_practitioner"
    PHYSICIAN_ASSISTANT = "physician_assistant"
    NURSE = "nurse"
    THERAPIST = "therapist"
    TECHNICIAN = "technician"


class ProviderSpecialty(Enum):
    EMERGENCY = "emergency"
    PRIMARY_CARE = "primary_care"
    MENTAL_HEALTH = "mental_health"
    SPECIALIST = "specialist"
    GENERAL = "general"


class ProviderAgent(BaseHealthcareAgent):
    """Healthcare provider with realistic behaviors and constraints"""
    
    def __init__(self, unique_id: str, model, **kwargs):
        super().__init__(unique_id, model, "provider")
        
        # Provider characteristics
        self.provider_type = kwargs.get('provider_type', ProviderType.PHYSICIAN)
        self.specialty = kwargs.get('specialty', ProviderSpecialty.GENERAL)
        self.experience_years = kwargs.get('experience_years', random.randint(1, 30))
        
        # Performance metrics
        self.base_efficiency = self._calculate_base_efficiency()
        self.current_efficiency = self.base_efficiency
        self.patients_seen_today = 0
        self.patients_seen_total = 0
        
        # State and availability
        self.is_available = True
        self.current_patient: Optional[Any] = None
        self.patient_queue: List[Any] = []
        
        # Well-being metrics
        self.energy_level = 100
        self.stress_level = 20
        self.burnout_risk = 0
        self.satisfaction = 70
        
        # Innovation adoption
        self.innovation_adoption_rate = self._calculate_innovation_adoption()
        self.vr_certified = random.random() < 0.3
        self.telehealth_certified = random.random() < 0.6
        
        # Schedule
        self.shift_start = kwargs.get('shift_start', 8)
        self.shift_end = kwargs.get('shift_end', 17)
        self.break_taken = False
        
    def _calculate_base_efficiency(self) -> float:
        """Calculate baseline efficiency based on experience and type"""
        type_modifiers = {
            ProviderType.PHYSICIAN: 1.0,
            ProviderType.NURSE_PRACTITIONER: 0.95,
            ProviderType.PHYSICIAN_ASSISTANT: 0.95,
            ProviderType.NURSE: 0.85,
            ProviderType.THERAPIST: 0.9,
            ProviderType.TECHNICIAN: 0.8
        }
        
        experience_factor = min(1.0, 0.7 + (self.experience_years * 0.02))
        return type_modifiers[self.provider_type] * experience_factor
        
    def _calculate_innovation_adoption(self) -> float:
        """Calculate likelihood of adopting new technologies"""
        # Younger/less experienced providers more likely to adopt
        age_factor = max(0.3, 1.0 - (self.experience_years / 40))
        
        # Mental health providers more open to VR
        specialty_bonus = 0.2 if self.specialty == ProviderSpecialty.MENTAL_HEALTH else 0
        
        return min(1.0, age_factor + specialty_bonus + random.uniform(-0.1, 0.1))
        
    def step(self):
        """Execute one step of provider behavior"""
        # Update energy and stress
        self.update_wellbeing()
        
        # Check if on shift
        current_hour = (self.model.time // 60) % 24
        if not (self.shift_start <= current_hour < self.shift_end):
            self.is_available = False
            return
            
        # Take break if needed
        if self.needs_break() and not self.break_taken:
            self.take_break()
            return
            
        # Process current patient or get next
        if self.current_patient:
            self.continue_treatment()
        elif self.is_available:
            self.get_next_patient()
            
    def update_wellbeing(self):
        """Update provider energy and stress levels"""
        # Energy decreases over time
        self.energy_level = max(0, self.energy_level - 0.5)
        
        # Stress increases with patient load
        if self.current_patient:
            stress_increase = 0.5
            if self.current_patient.urgency <= 2:  # High urgency
                stress_increase = 1.0
            self.stress_level = min(100, self.stress_level + stress_increase)
            
        # Burnout risk calculation
        if self.energy_level < 30 and self.stress_level > 70:
            self.burnout_risk = min(100, self.burnout_risk + 1)
            
        # Efficiency affected by wellbeing
        wellbeing_factor = (self.energy_level / 100) * (1 - self.stress_level / 200)
        self.current_efficiency = self.base_efficiency * wellbeing_factor
        
    def needs_break(self) -> bool:
        """Determine if provider needs a break"""
        return (self.energy_level < 40 or 
                self.stress_level > 80 or 
                self.patients_seen_today >= 15)
                
    def take_break(self):
        """Take a restorative break"""
        self.log_action("Taking break", {
            "energy": self.energy_level,
            "stress": self.stress_level
        })
        
        self.is_available = False
        self.break_taken = True
        
        # Restore energy and reduce stress
        self.energy_level = min(100, self.energy_level + 20)
        self.stress_level = max(0, self.stress_level - 15)
        
        # Schedule return from break
        self.model.schedule_event(15, self.return_from_break)
        
    def return_from_break(self):
        """Return from break refreshed"""
        self.is_available = True
        self.log_action("Returned from break")
        
    def get_next_patient(self):
        """Select next patient to treat"""
        # Get waiting patients appropriate for this provider
        eligible_patients = self.model.get_waiting_patients_for(self)
        
        if not eligible_patients:
            return
            
        # Prioritize by urgency and wait time
        def patient_priority(patient):
            urgency_weight = (6 - patient.urgency) * 10
            wait_weight = min(patient.wait_time / 5, 20)
            
            # Specialty match bonus
            specialty_bonus = 0
            if (self.specialty == ProviderSpecialty.MENTAL_HEALTH and 
                patient.condition.value == "mental_health"):
                specialty_bonus = 20
            elif (self.specialty == ProviderSpecialty.EMERGENCY and
                  patient.urgency <= 2):
                specialty_bonus = 30
                
            return urgency_weight + wait_weight + specialty_bonus
            
        # Select highest priority patient
        eligible_patients.sort(key=patient_priority, reverse=True)
        selected_patient = eligible_patients[0]
        
        self.start_treatment(selected_patient)
        
    def start_treatment(self, patient):
        """Begin treating a patient"""
        self.current_patient = patient
        self.is_available = False
        patient.patient_state = patient.PatientState.TREATMENT
        
        # Remove from waiting room
        if patient in self.model.waiting_room:
            self.model.waiting_room.remove(patient)
            
        # Determine treatment duration
        duration = self.calculate_treatment_duration(patient)
        
        self.log_action("Started treatment", {
            "patient": patient.unique_id,
            "condition": patient.condition.value,
            "estimated_duration": duration
        })
        
        # Schedule treatment completion
        self.model.schedule_event(duration, self.complete_treatment)
        
    def calculate_treatment_duration(self, patient) -> int:
        """Calculate how long treatment will take"""
        base_durations = {
            "emergency": 45,
            "urgent": 30,
            "routine": 20,
            "mental_health": 50,
            "chronic": 25,
            "preventive": 15
        }
        
        base = base_durations.get(patient.condition.value, 20)
        
        # Adjust for efficiency
        duration = int(base / self.current_efficiency)
        
        # Add complexity for comorbidities
        duration += len(patient.comorbidities) * 5
        
        # VR therapy might be faster
        if (patient.condition.value == "mental_health" and 
            patient.vr_willingness and 
            self.vr_certified and
            self.model.vr_stations_available > 0):
            duration = int(duration * 0.8)
            
        return duration
        
    def continue_treatment(self):
        """Continue treating current patient"""
        # Treatment happens via scheduled event
        pass
        
    def complete_treatment(self):
        """Finish treating current patient"""
        if not self.current_patient:
            return
            
        patient = self.current_patient
        
        # Update provider metrics
        self.patients_seen_today += 1
        self.patients_seen_total += 1
        
        # Calculate treatment quality
        quality = self.calculate_treatment_quality()
        
        # Apply treatment effects to patient
        self.apply_treatment_effects(patient, quality)
        
        self.log_action("Completed treatment", {
            "patient": patient.unique_id,
            "quality": quality,
            "total_time": self.model.time - patient.arrival_time
        })
        
        # Make provider available again
        self.current_patient = None
        self.is_available = True
        
        # Provider satisfaction from good outcomes
        if quality > 0.8:
            self.satisfaction = min(100, self.satisfaction + 2)
            
    def calculate_treatment_quality(self) -> float:
        """Calculate quality of treatment provided"""
        # Base quality from efficiency
        base_quality = self.current_efficiency
        
        # Adjust for provider state
        if self.stress_level > 70:
            base_quality *= 0.9
        if self.energy_level < 30:
            base_quality *= 0.85
            
        # Random variation
        variation = random.uniform(-0.1, 0.1)
        
        return max(0.5, min(1.0, base_quality + variation))
        
    def apply_treatment_effects(self, patient, quality):
        """Apply treatment outcomes to patient"""
        # Base satisfaction change
        satisfaction_delta = (quality - 0.5) * 40
        patient.satisfaction = max(0, min(100, 
                                        patient.satisfaction + satisfaction_delta))
        
        # Pain reduction
        pain_reduction = quality * 5
        patient.pain_level = max(0, patient.pain_level - pain_reduction)
        
        # Complete patient treatment
        patient.complete_treatment()
        
    def get_state_vector(self) -> list:
        """Return numerical representation for ML models"""
        provider_type_encoding = {
            ProviderType.PHYSICIAN: 0,
            ProviderType.NURSE_PRACTITIONER: 1,
            ProviderType.PHYSICIAN_ASSISTANT: 2,
            ProviderType.NURSE: 3,
            ProviderType.THERAPIST: 4,
            ProviderType.TECHNICIAN: 5
        }
        
        specialty_encoding = {
            ProviderSpecialty.EMERGENCY: 0,
            ProviderSpecialty.PRIMARY_CARE: 1,
            ProviderSpecialty.MENTAL_HEALTH: 2,
            ProviderSpecialty.SPECIALIST: 3,
            ProviderSpecialty.GENERAL: 4
        }
        
        return [
            provider_type_encoding[self.provider_type] / 5,
            specialty_encoding[self.specialty] / 4,
            self.experience_years / 30,
            self.current_efficiency,
            self.patients_seen_today / 30,
            self.energy_level / 100,
            self.stress_level / 100,
            self.burnout_risk / 100,
            self.satisfaction / 100,
            int(self.is_available),
            int(self.vr_certified),
            int(self.telehealth_certified)
        ]