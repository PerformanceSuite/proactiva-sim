"""
AI Preauthorization Agent - Automated insurance approval and prior authorization
"""
from .modernized_base_agent import ModernizedBaseAgent, AgentState
from enum import Enum
import random
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProcedureType(Enum):
    """Types of procedures requiring preauthorization"""
    MRI = "mri_scan"
    CT_SCAN = "ct_scan"
    SURGERY = "surgery"
    SPECIALIST_REFERRAL = "specialist_referral"
    DME = "durable_medical_equipment"  # wheelchairs, CPAP, etc.
    PHYSICAL_THERAPY = "physical_therapy"
    MENTAL_HEALTH = "mental_health_services"
    MEDICATIONS = "specialty_medications"
    GENETIC_TESTING = "genetic_testing"
    EXPERIMENTAL = "experimental_treatment"


class AuthorizationStatus(Enum):
    """Status of preauthorization requests"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    PARTIAL_APPROVAL = "partial_approval"
    ADDITIONAL_INFO_NEEDED = "additional_info_needed"
    PEER_REVIEW = "peer_review_required"
    EXPEDITED = "expedited_review"


class UrgencyLevel(Enum):
    """Urgency levels for authorization requests"""
    ROUTINE = "routine"  # 3-5 business days
    URGENT = "urgent"    # 24-48 hours
    EMERGENT = "emergent"  # Same day
    LIFE_THREATENING = "life_threatening"  # Immediate


class AIPreauthorizationAgent(ModernizedBaseAgent):
    """
    AI-powered preauthorization agent that automates insurance approvals
    
    Features:
    - Automated clinical criteria checking
    - Real-time eligibility verification
    - Medical necessity documentation review
    - Peer-to-peer facilitation
    - Appeals process automation
    - Cost estimation and alternatives
    """
    
    def __init__(self, unique_id: str, model, **kwargs):
        super().__init__(unique_id, model, "ai_preauthorization")
        
        # Configuration
        self.auto_approval_rate = kwargs.get('auto_approval_rate', 0.75)
        self.review_time_minutes = kwargs.get('review_time_minutes', 5.0)
        self.accuracy_rate = kwargs.get('accuracy_rate', 0.94)
        
        # Clinical criteria database (simplified)
        self.clinical_criteria = self._load_clinical_criteria()
        
        # State tracking
        self.active_requests = {}  # request_id -> authorization data
        self.completed_authorizations = []
        self.appeals_queue = []
        
        # Performance metrics
        self.metrics.update({
            'total_requests': 0,
            'auto_approved': 0,
            'auto_denied': 0,
            'sent_for_review': 0,
            'average_processing_time': 0.0,
            'approval_rate': 0.0,
            'cost_savings': 0.0,
            'provider_satisfaction': 0.0
        })
        
    def initialize(self):
        """Initialize the AI preauthorization system"""
        super().initialize()
        self.state = AgentState.ACTIVE
        logger.info(f"AI Preauthorization Agent {self.unique_id} initialized")
        
    def step(self):
        """Process preauthorization requests"""
        try:
            # Process new authorization requests
            self._process_new_requests()
            
            # Review pending requests
            self._review_pending_requests()
            
            # Handle appeals
            self._process_appeals()
            
            # Update metrics
            self._update_authorization_metrics()
            
        except Exception as e:
            self.handle_error(e, "preauth_step")
            
    def submit_authorization_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new preauthorization request"""
        request_id = f"AUTH_{self.model.schedule.time}_{request_data['patient_id']}_{request_data['procedure_type']}"
        
        # Extract key information
        auth_request = {
            'request_id': request_id,
            'patient_id': request_data['patient_id'],
            'provider_id': request_data['provider_id'],
            'procedure_type': ProcedureType(request_data['procedure_type']),
            'urgency': UrgencyLevel(request_data.get('urgency', 'routine')),
            'clinical_info': request_data.get('clinical_info', {}),
            'diagnosis_codes': request_data.get('diagnosis_codes', []),
            'submission_time': self.model.schedule.time,
            'status': AuthorizationStatus.PENDING,
            'estimated_cost': self._estimate_procedure_cost(request_data['procedure_type']),
            'insurance_plan': request_data.get('insurance_plan', 'standard')
        }
        
        self.active_requests[request_id] = auth_request
        self.metrics['total_requests'] += 1
        
        # Immediate eligibility check
        eligibility = self._check_eligibility(auth_request)
        
        if not eligibility['eligible']:
            auth_request['status'] = AuthorizationStatus.DENIED
            auth_request['denial_reason'] = eligibility['reason']
            return {
                'request_id': request_id,
                'status': 'denied',
                'reason': eligibility['reason'],
                'estimated_time': 'immediate'
            }
            
        # Estimate processing time
        estimated_time = self._estimate_processing_time(auth_request)
        
        logger.info(f"Preauthorization request {request_id} submitted")
        
        return {
            'request_id': request_id,
            'status': 'pending',
            'estimated_time': estimated_time,
            'requires_additional_info': self._check_missing_info(auth_request)
        }
        
    def _process_new_requests(self):
        """Process newly submitted authorization requests"""
        for request_id, request in list(self.active_requests.items()):
            if request['status'] == AuthorizationStatus.PENDING:
                # Perform automated review
                self._automated_clinical_review(request)
                
    def _automated_clinical_review(self, request: Dict[str, Any]):
        """Perform automated clinical criteria review"""
        procedure_type = request['procedure_type']
        
        # Check against clinical criteria
        criteria = self.clinical_criteria.get(procedure_type, {})
        
        # Simulate AI analysis
        meets_criteria = self._evaluate_clinical_criteria(request, criteria)
        
        if meets_criteria and random.random() < self.auto_approval_rate:
            # Auto-approve
            request['status'] = AuthorizationStatus.APPROVED
            request['approval_time'] = self.model.schedule.time
            request['approval_method'] = 'automated'
            request['auth_number'] = self._generate_auth_number()
            
            self.metrics['auto_approved'] += 1
            logger.info(f"Request {request['request_id']} auto-approved")
            
        elif not meets_criteria and random.random() < 0.3:
            # Auto-deny for clear cases
            request['status'] = AuthorizationStatus.DENIED
            request['denial_time'] = self.model.schedule.time
            request['denial_reason'] = self._generate_denial_reason(request, criteria)
            
            self.metrics['auto_denied'] += 1
            logger.info(f"Request {request['request_id']} auto-denied")
            
        else:
            # Send for manual review or additional information
            if random.random() < 0.4:
                request['status'] = AuthorizationStatus.ADDITIONAL_INFO_NEEDED
                request['info_requested'] = self._determine_missing_info(request, criteria)
            else:
                request['status'] = AuthorizationStatus.PEER_REVIEW
                self.metrics['sent_for_review'] += 1
                
    def _evaluate_clinical_criteria(self, request: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Evaluate if request meets clinical criteria"""
        # Simulate complex criteria evaluation
        score = 0.0
        max_score = 0.0
        
        # Check diagnosis codes
        if 'required_diagnoses' in criteria:
            max_score += 1.0
            if any(diag in request['diagnosis_codes'] for diag in criteria['required_diagnoses']):
                score += 1.0
                
        # Check prior treatments
        if 'prior_treatments' in criteria:
            max_score += 1.0
            # Simulate checking patient history
            if random.random() < 0.7:  # 70% have tried prior treatments
                score += 1.0
                
        # Check medical necessity
        if 'medical_necessity' in criteria:
            max_score += 1.0
            # Simulate AI evaluation of clinical notes
            if random.random() < 0.8:  # 80% meet medical necessity
                score += 1.0
                
        # Special considerations for urgency
        if request['urgency'] in [UrgencyLevel.EMERGENT, UrgencyLevel.LIFE_THREATENING]:
            score += 0.5
            
        return (score / max_score) >= 0.7 if max_score > 0 else True
        
    def _check_eligibility(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Check insurance eligibility"""
        # Simulate eligibility check
        if random.random() < 0.95:  # 95% are eligible
            return {'eligible': True}
        else:
            reasons = [
                "Insurance plan does not cover this procedure",
                "Patient has exceeded annual benefit limit",
                "Pre-existing condition exclusion applies",
                "Out-of-network provider"
            ]
            return {
                'eligible': False,
                'reason': random.choice(reasons)
            }
            
    def _estimate_processing_time(self, request: Dict[str, Any]) -> str:
        """Estimate processing time based on urgency and complexity"""
        urgency = request['urgency']
        
        if urgency == UrgencyLevel.LIFE_THREATENING:
            return "Within 1 hour"
        elif urgency == UrgencyLevel.EMERGENT:
            return "Within 4 hours"
        elif urgency == UrgencyLevel.URGENT:
            return "Within 24 hours"
        else:
            return "2-3 business days"
            
    def _estimate_procedure_cost(self, procedure_type: str) -> float:
        """Estimate procedure cost"""
        cost_ranges = {
            ProcedureType.MRI.value: (1000, 3000),
            ProcedureType.CT_SCAN.value: (500, 2000),
            ProcedureType.SURGERY.value: (5000, 50000),
            ProcedureType.SPECIALIST_REFERRAL.value: (200, 500),
            ProcedureType.DME.value: (100, 5000),
            ProcedureType.PHYSICAL_THERAPY.value: (100, 200),  # per session
            ProcedureType.MENTAL_HEALTH.value: (150, 300),  # per session
            ProcedureType.MEDICATIONS.value: (500, 10000),  # monthly
            ProcedureType.GENETIC_TESTING.value: (300, 5000),
            ProcedureType.EXPERIMENTAL.value: (10000, 100000)
        }
        
        min_cost, max_cost = cost_ranges.get(procedure_type, (100, 1000))
        return random.uniform(min_cost, max_cost)
        
    def _load_clinical_criteria(self) -> Dict[ProcedureType, Dict[str, Any]]:
        """Load clinical criteria for different procedures"""
        return {
            ProcedureType.MRI: {
                'required_diagnoses': ['M51.26', 'M54.5', 'G89.29'],  # Back pain codes
                'prior_treatments': ['physical_therapy', 'conservative_management'],
                'medical_necessity': True,
                'waiting_period_days': 30
            },
            ProcedureType.CT_SCAN: {
                'required_diagnoses': ['R06.02', 'R50.9', 'R10.9'],  # Various symptoms
                'medical_necessity': True,
                'contraindications': ['pregnancy', 'contrast_allergy']
            },
            ProcedureType.SURGERY: {
                'required_diagnoses': [],  # Varies by surgery type
                'prior_treatments': ['conservative_management'],
                'medical_necessity': True,
                'second_opinion_required': True
            },
            ProcedureType.PHYSICAL_THERAPY: {
                'session_limit': 20,  # per year
                'required_diagnoses': ['M25.50', 'M62.81', 'S13.4'],
                'medical_necessity': True
            }
        }
        
    def _generate_auth_number(self) -> str:
        """Generate unique authorization number"""
        return f"VA{random.randint(100000, 999999)}"
        
    def _generate_denial_reason(self, request: Dict[str, Any], criteria: Dict[str, Any]) -> str:
        """Generate specific denial reason"""
        reasons = [
            "Does not meet clinical criteria for medical necessity",
            "Required conservative treatment not attempted",
            "Experimental or investigational procedure",
            "Service not covered under patient's plan",
            "Frequency limitation exceeded"
        ]
        
        # Make reason specific to procedure if possible
        if 'prior_treatments' in criteria:
            return "Prior conservative treatments not documented"
        elif 'session_limit' in criteria:
            return f"Annual session limit of {criteria['session_limit']} exceeded"
        else:
            return random.choice(reasons)
            
    def _check_missing_info(self, request: Dict[str, Any]) -> List[str]:
        """Check for missing information"""
        missing = []
        
        if not request.get('diagnosis_codes'):
            missing.append("diagnosis_codes")
        if not request.get('clinical_info'):
            missing.append("clinical_documentation")
        if request['procedure_type'] == ProcedureType.SURGERY and 'operative_report' not in request:
            missing.append("planned_procedure_details")
            
        return missing
        
    def _determine_missing_info(self, request: Dict[str, Any], criteria: Dict[str, Any]) -> List[str]:
        """Determine what additional information is needed"""
        needed = []
        
        # Check specific requirements
        if criteria.get('prior_treatments'):
            needed.append("Documentation of prior conservative treatment attempts")
        if criteria.get('second_opinion_required'):
            needed.append("Second opinion from specialist")
        if request['procedure_type'] in [ProcedureType.MRI, ProcedureType.CT_SCAN]:
            needed.append("Recent clinical notes justifying imaging")
            
        return needed
        
    def _review_pending_requests(self):
        """Review requests pending manual review"""
        for request_id, request in list(self.active_requests.items()):
            if request['status'] == AuthorizationStatus.PEER_REVIEW:
                # Simulate peer review process
                time_elapsed = self.model.schedule.time - request['submission_time']
                
                if time_elapsed > 10:  # After 10 time steps
                    if random.random() < 0.8:  # 80% approval after review
                        request['status'] = AuthorizationStatus.APPROVED
                        request['auth_number'] = self._generate_auth_number()
                        request['approval_method'] = 'peer_review'
                    else:
                        request['status'] = AuthorizationStatus.DENIED
                        request['denial_reason'] = "Does not meet criteria after clinical review"
                        
    def _process_appeals(self):
        """Process authorization appeals"""
        for appeal in list(self.appeals_queue):
            # Simulate appeal review
            if random.random() < 0.3:  # 30% of appeals are successful
                original_request = appeal['original_request']
                original_request['status'] = AuthorizationStatus.APPROVED
                original_request['auth_number'] = self._generate_auth_number()
                original_request['approval_method'] = 'appeal'
                logger.info(f"Appeal successful for request {original_request['request_id']}")
                
            self.appeals_queue.remove(appeal)
            
    def submit_appeal(self, request_id: str, additional_info: Dict[str, Any]) -> Dict[str, Any]:
        """Submit an appeal for a denied authorization"""
        # Find the original request
        original_request = None
        for req in self.completed_authorizations:
            if req['request_id'] == request_id:
                original_request = req
                break
                
        if not original_request:
            return {'status': 'error', 'message': 'Original request not found'}
            
        appeal = {
            'appeal_id': f"APPEAL_{self.model.schedule.time}_{request_id}",
            'original_request': original_request,
            'additional_info': additional_info,
            'submission_time': self.model.schedule.time
        }
        
        self.appeals_queue.append(appeal)
        
        return {
            'status': 'appeal_submitted',
            'appeal_id': appeal['appeal_id'],
            'estimated_review_time': '48-72 hours'
        }
        
    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get current status of an authorization request"""
        # Check active requests
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            return {
                'request_id': request_id,
                'status': request['status'].value,
                'submitted': request['submission_time'],
                'procedure': request['procedure_type'].value,
                'urgency': request['urgency'].value
            }
            
        # Check completed requests
        for req in self.completed_authorizations:
            if req['request_id'] == request_id:
                return {
                    'request_id': request_id,
                    'status': req['status'].value,
                    'auth_number': req.get('auth_number'),
                    'denial_reason': req.get('denial_reason')
                }
                
        return {'status': 'not_found'}
        
    def _update_authorization_metrics(self):
        """Update performance metrics"""
        total = self.metrics['total_requests']
        if total > 0:
            self.metrics['approval_rate'] = (self.metrics['auto_approved'] / total) * 100
            
            # Calculate average processing time
            completed = [r for r in self.active_requests.values() 
                        if r['status'] in [AuthorizationStatus.APPROVED, AuthorizationStatus.DENIED]]
            
            if completed:
                processing_times = [self.model.schedule.time - r['submission_time'] for r in completed]
                self.metrics['average_processing_time'] = sum(processing_times) / len(processing_times)
                
            # Estimate cost savings (reduced manual review time)
            manual_review_cost = 50  # $ per review
            automated_reviews = self.metrics['auto_approved'] + self.metrics['auto_denied']
            self.metrics['cost_savings'] = automated_reviews * manual_review_cost * 0.8  # 80% savings
            
            # Provider satisfaction (based on approval rate and speed)
            self.metrics['provider_satisfaction'] = min(
                (self.metrics['approval_rate'] * 0.7 + 
                 (1 / (self.metrics['average_processing_time'] + 1)) * 30),
                100
            )
            
    def complete_authorization(self, request_id: str):
        """Move authorization to completed status"""
        if request_id in self.active_requests:
            request = self.active_requests.pop(request_id)
            self.completed_authorizations.append(request)
            
    def get_authorization_stats(self) -> Dict[str, Any]:
        """Get comprehensive authorization statistics"""
        return {
            'total_requests': self.metrics['total_requests'],
            'approval_rate': f"{self.metrics['approval_rate']:.1f}%",
            'auto_approval_rate': f"{(self.metrics['auto_approved'] / max(self.metrics['total_requests'], 1)) * 100:.1f}%",
            'average_processing_time': f"{self.metrics['average_processing_time']:.1f} time units",
            'cost_savings': f"${self.metrics['cost_savings']:,.2f}",
            'pending_reviews': len([r for r in self.active_requests.values() 
                                  if r['status'] == AuthorizationStatus.PEER_REVIEW]),
            'pending_appeals': len(self.appeals_queue),
            'provider_satisfaction': f"{self.metrics['provider_satisfaction']:.1f}%"
        }