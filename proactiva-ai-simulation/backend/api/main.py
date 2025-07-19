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
import os

from simulation.models.modernized_hospital_model import VAHospitalModel
from simulation.insights.insight_engine import InsightEngine

# OpenAI for natural language processing
try:
    import openai
    OPENAI_AVAILABLE = bool(os.getenv('OPENAI_API_KEY'))
except ImportError:
    OPENAI_AVAILABLE = False

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

class NaturalLanguageQuery(BaseModel):
    """Natural language query request"""
    query: str = Field(..., min_length=1, max_length=500)
    include_context: bool = Field(default=True)
    voice_response: bool = Field(default=False)

class QueryResponse(BaseModel):
    """Response to natural language query"""
    query: str
    response: str
    metrics: Optional[Dict[str, Any]] = None
    insights: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None

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
                state = model.get_simulation_state()
                state['step'] = sim['step_count']
                state['simulation_time'] = model.time
                
                # Get agent samples for visualization (limited for performance)
                agent_samples = self._sample_agents(model, limit=50)
                
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
                
                # Control simulation speed - reduce frequency for better performance
                await asyncio.sleep(0.2)  # 5 updates per second for better performance
                
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
            
    def _sample_agents(self, model, limit: int = 50) -> List[Dict[str, Any]]:
        """Efficiently sample agents for visualization"""
        agents = []
        
        # Use pre-filtered lists for better performance
        patients = [a for a in model.schedule.agents if getattr(a, 'agent_type', '') == 'veteran_patient']
        providers = [a for a in model.schedule.agents if getattr(a, 'agent_type', '') == 'provider']
        
        # Calculate sample sizes
        total_agents = len(patients) + len(providers)
        if total_agents == 0:
            return []
            
        # Sample proportionally but with minimum guarantees
        patient_ratio = len(patients) / total_agents if total_agents > 0 else 0
        patient_sample_size = max(1, min(len(patients), int(limit * patient_ratio)))
        provider_sample_size = min(len(providers), limit - patient_sample_size)
        
        # Use step sampling for better distribution across the agent population
        patient_step = max(1, len(patients) // patient_sample_size) if patient_sample_size > 0 else 1
        provider_step = max(1, len(providers) // provider_sample_size) if provider_sample_size > 0 else 1
        
        sampled_patients = patients[::patient_step][:patient_sample_size]
        sampled_providers = providers[::provider_step][:provider_sample_size]
        
        # Convert to visualization format with animation data
        for agent in sampled_patients:
            agent_data = {
                'id': agent.unique_id,
                'type': 'patient',
                'state': agent.patient_state.value if hasattr(agent, 'patient_state') else 'unknown',
                'condition': agent.condition.value if hasattr(agent, 'condition') else 'unknown',
                'wait_time': getattr(agent, 'wait_time', 0),
                'satisfaction': getattr(agent, 'satisfaction', 50),
                'location': getattr(agent, 'current_location', 'unknown'),
                'urgency': getattr(agent, 'urgency', 5)
            }
            
            # Add animation data if available
            if hasattr(agent, 'get_animation_data'):
                animation_data = agent.get_animation_data()
                agent_data.update({
                    'position': animation_data.get('position', {'x': 0, 'y': 0}),
                    'target_position': animation_data.get('target_position'),
                    'is_moving': animation_data.get('is_moving', False),
                    'movement_progress': animation_data.get('movement_progress', 0),
                    'movement_trail': animation_data.get('movement_trail', [])
                })
            
            agents.append(agent_data)
            
        for agent in sampled_providers:
            agent_data = {
                'id': agent.unique_id,
                'type': 'provider',
                'state': 'busy' if not getattr(agent, 'is_available', True) else 'available',
                'specialty': agent.specialty.value if hasattr(agent, 'specialty') else 'general',
                'patients_seen': getattr(agent, 'patients_seen_today', 0),
                'stress_level': getattr(agent, 'stress_level', 0),
                'location': getattr(agent, 'current_location', 'treatment_area')
            }
            
            # Add animation data for providers if available
            if hasattr(agent, 'get_animation_data'):
                animation_data = agent.get_animation_data()
                agent_data.update({
                    'position': animation_data.get('position', {'x': 8, 'y': 10}),
                    'is_moving': animation_data.get('is_moving', False)
                })
            
            agents.append(agent_data)
            
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
            'config': sim['config'].model_dump() if hasattr(sim['config'], 'model_dump') else sim['config'].dict(),
            'current_state': model.get_simulation_state(),
            'insights_found': len(sim['insights']),
            'step_count': sim['step_count'],
            'created_at': sim['created_at'].isoformat()
        }
        
    def get_insights(self, sim_id: str) -> List[Dict[str, Any]]:
        """Get all insights for a simulation"""
        if sim_id not in self.simulations:
            raise ValueError(f"Simulation {sim_id} not found")
            
        return self.simulations[sim_id]['insights']
    
    async def process_natural_language_query(self, sim_id: str, query_data: NaturalLanguageQuery) -> QueryResponse:
        """Process natural language query about simulation"""
        if sim_id not in self.simulations:
            raise ValueError(f"Simulation {sim_id} not found")
        
        sim = self.simulations[sim_id]
        model = sim['model']
        
        # Get current simulation context
        current_state = model.get_simulation_state()
        insights = self.get_insights(sim_id)
        
        # Build context for AI
        context = {
            "simulation_status": sim['status'],
            "current_time": sim['step_count'],
            "total_patients": current_state.get('total_patients', 0),
            "total_providers": current_state.get('total_providers', 0),
            "current_metrics": current_state,
            "recent_insights": insights[-5:] if insights else [],
            "innovations_active": sim['config'].model_dump() if hasattr(sim['config'], 'model_dump') else sim['config'].dict()
        }
        
        # Process query with or without OpenAI
        if OPENAI_AVAILABLE and openai.api_key:
            response_text = await self._process_with_openai(query_data.query, context, query_data.voice_response)
        else:
            response_text = self._process_with_fallback(query_data.query, context)
        
        return QueryResponse(
            query=query_data.query,
            response=response_text,
            metrics=current_state if query_data.include_context else None,
            insights=insights[-3:] if query_data.include_context and insights else None,
            context=context if query_data.include_context else None
        )
    
    async def _process_with_openai(self, query: str, context: Dict[str, Any], voice_optimized: bool = False) -> str:
        """Process query using OpenAI GPT"""
        try:
            # Prepare system prompt
            system_prompt = """You are VAL (Virtual Assistant for Leaders), an AI assistant specialized in healthcare administration for the PROACTIVA simulation platform. 
            You help healthcare administrators understand their simulation results and make data-driven decisions. 
            Speak as VAL in a professional, concise, and helpful manner.
            
            Current simulation context:
            - Status: {status}
            - Current time step: {time}
            - Total patients: {patients}
            - Total providers: {providers}
            - Wait times: {wait_times}
            - Utilization rates: {utilization}
            
            Recent insights discovered: {insights}
            
            Active innovations: {innovations}
            
            Provide clear, actionable responses. If asked about specific metrics, reference the exact numbers.
            If voice_optimized is true, keep responses concise and conversational for text-to-speech.""".format(
                status=context['simulation_status'],
                time=context['current_time'],
                patients=context['total_patients'],
                providers=context['total_providers'],
                wait_times=context['current_metrics'].get('avg_wait_time', 'N/A'),
                utilization=context['current_metrics'].get('provider_utilization', 'N/A'),
                insights=[insight.get('description', '') for insight in context['recent_insights']],
                innovations=context['innovations_active']
            )
            
            # Make API call
            client = openai.AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=200 if voice_optimized else 400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._process_with_fallback(query, context)
    
    def _process_with_fallback(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback query processing without OpenAI"""
        query_lower = query.lower()
        
        # Extract key metrics for responses
        current_metrics = context['current_metrics']
        
        # Pattern matching for common queries
        if any(word in query_lower for word in ['wait', 'waiting', 'time']):
            wait_time = current_metrics.get('avg_wait_time', 0)
            return f"The current average wait time is {wait_time:.1f} minutes. {self._get_wait_time_context(wait_time)}"
        
        elif any(word in query_lower for word in ['patient', 'patients', 'how many']):
            total_patients = context['total_patients']
            in_queue = current_metrics.get('patients_in_queue', 0)
            return f"There are currently {total_patients} total patients in the system, with {in_queue} waiting in queue."
        
        elif any(word in query_lower for word in ['busy', 'busiest', 'department']):
            utilization = current_metrics.get('provider_utilization', 0)
            return f"Provider utilization is currently at {utilization:.1f}%. {self._get_utilization_context(utilization)}"
        
        elif any(word in query_lower for word in ['vr', 'virtual reality', 'therapy']):
            if context['innovations_active'].get('vr_stations', 0) > 0:
                return f"VR therapy is active with {context['innovations_active']['vr_stations']} stations. This innovation is showing promising results in patient satisfaction and treatment effectiveness."
            else:
                return "VR therapy is not currently active in this simulation. Consider adding VR stations to improve patient outcomes."
        
        elif any(word in query_lower for word in ['insight', 'insights', 'recommendation']):
            insights = context['recent_insights']
            if insights:
                latest = insights[-1]
                return f"Latest insight: {latest.get('description', 'Analysis in progress')}. We've discovered {len(insights)} total insights so far."
            else:
                return "No specific insights have been generated yet. The simulation is still gathering data for analysis."
        
        elif any(word in query_lower for word in ['telehealth', 'telemedicine', 'remote']):
            telehealth_rooms = context['innovations_active'].get('telehealth_rooms', 0)
            if telehealth_rooms > 0:
                return f"Telehealth is active with {telehealth_rooms} virtual consultation rooms, helping reduce in-person visit loads."
            else:
                return "Telehealth is not currently implemented. Adding telehealth capabilities could reduce facility congestion."
        
        elif any(word in query_lower for word in ['status', 'overview', 'summary']):
            return f"Simulation overview: {context['total_patients']} patients, {context['total_providers']} providers. Average wait time: {current_metrics.get('avg_wait_time', 0):.1f} minutes. Status: {context['simulation_status']}."
        
        elif any(word in query_lower for word in ['add']) and any(word in query_lower for word in ['vr', 'headset']):
            return "I can help you add VR headsets to improve patient care. Each VR station typically reduces wait times by 2.5 minutes and improves satisfaction by 3%. Would you like me to run a simulation with additional VR stations?"
        
        elif any(word in query_lower for word in ['run', 'start']) and any(word in query_lower for word in ['simulation']):
            return "I can start a new simulation for you. You can specify parameters like 'run simulation with 200 patients and 15 providers' and I'll configure it automatically."
        
        else:
            return f"Hi, I'm VAL. I can help you understand your simulation data. Current status: {context['total_patients']} patients, {current_metrics.get('avg_wait_time', 0):.1f} min average wait time. Try asking about wait times, patient counts, or active innovations."
    
    def _get_wait_time_context(self, wait_time: float) -> str:
        """Provide context about wait times"""
        if wait_time < 15:
            return "This is excellent - well below the 30-minute VA standard."
        elif wait_time < 30:
            return "This meets VA standards but could be improved."
        else:
            return "This exceeds recommended wait times. Consider optimizing staffing or implementing innovations."
    
    def _get_utilization_context(self, utilization: float) -> str:
        """Provide context about provider utilization"""
        if utilization < 60:
            return "Providers have capacity for additional patients."
        elif utilization < 80:
            return "Good utilization levels with manageable workload."
        else:
            return "High utilization - consider adding staff or optimizing workflows."

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

@app.post("/api/v2/simulations/{sim_id}/query", response_model=QueryResponse)
async def process_natural_language_query(sim_id: str, query: NaturalLanguageQuery):
    """Process natural language query about simulation"""
    try:
        response = await sim_manager.process_natural_language_query(sim_id, query)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Query processing failed")

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