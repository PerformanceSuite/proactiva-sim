# PROACTIVA Documentation

Welcome to the comprehensive documentation for the PROACTIVA AI Healthcare Simulation Platform. This documentation covers all aspects of the project from high-level architecture to detailed implementation guides.

## 📋 Quick Links

### Getting Started
- **[Project Overview](PROJECT_OVERVIEW.md)** - Complete project description and business value
- **[README](../README.md)** - Quick start guide and project summary
- **[Phase 1 Setup](setup/phase1-setup.md)** - Frontend dashboard setup instructions

### Architecture & Design
- **[Project Vision](architecture/project-vision.md)** - Original vision and development phases
- **[Technical Architecture](architecture/tech-stack.md)** - Technology stack and implementation approach
- **[Original Vision](architecture/original-claude-vision.md)** - Historical project vision document

### Development Guides
- **[Backend API](api/backend-api.md)** - Complete REST API and WebSocket reference
- **[Agent Framework](simulation/agent-framework.md)** - Agent-based modeling architecture
- **[Frontend Components](frontend/components-overview.md)** - React component library and state management

### Deployment & Operations
- **[Production Setup](deployment/production-setup.md)** - Docker deployment and configuration
- **[Monitoring](deployment/monitoring.md)** - Observability and performance monitoring (coming soon)
- **[Security](deployment/security.md)** - Security best practices and compliance (coming soon)

## 📁 Documentation Structure

```
docs/
├── README.md                          # This file
├── PROJECT_OVERVIEW.md               # Complete project overview
├── architecture/                     # System architecture
│   ├── project-vision.md            # Vision and development phases
│   ├── tech-stack.md                # Technology choices
│   └── original-claude-vision.md    # Historical vision document
├── setup/                            # Setup and installation
│   └── phase1-setup.md              # Phase 1 setup guide
├── api/                              # API documentation
│   └── backend-api.md               # REST API and WebSocket docs
├── simulation/                       # Simulation system
│   └── agent-framework.md           # Agent-based modeling
├── frontend/                         # Frontend documentation
│   └── components-overview.md       # React components
├── deployment/                       # Deployment guides
│   └── production-setup.md          # Production deployment
└── guides/                           # User guides (coming soon)
```

## 🎯 Documentation by Role

### For Healthcare Administrators
- **[Project Overview](PROJECT_OVERVIEW.md)** - Business value and use cases
- **[Project Vision](architecture/project-vision.md)** - VA-specific considerations
- **[Production Setup](deployment/production-setup.md)** - Enterprise deployment

### For Developers
- **[Backend API](api/backend-api.md)** - API endpoints and WebSocket communication
- **[Agent Framework](simulation/agent-framework.md)** - Agent-based modeling system
- **[Frontend Components](frontend/components-overview.md)** - React component library
- **[Project Intelligence Integration](frontend/project-intelligence-integration.md)** - Dashboard integration guide
- **[Tech Stack](architecture/tech-stack.md)** - Implementation details

### For DevOps Engineers
- **[Production Setup](deployment/production-setup.md)** - Docker and infrastructure
- **[Monitoring](deployment/monitoring.md)** - Observability setup (coming soon)
- **[Security](deployment/security.md)** - Security configuration (coming soon)

### For Researchers
- **[Agent Framework](simulation/agent-framework.md)** - Simulation methodology
- **[Project Vision](architecture/project-vision.md)** - Research applications
- **[Backend API](api/backend-api.md)** - Data access and analysis

## 🔍 Quick Reference

### Key Concepts
- **Agent-Based Modeling** - Simulation using autonomous agents
- **Digital Twin** - Virtual representation of physical healthcare facility
- **Innovation Testing** - Evaluate new technologies before implementation
- **Real-Time Visualization** - Live updates of simulation state
- **AI Insights** - Pattern recognition and optimization recommendations

### Technology Stack
- **Backend**: FastAPI, Python, Mesa, PostgreSQL, Redis
- **Frontend**: React, TypeScript, Three.js, Tailwind CSS
- **AI/ML**: OpenAI GPT, Scikit-learn, Pandas, NumPy
- **Deployment**: Docker, Nginx, Prometheus, Grafana

### API Endpoints
- `GET /health` - Health check
- `POST /api/v2/simulations` - Create simulation
- `GET /api/v2/simulations/{sim_id}` - Get simulation details
- `POST /api/v2/simulations/{sim_id}/start` - Start simulation
- `POST /api/v2/simulations/{sim_id}/stop` - Stop simulation
- `WS /ws/{sim_id}` - WebSocket connection

## 🚀 Development Phases

### Phase 1: Interactive Dashboard ✅
- React-based innovation testing dashboard
- Basic KPI visualization and calculations
- Scenario management and ROI analysis
- 3D facility visualization

### Phase 2: AI Agent Simulation 🚧
- Agent-based modeling with Mesa framework
- Real-time simulation with WebSocket updates
- AI-powered insight detection
- Natural language query interface
- 3D visualization with Three.js

### Phase 3: Production Platform 🔮
- Enterprise authentication and authorization
- Real-time data integration
- Multi-facility support
- Advanced analytics and reporting
- Mobile applications
- Project Intelligence System

## 📊 Key Metrics

### Performance Targets
- **10,000+ agents** with real-time visualization
- **Sub-second response** times for user interactions
- **99.9% uptime** for production deployments
- **50+ concurrent simulations** support

### Business Impact
- **30% reduction** in wait times through optimization
- **25% improvement** in patient satisfaction scores
- **40% faster** innovation deployment cycles
- **$500K+ annual savings** through efficiency gains

## 🛠️ Contributing

### Documentation Updates
1. Edit relevant `.md` files in the `/docs` directory
2. Follow the existing structure and formatting
3. Update this README if adding new sections
4. Test all links and code examples

### Code Examples
- All code examples should be complete and functional
- Include necessary imports and dependencies
- Provide context and explanation for complex examples
- Test examples before including in documentation

### Review Process
- All documentation changes should be reviewed
- Verify technical accuracy and completeness
- Ensure consistency with existing documentation
- Check for broken links and formatting issues

## 📞 Support

### Getting Help
- **GitHub Issues** - Report bugs and request features
- **Documentation** - Comprehensive guides in this directory
- **Code Examples** - Complete implementation examples
- **Community** - Developer community and discussions

### Contact Information
- **Project Lead** - Daniel Connolly
- **Email** - support@proactiva.com
- **Repository** - https://github.com/company/proactiva
- **Demo** - https://demo.proactiva.com

---

**Need help finding something?** Use the search functionality in your IDE or browser, or check the [Project Overview](PROJECT_OVERVIEW.md) for a comprehensive view of the entire platform.

*Last updated: January 2024*