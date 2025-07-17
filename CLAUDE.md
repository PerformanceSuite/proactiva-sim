# CLAUDE.md - PROACTIVA Phase 2 AI Simulation Platform

## Overview

This document serves as the development guide for Phase 2 of the PROACTIVA AI Healthcare Simulation Platform. The complete implementation involves building a sophisticated agent-based modeling system with thousands of AI agents, real-time visualization, and intelligent insights.

## Quick Navigation

### 📋 Project Documentation
- **[Complete Project Overview](docs/PROJECT_OVERVIEW.md)** - Comprehensive project description and business value
- **[Project Vision](docs/architecture/project-vision.md)** - Original vision and development phases
- **[Technical Architecture](docs/architecture/tech-stack.md)** - Technology stack and implementation approach

### 🚀 Setup & Development
- **[Phase 1 Setup Guide](docs/setup/phase1-setup.md)** - Frontend dashboard setup instructions
- **[Backend API Documentation](docs/api/backend-api.md)** - Complete REST API and WebSocket reference
- **[Production Deployment](docs/deployment/production-setup.md)** - Docker deployment and configuration

### 🧠 AI Simulation System
- **[Agent Framework](docs/simulation/agent-framework.md)** - Agent-based modeling architecture
- **[Frontend Components](docs/frontend/components-overview.md)** - React component library and state management
- **[Project Intelligence System](docs/features/project-intelligence-system.md)** - AI-powered project optimization and resource management

## Core Implementation Goals

### Phase 2 Objectives
1. **Agent-Based Modeling** - Create thousands of autonomous AI agents representing patients, providers, and systems
2. **Real-Time Simulation** - Live visualization of healthcare operations with WebSocket updates
3. **AI Insight Engine** - Pattern recognition and optimization recommendations
4. **Natural Language Interface** - Query simulation data using plain English
5. **3D Visualization** - Immersive hospital environment with Three.js

### Key Features Built
- ✅ **FastAPI Backend** - High-performance API with WebSocket support
- ✅ **Mesa Agent Framework** - Sophisticated agent-based modeling system
- ✅ **Real-Time Visualization** - Live updates of agent behavior and metrics
- ✅ **AI Insight Detection** - Pattern recognition and bottleneck identification
- ✅ **Natural Language Queries** - GPT-powered simulation interrogation
- ✅ **3D Hospital Models** - Three.js-based immersive visualizations

## Technical Architecture

### Backend Stack
```python
# Core Dependencies
fastapi==0.104.1          # High-performance API framework
mesa==2.1.1              # Agent-based modeling
uvicorn==0.24.0          # ASGI server
websockets==12.0         # Real-time communication
pandas==2.0.3            # Data processing
numpy==1.24.3            # Numerical computing
scikit-learn==1.3.0      # Machine learning
openai==1.3.0            # Natural language processing
```

### Frontend Stack
```javascript
// Core Dependencies
react: "^18.2.0"         // UI framework
three: "^0.155.0"        // 3D visualization
recharts: "^2.8.0"       // Data visualization
lucide-react: "^0.263.1" // Icons
tailwindcss: "^3.3.0"    // Styling
```

### Agent Types
- **VeteranPatientAgent** - Individual veterans with realistic healthcare-seeking behaviors
- **ProviderAgent** - Healthcare professionals with specialties, schedules, and fatigue modeling
- **SystemAgent** - Automated systems like AI triage and scheduling algorithms

## Implementation Status

### ✅ Completed Components
- **Backend API** - Complete FastAPI implementation with all endpoints
- **Agent Framework** - Patient and provider agents with realistic behaviors
- **Simulation Engine** - Mesa-based hospital model with innovations
- **WebSocket System** - Real-time communication between frontend and backend
- **Insight Engine** - AI-powered pattern detection and recommendations
- **Frontend Components** - React components for visualization and interaction
- **3D Visualization** - Three.js-based hospital environment
- **Natural Language Interface** - GPT-powered query system

### 🚧 In Progress
- **Performance Optimization** - Scaling to 10,000+ agents
- **Machine Learning Integration** - Predictive analytics and optimization
- **Advanced Visualizations** - Flow patterns and heatmaps
- **Testing Suite** - Comprehensive unit and integration tests

### 🔮 Future Enhancements
- **Multi-facility Support** - Simulate healthcare networks
- **Real-time Data Integration** - Connect to actual healthcare systems
- **Enterprise Features** - Authentication, authorization, and audit logging
- **Mobile Applications** - Native mobile interfaces
- **Project Intelligence System** - AI-powered organizational optimization

## Development Workflow

### 1. Setup Development Environment
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
```

### 2. Run Development Servers
```bash
# Terminal 1 - Backend
cd backend
python run_server.py

# Terminal 2 - Frontend
cd frontend
npm start
```

### 3. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/{sim_id}

## Key Implementation Files

### Backend Core
- `backend/api/main.py` - FastAPI application and WebSocket handling
- `backend/simulation/models/hospital_model.py` - Main simulation model
- `backend/simulation/agents/patient_agent.py` - Veteran patient behaviors
- `backend/simulation/agents/provider_agent.py` - Healthcare provider agents
- `backend/simulation/insights/insight_engine.py` - AI pattern detection

### Frontend Core
- `frontend/src/components/AISimulation/AISimulation.jsx` - Main simulation container
- `frontend/src/components/AISimulation/MetricsDisplay.jsx` - Real-time metrics
- `frontend/src/components/AISimulation/SimulationVisualizer.jsx` - 2D visualization
- `frontend/src/components/AISimulation/Visualization3D.jsx` - 3D hospital model
- `frontend/src/components/AISimulation/NaturalLanguageQuery.jsx` - Query interface

## Business Value

### For Healthcare Administrators
- **Risk Mitigation** - Test innovations before expensive implementations
- **Resource Optimization** - Identify staffing and capacity improvements
- **Evidence-Based Decisions** - Data-driven insights for strategic planning
- **Cost Reduction** - Optimize operations to reduce waste and improve efficiency

### For Clinical Staff
- **Workflow Optimization** - Identify pain points in daily operations
- **Technology Adoption** - Understand impact of new tools and systems
- **Patient Experience** - Improve satisfaction through better care delivery
- **Burnout Prevention** - Optimize scheduling and workload distribution

### For Patients
- **Reduced Wait Times** - Optimized patient flow and resource allocation
- **Better Care Access** - Improved scheduling and availability
- **Enhanced Experience** - Streamlined processes and reduced friction
- **Innovative Treatments** - Access to cutting-edge therapeutic modalities

## Support & Resources

### Documentation
- **Complete Implementation Guide** - All code and configuration files provided
- **API Reference** - Comprehensive REST and WebSocket documentation
- **Component Library** - React component specifications and usage
- **Deployment Guide** - Production setup with Docker and monitoring

### Getting Help
- **GitHub Issues** - Report bugs and request features
- **Documentation** - Comprehensive guides in `/docs` directory
- **Code Examples** - Complete implementation examples provided
- **Community** - Developer community and discussions

---

**This is a living document that will be updated as the project evolves. For the complete implementation details, please refer to the individual documentation files linked above.**

*Last updated: January 2024*