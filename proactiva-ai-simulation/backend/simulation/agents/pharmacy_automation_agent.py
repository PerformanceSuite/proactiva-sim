"""
Pharmacy automation agents for medication management and dispensing
"""
from .modernized_base_agent import ModernizedBaseAgent, AgentState
from enum import Enum
import random
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PharmacyTask(Enum):
    IDLE = "idle"
    PRESCRIPTION_VERIFICATION = "prescription_verification"
    MEDICATION_DISPENSING = "medication_dispensing"
    INVENTORY_MANAGEMENT = "inventory_management"
    DRUG_INTERACTION_CHECK = "drug_interaction_check"
    PATIENT_COUNSELING = "patient_counseling"
    REFILL_PROCESSING = "refill_processing"
    COMPOUND_PREPARATION = "compound_preparation"
    QUALITY_CONTROL = "quality_control"
    EMERGENCY_DISPENSING = "emergency_dispensing"


class AutomationType(Enum):
    ROBOTIC_DISPENSING = "robotic_dispensing"
    AUTOMATED_PACKAGING = "automated_packaging"
    SMART_INVENTORY = "smart_inventory"
    AI_VERIFICATION = "ai_verification"
    AUTOMATED_COMPOUNDING = "automated_compounding"
    PNEUMATIC_TUBE = "pneumatic_tube"
    MEDICATION_CAROUSEL = "medication_carousel"
    BARCODE_SCANNING = "barcode_scanning"


class MedicationClass(Enum):
    CARDIOVASCULAR = "cardiovascular"
    PSYCHIATRIC = "psychiatric"
    PAIN_MANAGEMENT = "pain_management"
    DIABETES = "diabetes"
    RESPIRATORY = "respiratory"
    ANTIBIOTIC = "antibiotic"
    IMMUNOSUPPRESSANT = "immunosuppressant"
    CHEMOTHERAPY = "chemotherapy"


