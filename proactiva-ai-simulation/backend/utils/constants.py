"""
Constants and configuration for the PROACTIVA simulation backend
"""
from enum import Enum

# API Configuration
API_VERSION = "v2"
DEFAULT_SIMULATION_NAME = "VA Hospital Simulation"

# Simulation Defaults
DEFAULT_SIMULATION_CONFIG = {
    "num_patients": 100,
    "num_providers": 20,
    "vr_stations": 2,
    "telehealth_rooms": 0,
    "ai_triage_enabled": False,
    "mobile_units": 0,
    "robotic_assistants": 0
}

# Agent Limits
MAX_AGENTS = {
    "patients": 10000,
    "providers": 1000,
    "systems": 100
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "step_time_warning": 2.0,  # seconds
    "memory_warning": 2048,    # MB
    "agent_count_warning": 5000
}

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL = 30  # seconds
WS_MAX_CONNECTIONS = 100

# AI System Configuration
AI_PHONE_CONFIG = {
    "max_concurrent_calls": 50,
    "avg_call_duration": 3.5,  # minutes
    "cost_per_minute": 0.05,
    "human_agent_cost": 2.50
}

AI_NOTES_CONFIG = {
    "transcription_accuracy": 0.95,
    "generation_time": 2.0,  # minutes
    "manual_time": 18.0,     # minutes average
    "quality_threshold": 0.8
}

AI_PREAUTH_CONFIG = {
    "auto_approval_rate": 0.75,
    "review_time": 5.0,      # minutes
    "manual_time": 2880.0,   # minutes (2 days)
    "accuracy_rate": 0.94
}

# Error Codes
class ErrorCode(Enum):
    SIMULATION_NOT_FOUND = "SIMULATION_NOT_FOUND"
    INVALID_CONFIG = "INVALID_CONFIG"
    AGENT_LIMIT_EXCEEDED = "AGENT_LIMIT_EXCEEDED"
    PERFORMANCE_DEGRADED = "PERFORMANCE_DEGRADED"
    WEBSOCKET_ERROR = "WEBSOCKET_ERROR"
    
# Status Codes
class SimulationStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class AgentType(Enum):
    PATIENT = "patient"
    PROVIDER = "provider"
    AI_PHONE = "ai_phone"
    AI_NOTES = "ai_notes"
    AI_PREAUTH = "ai_preauth"
    SYSTEM = "system"

# Hospital Areas (for spatial modeling)
HOSPITAL_AREAS = [
    "reception",
    "waiting_room", 
    "triage",
    "examination_rooms",
    "vr_therapy_room",
    "telehealth_room",
    "pharmacy",
    "laboratory",
    "radiology",
    "surgery",
    "recovery",
    "discharge",
    "emergency",
    "administration"
]

# Innovation Types
INNOVATION_TYPES = {
    "vr_therapy": {
        "name": "VR Therapy Stations",
        "cost_per_unit": 15000,
        "patients_per_year": 200,
        "cost_savings_per_patient": 85
    },
    "telehealth": {
        "name": "Telehealth Capacity",
        "cost_per_unit": 5000,
        "patients_per_year": 500,
        "cost_savings_per_patient": 45
    },
    "ai_triage": {
        "name": "AI Triage System",
        "cost_per_unit": 50000,
        "patients_per_year": 5000,
        "cost_savings_per_patient": 12
    },
    "mobile_units": {
        "name": "Mobile Health Units",
        "cost_per_unit": 100000,
        "patients_per_year": 1000,
        "cost_savings_per_patient": 150
    }
}

# Metrics Configuration
METRICS_CONFIG = {
    "update_interval": 1.0,  # seconds
    "history_length": 100,   # data points
    "alert_thresholds": {
        "wait_time": 60,      # minutes
        "utilization": 0.9,   # 90%
        "satisfaction": 0.7   # 70%
    }
}