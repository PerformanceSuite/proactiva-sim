# CLAUDE.md

# CLAUDE.md - PROACTIVA Healthcare Simulation Platform

## Project Overview

PROACTIVA is building an AI-powered healthcare operations simulation platform that helps VA medical centers and other healthcare facilities test innovations before implementation. The platform simulates everything from simple KPI impacts to complex AI agents making thousands of healthcare delivery decisions.

### Core Vision
- **Phase 1 (Current)**: Interactive dashboard for testing innovation scenarios (VR therapy, AR tools, etc.)
- **Phase 2 (Next)**: AI agents simulating patient journeys and healthcare operations
- **Phase 3 (Future)**: Full digital twin of healthcare facilities with predictive capabilities

### Key Features to Implement
1. Real-time healthcare KPI simulation
2. VA-specific metrics and workflows
3. Innovation impact modeling (VR/AR/AI/Robotics)
4. 3D facility visualization
5. Scenario saving and comparison
6. ROI calculations
7. AI agent simulation framework (Phase 2)

## Tech Stack

- **Frontend**: React with TypeScript (optional)
- **UI Components**: Recharts for charts, Lucide React for icons, Three.js for 3D
- **Styling**: Tailwind CSS
- **State Management**: React hooks (initially), Redux/Zustand (if needed)
- **Backend** (Phase 2): FastAPI (Python) or Express (Node.js)
- **AI Simulation** (Phase 2): Python with SimPy, Mesa, or custom agent framework
- **Database** (Phase 2): PostgreSQL with TimescaleDB for time-series data

## Project Structure

```
proactiva-simulation/
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Dashboard.css
│   │   │   └── index.js
│   │   ├── ControlPanel/
│   │   │   ├── ControlPanel.jsx
│   │   │   ├── InnovationSlider.jsx
│   │   │   └── index.js
│   │   ├── Metrics/
│   │   │   ├── MetricsGrid.jsx
│   │   │   ├── KPICard.jsx
│   │   │   ├── VAMetrics.jsx
│   │   │   └── index.js
│   │   ├── Visualizations/
│   │   │   ├── RadarChart.jsx
│   │   │   ├── TimeSeriesChart.jsx
│   │   │   ├── Visualization3D.jsx
│   │   │   └── index.js
│   │   ├── Scenarios/
│   │   │   ├── ScenarioManager.jsx
│   │   │   ├── ScenarioComparison.jsx
│   │   │   └── index.js
│   │   └── ROI/
│   │       ├── ROIAnalysis.jsx
│   │       └── index.js
│   ├── hooks/
│   │   ├── useSimulation.js
│   │   ├── useMetrics.js
│   │   └── useScenarios.js
│   ├── utils/
│   │   ├── calculations.js
│   │   ├── constants.js
│   │   ├── vaMetrics.js
│   │   └── simulationEngine.js
│   ├── services/
│   │   ├── api.js
│   │   └── storage.js
│   ├── App.js
│   ├── App.css
│   └── index.js
├── public/
│   └── index.html
├── docs/
│   ├── AI_SIMULATION_PLAN.md
│   ├── VA_METRICS.md
│   └── INNOVATION_VARIABLES.md
├── .gitignore
├── package.json
├── README.md
└── CLAUDE.md
```

## Implementation Instructions

### Step 1: Project Setup

Create a new React application and install dependencies:

```bash
npx create-react-app proactiva-simulation
cd proactiva-simulation
npm install recharts lucide-react three @types/three
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 2: Configure Tailwind CSS

Update `tailwind.config.js`:
```javascript
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Add to `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 3: Create Core Components

The main application should have these key components:

1. **App.js** - Main container with header and layout
2. **Dashboard** - Overall dashboard container
3. **ControlPanel** - All innovation control sliders and toggles
4. **MetricsGrid** - Display of KPIs and VA-specific metrics
5. **Visualizations** - Charts and 3D view
6. **ScenarioManager** - Save, load, compare scenarios
7. **ROIAnalysis** - Financial impact calculations

### Step 4: Implement State Management

Create a simulation context or use hooks to manage:
- Innovation variables (VR stations, AR devices, etc.)
- Calculated metrics (wait times, costs, satisfaction)
- VA-specific metrics (mental health access, veteran satisfaction)
- Saved scenarios
- UI state (3D view toggle, comparison mode)

### Step 5: Add Simulation Logic

The simulation engine should:
1. Take innovation inputs
2. Apply impact formulas
3. Calculate new metrics
4. Update visualizations in real-time

## Key Code Snippets

### Main App Structure (App.js)
```jsx
import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold">
            <span className="text-blue-600">PROACTI</span>
            <span className="text-red-600">VA</span>
          </h1>
        </div>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
