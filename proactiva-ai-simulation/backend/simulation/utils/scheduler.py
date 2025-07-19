"""
Custom scheduler for Mesa 3.0 compatibility
"""
import random
from typing import List, Any
from mesa import Agent


class RandomActivation:
    """Simple random activation scheduler for Mesa 3.0"""
    
    def __init__(self, model):
        self.model = model
        self.agents = []
        self._agent_buffer = []
    
    def add(self, agent: Agent):
        """Add an agent to the scheduler"""
        if agent not in self.agents:
            self.agents.append(agent)
    
    def remove(self, agent: Agent):
        """Remove an agent from the scheduler"""
        if agent in self.agents:
            self.agents.remove(agent)
    
    def step(self):
        """Execute step for all agents in random order"""
        # Create a shuffled copy to avoid modifying the original list during iteration
        agent_list = self.agents.copy()
        random.shuffle(agent_list)
        
        for agent in agent_list:
            # Check if agent is still in the scheduler (might have been removed)
            if agent in self.agents:
                try:
                    agent.step()
                except Exception as e:
                    # Handle agent errors gracefully
                    print(f"Agent {agent.unique_id} step failed: {e}")
    
    def get_agent_count(self) -> int:
        """Get the number of agents"""
        return len(self.agents)
    
    def get_agents(self) -> List[Agent]:
        """Get all agents"""
        return self.agents.copy()
    
    @property
    def agent_buffer(self) -> List[Agent]:
        """Agent buffer for compatibility"""
        return self._agent_buffer