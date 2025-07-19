"""
Main hospital simulation model - Refactored with improved error handling
"""
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
import networkx as nx
import random
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from ..agents.patient_agent import VeteranPatientAgent, PatientCondition
from ..agents.provider_agent import ProviderAgent, ProviderType, ProviderSpecialty
from ..insights.insight_engine import InsightEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VAHospitalModel(Model):
    """VA Hospital simulation model with realistic operations"""
    
    def __init__(self, 
                 num_initial_patients: int = 100,
                 num_providers: int = 20,
                 provider_mix: Optional[Dict[str, int]] = None,
                 innovations: Optional[Dict[str, Any]] = None,
                 **kwargs):
        
        super().__init__()
        
        # Model parameters
        self.num_initial_patients = num_initial_patients
        self.num_providers = num_providers
        
        # Innovation configurations
        innovations = innovations or {}
        self.vr_stations = innovations.get('vr_stations', 0)
        self.vr_stations_available = self.vr_stations
        self.telehealth_rooms = innovations.get('telehealth_rooms', 0)
        self.telehealth_rooms_available = self.telehealth_rooms
        self.ai_triage_enabled = innovations.get('ai_triage_enabled', False)
        self.mobile_units = innovations.get('mobile_units', 0)
        self.robotic_assistants = innovations.get('robotic_assistants', 0)
        
        # Facility layout
        self.G = self._create_hospital_network()
        if self.G is not None:
            self.grid = NetworkGrid(self.G)
        else:
            self.grid = None
        
        # Custom agent tracking - Mesa 3.0+ compatibility
        self.custom_agents = []
        self.time = 0
        
        # Use Mesa's built-in scheduling - Mesa 3.0+ doesn't have separate time module
        # We'll use a simple list for agent management
        self.schedule = None
        
        # Waiting areas and queues
        self.waiting_room = []
        self.triage_queue = []
        self.treatment_rooms = {
            'emergency': 10,
            'primary_care': 20,
            'mental_health': 15,
            'specialist': 10
        }
        
        # Metrics tracking
        self.patient_arrivals = 0
        self.patients_treated = 0
        self.patients_left_without_treatment = 0
        self.vr_sessions_completed = 0
        self.telehealth_sessions_completed = 0
        self.total_wait_time = 0
        self.total_treatment_time = 0
        
        # Social network for veterans
        self.veteran_network = nx.Graph()
        
        # Events system
        self.event_queue = []
        
        # Create insight engine
        self.insight_engine = InsightEngine(self)
        
        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Patients_Waiting": lambda m: len(m.waiting_room),
                "Average_Wait_Time": self._compute_average_wait_time,
                "Average_Satisfaction": self._compute_average_satisfaction,
                "Provider_Utilization": self._compute_provider_utilization,
                "VR_Utilization": lambda m: m.vr_sessions_completed,
                "Telehealth_Utilization": lambda m: m.telehealth_sessions_completed,
                "Left_Without_Treatment_Rate": self._compute_lwot_rate,
                "Mental_Health_Access": self._compute_mental_health_access,
                "Cost_Per_Visit": self._compute_cost_per_visit
            },
            agent_reporters={
                "Type": lambda a: a.agent_type,
                "State": lambda a: a.state.value if hasattr(a, 'state') else None,
                "Wait_Time": lambda a: getattr(a, 'wait_time', None),
                "Satisfaction": lambda a: getattr(a, 'satisfaction', None),
                "Condition": lambda a: getattr(a, 'condition', None)
            }
        )
        
        # Initialize agents
        self._create_providers(provider_mix)
        self._create_initial_patients()
        self._create_veteran_social_network()
        
    def _create_hospital_network(self) -> nx.Graph:
        """Create network representation of hospital layout"""
        G = nx.DiGraph()
        
        # Define hospital areas
        areas = {
            'entrance': {'type': 'access', 'capacity': 100},
            'reception': {'type': 'admin', 'capacity': 5},
            'waiting_room': {'type': 'waiting', 'capacity': 50},
            'triage': {'type': 'clinical', 'capacity': 5},
            'emergency': {'type': 'treatment', 'capacity': 10},
            'primary_care': {'type': 'treatment', 'capacity': 20},
            'mental_health': {'type': 'treatment', 'capacity': 15},
            'specialist': {'type': 'treatment', 'capacity': 10},
            'pharmacy': {'type': 'support', 'capacity': 5},
            'lab': {'type': 'support', 'capacity': 8},
            'imaging': {'type': 'support', 'capacity': 4},
            'vr_therapy_suite': {'type': 'innovation', 'capacity': self.vr_stations},
            'telehealth_center': {'type': 'innovation', 'capacity': self.telehealth_rooms},
            'discharge': {'type': 'access', 'capacity': 10}
        }
        
        # Add nodes with attributes
        for area, attrs in areas.items():
            G.add_node(area, **attrs)
            
        # Define connections (directed paths)
        connections = [
            ('entrance', 'reception'),
            ('reception', 'waiting_room'),
            ('reception', 'triage'),
            ('waiting_room', 'triage'),
            ('triage', 'emergency'),
            ('triage', 'primary_care'),
            ('triage', 'mental_health'),
            ('triage', 'specialist'),
            ('primary_care', 'lab'),
            ('primary_care', 'imaging'),
            ('primary_care', 'pharmacy'),
            ('emergency', 'lab'),
            ('emergency', 'imaging'),
            ('mental_health', 'vr_therapy_suite'),
            ('specialist', 'lab'),
            ('specialist', 'imaging'),
            ('pharmacy', 'discharge'),
            ('primary_care', 'discharge'),
            ('emergency', 'discharge'),
            ('mental_health', 'discharge'),
            ('specialist', 'discharge'),
            ('telehealth_center', 'discharge')
        ]
        
        G.add_edges_from(connections)
        
        return G
        
    def _create_providers(self, provider_mix: Optional[Dict[str, int]] = None):
        """Create healthcare provider agents"""
        if provider_mix is None:
            # Default provider mix for VA hospital
            provider_mix = {
                'emergency_physicians': 3,
                'primary_care_physicians': 5,
                'mental_health_providers': 4,
                'specialists': 3,
                'nurses': 8,
                'nurse_practitioners': 3,
                'technicians': 4
            }
            
        provider_configs = [
            ('emergency_physicians', ProviderType.PHYSICIAN, ProviderSpecialty.EMERGENCY),
            ('primary_care_physicians', ProviderType.PHYSICIAN, ProviderSpecialty.PRIMARY_CARE),
            ('mental_health_providers', ProviderType.THERAPIST, ProviderSpecialty.MENTAL_HEALTH),
            ('specialists', ProviderType.PHYSICIAN, ProviderSpecialty.SPECIALIST),
            ('nurses', ProviderType.NURSE, ProviderSpecialty.GENERAL),
            ('nurse_practitioners', ProviderType.NURSE_PRACTITIONER, ProviderSpecialty.PRIMARY_CARE),
            ('technicians', ProviderType.TECHNICIAN, ProviderSpecialty.GENERAL)
        ]
        
        provider_id = 0
        for role, p_type, specialty in provider_configs:
            count = provider_mix.get(role, 0)
            for _ in range(count):
                provider = ProviderAgent(
                    f"provider_{provider_id}",
                    self,
                    provider_type=p_type,
                    specialty=specialty,
                    experience_years=random.randint(1, 25)
                )
                self.custom_agents.append(provider)
                
                # Place provider in appropriate location
                if specialty == ProviderSpecialty.EMERGENCY:
                    if self.grid:
                        self.grid.place_agent(provider, 'emergency')
                elif specialty == ProviderSpecialty.MENTAL_HEALTH:
                    if self.grid:
                        self.grid.place_agent(provider, 'mental_health')
                elif specialty == ProviderSpecialty.PRIMARY_CARE:
                    if self.grid:
                        self.grid.place_agent(provider, 'primary_care')
                else:
                    if self.grid:
                        self.grid.place_agent(provider, 'specialist')
                    
                provider_id += 1
                
    def _create_initial_patients(self):
        """Create initial patient population"""
        # Realistic condition distribution for VA
        condition_weights = {
            PatientCondition.EMERGENCY: 0.05,
            PatientCondition.URGENT: 0.15,
            PatientCondition.ROUTINE: 0.40,
            PatientCondition.MENTAL_HEALTH: 0.25,
            PatientCondition.CHRONIC: 0.10,
            PatientCondition.PREVENTIVE: 0.05
        }
        
        conditions = list(condition_weights.keys())
        weights = list(condition_weights.values())
        
        for i in range(self.num_initial_patients):
            condition = random.choices(conditions, weights=weights)[0]
            
            patient = VeteranPatientAgent(
                f"patient_{i}",
                self,
                condition=condition,
                age=random.normalvariate(55, 15)  # Veterans skew older
            )
            
            self.custom_agents.append(patient)
            if self.grid:
                self.grid.place_agent(patient, 'entrance')
            
    def _create_veteran_social_network(self):
        """Create social connections between veterans"""
        veterans = [a for a in self.custom_agents 
                   if isinstance(a, VeteranPatientAgent)]
        
        # Create connections based on service era and other factors
        for v1 in veterans:
            for v2 in veterans:
                if v1 != v2:
                    # Same service era increases connection probability
                    if v1.service_era == v2.service_era:
                        if random.random() < 0.3:
                            self.veteran_network.add_edge(v1.unique_id, v2.unique_id)
                            v1.social_connections.append(v2)
                            v2.social_connections.append(v1)
                    # General connection probability
                    elif random.random() < 0.1:
                        self.veteran_network.add_edge(v1.unique_id, v2.unique_id)
                        v1.social_connections.append(v2)
                        v2.social_connections.append(v1)
                        
    def step(self):
        """Advance simulation by one step with improved error handling"""
        step_start_time = datetime.now()
        
        try:
            # Collect data
            self.datacollector.collect(self)
            
            # Process scheduled events
            self._process_events()
            
            # Step all agents with performance optimization
            self._step_agents_optimized()
            self.time += 1
            
            # Reset available resources
            self.vr_stations_available = self.vr_stations
            self.telehealth_rooms_available = self.telehealth_rooms
            
            # Log performance every 100 steps
            if self.time % 100 == 0:
                step_duration = (datetime.now() - step_start_time).total_seconds()
                logger.info(f"Step {self.time}: {len(self.custom_agents)} agents, {step_duration:.3f}s duration")
            
        except Exception as e:
            logger.error(f"Step {self.time} failed: {e}")
            # Continue simulation despite errors
        
        # Generate new patient arrivals
        self._generate_arrivals()
        
        # Run insight detection periodically
        if self.time % 50 == 0:
            insights = self.insight_engine.detect_insights()
            if insights:
                self.log_insights(insights)
                
    def _process_events(self):
        """Process scheduled events"""
        current_time = self.time
        due_events = [e for e in self.event_queue if e['time'] <= current_time]
        
        for event in due_events:
            event['function'](*event.get('args', []))
            self.event_queue.remove(event)
            
    def schedule_event(self, delay: int, function: callable, *args):
        """Schedule a future event"""
        self.event_queue.append({
            'time': self.time + delay,
            'function': function,
            'args': args
        })
        
    def _generate_arrivals(self):
        """Generate new patient arrivals based on time of day"""
        # Simplified arrival pattern - more arrivals during business hours
        hour = (self.time // 60) % 24
        
        if 8 <= hour <= 17:  # Business hours
            arrival_rate = 0.3
        elif 17 <= hour <= 22:  # Evening
            arrival_rate = 0.2
        elif hour < 8 or hour > 22:  # Night
            arrival_rate = 0.1
        else:
            arrival_rate = 0.1
            
        # Emergency arrivals are constant
        if random.random() < 0.05:
            self._create_emergency_patient()
        # Regular arrivals
        elif random.random() < arrival_rate:
            self._create_new_patient()
            
    def _create_emergency_patient(self):
        """Create new emergency patient"""
        patient_id = f"patient_{self.patient_arrivals}"
        patient = VeteranPatientAgent(
            patient_id,
            self,
            condition=PatientCondition.EMERGENCY
        )
        self.custom_agents.append(patient)
        if self.grid:
            self.grid.place_agent(patient, 'entrance')
        self.patient_arrivals += 1
        
    def _create_new_patient(self):
        """Create new routine patient"""
        # Random condition based on typical distribution
        condition = random.choices(
            [PatientCondition.URGENT, PatientCondition.ROUTINE, 
             PatientCondition.MENTAL_HEALTH, PatientCondition.CHRONIC],
            weights=[0.2, 0.5, 0.2, 0.1]
        )[0]
        
        patient_id = f"patient_{self.patient_arrivals}"
        patient = VeteranPatientAgent(
            patient_id,
            self,
            condition=condition
        )
        self.custom_agents.append(patient)
        if self.grid:
            self.grid.place_agent(patient, 'entrance')
        self.patient_arrivals += 1
        
    def reception_available(self) -> bool:
        """Check if reception desk is available"""
        reception_agents = self.grid.get_cell_list_contents(['reception'])
        return len(reception_agents) < self.G.nodes['reception']['capacity']
        
    def provider_available_for(self, patient) -> bool:
        """Check if appropriate provider is available for patient"""
        providers = [a for a in self.custom_agents 
                    if isinstance(a, ProviderAgent) and a.is_available]
        
        # Match provider to patient need
        if patient.condition == PatientCondition.EMERGENCY:
            return any(p.specialty == ProviderSpecialty.EMERGENCY for p in providers)
        elif patient.condition == PatientCondition.MENTAL_HEALTH:
            return any(p.specialty == ProviderSpecialty.MENTAL_HEALTH for p in providers)
        else:
            return any(p.specialty in [ProviderSpecialty.PRIMARY_CARE, 
                                     ProviderSpecialty.GENERAL] for p in providers)
            
    def get_waiting_patients_for(self, provider) -> List[VeteranPatientAgent]:
        """Get patients waiting that this provider can treat"""
        eligible = []
        
        for patient in self.waiting_room:
            # Emergency providers see emergency patients
            if (provider.specialty == ProviderSpecialty.EMERGENCY and 
                patient.urgency <= 2):
                eligible.append(patient)
            # Mental health providers see mental health patients
            elif (provider.specialty == ProviderSpecialty.MENTAL_HEALTH and
                  patient.condition == PatientCondition.MENTAL_HEALTH):
                eligible.append(patient)
            # Primary care sees most patients
            elif provider.specialty == ProviderSpecialty.PRIMARY_CARE:
                if patient.condition in [PatientCondition.ROUTINE, 
                                       PatientCondition.CHRONIC,
                                       PatientCondition.PREVENTIVE]:
                    eligible.append(patient)
            # General providers can see non-specialized cases
            elif provider.specialty == ProviderSpecialty.GENERAL:
                if patient.urgency >= 3:  # Non-emergency
                    eligible.append(patient)
                    
        return eligible
        
    def telehealth_available(self) -> bool:
        """Check if telehealth room is available"""
        return self.telehealth_rooms_available > 0
        
    def log_insights(self, insights: List[Dict[str, Any]]):
        """Log discovered insights"""
        for insight in insights:
            print(f"\n🔍 INSIGHT DISCOVERED: {insight['title']}")
            print(f"   {insight['description']}")
            print(f"   Recommendation: {insight['recommendation']}")
            print(f"   Confidence: {insight['confidence']:.0%}\n")
            
    # Metric computation methods
    def _compute_average_wait_time(self) -> float:
        """Compute average wait time for all patients"""
        wait_times = []
        for agent in self.custom_agents:
            if isinstance(agent, VeteranPatientAgent) and hasattr(agent, 'wait_time'):
                wait_times.append(agent.wait_time)
        return np.mean(wait_times) if wait_times else 0
        
    def _compute_average_satisfaction(self) -> float:
        """Compute average patient satisfaction"""
        satisfactions = []
        for agent in self.custom_agents:
            if isinstance(agent, VeteranPatientAgent):
                satisfactions.append(agent.satisfaction)
        return np.mean(satisfactions) if satisfactions else 50
        
    def _compute_provider_utilization(self) -> float:
        """Compute provider utilization rate"""
        providers = [a for a in self.custom_agents if isinstance(a, ProviderAgent)]
        if not providers:
            return 0
        busy_providers = sum(1 for p in providers if not p.is_available)
        return busy_providers / len(providers)
        
    def _compute_lwot_rate(self) -> float:
        """Compute left without treatment rate"""
        if self.patient_arrivals == 0:
            return 0
        return self.patients_left_without_treatment / self.patient_arrivals
        
    def _compute_mental_health_access(self) -> float:
        """Compute mental health access metric"""
        mh_patients = [a for a in self.custom_agents 
                      if isinstance(a, VeteranPatientAgent) and 
                      a.condition == PatientCondition.MENTAL_HEALTH]
        if not mh_patients:
            return 100
            
        treated = sum(1 for p in mh_patients 
                     if p.patient_state.value in ['treatment', 'discharged'])
        return (treated / len(mh_patients)) * 100
        
    def _compute_cost_per_visit(self) -> float:
        """Compute average cost per patient visit"""
        # Simplified cost model
        base_cost = 150
        
        # Adjust for wait time (longer waits = higher costs)
        avg_wait = self._compute_average_wait_time()
        wait_cost = avg_wait * 0.5
        
        # Adjust for innovation usage (initial investment but lower per-visit)
        innovation_savings = 0
        if self.vr_sessions_completed > 0:
            innovation_savings += 10
        if self.telehealth_sessions_completed > 0:
            innovation_savings += 15
            
        return base_cost + wait_cost - innovation_savings
        
    def _step_agents_optimized(self):
        """Optimized agent stepping for better performance with 1000+ agents"""
        # Batch agents by type for more efficient processing
        patients = [a for a in self.custom_agents if a.agent_type == 'veteran_patient']
        providers = [a for a in self.custom_agents if a.agent_type == 'provider']
        
        # Process providers first (they have simpler logic)
        for provider in providers:
            provider.step()
        
        # Process patients in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(patients), batch_size):
            batch = patients[i:i + batch_size]
            for patient in batch:
                patient.step()
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current model state for API"""
        return {
            'time': self.time,
            'patients_waiting': len(self.waiting_room),
            'average_wait_time': self._compute_average_wait_time(),
            'average_satisfaction': self._compute_average_satisfaction(),
            'provider_utilization': self._compute_provider_utilization(),
            'vr_sessions': self.vr_sessions_completed,
            'telehealth_sessions': self.telehealth_sessions_completed,
            'patients_treated': self.patients_treated,
            'left_without_treatment': self.patients_left_without_treatment,
            'mental_health_access': self._compute_mental_health_access(),
            'cost_per_visit': self._compute_cost_per_visit()
        }