"""
Modernized Mesa 3.0 hospital simulation model with improved architecture
"""
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
from ..utils.scheduler import RandomActivation
import networkx as nx
import random
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import numpy as np

from ..agents.patient_agent import VeteranPatientAgent, PatientCondition
from ..agents.provider_agent import ProviderAgent, ProviderType, ProviderSpecialty
from ..agents.ai_phone_agent import AIPhoneAgent, CallType
from ..insights.insight_engine import InsightEngine
from ..utils.performance_optimizer import AdaptivePerformanceManager, PerformanceThresholds


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VAHospitalModel(Model):
    """
    Modernized VA Hospital simulation model with Mesa 3.0 best practices
    
    Features:
    - Proper Mesa 3.0 agent scheduling
    - Centralized error handling
    - Performance optimizations
    - Comprehensive logging
    - Memory-efficient agent management
    """
    
    def __init__(self, 
                 num_initial_patients: int = 100,
                 num_providers: int = 20,
                 provider_mix: Optional[Dict[str, int]] = None,
                 innovations: Optional[Dict[str, Any]] = None,
                 **kwargs):
        
        super().__init__()
        logger.info(f"Initializing VA Hospital Model with {num_initial_patients} patients, {num_providers} providers")
        
        # Model parameters
        self.num_initial_patients = num_initial_patients
        self.num_providers = num_providers
        self.provider_mix = provider_mix or self._default_provider_mix()
        
        # Innovation configuration
        self.vr_stations = innovations.get('vr_stations', 2) if innovations else 2
        self.telehealth_rooms = innovations.get('telehealth_rooms', 3) if innovations else 3
        self.ai_triage_enabled = innovations.get('ai_triage_enabled', False) if innovations else False
        self.mobile_units = innovations.get('mobile_units', 1) if innovations else 1
        self.robotic_assistants = innovations.get('robotic_assistants', 2) if innovations else 2
        self.ai_phone_systems = innovations.get('ai_phone_systems', 1) if innovations else 1
        
        # Simulation state
        self.time = 0
        self.step_count = 0
        self.running = True
        
        # Performance tracking
        self.performance_metrics = {
            'agent_count': 0,
            'step_duration': 0,
            'memory_usage': 0,
            'error_count': 0
        }
        
        # Initialize Mesa 3.0 scheduler
        self.schedule = RandomActivation(self)
        
        # Initialize hospital network
        self.grid = self._create_hospital_network()
        
        # Operational metrics
        self.waiting_room = []
        self.patients_treated = 0
        self.patients_left_without_treatment = 0
        self.vr_sessions_completed = 0
        self.telehealth_sessions_completed = 0
        self.vr_stations_available = self.vr_stations
        self.ai_triage_assessments = 0
        
        # Initialize insight engine
        try:
            self.insight_engine = InsightEngine(self)
        except Exception as e:
            logger.error(f"Failed to initialize insight engine: {e}")
            self.insight_engine = None
        
        # Initialize performance optimizer for large-scale simulations
        thresholds = PerformanceThresholds(
            max_agent_count=10000,
            max_memory_usage=2048.0,  # 2GB
            max_step_duration=2.0  # 2 seconds max per step
        )
        self.performance_manager = AdaptivePerformanceManager(thresholds)
        
        # Initialize data collector with Mesa 3.0 pattern
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
                "Cost_Per_Visit": self._compute_cost_per_visit,
                "Agent_Count": lambda m: m.schedule.get_agent_count(),
                "Step_Duration": lambda m: m.performance_metrics['step_duration'],
                "Memory_Usage": lambda m: m.performance_metrics['memory_usage']
            },
            agent_reporters={
                "Type": lambda a: getattr(a, 'agent_type', 'unknown'),
                "State": lambda a: getattr(a, 'state', None),
                "Wait_Time": lambda a: getattr(a, 'wait_time', None),
                "Satisfaction": lambda a: getattr(a, 'satisfaction', None),
                "Position": lambda a: getattr(a, 'pos', None)
            }
        )
        
        # Create initial agents
        self._initialize_agents()
        
        # Collect initial data
        self.datacollector.collect(self)
        
        logger.info(f"Model initialized successfully with {self.schedule.get_agent_count()} agents")
    
    def _default_provider_mix(self) -> Dict[str, int]:
        """Default provider specialty distribution"""
        return {
            'primary_care': 8,
            'mental_health': 4,
            'emergency': 3,
            'specialist': 5
        }
    
    def _create_hospital_network(self) -> NetworkGrid:
        """Create hospital layout as network graph with error handling"""
        try:
            G = nx.Graph()
            
            # Define hospital areas with improved connectivity
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
            
            # Define realistic hospital flow connections
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
                ('mental_health', 'vr_therapy_suite'),
                ('mental_health', 'telehealth_center'),
                ('specialist', 'lab'),
                ('specialist', 'imaging'),
                ('emergency', 'lab'),
                ('emergency', 'imaging'),
                ('emergency', 'pharmacy'),
                ('lab', 'discharge'),
                ('imaging', 'discharge'),
                ('pharmacy', 'discharge'),
                ('vr_therapy_suite', 'discharge'),
                ('telehealth_center', 'discharge'),
                ('primary_care', 'discharge'),
                ('mental_health', 'discharge'),
                ('specialist', 'discharge'),
                ('emergency', 'discharge')
            ]
            
            G.add_edges_from(connections)
            
            return NetworkGrid(G)
            
        except Exception as e:
            logger.error(f"Failed to create hospital network: {e}")
            # Return minimal fallback network
            G = nx.Graph()
            G.add_node('entrance')
            return NetworkGrid(G)
    
    def _initialize_agents(self):
        """Initialize all agents with improved error handling"""
        try:
            self._create_providers()
            self._create_initial_patients()
            self._create_ai_phone_systems()
            logger.info(f"Created {self.schedule.get_agent_count()} agents successfully")
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise
    
    def _create_providers(self):
        """Create provider agents with specialties"""
        provider_id = 0
        
        for specialty_name, count in self.provider_mix.items():
            try:
                specialty = ProviderSpecialty(specialty_name)
                for _ in range(count):
                    # Determine provider type based on specialty
                    if specialty == ProviderSpecialty.EMERGENCY:
                        p_type = ProviderType.PHYSICIAN
                    elif specialty == ProviderSpecialty.MENTAL_HEALTH:
                        p_type = random.choice([ProviderType.PHYSICIAN, ProviderType.THERAPIST])
                    else:
                        p_type = random.choice([ProviderType.PHYSICIAN, ProviderType.NURSE_PRACTITIONER])
                    
                    provider = ProviderAgent(
                        provider_id,
                        self,
                        provider_type=p_type,
                        specialty=specialty,
                        experience_years=random.randint(1, 25)
                    )
                    
                    # Add to Mesa scheduler
                    self.schedule.add(provider)
                    
                    # Place in appropriate location with error handling
                    try:
                        if specialty == ProviderSpecialty.EMERGENCY and 'emergency' in self.grid.G.nodes:
                            self.grid.place_agent(provider, 'emergency')
                        elif specialty == ProviderSpecialty.MENTAL_HEALTH and 'mental_health' in self.grid.G.nodes:
                            self.grid.place_agent(provider, 'mental_health')
                        elif specialty == ProviderSpecialty.PRIMARY_CARE and 'primary_care' in self.grid.G.nodes:
                            self.grid.place_agent(provider, 'primary_care')
                        elif 'specialist' in self.grid.G.nodes:
                            self.grid.place_agent(provider, 'specialist')
                        else:
                            logger.warning(f"Could not place provider {provider_id} - using entrance")
                            if 'entrance' in self.grid.G.nodes:
                                self.grid.place_agent(provider, 'entrance')
                    except Exception as e:
                        logger.warning(f"Failed to place provider {provider_id}: {e}")
                    
                    provider_id += 1
                    
            except Exception as e:
                logger.error(f"Failed to create providers for specialty {specialty_name}: {e}")
                continue
    
    def _create_initial_patients(self):
        """Create initial patient population"""
        condition_weights = {
            PatientCondition.EMERGENCY: 0.05,
            PatientCondition.URGENT: 0.15,
            PatientCondition.ROUTINE: 0.40,
            PatientCondition.MENTAL_HEALTH: 0.20,
            PatientCondition.CHRONIC: 0.15,
            PatientCondition.PREVENTIVE: 0.05
        }
        
        for i in range(self.num_initial_patients):
            try:
                # Select condition based on weights
                condition = random.choices(
                    list(condition_weights.keys()),
                    weights=list(condition_weights.values())
                )[0]
                
                patient = VeteranPatientAgent(
                    f"patient_{i}",
                    self,
                    condition=condition,
                    age=random.randint(25, 85)
                )
                
                # Add to Mesa scheduler
                self.schedule.add(patient)
                
                # Place at entrance with error handling
                try:
                    if 'entrance' in self.grid.G.nodes:
                        self.grid.place_agent(patient, 'entrance')
                    else:
                        logger.warning(f"No entrance node for patient {i}")
                except Exception as e:
                    logger.warning(f"Failed to place patient {i}: {e}")
                
            except Exception as e:
                logger.error(f"Failed to create patient {i}: {e}")
                continue
    
    def _create_ai_phone_systems(self):
        """Create AI phone system agents"""
        for i in range(self.ai_phone_systems):
            try:
                ai_phone = AIPhoneAgent(
                    f"ai_phone_{i}",
                    self,
                    max_concurrent_calls=50,
                    nlp_accuracy=0.95
                )
                
                # Add to scheduler
                self.schedule.add(ai_phone)
                
                # Place in virtual call center (no physical location needed)
                logger.info(f"Created AI Phone System {i} with 50 concurrent call capacity")
                
            except Exception as e:
                logger.error(f"Failed to create AI phone system {i}: {e}")
                continue
    
    def step(self):
        """Execute one step of the simulation with performance monitoring"""
        step_start_time = datetime.now()
        
        try:
            # Update simulation time
            self.time += 1
            self.step_count += 1
            
            # Use performance optimizer for large agent counts
            if self.schedule.get_agent_count() > 1000:
                # Use adaptive performance optimization
                perf_result = self.performance_manager.optimize_step(self)
                if 'error' not in perf_result:
                    self.performance_metrics.update({
                        'agent_count': perf_result['agent_count'],
                        'step_duration': perf_result['step_duration'],
                        'memory_usage': perf_result['memory_usage']
                    })
            else:
                # Standard Mesa scheduler for smaller simulations
                self.schedule.step()
                
                # Update performance metrics
                step_duration = (datetime.now() - step_start_time).total_seconds()
                self.performance_metrics.update({
                    'agent_count': self.schedule.get_agent_count(),
                    'step_duration': step_duration,
                    'memory_usage': self._estimate_memory_usage()
                })
            
            # Collect data
            self.datacollector.collect(self)
            
            # Generate insights periodically
            if self.time % 50 == 0 and self.insight_engine:
                try:
                    self.insight_engine.analyze_patterns()
                except Exception as e:
                    logger.error(f"Insight generation failed: {e}")
                    self.performance_metrics['error_count'] += 1
            
            # Log performance every 100 steps
            if self.step_count % 100 == 0:
                logger.info(f"Step {self.step_count}: {self.schedule.get_agent_count()} agents, "
                          f"{self.performance_metrics['step_duration']:.3f}s duration")
                
                # Log optimization report for large simulations
                if self.schedule.get_agent_count() > 1000:
                    opt_report = self.performance_manager.get_optimization_report()
                    logger.info(f"Performance score: {opt_report['profiler_summary'].get('performance_score', 0):.1f}/100")
            
        except Exception as e:
            logger.error(f"Step {self.step_count} failed: {e}")
            self.performance_metrics['error_count'] += 1
            # Continue running despite errors
    
    def _estimate_memory_usage(self) -> float:
        """Estimate current memory usage (simplified)"""
        # Rough estimate based on agent count and data structures
        agent_memory = self.schedule.get_agent_count() * 0.001  # 1KB per agent estimate
        data_memory = len(self.waiting_room) * 0.0001  # 0.1KB per waiting patient
        return agent_memory + data_memory
    
    # Utility methods for data collection
    def _compute_average_wait_time(self) -> float:
        """Compute average wait time across all patients"""
        try:
            patients = [a for a in self.schedule.agents if hasattr(a, 'wait_time')]
            return np.mean([p.wait_time for p in patients]) if patients else 0.0
        except Exception as e:
            logger.error(f"Wait time computation failed: {e}")
            return 0.0
    
    def _compute_average_satisfaction(self) -> float:
        """Compute average patient satisfaction"""
        try:
            patients = [a for a in self.schedule.agents if hasattr(a, 'satisfaction')]
            return np.mean([p.satisfaction for p in patients]) if patients else 50.0
        except Exception as e:
            logger.error(f"Satisfaction computation failed: {e}")
            return 50.0
    
    def _compute_provider_utilization(self) -> float:
        """Compute provider utilization rate"""
        try:
            providers = [a for a in self.schedule.agents if hasattr(a, 'is_available')]
            if not providers:
                return 0.0
            busy_providers = sum(1 for p in providers if not p.is_available)
            return busy_providers / len(providers)
        except Exception as e:
            logger.error(f"Provider utilization computation failed: {e}")
            return 0.0
    
    def _compute_lwot_rate(self) -> float:
        """Compute left-without-treatment rate"""
        try:
            total_patients = self.patients_treated + self.patients_left_without_treatment
            return (self.patients_left_without_treatment / total_patients) if total_patients > 0 else 0.0
        except Exception as e:
            logger.error(f"LWOT rate computation failed: {e}")
            return 0.0
    
    def _compute_mental_health_access(self) -> float:
        """Compute mental health access rate"""
        try:
            mh_patients = [a for a in self.schedule.agents 
                          if hasattr(a, 'condition') and a.condition == PatientCondition.MENTAL_HEALTH]
            if not mh_patients:
                return 0.0
            treated = sum(1 for p in mh_patients if hasattr(p, 'patient_state') and 
                         p.patient_state.value in ['treatment', 'discharged'])
            return treated / len(mh_patients)
        except Exception as e:
            logger.error(f"Mental health access computation failed: {e}")
            return 0.0
    
    def _compute_cost_per_visit(self) -> float:
        """Compute estimated cost per visit"""
        try:
            base_cost = 150.0
            innovation_cost = (self.vr_sessions_completed * 50 + 
                              self.telehealth_sessions_completed * 25)
            total_visits = max(self.patients_treated, 1)
            return base_cost + (innovation_cost / total_visits)
        except Exception as e:
            logger.error(f"Cost computation failed: {e}")
            return 150.0
    
    def get_simulation_state(self) -> Dict[str, Any]:
        """Get current simulation state for API"""
        try:
            return {
                'time': self.time,
                'step_count': self.step_count,
                'patients_waiting': len(self.waiting_room),
                'average_wait_time': self._compute_average_wait_time(),
                'average_satisfaction': self._compute_average_satisfaction(),
                'provider_utilization': self._compute_provider_utilization(),
                'vr_sessions': self.vr_sessions_completed,
                'telehealth_sessions': self.telehealth_sessions_completed,
                'patients_treated': self.patients_treated,
                'left_without_treatment': self.patients_left_without_treatment,
                'mental_health_access': self._compute_mental_health_access(),
                'cost_per_visit': self._compute_cost_per_visit(),
                'performance': self.performance_metrics,
                'agent_count': self.schedule.get_agent_count()
            }
        except Exception as e:
            logger.error(f"State retrieval failed: {e}")
            return {'error': str(e)}
    
    def reception_available(self) -> bool:
        """Check if reception is available"""
        try:
            reception_agents = [a for a in self.schedule.agents 
                              if hasattr(a, 'current_location') and a.current_location == 'reception']
            return len(reception_agents) < 5  # Reception capacity
        except Exception as e:
            logger.error(f"Reception check failed: {e}")
            return True
    
    def telehealth_available(self) -> bool:
        """Check if telehealth is available"""
        try:
            telehealth_agents = [a for a in self.schedule.agents 
                               if hasattr(a, 'current_location') and a.current_location == 'telehealth_center']
            return len(telehealth_agents) < self.telehealth_rooms
        except Exception as e:
            logger.error(f"Telehealth check failed: {e}")
            return True
    
    def get_waiting_patients_for(self, provider):
        """Get patients waiting for treatment that match provider specialty"""
        try:
            eligible_patients = []
            for patient in self.waiting_room:
                # Match specialty to condition
                if (provider.specialty == ProviderSpecialty.MENTAL_HEALTH and 
                    patient.condition == PatientCondition.MENTAL_HEALTH):
                    eligible_patients.append(patient)
                elif (provider.specialty == ProviderSpecialty.EMERGENCY and 
                      patient.condition == PatientCondition.EMERGENCY):
                    eligible_patients.append(patient)
                elif provider.specialty == ProviderSpecialty.PRIMARY_CARE:
                    # Primary care can see most conditions
                    if patient.condition in [PatientCondition.ROUTINE, PatientCondition.CHRONIC,
                                           PatientCondition.PREVENTIVE]:
                        eligible_patients.append(patient)
                elif provider.specialty == ProviderSpecialty.SPECIALIST:
                    # Specialists see urgent and chronic cases
                    if patient.condition in [PatientCondition.URGENT, PatientCondition.CHRONIC]:
                        eligible_patients.append(patient)
            
            return eligible_patients
        except Exception as e:
            logger.error(f"Get waiting patients failed: {e}")
            return []
    
    def cleanup(self):
        """Clean up model resources"""
        try:
            logger.info(f"Cleaning up model with {self.schedule.get_agent_count()} agents")
            # Clear all agents from scheduler
            for agent in list(self.schedule.agents):
                self.schedule.remove(agent)
            
            # Clear data structures
            self.waiting_room.clear()
            
            logger.info("Model cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")