class PharmacyAutomationAgent(ModernizedBaseAgent):
    """Advanced pharmacy automation system for medication management"""
    
    def __init__(self, unique_id: str, model, **kwargs):
        super().__init__(unique_id, model, "pharmacy_automation")
        
        # System specifications
        self.system_type = kwargs.get('system_type', AutomationType.ROBOTIC_DISPENSING)
        self.dispensing_capacity = kwargs.get('dispensing_capacity', 500)  # Prescriptions per hour
        self.accuracy_rate = kwargs.get('accuracy_rate', 0.9999)  # 99.99% accuracy
        self.processing_speed = kwargs.get('processing_speed', 2.0)  # Relative speed multiplier
        
        # Automation capabilities
        self.automation_features = kwargs.get('automation_features', [
            AutomationType.ROBOTIC_DISPENSING,
            AutomationType.AUTOMATED_PACKAGING,
            AutomationType.SMART_INVENTORY,
            AutomationType.AI_VERIFICATION,
            AutomationType.BARCODE_SCANNING,
            AutomationType.MEDICATION_CAROUSEL
        ])
        
        # Current state
        self.current_task = PharmacyTask.IDLE
        self.prescription_queue: List[Dict[str, Any]] = []
        self.active_prescription = None
        self.task_completion_time = 0
        
        # Inventory management
        self.medication_inventory = self._initialize_inventory()
        self.reorder_points = self._set_reorder_points()
        self.pending_orders = []
        
        # Performance metrics
        self.prescriptions_filled = 0
        self.errors_prevented = 0
        self.drug_interactions_detected = 0
        self.average_fill_time = []
        self.inventory_stockouts = 0
        self.emergency_dispenses = 0
        
        # Safety and compliance
        self.verification_level = kwargs.get('verification_level', 'high')
        self.controlled_substance_access = kwargs.get('controlled_access', True)
        self.audit_trail = []
        self.last_maintenance = 0
        self.maintenance_interval = 168  # Hours (weekly)
        
        # AI and learning
        self.ai_model_version = kwargs.get('ai_version', '3.0')
        self.interaction_database = self._load_drug_interactions()
        self.prescription_patterns = {}
        self.fraud_detection_enabled = True
        
        # Physical location
        self.location = 'pharmacy'
        self.connected_departments = ['emergency', 'outpatient', 'inpatient']
        
        # Integration with other systems
        self.ehr_connected = True
        self.insurance_verification = True
        self.provider_alerts_enabled = True
        
    def agent_step(self):
        """Mesa 3.x required method - delegates to step"""
        self.step()
        
    def step(self):
        """Execute one step of pharmacy automation behavior"""
        if not self.is_active():
            return
            
        # Check maintenance schedule
        self._check_maintenance()
        
        # Process current task
        if self.current_task != PharmacyTask.IDLE:
            self._process_current_task()
        else:
            # Look for new tasks
            self._find_new_task()
            
        # Monitor inventory levels
        self._monitor_inventory()
        
        # Update metrics
        self.track_metric('prescriptions_filled', self.prescriptions_filled)
        self.track_metric('queue_length', len(self.prescription_queue))
        self.track_metric('errors_prevented', self.errors_prevented)
        self.track_metric('current_task', self.current_task.value)
        
    def _initialize_inventory(self) -> Dict[str, Dict[str, Any]]:
        """Initialize medication inventory"""
        medications = {}
        
        # Common VA medications
        common_meds = [
            ('lisinopril', MedicationClass.CARDIOVASCULAR, 5000),
            ('metformin', MedicationClass.DIABETES, 4000),
            ('sertraline', MedicationClass.PSYCHIATRIC, 3500),
            ('atorvastatin', MedicationClass.CARDIOVASCULAR, 4500),
            ('gabapentin', MedicationClass.PAIN_MANAGEMENT, 3000),
            ('amlodipine', MedicationClass.CARDIOVASCULAR, 3500),
            ('omeprazole', MedicationClass.RESPIRATORY, 4000),
            ('hydrocodone', MedicationClass.PAIN_MANAGEMENT, 500),  # Controlled
            ('alprazolam', MedicationClass.PSYCHIATRIC, 800),  # Controlled
            ('insulin', MedicationClass.DIABETES, 2000)
        ]
        
        for med_name, med_class, quantity in common_meds:
            medications[med_name] = {
                'quantity': quantity,
                'class': med_class,
                'controlled': med_name in ['hydrocodone', 'alprazolam', 'oxycodone'],
                'unit_cost': random.uniform(0.10, 50.00),
                'expiration_dates': self._generate_expiration_dates(quantity),
                'lot_numbers': self._generate_lot_numbers(quantity)
            }
            
        return medications
        
    def _set_reorder_points(self) -> Dict[str, int]:
        """Set automatic reorder points for medications"""
        reorder_points = {}
        for med_name, med_info in self.medication_inventory.items():
            # Higher reorder point for controlled substances and critical meds
            if med_info['controlled']:
                reorder_points[med_name] = 200
            elif med_info['class'] in [MedicationClass.CARDIOVASCULAR, MedicationClass.DIABETES]:
                reorder_points[med_name] = 1000
            else:
                reorder_points[med_name] = 500
                
        return reorder_points
        
    def _load_drug_interactions(self) -> Dict[Tuple[str, str], str]:
        """Load drug interaction database"""
        # Simplified interaction database
        interactions = {
            ('warfarin', 'aspirin'): 'major',
            ('lisinopril', 'potassium'): 'moderate',
            ('metformin', 'alcohol'): 'moderate',
            ('sertraline', 'tramadol'): 'major',
            ('hydrocodone', 'alprazolam'): 'major',
            ('atorvastatin', 'gemfibrozil'): 'moderate'
        }
        
        # Make bidirectional
        bidirectional = {}
        for (drug1, drug2), severity in interactions.items():
            bidirectional[(drug1, drug2)] = severity
            bidirectional[(drug2, drug1)] = severity
            
        return bidirectional
        
    def add_prescription(self, prescription: Dict[str, Any]):
        """Add prescription to processing queue"""
        # Validate prescription
        prescription['received_time'] = self.model.time if self.model else 0
        prescription['status'] = 'pending'
        prescription['priority'] = self._calculate_priority(prescription)
        
        # Add to queue based on priority
        if prescription['priority'] == 'emergency':
            self.prescription_queue.insert(0, prescription)
        else:
            self.prescription_queue.append(prescription)
            
        logger.info(f"Pharmacy received prescription for {prescription.get('patient_id')}")
        
    def _calculate_priority(self, prescription: Dict[str, Any]) -> str:
        """Calculate prescription priority"""
        if prescription.get('emergency', False):
            return 'emergency'
        elif prescription.get('medication') in ['insulin', 'epinephrine', 'nitroglycerin']:
            return 'urgent'
        else:
            return 'routine'
            
    def _find_new_task(self):
        """Find and assign new task"""
        # Check for emergency prescriptions first
        emergency_scripts = [p for p in self.prescription_queue if p['priority'] == 'emergency']
        if emergency_scripts:
            self._start_prescription_processing(emergency_scripts[0])
            return
            
        # Regular prescription processing
        if self.prescription_queue:
            prescription = self.prescription_queue[0]
            self._start_prescription_processing(prescription)
            return
            
        # Inventory management tasks
        if random.random() < 0.1:  # 10% chance to do inventory check
            self._start_task(PharmacyTask.INVENTORY_MANAGEMENT, duration=10)
            
    def _start_prescription_processing(self, prescription: Dict[str, Any]):
        """Start processing a prescription"""
        self.active_prescription = prescription
        self.prescription_queue.remove(prescription)
        
        # Start with verification
        self._start_task(PharmacyTask.PRESCRIPTION_VERIFICATION, duration=3)
        
    def _start_task(self, task: PharmacyTask, duration: int):
        """Start a new task"""
        self.current_task = task
        self.task_completion_time = int(duration / self.processing_speed)
        
    def _process_current_task(self):
        """Process the current task"""
        self.task_completion_time -= 1
        
        if self.task_completion_time <= 0:
            self._complete_current_task()
            
    def _complete_current_task(self):
        """Complete the current task"""
        if self.current_task == PharmacyTask.PRESCRIPTION_VERIFICATION:
            # Verify prescription
            if self._verify_prescription(self.active_prescription):
                # Check drug interactions
                self._start_task(PharmacyTask.DRUG_INTERACTION_CHECK, duration=2)
            else:
                # Reject prescription
                self._reject_prescription(self.active_prescription, "Verification failed")
                
        elif self.current_task == PharmacyTask.DRUG_INTERACTION_CHECK:
            # Check interactions
            interactions = self._check_drug_interactions(self.active_prescription)
            if not interactions or all(i['severity'] != 'major' for i in interactions):
                # Proceed to dispensing
                self._start_task(PharmacyTask.MEDICATION_DISPENSING, duration=5)
            else:
                # Alert provider
                self._alert_provider(self.active_prescription, interactions)
                self.drug_interactions_detected += 1
                
        elif self.current_task == PharmacyTask.MEDICATION_DISPENSING:
            # Dispense medication
            if self._dispense_medication(self.active_prescription):
                self.prescriptions_filled += 1
                fill_time = (self.model.time if self.model else 0) - self.active_prescription['received_time']
                self.average_fill_time.append(fill_time)
                
                # Log completion
                self.audit_trail.append({
                    'prescription_id': self.active_prescription.get('id'),
                    'completed_time': self.model.time if self.model else 0,
                    'fill_time': fill_time
                })
                
                # Simulate patient counseling for certain medications
                if self.active_prescription.get('medication') in ['warfarin', 'insulin', 'methotrexate']:
                    self._start_task(PharmacyTask.PATIENT_COUNSELING, duration=5)
                else:
                    self.active_prescription = None
                    self.current_task = PharmacyTask.IDLE
            else:
                # Out of stock
                self._handle_stockout(self.active_prescription)
                
        elif self.current_task == PharmacyTask.PATIENT_COUNSELING:
            # Complete counseling
            logger.info(f"Completed patient counseling for {self.active_prescription.get('medication')}")
            self.active_prescription = None
            self.current_task = PharmacyTask.IDLE
            
        elif self.current_task == PharmacyTask.INVENTORY_MANAGEMENT:
            # Complete inventory check
            self._perform_inventory_check()
            self.current_task = PharmacyTask.IDLE
            
    def _verify_prescription(self, prescription: Dict[str, Any]) -> bool:
        """Verify prescription validity"""
        # Check for required fields
        required_fields = ['patient_id', 'provider_id', 'medication', 'dosage', 'quantity']
        if not all(field in prescription for field in required_fields):
            return False
            
        # Verify provider credentials (simulated)
        if random.random() < 0.001:  # 0.1% fraud rate
            self.errors_prevented += 1
            return False
            
        # Check dosage limits
        if self._check_dosage_limits(prescription):
            return True
        else:
            self.errors_prevented += 1
            return False
            
    def _check_dosage_limits(self, prescription: Dict[str, Any]) -> bool:
        """Check if dosage is within safe limits"""
        # Simplified dosage checking
        max_dosages = {
            'hydrocodone': 60,  # mg/day
            'alprazolam': 4,    # mg/day
            'metformin': 2000,  # mg/day
            'lisinopril': 40    # mg/day
        }
        
        med = prescription.get('medication')
        if med in max_dosages:
            dosage = prescription.get('dosage', 0)
            return dosage <= max_dosages[med]
            
        return True
        
    def _check_drug_interactions(self, prescription: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for drug interactions with patient's current medications"""
        interactions = []
        
        # Get patient's current medications (simulated)
        current_meds = prescription.get('current_medications', [])
        new_med = prescription.get('medication')
        
        for current_med in current_meds:
            interaction_key = (new_med, current_med)
            if interaction_key in self.interaction_database:
                interactions.append({
                    'drug1': new_med,
                    'drug2': current_med,
                    'severity': self.interaction_database[interaction_key]
                })
                
        return interactions
        
    def _dispense_medication(self, prescription: Dict[str, Any]) -> bool:
        """Dispense medication from inventory"""
        med = prescription.get('medication')
        quantity = prescription.get('quantity', 30)
        
        if med in self.medication_inventory:
            if self.medication_inventory[med]['quantity'] >= quantity:
                # Dispense
                self.medication_inventory[med]['quantity'] -= quantity
                
                # Use FIFO for lot numbers
                self._update_lot_tracking(med, quantity)
                
                return True
                
        return False
        
    def _monitor_inventory(self):
        """Monitor inventory levels and create reorders"""
        for med, info in self.medication_inventory.items():
            if info['quantity'] <= self.reorder_points.get(med, 500):
                # Create reorder
                if not any(order['medication'] == med for order in self.pending_orders):
                    reorder_quantity = self.reorder_points[med] * 5  # Order 5x reorder point
                    self.pending_orders.append({
                        'medication': med,
                        'quantity': reorder_quantity,
                        'order_time': self.model.time if self.model else 0,
                        'expected_delivery': (self.model.time if self.model else 0) + 24  # 24 hours
                    })
                    logger.info(f"Reordering {reorder_quantity} units of {med}")
                    
    def _generate_expiration_dates(self, quantity: int) -> List[datetime]:
        """Generate expiration dates for medication lots"""
        dates = []
        base_date = datetime.now()
        for _ in range(min(10, quantity // 100 + 1)):  # Create lots
            expiration = base_date + timedelta(days=random.randint(180, 730))
            dates.append(expiration)
        return dates
        
    def _generate_lot_numbers(self, quantity: int) -> List[str]:
        """Generate lot numbers for tracking"""
        return [f"LOT{random.randint(100000, 999999)}" for _ in range(min(10, quantity // 100 + 1))]
        
    def _update_lot_tracking(self, medication: str, quantity: int):
        """Update lot tracking after dispensing"""
        # FIFO - remove from oldest lots first
        # Simplified for simulation
        pass
        
    def _reject_prescription(self, prescription: Dict[str, Any], reason: str):
        """Reject a prescription"""
        prescription['status'] = 'rejected'
        prescription['rejection_reason'] = reason
        logger.warning(f"Prescription rejected: {reason}")
        self.active_prescription = None
        self.current_task = PharmacyTask.IDLE
        
    def _alert_provider(self, prescription: Dict[str, Any], interactions: List[Dict[str, Any]]):
        """Alert provider about drug interactions"""
        alert = {
            'type': 'drug_interaction',
            'prescription': prescription,
            'interactions': interactions,
            'timestamp': self.model.time if self.model else 0
        }
        logger.warning(f"Drug interaction alert sent for {prescription.get('patient_id')}")
        
        # For now, assume provider approves with modifications
        if random.random() < 0.8:  # 80% approval rate
            self._start_task(PharmacyTask.MEDICATION_DISPENSING, duration=5)
        else:
            self._reject_prescription(prescription, "Provider cancelled due to interactions")
            
    def _handle_stockout(self, prescription: Dict[str, Any]):
        """Handle medication stockout"""
        self.inventory_stockouts += 1
        prescription['status'] = 'backorder'
        logger.warning(f"Stockout for {prescription.get('medication')}")
        
        # Try to find alternative
        # For simulation, just mark as backorder
        self.active_prescription = None
        self.current_task = PharmacyTask.IDLE
        
    def _perform_inventory_check(self):
        """Perform inventory reconciliation"""
        # Check for expired medications
        expired_count = 0
        for med, info in self.medication_inventory.items():
            for exp_date in info['expiration_dates']:
                if exp_date < datetime.now():
                    expired_count += 1
                    
        if expired_count > 0:
            logger.info(f"Found {expired_count} expired medication lots")
            
    def _check_maintenance(self):
        """Check if maintenance is needed"""
        hours_since_maintenance = (self.model.time if self.model else 0) - self.last_maintenance
        if hours_since_maintenance >= self.maintenance_interval * 60:  # Convert hours to minutes
            self.last_maintenance = self.model.time if self.model else 0
            logger.info("Pharmacy automation system maintenance completed")
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get pharmacy automation performance metrics"""
        avg_fill_time = np.mean(self.average_fill_time) if self.average_fill_time else 0
        
        return {
            'prescriptions_filled': self.prescriptions_filled,
            'average_fill_time': avg_fill_time,
            'errors_prevented': self.errors_prevented,
            'drug_interactions_detected': self.drug_interactions_detected,
            'stockout_rate': self.inventory_stockouts / max(self.prescriptions_filled, 1),
            'queue_length': len(self.prescription_queue),
            'inventory_value': sum(info['quantity'] * info['unit_cost'] 
                                 for info in self.medication_inventory.values()),
            'automation_efficiency': self.processing_speed,
            'accuracy_rate': self.accuracy_rate
        }