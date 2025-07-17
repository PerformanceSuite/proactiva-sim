import React, { useRef, useEffect } from 'react';

const SimulationVisualizer = ({ agents, onAgentSelect, selectedAgent }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#f3f4f6';
    ctx.fillRect(0, 0, width, height);

    // Draw hospital layout
    drawHospitalLayout(ctx, width, height);

    // Draw agents
    agents.forEach(agent => {
      drawAgent(ctx, agent, width, height, agent.id === selectedAgent?.id);
    });

  }, [agents, selectedAgent]);

  const drawHospitalLayout = (ctx, width, height) => {
    // Draw departments
    const departments = [
      { name: 'Entrance', x: 50, y: height/2, w: 60, h: 100, color: '#e5e7eb' },
      { name: 'Waiting Room', x: 150, y: height/2 - 75, w: 150, h: 150, color: '#fef3c7' },
      { name: 'Emergency', x: 350, y: 50, w: 120, h: 80, color: '#fee2e2' },
      { name: 'Primary Care', x: 350, y: 150, w: 120, h: 80, color: '#dbeafe' },
      { name: 'Mental Health', x: 350, y: 250, w: 120, h: 80, color: '#e9d5ff' },
      { name: 'VR Therapy', x: 500, y: 250, w: 100, h: 80, color: '#c7d2fe' }
    ];

    departments.forEach(dept => {
      ctx.fillStyle = dept.color;
      ctx.fillRect(dept.x, dept.y, dept.w, dept.h);
      ctx.strokeStyle = '#6b7280';
      ctx.strokeRect(dept.x, dept.y, dept.w, dept.h);
      
      ctx.fillStyle = '#374151';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(dept.name, dept.x + dept.w/2, dept.y + dept.h/2);
    });
  };

  const drawAgent = (ctx, agent, width, height, isSelected) => {
    // Map location to coordinates
    const locationMap = {
      'entrance': { x: 80, y: height/2 },
      'reception': { x: 130, y: height/2 },
      'waiting_room': { x: 225, y: height/2 },
      'emergency': { x: 410, y: 90 },
      'primary_care': { x: 410, y: 190 },
      'mental_health': { x: 410, y: 290 },
      'vr_therapy_suite': { x: 550, y: 290 },
      'unknown': { x: 50 + Math.random() * (width - 100), y: 50 + Math.random() * (height - 100) }
    };

    const pos = locationMap[agent.location] || locationMap['unknown'];
    
    // Add some randomness to prevent overlap
    const x = pos.x + (Math.random() - 0.5) * 20;
    const y = pos.y + (Math.random() - 0.5) * 20;

    // Determine color based on agent type and state
    let color = '#6b7280'; // Default gray
    
    if (agent.type === 'patient') {
      if (agent.state === 'waiting') {
        color = '#f59e0b'; // Yellow for waiting
      } else if (agent.state === 'treatment') {
        color = '#10b981'; // Green for in treatment
      } else if (agent.state === 'discharged') {
        color = '#3b82f6'; // Blue for discharged
      }
      
      // Urgency affects size
      const size = agent.urgency <= 2 ? 6 : 4;
      
      ctx.beginPath();
      ctx.arc(x, y, size, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      
      if (isSelected) {
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    } else if (agent.type === 'provider') {
      // Providers as squares
      const size = 8;
      ctx.fillStyle = agent.state === 'busy' ? '#dc2626' : '#059669';
      ctx.fillRect(x - size/2, y - size/2, size, size);
      
      if (isSelected) {
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.strokeRect(x - size/2 - 1, y - size/2 - 1, size + 2, size + 2);
      }
    }
  };

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Find clicked agent (simplified)
    const clickedAgent = agents.find(agent => {
      const locationMap = {
        'entrance': { x: 80, y: canvas.height/2 },
        'waiting_room': { x: 225, y: canvas.height/2 },
        // ... other locations
      };
      
      const pos = locationMap[agent.location] || { x: 50, y: 50 };
      const distance = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
      
      return distance < 20; // Click radius
    });

    if (clickedAgent) {
      onAgentSelect(clickedAgent);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Hospital Simulation View</h3>
      
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={650}
          height={400}
          className="border border-gray-200 rounded cursor-pointer"
          onClick={handleCanvasClick}
        />
        
        {/* Legend */}
        <div className="absolute bottom-4 right-4 bg-white bg-opacity-90 p-3 rounded shadow">
          <p className="text-xs font-semibold mb-2">Legend</p>
          <div className="space-y-1">
            <div className="flex items-center text-xs">
              <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2" />
              <span>Waiting</span>
            </div>
            <div className="flex items-center text-xs">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-2" />
              <span>In Treatment</span>
            </div>
            <div className="flex items-center text-xs">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-2" />
              <span>Discharged</span>
            </div>
            <div className="flex items-center text-xs">
              <div className="w-3 h-3 bg-red-600 mr-2" />
              <span>Busy Provider</span>
            </div>
            <div className="flex items-center text-xs">
              <div className="w-3 h-3 bg-green-600 mr-2" />
              <span>Available Provider</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        <p>Click on any agent to see details. Larger circles indicate higher urgency patients.</p>
      </div>
    </div>
  );
};

export default SimulationVisualizer;