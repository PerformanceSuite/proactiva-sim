# Backend API Documentation

## Overview

The PROACTIVA AI Simulation backend is built with FastAPI and provides REST endpoints and WebSocket connections for real-time simulation management.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication is required for development. Production will implement JWT tokens.

## Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API server.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "active_simulations": 3
}
```

### Root Endpoint
```
GET /
```
Returns application information and available endpoints.

### Simulation Management

#### Create Simulation
```
POST /api/v2/simulations
```

**Request Body:**
```json
{
  "name": "VA Hospital Simulation",
  "num_patients": 100,
  "num_providers": 20,
  "vr_stations": 5,
  "telehealth_rooms": 3,
  "ai_triage_enabled": true,
  "mobile_units": 2,
  "robotic_assistants": 1
}
```

**Response:**
```json
{
  "simulation_id": "sim_abc123",
  "status": "created",
  "config": { ... },
  "websocket_url": "ws://localhost:8000/ws/sim_abc123"
}
```

#### List Simulations
```
GET /api/v2/simulations
```

**Response:**
```json
{
  "simulations": [
    {
      "simulation_id": "sim_abc123",
      "name": "VA Hospital Simulation",
      "status": "running",
      "created_at": "2024-01-01T12:00:00Z",
      "step_count": 1250
    }
  ]
}
```

#### Get Simulation Details
```
GET /api/v2/simulations/{sim_id}
```

**Response:**
```json
{
  "simulation_id": "sim_abc123",
  "name": "VA Hospital Simulation",
  "status": "running",
  "config": { ... },
  "current_state": {
    "patients_waiting": 25,
    "average_wait_time": 18.5,
    "provider_utilization": 0.78
  },
  "insights_found": 12,
  "step_count": 1250
}
```

#### Start Simulation
```
POST /api/v2/simulations/{sim_id}/start
```

**Response:**
```json
{
  "message": "Simulation started",
  "simulation_id": "sim_abc123",
  "websocket_url": "ws://localhost:8000/ws/sim_abc123"
}
```

#### Stop Simulation
```
POST /api/v2/simulations/{sim_id}/stop
```

**Response:**
```json
{
  "message": "Simulation stopped",
  "simulation_id": "sim_abc123"
}
```

#### Get Simulation Insights
```
GET /api/v2/simulations/{sim_id}/insights
```

**Response:**
```json
{
  "simulation_id": "sim_abc123",
  "total_insights": 5,
  "insights": [
    {
      "id": "insight_xyz789",
      "type": "wait_time_crisis",
      "severity": "high",
      "title": "Mental Health Wait Times at Critical Level",
      "description": "Mental health patients experiencing 45 minute average wait times",
      "recommendation": "Immediate intervention needed. VR therapy expansion could reduce waits by 30%",
      "confidence": 0.88
    }
  ]
}
```

#### Natural Language Query
```
POST /api/v2/simulations/{sim_id}/query
```

**Request Body:**
```json
{
  "text": "What if we had 20% less nurses during the day shift?"
}
```

**Response:**
```json
{
  "query": "What if we had 20% less nurses during the day shift?",
  "intent": "what_if",
  "response": "Based on your question... wait times would increase by 40% to approximately 39 minutes...",
  "confidence": 0.85,
  "scenario": {
    "staff_reduction": 0.2
  }
}
```

## WebSocket Connection

### Connection
```
ws://localhost:8000/ws/{sim_id}
```

### Message Types

#### Initial State
Sent when WebSocket connects:
```json
{
  "type": "initial_state",
  "data": {
    "simulation_id": "sim_abc123",
    "current_state": { ... }
  }
}
```

#### Simulation Update
Sent every simulation step:
```json
{
  "type": "simulation_update",
  "simulation_id": "sim_abc123",
  "timestamp": "2024-01-01T12:00:00Z",
  "state": {
    "patients_waiting": 25,
    "average_wait_time": 18.5,
    "provider_utilization": 0.78
  },
  "agents": [
    {
      "id": "patient_1",
      "type": "patient",
      "state": "waiting",
      "condition": "routine",
      "wait_time": 15,
      "satisfaction": 65
    }
  ],
  "new_insights": [
    {
      "type": "bottleneck_detected",
      "title": "Triage Bottleneck Detected",
      "description": "Triage station experiencing 50% above normal volume"
    }
  ]
}
```

#### Simulation Completed
```json
{
  "type": "simulation_completed",
  "simulation_id": "sim_abc123",
  "total_steps": 5000,
  "final_metrics": { ... }
}
```

#### Simulation Error
```json
{
  "type": "simulation_error",
  "simulation_id": "sim_abc123",
  "error": "Error message description"
}
```

## Error Handling

All endpoints follow standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

Error responses include details:
```json
{
  "detail": "Simulation sim_abc123 not found"
}
```

## Rate Limiting

Currently no rate limiting in development. Production will implement:
- 100 requests per minute per IP
- 10 simulation creations per hour per IP
- WebSocket connections limited to 5 per simulation

## Development

### Running the Server
```bash
cd backend
python run_server.py
```

### API Documentation
Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`