```

### Simulation Calculations (utils/calculations.js)
```javascript
export const calculateMetrics = (variables) => {
  const { vrStations, arDevices, telehealthRooms, aiTriageEnabled, staffingLevel } = variables;
  
  // Base metrics
  let metrics = {
    waitTime: 28,
    costPerSession: 185,
    patientSatisfaction: 72,
    utilization: 78
  };
  
  // Apply VR impact
  metrics.waitTime -= vrStations * 0.8;
  metrics.costPerSession -= vrStations * 3;
  
  // Apply other innovations...
  
  return metrics;
};

export const calculateROI = (variables, metrics) => {
  // ROI calculation logic
};
```

## AI-Powered Simulation (Phase 2 Vision)

### Concept: Agent-Based Healthcare Simulation

Instead of simple mathematical formulas, implement AI agents that:

1. **Patient Agents**
   - Have conditions, preferences, urgency levels
   - Make decisions about seeking care
   - Navigate the healthcare system
   - Respond to wait times and quality

2. **Provider Agents**
   - Have specialties, efficiency rates, schedules
   - Make treatment decisions
   - Use available tools (VR, AR, AI)
   - Experience fatigue and satisfaction

3. **System Agents**
   - Scheduling algorithms
   - Resource allocation
   - Triage decisions
   - Quality monitoring

### Implementation Approach

```python
# Example agent framework structure
class PatientAgent:
    def __init__(self, condition, urgency, preferences):
        self.condition = condition
        self.urgency = urgency
        self.preferences = preferences
        self.satisfaction = 50
        
    def decide_care_path(self, available_options):
        # AI logic to choose between ER, telehealth, VR therapy, etc.
        pass
        
    def experience_care(self, wait_time, quality):
        # Update satisfaction based on experience
        pass

class HealthcareSimulation:
    def __init__(self, num_patients=1000):
        self.patients = [PatientAgent(...) for _ in range(num_patients)]
        self.providers = [ProviderAgent(...) for _ in range(50)]
        self.innovations = {'vr_stations': 10, 'ar_devices': 5}
        
    def run_day(self):
        # Simulate one day of operations
        for patient in self.patients:
            care_path = patient.decide_care_path(self.available_services)
            self.route_patient(patient, care_path)
```

### AI Simulation Features to Research

1. **Multi-Agent Reinforcement Learning**
   - Agents learn optimal strategies over time
   - Emergent behaviors from simple rules
   - Can discover non-obvious optimizations

2. **Digital Twin Technology**
   - Real-time synchronization with actual facility
   - Predictive capabilities
   - What-if scenario testing

3. **Large Language Model Integration**
   - Natural language scenario descriptions
   - Automated insight generation
   - Conversational interface for exploring results

4. **Monte Carlo Simulations**
   - Run thousands of scenarios automatically
   - Statistical confidence intervals
   - Risk assessment

## Development Phases

### Phase 1: MVP Dashboard (Current)
- [ ] Basic innovation controls
- [ ] Real-time metric updates
- [ ] VA-specific KPIs
- [ ] 3D visualization
- [ ] Scenario management
- [ ] ROI calculations

### Phase 2: AI Agent Simulation
- [ ] Patient agent framework
- [ ] Provider agent behaviors
- [ ] Multi-day simulations
- [ ] Statistical analysis
- [ ] Performance optimization

### Phase 3: Production Platform
- [ ] Real data integration
- [ ] Multi-facility support
- [ ] Predictive analytics
- [ ] API for external systems
- [ ] Enterprise features

## VA-Specific Considerations

### Metrics to Track
- Veteran wait times (different from civilian)
- Mental health access rates
- Service-connected disability processing
- Community care referrals and costs
- Suicide prevention screening rates
- Homeless veteran outreach effectiveness

### Innovation Focus Areas
- PTSD and mental health (VR therapy)
- Prosthetics and assistive technology
- Telehealth for rural veterans
- AI-powered triage for crisis intervention
- Mobile units for homeless veterans

## Getting Started Checklist

1. [ ] Set up React project with dependencies
2. [ ] Create component structure
3. [ ] Implement basic dashboard with controls
4. [ ] Add metric calculations
5. [ ] Create visualizations
6. [ ] Add 3D facility view
7. [ ] Implement scenario saving
8. [ ] Add VA-specific metrics
9. [ ] Create ROI analysis
10. [ ] Plan Phase 2 AI simulation

## Additional Resources

- VA Innovation Ecosystem: https://www.innovation.va.gov/
- Healthcare Simulation Research: https://www.ssih.org/
- Agent-Based Modeling: https://mesa.readthedocs.io/
- Three.js Documentation: https://threejs.org/docs/

## Questions for Product Development

1. Which VA facilities should we model first?
2. What are the most critical metrics for Kevin's demo?
3. Should we integrate with actual VA data systems?
4. How detailed should the AI simulation be for Phase 2?
5. What innovations beyond VR/AR should we include?

## Contact

Project Lead: [Daniel Connolly]
Repository: [https://github.com/PerformanceSuite/proactiva-sim]
Demo Site: [Deployment URL]