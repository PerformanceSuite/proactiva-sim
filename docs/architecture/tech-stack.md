# Technology Stack

## Frontend Stack
- **Frontend**: React with TypeScript (optional)
- **UI Components**: Recharts for charts, Lucide React for icons, Three.js for 3D
- **Styling**: Tailwind CSS
- **State Management**: React hooks (initially), Redux/Zustand (if needed)

## Backend Stack (Phase 2)
- **Backend**: FastAPI (Python) or Express (Node.js)
- **AI Simulation**: Python with SimPy, Mesa, or custom agent framework
- **Database**: PostgreSQL with TimescaleDB for time-series data

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

## Key Implementation Examples

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

### Implementation Approach (Phase 2)

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