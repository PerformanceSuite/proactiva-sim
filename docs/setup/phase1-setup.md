# Phase 1 Setup Guide

## Initial Project Setup

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