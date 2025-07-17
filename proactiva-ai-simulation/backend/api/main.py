"""
PROACTIVA AI Simulation - FastAPI Backend
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import asyncio
import json
import uuid
from datetime import datetime
import logging

from simulation.models.hospital_model import VAHospitalModel
from simulation.insights.insight_engine import InsightEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PROACTIVA AI Simulation API",
    description="Agent-based healthcare simulation platform",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SimulationConfig(BaseModel):
    """Configuration for creating a new simulation"""
    name: str = Field(default="VA Hospital Simulation")
    num_patients: int = Field(default=100, ge=10, le=10000)
    num_providers: int = Field(default=20, ge=5, le=200)
    vr_stations: int = Field(default=0, ge=0, le=50)
    telehealth_rooms: int = Field(default=0, ge=0, le=30)
    ai_triage_enabled: bool = Field(default=False)
    mobile_units: int = Field(default=0, ge=0, le=10)
    robotic_assistants: int = Field(default=0, ge=0, le=20)
    
class SimulationResponse(BaseModel):
    """Response when creating a simulation"""
    simulation_id: str
    status: str
    config: SimulationConfig
    websocket_url: str
    
class SimulationState(BaseModel):
    """Current state of a simulation"""
    simulation_id: str
    status: str
    current_time: int
    metrics: Dict[str, float]
    insights_found: int
    agents_active: int

# Simulation Manager
class SimulationManager:
    """Manages multiple concurrent simulations"""
    
    def __init__(self):
        self.simulations: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, List[WebSocket]] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
    async def create_simulation(self, config: SimulationConfig) -> str:
        """Create new simulation instance"""
        sim_id = f"sim_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Creating simulation {sim_id} with config: {config}")
        
        # Create Mesa model with innovations
        innovations = {
            'vr_stations': config.vr_stations,
            'telehealth_rooms': config.telehealth_rooms,
            'ai_triage_enabled': config.ai_triage_enabled,
            'mobile_units': config.mobile_units,
            'robotic_assistants': config.robotic_assistants
        }
        
        model = VAHospitalModel(
            num_initial_patients=config.num_patients,
            num_providers=config.num_providers,
            innovations=innovations
        )
        
        # Create insight engine
        insight_engine = InsightEngine(model)
        
        # Store simulation
        self.simulations[sim_id] = {
            'id': sim_id,
            'name': config.name,
            'model': model,
            'config': config,
            'status': 'created',
            'insight_engine': insight_engine,
            'created_at': datetime.now(),
            'insights': [],
            'step_count': 0
        }
        
        logger.info(f"Simulation {sim_id} created successfully")
        return sim_id
        
    async def start_simulation(self, sim_id: str):
        """Start running a simulation"""
        if sim_id not in self.simulations:
            raise ValueError(f"Simulation {sim_id} not found")
            
        sim = self.simulations[sim_id]
        sim['status'] = 'running'
        
        # Create and store the task
        task = asyncio.create_task(self._run_simulation_loop(sim_id))
        self.running_tasks[sim_id] = task
        
        logger.info(f"Simulation {sim_id} started")
        
    async def stop_simulation(self, sim_id: str):
        """Stop a running simulation"""
        if sim_id in self.simulations:
            self.simulations[sim_id]['status'] = 'stopped'
            
        # Cancel the running task
        if sim_id in self.running_tasks:
            self.running_tasks[sim_id].cancel()
            del self.running_tasks[sim_id]
            
        logger.info(f"Simulation {sim_id} stopped")
        
    async def _run_simulation_loop(self, sim_id: str):
        """Main simulation loop"""
        sim = self.simulations[sim_id]
        model = sim['model']
        insight_engine = sim['insight_engine']
        
        try:
            while sim['status'] == 'running':
                # Step the model
                model.step()
                sim['step_count'] += 1
                
                # Get current state
                state = model.get_current_state()
                state['step'] = sim['step_count']
                state['simulation_time'] = model.time
                
                # Get agent samples for visualization
                agent_samples = self._sample_agents(model, limit=200)
                
                # Check for insights every 50 steps
                new_insights = []
                if sim['step_count'] % 50 == 0:
                    new_insights = insight_engine.detect_insights()
                    if new_insights:
                        sim['insights'].extend(new_insights)
                        logger.info(f"Simulation {sim_id}: {len(new_insights)} new insights discovered")
                
                # Prepare update message
                update = {
                    'type': 'simulation_update',
                    'simulation_id': sim_id,
                    'timestamp': datetime.now().isoformat(),
                    'state': state,
                    'agents': agent_samples,
                    'new_insights': new_insights,
                    'total_insights': len(sim['insights'])
                }
                
                # Broadcast to all connected clients
                await self._broadcast_update(sim_id, update)
                
                # Control simulation speed
                await asyncio.sleep(0.1)  # 10 updates per second
                
                # Auto-stop after certain steps for demo
                if sim['step_count'] >= 5000:  # About 8 hours simulated
                    sim['status'] = 'completed'
                    await self._broadcast_update(sim_id, {
                        'type': 'simulation_completed',
                        'simulation_id': sim_id,
                        'total_steps': sim['step_count'],
                        'final_metrics': state
                    })
                    
        except asyncio.CancelledError:
            logger.info(f"Simulation {sim_id} loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in simulation {sim_id}: {str(e)}")
            sim['status'] = 'error'
            await self._broadcast_update(sim_id, {
                'type': 'simulation_error',
                'simulation_id': sim_id,
                'error': str(e)
            })
            
    def _sample_agents(self, model, limit: int = 100) -> List[Dict[str, Any]]:
        """Sample agents for visualization"""
        agents = []
        
        # Get a diverse sample of agents
        all_agents = list(model.agents)
        sample_size = min(len(all_agents), limit)
        
        # Try to get a mix of agent types
        patients = [a for a in all_agents if a.agent_type == 'veteran_patient']
        providers = [a for a in all_agents if a.agent_type == 'provider']
        
        # Sample proportionally
        patient_sample_size = int(sample_size * 0.8)
        provider_sample_size = sample_size - patient_sample_size
        
        sampled_patients = patients[:patient_sample_size]
        sampled_providers = providers[:provider_sample_size]
        
        # Convert to visualization format
        for agent in sampled_patients:
            agents.append({
                'id': agent.unique_id,
                'type': 'patient',
                'state': agent.patient_state.value if hasattr(agent, 'patient_state') else 'unknown',
                'condition': agent.condition.value if hasattr(agent, 'condition') else 'unknown',
                'wait_time': getattr(agent, 'wait_time', 0),
                'satisfaction': getattr(agent, 'satisfaction', 50),
                'location': getattr(agent, 'current_location', 'unknown'),
                'urgency': getattr(agent, 'urgency', 5)
            })
            
        for agent in sampled_providers:
            agents.append({
                'id': agent.unique_id,
                'type': 'provider',
                'state': 'busy' if not agent.is_available else 'available',
                'specialty': agent.specialty.value if hasattr(agent, 'specialty') else 'general',
                'patients_seen': getattr(agent, 'patients_seen_today', 0),
                'stress_level': getattr(agent, 'stress_level', 0),
                'location': 'treatment_area'
            })
            
        return agents
        
    async def _broadcast_update(self, sim_id: str, update: Dict[str, Any]):
        """Broadcast update to all connected WebSocket clients"""
        if sim_id in self.connections:
            disconnected = []
            
            for websocket in self.connections[sim_id]:
                try:
                    await websocket.send_json(update)
                except Exception:
                    disconnected.append(websocket)
                    
            # Remove disconnected clients
            for ws in disconnected:
                self.connections[sim_id].remove(ws)
                
    def get_simulation_state(self, sim_id: str) -> Dict[str, Any]:
        """Get current simulation state"""
        if sim_id not in self.simulations:
            raise ValueError(f"Simulation {sim_id} not found")
            
        sim = self.simulations[sim_id]
        model = sim['model']
        
        return {
            'simulation_id': sim_id,
            'name': sim['name'],
            'status': sim['status'],
            'config': sim['config'].dict(),
            'current_state': model.get_current_state(),
            'insights_found': len(sim['insights']),
            'step_count': sim['step_count'],
            'created_at': sim['created_at'].isoformat()
        }
        
    def get_insights(self, sim_id: str) -> List[Dict[str, Any]]:
        """Get all insights for a simulation"""
        if sim_id not in self.simulations:
            raise ValueError(f"Simulation {sim_id} not found")
            
        return self.simulations[sim_id]['insights']

# Initialize manager
sim_manager = SimulationManager()

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "application": "PROACTIVA AI Simulation API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "create_simulation": "/api/v2/simulations",
            "get_simulation": "/api/v2/simulations/{sim_id}",
            "websocket": "/ws/{sim_id}",
            "api_docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_simulations": len(sim_manager.simulations)
    }

@app.post("/api/v2/simulations", response_model=SimulationResponse)
async def create_simulation(config: SimulationConfig):
    """Create a new simulation"""
    try:
        sim_id = await sim_manager.create_simulation(config)
        
        return SimulationResponse(
            simulation_id=sim_id,
            status="created",
            config=config,
            websocket_url=f"ws://localhost:8000/ws/{sim_id}"
        )
    except Exception as e:
        logger.error(f"Error creating simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/simulations")
async def list_simulations():
    """List all simulations"""
    simulations = []
    
    for sim_id, sim in sim_manager.simulations.items():
        simulations.append({
            'simulation_id': sim_id,
            'name': sim['name'],
            'status': sim['status'],
            'created_at': sim['created_at'].isoformat(),
            'step_count': sim['step_count']
        })
        
    return {"simulations": simulations}

@app.get("/api/v2/simulations/{sim_id}")
async def get_simulation(sim_id: str):
    """Get simulation details"""
    try:
        return sim_manager.get_simulation_state(sim_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/v2/simulations/{sim_id}/start")
async def start_simulation(sim_id: str):
    """Start a simulation"""
    try:
        await sim_manager.start_simulation(sim_id)
        return {
            "message": "Simulation started",
            "simulation_id": sim_id,
            "websocket_url": f"ws://localhost:8000/ws/{sim_id}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/v2/simulations/{sim_id}/stop")
async def stop_simulation(sim_id: str):
    """Stop a running simulation"""
    try:
        await sim_manager.stop_simulation(sim_id)
        return {"message": "Simulation stopped", "simulation_id": sim_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/v2/simulations/{sim_id}/insights")
async def get_simulation_insights(sim_id: str):
    """Get insights discovered by the simulation"""
    try:
        insights = sim_manager.get_insights(sim_id)
        return {
            "simulation_id": sim_id,
            "total_insights": len(insights),
            "insights": insights
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws/{sim_id}")
async def websocket_endpoint(websocket: WebSocket, sim_id: str):
    """WebSocket connection for real-time simulation updates"""
    await websocket.accept()
    
    # Validate simulation exists
    if sim_id not in sim_manager.simulations:
        await websocket.send_json({
            "type": "error",
            "message": f"Simulation {sim_id} not found"
        })
        await websocket.close(code=4004)
        return
        
    # Add to connections
    if sim_id not in sim_manager.connections:
        sim_manager.connections[sim_id] = []
    sim_manager.connections[sim_id].append(websocket)
    
    logger.info(f"WebSocket connected for simulation {sim_id}")
    
    # Send initial state
    try:
        initial_state = sim_manager.get_simulation_state(sim_id)
        await websocket.send_json({
            "type": "initial_state",
            "data": initial_state
        })
    except Exception as e:
        logger.error(f"Error sending initial state: {str(e)}")
    
    try:
        # Keep connection alive
        while True:
            # Wait for any message from client (ping/pong)
            data = await websocket.receive_text()
            
            # Handle client commands if needed
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        # Remove from connections
        if sim_id in sim_manager.connections:
            sim_manager.connections[sim_id].remove(websocket)
        logger.info(f"WebSocket disconnected for simulation {sim_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if sim_id in sim_manager.connections:
            sim_manager.connections[sim_id].remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)