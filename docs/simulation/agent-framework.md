# Agent-Based Simulation Framework

## Overview

The PROACTIVA simulation uses Mesa, a Python agent-based modeling framework, to create realistic healthcare facility simulations with thousands of autonomous agents.

## Core Architecture

### Agent Types

#### 1. Patient Agents (VeteranPatientAgent)
Represent individual veterans seeking healthcare services.

**Key Properties:**
- Demographics (age, service era, disability rating)
- Medical condition and urgency level
- Wait time tolerance and satisfaction
- Technology comfort level
- Social network connections

**Behaviors:**
- Arrive at facility
- Check in and wait for care
- Navigate through care pathway
- Respond to wait times and service quality
- Influence other veterans through social networks

**States:**
- `ARRIVAL` - Just arrived at facility
- `CHECK_IN` - Checking in at reception
- `WAITING` - Waiting for care
- `TRIAGE` - Being triaged
- `TREATMENT` - Receiving care
- `DISCHARGED` - Completed care
- `LEFT_WITHOUT_TREATMENT` - Left due to excessive wait

#### 2. Provider Agents (ProviderAgent)
Represent healthcare providers (doctors, nurses, therapists).

**Key Properties:**
- Provider type and specialty
- Experience level and efficiency
- Energy, stress, and burnout risk
- Innovation adoption rate
- Schedule and availability

**Behaviors:**
- Treat patients based on urgency and specialty match
- Experience fatigue and stress over time
- Adopt new technologies at different rates
- Take breaks when needed
- Influence patient satisfaction through care quality

**Types:**
- `PHYSICIAN` - Doctors with various specialties
- `NURSE_PRACTITIONER` - Advanced practice nurses
- `PHYSICIAN_ASSISTANT` - Physician assistants
- `NURSE` - Registered nurses
- `THERAPIST` - Mental health therapists
- `TECHNICIAN` - Medical technicians

#### 3. System Agents (Future)
Will represent automated systems and processes.

**Planned Types:**
- AI Triage System
- Scheduling Algorithm
- Resource Allocation System
- Quality Monitoring System

## Simulation Environment

### Hospital Layout
The simulation models a realistic VA hospital with:
- **Entrance/Reception** - Patient arrival and check-in
- **Waiting Areas** - Multiple waiting rooms by specialty
- **Treatment Areas** - Emergency, Primary Care, Mental Health, Specialist
- **Support Services** - Lab, Imaging, Pharmacy
- **Innovation Areas** - VR Therapy Suite, Telehealth Center

### Network Topology
Hospital areas are connected via a directed graph representing:
- Patient flow pathways
- Provider movement patterns
- Resource accessibility
- Innovation integration points

## Innovation Integration

### VR Therapy Stations
- Mental health patients can use VR for therapy
- Reduces treatment time and improves satisfaction
- Requires provider certification
- Patient willingness based on tech comfort

### Telehealth Capabilities
- Enables remote consultations
- Reduces facility congestion
- Suitable for routine and follow-up care
- Requires both provider and patient adoption

### AI Triage System
- Automatically prioritizes patients
- Reduces wait times in triage
- Improves resource allocation
- Learns from provider decisions

## Simulation Mechanics

### Time Management
- **Discrete Time Steps** - Each step represents 1 minute
- **Simultaneous Activation** - All agents act simultaneously
- **Event Scheduling** - Future events (treatment completion, breaks) are scheduled

### Agent Interactions
- **Patient-Provider Matching** - Based on specialty, urgency, and availability
- **Social Influence** - Veterans influence each other's technology adoption
- **Resource Competition** - Agents compete for limited resources
- **Quality Feedback** - Patient satisfaction affects provider performance

### Metrics Collection
Real-time tracking of:
- Patient wait times and satisfaction
- Provider utilization and stress levels
- Innovation adoption rates
- System bottlenecks and inefficiencies
- Cost per visit and ROI calculations

## Simulation Configuration

### Basic Parameters
```python
VAHospitalModel(
    num_initial_patients=100,
    num_providers=20,
    innovations={
        'vr_stations': 5,
        'telehealth_rooms': 3,
        'ai_triage_enabled': True,
        'mobile_units': 2,
        'robotic_assistants': 1
    }
)
```

### Provider Mix
```python
provider_mix = {
    'emergency_physicians': 3,
    'primary_care_physicians': 5,
    'mental_health_providers': 4,
    'specialists': 3,
    'nurses': 8,
    'nurse_practitioners': 3,
    'technicians': 4
}
```

## Data Collection

### Agent-Level Metrics
- Individual agent states and behaviors
- Treatment pathways and outcomes
- Social network influences
- Technology adoption patterns

### System-Level Metrics
- Average wait times by condition
- Provider utilization rates
- Innovation effectiveness
- Cost and efficiency measures
- Patient satisfaction scores

### Insight Generation
The simulation includes an AI-powered insight engine that:
- Detects patterns and anomalies
- Identifies bottlenecks and optimization opportunities
- Provides recommendations for improvement
- Tracks the impact of interventions

## Simulation Scenarios

### Baseline Operations
Standard hospital operations without innovations for comparison.

### Innovation Testing
Test impact of:
- Adding VR therapy stations
- Expanding telehealth capabilities
- Implementing AI triage
- Deploying mobile health units
- Introducing robotic assistants

### Crisis Scenarios
Model response to:
- Staff shortages
- Patient surges
- Equipment failures
- Pandemic conditions
- Emergency situations

### Optimization Studies
Explore:
- Optimal staffing levels
- Resource allocation strategies
- Innovation deployment timing
- Cost-effectiveness of improvements
- Patient flow redesign

## Technical Implementation

### Mesa Framework Integration
```python
from mesa import Agent, Model
from mesa.time import RandomActivation, SimultaneousActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
```

### Agent State Management
```python
class BaseHealthcareAgent(Agent):
    def __init__(self, unique_id, model, agent_type):
        super().__init__(unique_id, model)
        self.agent_type = agent_type
        self.state = AgentState.IDLE
        self.history = []
        self.metrics = {}
```

### Simulation Loop
```python
def step(self):
    # Collect data
    self.datacollector.collect(self)
    
    # Process scheduled events
    self._process_events()
    
    # Step all agents
    self.schedule.step()
    
    # Generate new arrivals
    self._generate_arrivals()
    
    # Run insight detection
    insights = self.insight_engine.detect_insights()
```

## Performance Considerations

### Scalability
- Supports 1000+ agents with real-time visualization
- Efficient agent scheduling and memory management
- Configurable simulation speed and detail level
- Distributed computing support for large scenarios

### Optimization
- Vectorized calculations where possible
- Efficient data structures for agent lookups
- Lazy evaluation of complex metrics
- Caching of frequently accessed data

### Memory Management
- Agent pooling for creation/destruction
- Circular buffers for historical data
- Garbage collection optimization
- Memory profiling and monitoring