# Frontend Components Overview

## Architecture

The PROACTIVA frontend is built with React and provides real-time visualization of the agent-based simulation.

## Component Structure

### Core Components

#### 1. AISimulation (Main Container)
**Location:** `frontend/src/components/AISimulation/AISimulation.jsx`

**Purpose:** Main container component that manages simulation state and WebSocket connections.

**Key Features:**
- Simulation lifecycle management (create, start, stop)
- WebSocket connection handling
- Real-time state updates
- Innovation parameter integration

**Props:**
```jsx
<AISimulation 
  innovations={{
    vrStations: 5,
    telehealthRooms: 3,
    aiTriageEnabled: true,
    mobileHealthUnits: 2,
    roboticAssistants: 1
  }}
/>
```

#### 2. MetricsDisplay
**Location:** `frontend/src/components/AISimulation/MetricsDisplay.jsx`

**Purpose:** Real-time display of key performance indicators.

**Metrics Shown:**
- Patients Waiting
- Average Wait Time
- Patient Satisfaction
- Provider Utilization
- Cost per Visit
- Mental Health Access

**Features:**
- Trend indicators (up/down arrows)
- Baseline comparisons
- Color-coded status indicators
- Responsive grid layout

#### 3. SimulationVisualizer
**Location:** `frontend/src/components/AISimulation/SimulationVisualizer.jsx`

**Purpose:** 2D canvas-based visualization of hospital layout and agent movement.

**Features:**
- Hospital floor plan rendering
- Agent visualization (patients, providers)
- Real-time position updates
- Interactive agent selection
- Department highlighting
- Movement path tracing

**Agent Visualization:**
- **Patients** - Circles with size based on urgency
- **Providers** - Squares with color based on availability
- **Colors** - Yellow (waiting), Green (treatment), Blue (discharged), Red (emergency)

#### 4. InsightPanel
**Location:** `frontend/src/components/AISimulation/InsightPanel.jsx`

**Purpose:** Display AI-discovered insights and recommendations.

**Insight Types:**
- Wait Time Crisis
- Bottleneck Detection
- Innovation Success
- Resource Optimization
- Social Network Patterns

**Features:**
- Severity color coding
- Confidence indicators
- Actionable recommendations
- Real-time updates
- Expandable details

#### 5. AgentDetails
**Location:** `frontend/src/components/AISimulation/AgentDetails.jsx`

**Purpose:** Detailed information about selected agents.

**Patient Details:**
- Demographics and condition
- Wait time and satisfaction
- Urgency level
- Current location
- Treatment history

**Provider Details:**
- Specialty and experience
- Patients seen today
- Stress and energy levels
- Available/busy status
- Innovation adoption

#### 6. Visualization3D
**Location:** `frontend/src/components/AISimulation/Visualization3D.jsx`

**Purpose:** 3D visualization using Three.js for immersive hospital view.

**Features:**
- 3D hospital building model
- Multi-floor navigation
- Agent movement in 3D space
- Interactive camera controls
- Heatmap overlays
- Flow visualization

**Controls:**
- Mouse drag to rotate
- Scroll to zoom
- Right-click to pan
- Click agents for details

#### 7. NaturalLanguageQuery
**Location:** `frontend/src/components/AISimulation/NaturalLanguageQuery.jsx`

**Purpose:** Natural language interface for querying simulation data.

**Features:**
- Text input for questions
- Example queries
- AI-powered responses
- Confidence indicators
- Scenario parameters display

**Example Queries:**
- "What if we had 20% less nurses?"
- "Why are mental health wait times so high?"
- "How can we reduce patient wait times?"
- "What would happen if we added 5 VR stations?"

## State Management

### Simulation State
```javascript
const [simulationState, setSimulationState] = useState({
  simulationId: null,
  isRunning: false,
  isConnected: false,
  currentState: {},
  agents: [],
  insights: [],
  selectedAgent: null
});
```

### WebSocket Integration
```javascript
const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'initial_state':
      setCurrentState(data.data.current_state);
      break;
    case 'simulation_update':
      setCurrentState(data.state);
      setAgents(data.agents);
      if (data.new_insights) {
        setInsights(prev => [...data.new_insights, ...prev]);
      }
      break;
    case 'simulation_completed':
      setIsRunning(false);
      break;
  }
};
```

## Data Flow

### 1. Simulation Creation
```
AISimulation → POST /api/v2/simulations → Backend creates simulation → Returns simulation_id
```

### 2. Real-time Updates
```
WebSocket Connection → simulation_update messages → State updates → Component re-renders
```

### 3. User Interactions
```
User clicks agent → onAgentSelect → AgentDetails updates → Display agent information
```

## Styling and UI

### CSS Framework
- **Tailwind CSS** for utility-first styling
- **Responsive design** for mobile and desktop
- **Dark mode support** (planned)
- **Accessibility compliance** (WCAG 2.1)

### Color Scheme
- **Primary:** Blue (#3B82F6)
- **Secondary:** Purple (#8B5CF6)
- **Success:** Green (#10B981)
- **Warning:** Yellow (#F59E0B)
- **Error:** Red (#EF4444)
- **Gray Scale:** Multiple shades for backgrounds and text

### Icons
- **Lucide React** for consistent iconography
- **Brain** - AI simulation
- **Users** - Patient metrics
- **Clock** - Wait times
- **TrendingUp** - Performance metrics
- **AlertCircle** - Insights and alerts

## Performance Optimization

### Rendering Optimization
- **React.memo** for expensive components
- **useMemo** for complex calculations
- **useCallback** for event handlers
- **Virtualization** for large agent lists

### WebSocket Optimization
- **Message batching** to reduce update frequency
- **Selective updates** to avoid unnecessary re-renders
- **Connection pooling** for multiple simulations
- **Automatic reconnection** on connection loss

### Canvas Performance
- **RequestAnimationFrame** for smooth animations
- **Offscreen canvas** for complex rendering
- **Level of detail** for distant agents
- **Culling** for off-screen agents

## Development Tools

### Development Server
```bash
cd frontend
npm start
```

### Build Process
```bash
npm run build
```

### Testing
```bash
npm test
```

### Linting
```bash
npm run lint
```

## Integration Points

### Backend API
- REST endpoints for simulation management
- WebSocket for real-time updates
- Natural language query processing
- Insight retrieval and filtering

### Innovation Controls
- Receives innovation parameters from parent dashboard
- Passes parameters to simulation creation
- Updates simulation when parameters change
- Displays impact of innovations in real-time

### Data Export
- CSV export of simulation data
- JSON export of insights
- Screenshot capture of visualizations
- Report generation (planned)

## Future Enhancements

### Planned Features
- **Multi-simulation comparison** - Side-by-side visualization
- **Time-series analysis** - Historical trend analysis
- **Scenario templates** - Pre-configured test scenarios
- **Collaboration tools** - Multi-user simulation sessions
- **Mobile app** - Native mobile interface
- **VR interface** - Virtual reality simulation viewing

### Technical Improvements
- **GraphQL integration** - More efficient data fetching
- **PWA support** - Offline capabilities
- **Real-time collaboration** - Multiple users in same simulation
- **Advanced analytics** - ML-powered insights
- **Custom dashboards** - User-configurable layouts