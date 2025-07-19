"""
Pydantic response models for consistent API responses
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Base response model
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Error response model
class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Simulation models
class SimulationConfig(BaseModel):
    name: str = "VA Hospital Simulation"
    num_patients: int = Field(ge=1, le=10000)
    num_providers: int = Field(ge=1, le=1000)
    vr_stations: int = Field(ge=0, le=20)
    telehealth_rooms: int = Field(ge=0, le=50)
    ai_triage_enabled: bool = False
    mobile_units: int = Field(ge=0, le=10)
    robotic_assistants: int = Field(ge=0, le=100)

class SimulationStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class SimulationResponse(BaseResponse):
    simulation_id: str
    status: SimulationStatus
    config: SimulationConfig
    websocket_url: str

class SimulationListResponse(BaseResponse):
    simulations: List[Dict[str, Any]]

# Metrics models
class MetricsData(BaseModel):
    patients_waiting: int = 0
    avg_wait_time: float = 0.0
    provider_utilization: float = 0.0
    patient_satisfaction: float = 0.0
    throughput: int = 0
    cost_savings: float = 0.0
    
class MetricsResponse(BaseResponse):
    metrics: MetricsData
    simulation_id: str

# Agent models
class AgentData(BaseModel):
    agent_id: str
    agent_type: str
    position: Optional[Dict[str, float]] = None
    status: str
    metadata: Dict[str, Any] = {}

class AgentListResponse(BaseResponse):
    agents: List[AgentData]
    total_count: int

# Insight models
class InsightData(BaseModel):
    insight_id: str
    type: str
    title: str
    description: str
    priority: str
    confidence: float = Field(ge=0.0, le=1.0)
    actionable: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}

class InsightResponse(BaseResponse):
    insights: List[InsightData]

# AI System models
class AIPhoneMetrics(BaseModel):
    active_calls: int = 0
    total_calls: int = 0
    success_rate: float = 0.95
    cost_savings_per_minute: float = 2.45
    languages_supported: List[str] = ["en", "es", "zh", "vi", "tl"]

class AINotesMetrics(BaseModel):
    active_encounters: int = 0
    total_notes: int = 0
    quality_score: float = 0.92
    time_saved_hours: float = 0.0
    transcription_accuracy: float = 0.95

class AIPreAuthMetrics(BaseModel):
    pending_requests: int = 0
    total_requests: int = 0
    approval_rate: float = 0.78
    avg_processing_time: float = 5.0
    cost_savings: float = 0.0

class AISystemsResponse(BaseResponse):
    ai_phone: AIPhoneMetrics
    ai_notes: AINotesMetrics
    ai_preauth: AIPreAuthMetrics

# Query models
class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseResponse):
    query: str
    response: str
    insights: Optional[List[InsightData]] = None
    metrics: Optional[Dict[str, Any]] = None

# Performance models
class PerformanceMetrics(BaseModel):
    step_time: float = 0.0
    memory_usage_mb: float = 0.0
    agent_count: int = 0
    fps: float = 0.0
    performance_score: float = 100.0

class PerformanceResponse(BaseResponse):
    performance: PerformanceMetrics
    warnings: List[str] = []

# WebSocket models
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

# Validation helpers
def validate_simulation_config(config: Dict[str, Any]) -> SimulationConfig:
    """Validate and return simulation configuration"""
    try:
        return SimulationConfig(**config)
    except Exception as e:
        raise ValueError(f"Invalid simulation configuration: {str(e)}")

def create_error_response(message: str, error_code: str = None, details: Dict[str, Any] = None) -> ErrorResponse:
    """Create standardized error response"""
    return ErrorResponse(
        message=message,
        error_code=error_code,
        details=details
    )

def create_success_response(data: Dict[str, Any] = None, message: str = None) -> BaseResponse:
    """Create standardized success response"""
    response_data = {"success": True}
    if message:
        response_data["message"] = message
    if data:
        response_data.update(data)
    return BaseResponse(**response_data)