import React, { useState, useEffect, useRef } from 'react';
import { Brain, Play, Pause, AlertCircle, Users, Clock, TrendingUp, Activity } from 'lucide-react';
import SimulationVisualizer from './SimulationVisualizer';
import InsightPanel from './InsightPanel';
import MetricsDisplay from './MetricsDisplay';
import AgentDetails from './AgentDetails';
import { NaturalLanguageQuery } from '../NaturalLanguage';

const AISimulation = ({ innovations }) => {
  const [simulationId, setSimulationId] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [currentState, setCurrentState] = useState({});
  const [insights, setInsights] = useState([]);
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [queryResponse, setQueryResponse] = useState(null);
  const ws = useRef(null);

  // Create simulation when component mounts or innovations change
  useEffect(() => {
    createSimulation();
    
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [innovations.vrStations, innovations.telehealthRooms, innovations.aiTriageEnabled]);

  const createSimulation = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/simulations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'VA Gulf Coast Simulation',
          num_patients: 1000,
          num_providers: 50,
          vr_stations: innovations.vrStations || 0,
          telehealth_rooms: innovations.telehealthRooms || 0,
          ai_triage_enabled: innovations.aiTriageEnabled || false,
          mobile_units: innovations.mobileHealthUnits || 0,
          robotic_assistants: innovations.roboticAssistants || 0
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to create simulation');
      }
      
      const data = await response.json();
      setSimulationId(data.simulation_id);
    } catch (error) {
      console.error('Error creating simulation:', error);
    }
  };

  const startSimulation = async () => {
    if (!simulationId) return;
    
    try {
      // Start simulation
      const response = await fetch(`http://localhost:8000/api/v2/simulations/${simulationId}/start`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to start simulation');
      }
      
      setIsRunning(true);
      
      // Connect WebSocket
      ws.current = new WebSocket(`ws://localhost:8000/ws/${simulationId}`);
      
      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };
      
      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
      
      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setIsRunning(false);
      };
      
    } catch (error) {
      console.error('Error starting simulation:', error);
      setIsRunning(false);
    }
  };

  const stopSimulation = async () => {
    if (simulationId) {
      try {
        await fetch(`http://localhost:8000/api/v2/simulations/${simulationId}/stop`, {
          method: 'POST'
        });
      } catch (error) {
        console.error('Error stopping simulation:', error);
      }
    }
    
    if (ws.current) {
      ws.current.close();
    }
    
    setIsRunning(false);
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'initial_state':
        setCurrentState(data.data.current_state);
        break;
        
      case 'simulation_update':
        setCurrentState(data.state);
        setAgents(data.agents);
        
        // Add new insights to the list
        if (data.new_insights && data.new_insights.length > 0) {
          setInsights(prev => [...data.new_insights, ...prev].slice(0, 20)); // Keep last 20
        }
        break;
        
      case 'simulation_completed':
        console.log('Simulation completed:', data);
        setIsRunning(false);
        break;
        
      case 'simulation_error':
        console.error('Simulation error:', data.error);
        setIsRunning(false);
        break;
        
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const handleQueryResult = (result) => {
    setQueryResponse(result);
    
    // If query returned new insights, add them to insights list
    if (result.insights && result.insights.length > 0) {
      setInsights(prev => [...result.insights, ...prev].slice(0, 20));
    }
    
    // If query returned updated metrics, update current state
    if (result.metrics) {
      setCurrentState(prev => ({ ...prev, ...result.metrics }));
    }
  };

  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 flex items-center">
              <Brain className="w-8 h-8 text-purple-600 mr-2" />
              AI Agent Simulation
            </h2>
            <p className="text-gray-600 mt-1">
              {agents.length} agents active • Step {currentState.simulation_time || 0}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <button
              onClick={isRunning ? stopSimulation : startSimulation}
              disabled={!simulationId}
              className={`px-6 py-2 rounded-lg font-medium transition-all flex items-center ${
                isRunning 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-green-500 hover:bg-green-600 text-white'
              } ${!simulationId ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isRunning ? (
                <>
                  <Pause className="w-5 h-5 mr-2" />
                  Stop Simulation
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  Start Simulation
                </>
              )}
            </button>
          </div>
        </div>

        {/* Real-time Metrics */}
        <MetricsDisplay metrics={currentState} />
      </div>

      {/* Natural Language Query Interface */}
      {simulationId && (
        <NaturalLanguageQuery 
          simulationId={simulationId}
          onQueryResult={handleQueryResult}
        />
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visualization Panel (2 columns) */}
        <div className="lg:col-span-2">
          <SimulationVisualizer 
            agents={agents}
            onAgentSelect={setSelectedAgent}
            selectedAgent={selectedAgent}
          />
        </div>

        {/* Side Panel (1 column) */}
        <div className="space-y-6">
          {/* Agent Details */}
          {selectedAgent && (
            <AgentDetails agent={selectedAgent} />
          )}

          {/* VAL Response Display */}
          {queryResponse && (
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-2">
                  <span className="text-white font-bold text-xs">V</span>
                </div>
                VAL Analysis
              </h4>
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">
                  Q: {queryResponse.query}
                </p>
                <p className="text-sm text-gray-800 bg-gradient-to-r from-blue-50 to-purple-50 p-3 rounded">
                  {queryResponse.response}
                </p>
              </div>
            </div>
          )}

          {/* Insights */}
          <InsightPanel insights={insights} />
        </div>
      </div>
    </div>
  );
};

export default AISimulation;