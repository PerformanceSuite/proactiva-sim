#!/usr/bin/env python3
"""
Test script for the modernized PROACTIVA simulation system
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.models.modernized_hospital_model import VAHospitalModel
from simulation.agents.ai_phone_agent import CallType
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_modernized_system():
    """Test the modernized simulation components"""
    logger.info("Starting modernized system test...")
    
    # Create model with innovations
    innovations = {
        'vr_stations': 3,
        'telehealth_rooms': 5,
        'ai_triage_enabled': True,
        'mobile_units': 2,
        'robotic_assistants': 3,
        'ai_phone_systems': 2
    }
    
    try:
        # Create the model
        model = VAHospitalModel(
            num_initial_patients=50,
            num_providers=10,
            innovations=innovations
        )
        
        logger.info(f"Model created with {model.schedule.get_agent_count()} agents")
        
        # Get AI phone systems
        ai_phones = [agent for agent in model.schedule.agents 
                     if hasattr(agent, 'agent_type') and agent.agent_type == 'ai_phone_system']
        
        logger.info(f"Found {len(ai_phones)} AI phone systems")
        
        # Add some calls to the AI phone system
        if ai_phones:
            ai_phone = ai_phones[0]
            
            # Add various types of calls
            ai_phone.add_call_to_queue(CallType.APPOINTMENT_SCHEDULING, "patient_test_1")
            ai_phone.add_call_to_queue(CallType.APPOINTMENT_REMINDER, "patient_test_2")
            ai_phone.add_call_to_queue(CallType.PRESCRIPTION_REFILL, "patient_test_3")
            
            logger.info(f"Added {len(ai_phone.call_queue)} calls to AI phone queue")
        
        # Run simulation for 10 steps
        logger.info("Running simulation for 10 steps...")
        for step in range(10):
            model.step()
            
            if step % 5 == 0:
                state = model.get_simulation_state()
                logger.info(f"Step {step}: {state['patients_waiting']} patients waiting, "
                          f"{state['provider_utilization']:.2%} provider utilization")
                
                # Check AI phone stats
                if ai_phones:
                    phone_stats = ai_phones[0].get_system_stats()
                    logger.info(f"AI Phone: {phone_stats['active_calls']} active calls, "
                              f"{phone_stats['total_completed']} completed, "
                              f"${phone_stats['total_cost_saved']:.2f} saved")
        
        # Final statistics
        logger.info("\n=== Final Statistics ===")
        final_state = model.get_simulation_state()
        logger.info(f"Total agents: {final_state['agent_count']}")
        logger.info(f"Patients treated: {final_state['patients_treated']}")
        logger.info(f"Average wait time: {final_state['average_wait_time']:.1f} minutes")
        logger.info(f"Average satisfaction: {final_state['average_satisfaction']:.1f}/100")
        
        if ai_phones:
            logger.info("\n=== AI Phone System Statistics ===")
            for i, ai_phone in enumerate(ai_phones):
                stats = ai_phone.get_system_stats()
                logger.info(f"AI Phone System {i}:")
                logger.info(f"  - Completed calls: {stats['total_completed']}")
                logger.info(f"  - Appointments scheduled: {stats['appointments_scheduled']}")
                logger.info(f"  - Transfer rate: {stats['transfer_rate']:.2%}")
                logger.info(f"  - Cost saved: ${stats['total_cost_saved']:.2f}")
                logger.info(f"  - Patient satisfaction: {stats['average_satisfaction']}/5.0")
        
        # Clean up
        model.cleanup()
        logger.info("\nTest completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


async def test_websocket_integration():
    """Test WebSocket integration with modernized model"""
    logger.info("\n=== Testing WebSocket Integration ===")
    
    try:
        # Import FastAPI components
        from api.main import app, simulations, SimulationConfig
        from fastapi.testclient import TestClient
        
        # Create test client
        client = TestClient(app)
        
        # Create simulation via API
        config = SimulationConfig(
            name="Test Simulation",
            num_patients=30,
            num_providers=8,
            ai_triage_enabled=True,
            ai_phone_systems=1
        )
        
        response = client.post("/simulations", json=config.dict())
        assert response.status_code == 200
        
        sim_data = response.json()
        sim_id = sim_data['id']
        logger.info(f"Created simulation via API: {sim_id}")
        
        # Get simulation state
        response = client.get(f"/simulations/{sim_id}")
        assert response.status_code == 200
        
        state = response.json()
        logger.info(f"Simulation state retrieved: {state['status']}")
        
        # Run a few steps
        for _ in range(5):
            response = client.post(f"/simulations/{sim_id}/step")
            assert response.status_code == 200
        
        # Get updated metrics
        response = client.get(f"/simulations/{sim_id}/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        logger.info(f"Metrics after 5 steps: {metrics['patients_waiting']} waiting, "
                   f"{metrics['provider_utilization']:.2%} utilization")
        
        # Stop simulation
        response = client.post(f"/simulations/{sim_id}/stop")
        assert response.status_code == 200
        
        logger.info("WebSocket integration test passed!")
        return True
        
    except Exception as e:
        logger.error(f"WebSocket test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # Run basic system test
    if test_modernized_system():
        logger.info("\n✅ Modernized system test PASSED")
    else:
        logger.error("\n❌ Modernized system test FAILED")
        sys.exit(1)
    
    # Run WebSocket integration test
    if asyncio.run(test_websocket_integration()):
        logger.info("\n✅ WebSocket integration test PASSED")
    else:
        logger.error("\n❌ WebSocket integration test FAILED")
        sys.exit(1)
    
    logger.info("\n🎉 All tests completed successfully!")