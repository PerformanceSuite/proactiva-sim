"""
AI Clinical Note-Taking Agent - Automated medical documentation assistant
"""
from .modernized_base_agent import ModernizedBaseAgent, AgentState
from enum import Enum
import random
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NoteType(Enum):
    """Types of clinical notes the AI can generate"""
    SOAP_NOTE = "soap_note"  # Subjective, Objective, Assessment, Plan
    PROGRESS_NOTE = "progress_note"
    DISCHARGE_SUMMARY = "discharge_summary"
    CONSULTATION_NOTE = "consultation_note"
    PROCEDURE_NOTE = "procedure_note"
    MEDICATION_RECONCILIATION = "medication_reconciliation"


class DocumentationQuality(Enum):
    """Quality levels of generated documentation"""
    EXCELLENT = "excellent"  # Comprehensive, accurate, well-structured
    GOOD = "good"  # Complete with minor improvements needed
    FAIR = "fair"  # Adequate but requires human review
    NEEDS_REVIEW = "needs_review"  # Requires significant human input


class AINoteTakingAgent(ModernizedBaseAgent):
    """
    AI-powered clinical documentation agent that assists with medical note-taking
    
    Features:
    - Real-time transcription of patient encounters
    - SOAP note generation from conversation
    - ICD-10 and CPT code suggestions
    - Medication reconciliation assistance
    - Quality assurance checks
    - HIPAA-compliant processing
    """
    
    def __init__(self, unique_id: str, model, **kwargs):
        super().__init__(unique_id, model, "ai_note_taking")
        
        # Configuration
        self.transcription_accuracy = kwargs.get('transcription_accuracy', 0.95)
        self.note_generation_time = kwargs.get('note_generation_time', 2.0)  # minutes
        self.code_suggestion_accuracy = kwargs.get('code_suggestion_accuracy', 0.92)
        
        # State tracking
        self.active_encounters = {}  # provider_id -> encounter data
        self.completed_notes = []
        self.quality_metrics = {
            'total_notes': 0,
            'excellent_quality': 0,
            'time_saved_minutes': 0.0,
            'provider_satisfaction': 0.0
        }
        
        # Performance metrics
        self.metrics.update({
            'notes_generated': 0,
            'average_generation_time': 0.0,
            'quality_score': 0.0,
            'provider_time_saved': 0.0,
            'coding_accuracy': 0.0
        })
        
    def initialize(self):
        """Initialize the AI note-taking system"""
        super().initialize()
        self.state = AgentState.ACTIVE
        logger.info(f"AI Note-Taking Agent {self.unique_id} initialized")
        
    def step(self):
        """Process documentation tasks"""
        try:
            # Process active encounters
            self._process_active_encounters()
            
            # Generate notes for completed encounters
            self._generate_clinical_notes()
            
            # Perform quality checks
            self._quality_assurance()
            
            # Update metrics
            self._update_documentation_metrics()
            
        except Exception as e:
            self.handle_error(e, "note_taking_step")
            
    def start_encounter(self, provider_id: str, patient_id: str, encounter_type: str) -> Dict[str, Any]:
        """Start documenting a new patient encounter"""
        encounter_id = f"ENC_{self.model.schedule.time}_{provider_id}_{patient_id}"
        
        encounter_data = {
            'encounter_id': encounter_id,
            'provider_id': provider_id,
            'patient_id': patient_id,
            'encounter_type': encounter_type,
            'start_time': self.model.schedule.time,
            'transcript': [],
            'key_findings': [],
            'medications_discussed': [],
            'procedures_mentioned': [],
            'follow_up_needed': False
        }
        
        self.active_encounters[provider_id] = encounter_data
        logger.info(f"Started documenting encounter {encounter_id}")
        
        return {
            'encounter_id': encounter_id,
            'status': 'recording',
            'ai_ready': True
        }
        
    def add_transcript_segment(self, provider_id: str, text: str, speaker: str = "provider"):
        """Add a segment to the encounter transcript"""
        if provider_id not in self.active_encounters:
            return
            
        encounter = self.active_encounters[provider_id]
        
        # Simulate transcription with potential errors
        if random.random() > self.transcription_accuracy:
            # Simulate transcription error
            text = self._simulate_transcription_error(text)
            
        encounter['transcript'].append({
            'time': self.model.schedule.time,
            'speaker': speaker,
            'text': text
        })
        
        # Extract key medical information in real-time
        self._extract_medical_entities(text, encounter)
        
    def complete_encounter(self, provider_id: str) -> Dict[str, Any]:
        """Complete an encounter and generate the clinical note"""
        if provider_id not in self.active_encounters:
            return {'status': 'error', 'message': 'No active encounter'}
            
        encounter = self.active_encounters.pop(provider_id)
        encounter['end_time'] = self.model.schedule.time
        
        # Generate clinical note
        note = self._generate_soap_note(encounter)
        
        # Suggest medical codes
        codes = self._suggest_medical_codes(encounter)
        
        # Calculate quality score
        quality = self._assess_documentation_quality(note, encounter)
        
        # Store completed note
        completed_note = {
            'encounter': encounter,
            'note': note,
            'codes': codes,
            'quality': quality,
            'generation_time': self.note_generation_time,
            'time_saved': self._calculate_time_saved()
        }
        
        self.completed_notes.append(completed_note)
        self.metrics['notes_generated'] += 1
        self.quality_metrics['total_notes'] += 1
        
        if quality == DocumentationQuality.EXCELLENT:
            self.quality_metrics['excellent_quality'] += 1
            
        return {
            'status': 'completed',
            'note': note,
            'codes': codes,
            'quality': quality.value,
            'time_saved_minutes': completed_note['time_saved']
        }
        
    def _process_active_encounters(self):
        """Process ongoing encounters"""
        for provider_id, encounter in self.active_encounters.items():
            # Simulate real-time analysis
            if len(encounter['transcript']) > 5:
                # Analyze conversation patterns
                self._analyze_conversation_flow(encounter)
                
    def _generate_clinical_notes(self):
        """Generate notes for any auto-completed encounters"""
        # Auto-complete encounters that have been inactive
        inactive_threshold = 30  # steps
        current_time = self.model.schedule.time
        
        for provider_id, encounter in list(self.active_encounters.items()):
            last_activity = encounter['transcript'][-1]['time'] if encounter['transcript'] else encounter['start_time']
            if current_time - last_activity > inactive_threshold:
                logger.info(f"Auto-completing inactive encounter for provider {provider_id}")
                self.complete_encounter(provider_id)
                
    def _generate_soap_note(self, encounter: Dict[str, Any]) -> Dict[str, str]:
        """Generate a SOAP note from encounter data"""
        transcript_text = " ".join([seg['text'] for seg in encounter['transcript']])
        
        # Simulate AI processing
        soap_note = {
            'subjective': self._extract_subjective(transcript_text, encounter),
            'objective': self._extract_objective(encounter),
            'assessment': self._generate_assessment(encounter),
            'plan': self._generate_plan(encounter)
        }
        
        return soap_note
        
    def _extract_subjective(self, transcript: str, encounter: Dict[str, Any]) -> str:
        """Extract subjective information from encounter"""
        # Simulate extraction of chief complaint and HPI
        templates = [
            "Patient presents with chief complaint of {}. Symptoms have been present for {}.",
            "Patient reports {} with associated symptoms of {}.",
            "Chief concern today is {} which started {}."
        ]
        
        # In real implementation, this would use NLP
        return random.choice(templates).format(
            random.choice(["headache", "chest pain", "shortness of breath", "back pain"]),
            random.choice(["2 days", "1 week", "3 weeks", "1 month"])
        )
        
    def _extract_objective(self, encounter: Dict[str, Any]) -> str:
        """Extract objective findings"""
        vitals = f"Vitals: BP {random.randint(110, 140)}/{random.randint(70, 90)}, "
        vitals += f"HR {random.randint(60, 100)}, "
        vitals += f"T {random.uniform(97.5, 99.0):.1f}°F, "
        vitals += f"SpO2 {random.randint(95, 100)}%"
        
        exam = "Physical exam reveals " + random.choice([
            "no acute distress, normal cardiovascular and respiratory exam",
            "mild distress, clear lungs, regular heart rhythm",
            "alert and oriented x3, no focal neurological deficits"
        ])
        
        return f"{vitals}. {exam}."
        
    def _generate_assessment(self, encounter: Dict[str, Any]) -> str:
        """Generate clinical assessment"""
        diagnoses = [
            "Tension headache, likely stress-related",
            "Acute bronchitis, viral etiology suspected",
            "Mechanical back pain, no red flags identified",
            "Gastroesophageal reflux disease, uncontrolled"
        ]
        
        return random.choice(diagnoses)
        
    def _generate_plan(self, encounter: Dict[str, Any]) -> str:
        """Generate treatment plan"""
        plans = [
            "1. Start ibuprofen 400mg TID PRN\n2. Stress management counseling\n3. Follow up in 2 weeks",
            "1. Supportive care with rest and fluids\n2. Albuterol inhaler PRN\n3. Return if symptoms worsen",
            "1. Physical therapy referral\n2. Muscle relaxants as needed\n3. Ergonomic assessment",
            "1. Increase PPI to BID dosing\n2. Dietary modification counseling\n3. Consider H. pylori testing"
        ]
        
        return random.choice(plans)
        
    def _suggest_medical_codes(self, encounter: Dict[str, Any]) -> Dict[str, List[str]]:
        """Suggest ICD-10 and CPT codes based on encounter"""
        # Simulate code suggestion with high accuracy
        icd10_codes = {
            "headache": ["R51.9", "G44.1"],
            "back pain": ["M54.5", "M54.9"],
            "bronchitis": ["J20.9", "J40"],
            "gerd": ["K21.0", "K21.9"]
        }
        
        cpt_codes = {
            "office_visit": ["99213", "99214"],
            "consultation": ["99243", "99244"],
            "procedure": ["20610", "20605"]
        }
        
        # Select appropriate codes based on encounter type
        suggested_icd = random.choice(list(icd10_codes.values()))
        suggested_cpt = cpt_codes.get(encounter['encounter_type'], ["99213"])
        
        return {
            'icd10': suggested_icd,
            'cpt': suggested_cpt,
            'confidence': self.code_suggestion_accuracy
        }
        
    def _assess_documentation_quality(self, note: Dict[str, str], encounter: Dict[str, Any]) -> DocumentationQuality:
        """Assess the quality of generated documentation"""
        # Simulate quality assessment
        quality_score = random.random()
        
        if quality_score > 0.9:
            return DocumentationQuality.EXCELLENT
        elif quality_score > 0.7:
            return DocumentationQuality.GOOD
        elif quality_score > 0.5:
            return DocumentationQuality.FAIR
        else:
            return DocumentationQuality.NEEDS_REVIEW
            
    def _extract_medical_entities(self, text: str, encounter: Dict[str, Any]):
        """Extract medical entities from text (medications, procedures, etc.)"""
        # Simulate NER for medical entities
        medication_keywords = ["medication", "prescribe", "mg", "tablet", "dose"]
        procedure_keywords = ["procedure", "surgery", "biopsy", "scan", "test"]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in medication_keywords):
            encounter['medications_discussed'].append({
                'time': self.model.schedule.time,
                'text': text
            })
            
        if any(keyword in text_lower for keyword in procedure_keywords):
            encounter['procedures_mentioned'].append({
                'time': self.model.schedule.time,
                'text': text
            })
            
    def _analyze_conversation_flow(self, encounter: Dict[str, Any]):
        """Analyze the conversation flow for quality metrics"""
        # Check for important elements
        has_chief_complaint = any("complaint" in seg['text'].lower() for seg in encounter['transcript'])
        has_assessment = any("assessment" in seg['text'].lower() for seg in encounter['transcript'])
        has_plan = any("plan" in seg['text'].lower() for seg in encounter['transcript'])
        
        encounter['conversation_quality'] = {
            'has_chief_complaint': has_chief_complaint,
            'has_assessment': has_assessment,
            'has_plan': has_plan
        }
        
    def _calculate_time_saved(self) -> float:
        """Calculate time saved compared to manual documentation"""
        # Average manual documentation time: 15-20 minutes
        manual_time = random.uniform(15, 20)
        ai_time = self.note_generation_time
        
        time_saved = manual_time - ai_time
        self.quality_metrics['time_saved_minutes'] += time_saved
        
        return time_saved
        
    def _simulate_transcription_error(self, text: str) -> str:
        """Simulate a transcription error"""
        # Simple error simulation - in reality would be more sophisticated
        errors = [
            lambda t: t.replace("patient", "patent"),
            lambda t: t.replace("pain", "pan"),
            lambda t: t + " [inaudible]",
            lambda t: t.replace("mg", "ng")
        ]
        
        return random.choice(errors)(text)
        
    def _quality_assurance(self):
        """Perform quality checks on generated documentation"""
        if not self.completed_notes:
            return
            
        # Check recent notes for quality issues
        recent_notes = self.completed_notes[-10:]
        quality_scores = [1.0 if note['quality'] == DocumentationQuality.EXCELLENT else 0.5 
                         for note in recent_notes]
        
        self.metrics['quality_score'] = sum(quality_scores) / len(quality_scores)
        
    def _update_documentation_metrics(self):
        """Update performance metrics"""
        if self.completed_notes:
            # Average generation time
            gen_times = [note['generation_time'] for note in self.completed_notes[-20:]]
            self.metrics['average_generation_time'] = sum(gen_times) / len(gen_times)
            
            # Total time saved
            self.metrics['provider_time_saved'] = self.quality_metrics['time_saved_minutes']
            
            # Coding accuracy (simulated based on quality)
            high_quality_notes = sum(1 for note in self.completed_notes 
                                   if note['quality'] in [DocumentationQuality.EXCELLENT, DocumentationQuality.GOOD])
            self.metrics['coding_accuracy'] = high_quality_notes / len(self.completed_notes) if self.completed_notes else 0
            
    def get_documentation_stats(self) -> Dict[str, Any]:
        """Get comprehensive documentation statistics"""
        return {
            'total_notes_generated': self.metrics['notes_generated'],
            'active_encounters': len(self.active_encounters),
            'quality_distribution': {
                'excellent': self.quality_metrics['excellent_quality'],
                'total': self.quality_metrics['total_notes']
            },
            'time_saved_hours': self.quality_metrics['time_saved_minutes'] / 60,
            'average_quality_score': self.metrics['quality_score'],
            'transcription_accuracy': self.transcription_accuracy,
            'code_suggestion_accuracy': self.code_suggestion_accuracy
        }