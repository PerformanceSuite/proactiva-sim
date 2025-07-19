"""
AI Phone System Agent - Automated appointment scheduling and reminder calls
"""
from .modernized_base_agent import ModernizedBaseAgent, AgentState
from enum import Enum
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CallType(Enum):
    """Types of calls the AI system can handle"""
    APPOINTMENT_SCHEDULING = "appointment_scheduling"
    APPOINTMENT_REMINDER = "appointment_reminder"
    PRESCRIPTION_REFILL = "prescription_refill"
    TEST_RESULTS = "test_results"
    FOLLOW_UP = "follow_up"
    GENERAL_INQUIRY = "general_inquiry"


class CallOutcome(Enum):
    """Possible outcomes of AI phone calls"""
    SUCCESSFUL = "successful"
    NO_ANSWER = "no_answer"
    VOICEMAIL = "voicemail"
    TRANSFERRED_TO_HUMAN = "transferred_to_human"
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    APPOINTMENT_RESCHEDULED = "appointment_rescheduled"
    APPOINTMENT_CANCELLED = "appointment_cancelled"


class AIPhoneAgent(ModernizedBaseAgent):
    """
    AI-powered phone system agent that handles automated calls
    
    Features:
    - Natural language processing for patient interactions
    - Appointment scheduling and management
    - Prescription refill requests
    - Reminder calls for appointments and medications
    - Cost tracking and efficiency metrics
    """
    
    def __init__(self, unique_id: str, model, **kwargs):
        super().__init__(unique_id, model, "ai_phone_system")
        
        # System capabilities
        self.max_concurrent_calls = kwargs.get('max_concurrent_calls', 50)
        self.nlp_accuracy = kwargs.get('nlp_accuracy', 0.95)  # 95% understanding rate
        self.voice_quality = kwargs.get('voice_quality', 0.98)  # 98% natural sounding
        
        # Current state
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.call_queue: List[Dict[str, Any]] = []
        self.completed_calls = 0
        self.transferred_calls = 0
        
        # Cost metrics
        self.cost_per_minute = 0.05  # $0.05 per minute vs $2-5 for human agent
        self.average_call_duration = 3.5  # minutes
        self.human_agent_cost_per_minute = 2.50
        
        # Performance metrics
        self.total_cost_saved = 0.0
        self.appointments_scheduled = 0
        self.appointments_confirmed = 0
        self.prescriptions_processed = 0
        self.patient_satisfaction_scores: List[float] = []
        
        # Language support
        self.supported_languages = ["English", "Spanish", "Mandarin", "Vietnamese", "Tagalog"]
        self.translation_accuracy = 0.93
        
        logger.info(f"AI Phone System {unique_id} initialized with {self.max_concurrent_calls} lines")
    
    def agent_step(self):
        """Execute one step of AI phone system behavior"""
        # Process active calls
        self.process_active_calls()
        
        # Start new calls from queue if capacity available
        self.process_call_queue()
        
        # Generate outbound calls (reminders, follow-ups)
        self.generate_outbound_calls()
        
        # Update metrics
        self.update_metrics()
    
    def process_active_calls(self):
        """Process all currently active calls"""
        completed_calls = []
        
        for call_id, call_data in self.active_calls.items():
            call_duration = self.get_current_time() - call_data['start_time']
            
            # Simulate call progression
            if call_duration >= call_data['expected_duration']:
                # Complete the call
                outcome = self.complete_call(call_id, call_data)
                completed_calls.append(call_id)
                self.log_call_completion(call_id, call_data, outcome)
            else:
                # Continue processing call
                self.process_call_interaction(call_id, call_data)
        
        # Remove completed calls
        for call_id in completed_calls:
            del self.active_calls[call_id]
            self.completed_calls += 1
    
    def complete_call(self, call_id: str, call_data: Dict[str, Any]) -> CallOutcome:
        """Complete a call and determine outcome"""
        call_type = call_data['type']
        
        # Simulate different outcomes based on call type
        if call_type == CallType.APPOINTMENT_SCHEDULING:
            if random.random() < 0.85:  # 85% success rate
                self.appointments_scheduled += 1
                return CallOutcome.APPOINTMENT_SCHEDULED
            elif random.random() < 0.5:
                self.transferred_calls += 1
                return CallOutcome.TRANSFERRED_TO_HUMAN
            else:
                return CallOutcome.APPOINTMENT_RESCHEDULED
                
        elif call_type == CallType.APPOINTMENT_REMINDER:
            if random.random() < 0.70:  # 70% answer rate
                self.appointments_confirmed += 1
                return CallOutcome.APPOINTMENT_CONFIRMED
            else:
                return CallOutcome.VOICEMAIL
                
        elif call_type == CallType.PRESCRIPTION_REFILL:
            if random.random() < 0.90:  # 90% can be handled by AI
                self.prescriptions_processed += 1
                return CallOutcome.SUCCESSFUL
            else:
                self.transferred_calls += 1
                return CallOutcome.TRANSFERRED_TO_HUMAN
                
        return CallOutcome.SUCCESSFUL
    
    def process_call_queue(self):
        """Start new calls from queue if capacity available"""
        available_lines = self.max_concurrent_calls - len(self.active_calls)
        
        while available_lines > 0 and self.call_queue:
            call_request = self.call_queue.pop(0)
            self.initiate_call(call_request)
            available_lines -= 1
    
    def initiate_call(self, call_request: Dict[str, Any]):
        """Initiate a new call"""
        call_id = f"call_{self.unique_id}_{self.get_current_time()}"
        
        # Determine expected duration based on call type
        duration_map = {
            CallType.APPOINTMENT_SCHEDULING: random.uniform(3, 7),
            CallType.APPOINTMENT_REMINDER: random.uniform(1, 3),
            CallType.PRESCRIPTION_REFILL: random.uniform(2, 4),
            CallType.TEST_RESULTS: random.uniform(2, 5),
            CallType.FOLLOW_UP: random.uniform(3, 6),
            CallType.GENERAL_INQUIRY: random.uniform(2, 8)
        }
        
        expected_duration = duration_map.get(call_request['type'], 5)
        
        self.active_calls[call_id] = {
            'patient_id': call_request.get('patient_id'),
            'type': call_request['type'],
            'start_time': self.get_current_time(),
            'expected_duration': expected_duration,
            'language': call_request.get('language', 'English'),
            'priority': call_request.get('priority', 'normal')
        }
        
        self.log_action("call_initiated", {
            'call_id': call_id,
            'type': call_request['type'].value,
            'patient_id': call_request.get('patient_id')
        })
    
    def generate_outbound_calls(self):
        """Generate outbound calls for reminders and follow-ups"""
        current_time = self.get_current_time()
        
        # Generate appointment reminders (simulate checking schedule)
        if current_time % 30 == 0:  # Every 30 time units
            num_reminders = random.randint(5, 15)
            for _ in range(num_reminders):
                self.call_queue.append({
                    'type': CallType.APPOINTMENT_REMINDER,
                    'patient_id': f"patient_{random.randint(1000, 9999)}",
                    'priority': 'normal'
                })
        
        # Generate follow-up calls
        if current_time % 60 == 0:  # Every 60 time units
            num_followups = random.randint(2, 8)
            for _ in range(num_followups):
                self.call_queue.append({
                    'type': CallType.FOLLOW_UP,
                    'patient_id': f"patient_{random.randint(1000, 9999)}",
                    'priority': 'low'
                })
    
    def process_call_interaction(self, call_id: str, call_data: Dict[str, Any]):
        """Simulate ongoing call interaction"""
        # Simulate NLP processing and response generation
        if random.random() < self.nlp_accuracy:
            # Successful understanding and response
            self.log_action("nlp_success", {'call_id': call_id})
        else:
            # May need clarification or transfer
            if random.random() < 0.3:  # 30% chance of transfer when not understood
                self.transferred_calls += 1
                self.log_action("transfer_to_human", {
                    'call_id': call_id,
                    'reason': 'nlp_failure'
                })
    
    def log_call_completion(self, call_id: str, call_data: Dict[str, Any], outcome: CallOutcome):
        """Log call completion and calculate cost savings"""
        duration = self.get_current_time() - call_data['start_time']
        ai_cost = duration * self.cost_per_minute
        human_cost = duration * self.human_agent_cost_per_minute
        cost_saved = human_cost - ai_cost
        
        self.total_cost_saved += cost_saved
        
        # Generate satisfaction score (higher for successful AI completions)
        if outcome in [CallOutcome.SUCCESSFUL, CallOutcome.APPOINTMENT_SCHEDULED, 
                      CallOutcome.APPOINTMENT_CONFIRMED]:
            satisfaction = random.uniform(4.2, 5.0)  # 4.2-5.0 rating
        elif outcome == CallOutcome.TRANSFERRED_TO_HUMAN:
            satisfaction = random.uniform(3.5, 4.5)  # 3.5-4.5 rating
        else:
            satisfaction = random.uniform(3.0, 4.0)  # 3.0-4.0 rating
        
        self.patient_satisfaction_scores.append(satisfaction)
        
        self.log_action("call_completed", {
            'call_id': call_id,
            'duration': duration,
            'outcome': outcome.value,
            'cost_saved': round(cost_saved, 2),
            'satisfaction': round(satisfaction, 1)
        })
    
    def update_metrics(self):
        """Update system metrics"""
        if self.completed_calls > 0:
            # Calculate average satisfaction
            avg_satisfaction = sum(self.patient_satisfaction_scores[-100:]) / min(100, len(self.patient_satisfaction_scores))
            
            # Update performance metrics
            self.performance_metrics.update({
                'active_calls': len(self.active_calls),
                'queued_calls': len(self.call_queue),
                'completed_calls': self.completed_calls,
                'transfer_rate': self.transferred_calls / max(1, self.completed_calls),
                'total_cost_saved': round(self.total_cost_saved, 2),
                'avg_satisfaction': round(avg_satisfaction, 2)
            })
    
    def add_call_to_queue(self, call_type: CallType, patient_id: str = None, 
                         language: str = "English", priority: str = "normal"):
        """Add a call request to the queue"""
        self.call_queue.append({
            'type': call_type,
            'patient_id': patient_id or f"patient_{random.randint(1000, 9999)}",
            'language': language,
            'priority': priority,
            'queued_time': self.get_current_time()
        })
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        avg_satisfaction = sum(self.patient_satisfaction_scores[-100:]) / max(1, len(self.patient_satisfaction_scores[-100:]))
        
        return {
            'system_id': self.unique_id,
            'active_calls': len(self.active_calls),
            'calls_in_queue': len(self.call_queue),
            'total_completed': self.completed_calls,
            'appointments_scheduled': self.appointments_scheduled,
            'appointments_confirmed': self.appointments_confirmed,
            'prescriptions_processed': self.prescriptions_processed,
            'transfer_rate': round(self.transferred_calls / max(1, self.completed_calls), 3),
            'total_cost_saved': round(self.total_cost_saved, 2),
            'average_cost_per_call': round(self.average_call_duration * self.cost_per_minute, 2),
            'human_cost_equivalent': round(self.average_call_duration * self.human_agent_cost_per_minute, 2),
            'average_satisfaction': round(avg_satisfaction, 2),
            'supported_languages': self.supported_languages,
            'nlp_accuracy': self.nlp_accuracy
        }
    
    def emergency_override(self):
        """Handle emergency situations by prioritizing or transferring calls"""
        # Transfer all non-emergency calls to human agents
        for call_id, call_data in list(self.active_calls.items()):
            if call_data.get('priority') != 'emergency':
                self.transferred_calls += 1
                del self.active_calls[call_id]
                self.log_action("emergency_transfer", {'call_id': call_id})