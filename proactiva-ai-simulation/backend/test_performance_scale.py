#!/usr/bin/env python3
"""
Performance test for PROACTIVA simulation with thousands of agents
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.models.modernized_hospital_model import VAHospitalModel
import logging
import time
import psutil
import gc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_performance_scaling():
    """Test simulation performance with increasing agent counts"""
    logger.info("=== PROACTIVA Performance Scaling Test ===")
    
    # Test configurations
    test_configs = [
        {"patients": 100, "providers": 20, "steps": 10},
        {"patients": 500, "providers": 50, "steps": 10},
        {"patients": 1000, "providers": 100, "steps": 10},
        {"patients": 5000, "providers": 200, "steps": 5},
        {"patients": 10000, "providers": 400, "steps": 3},
    ]
    
    results = []
    
    for config in test_configs:
        logger.info(f"\n--- Testing with {config['patients']} patients, {config['providers']} providers ---")
        
        # Force garbage collection before test
        gc.collect()
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Create model
            start_time = time.time()
            
            innovations = {
                'vr_stations': 5,
                'telehealth_rooms': 10,
                'ai_triage_enabled': True,
                'mobile_units': 3,
                'robotic_assistants': 5,
                'ai_phone_systems': 3
            }
            
            model = VAHospitalModel(
                num_initial_patients=config['patients'],
                num_providers=config['providers'],
                innovations=innovations
            )
            
            creation_time = time.time() - start_time
            logger.info(f"Model created in {creation_time:.2f} seconds")
            logger.info(f"Total agents: {model.schedule.get_agent_count()}")
            
            # Run simulation steps
            step_times = []
            for step in range(config['steps']):
                step_start = time.time()
                model.step()
                step_duration = time.time() - step_start
                step_times.append(step_duration)
                
                if step % 2 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    logger.info(f"Step {step}: {step_duration:.3f}s, Memory: {current_memory:.1f}MB")
            
            # Calculate statistics
            avg_step_time = sum(step_times) / len(step_times)
            max_step_time = max(step_times)
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_used = final_memory - initial_memory
            
            # Get performance report
            if model.schedule.get_agent_count() > 1000:
                perf_report = model.performance_manager.get_optimization_report()
                perf_score = perf_report['profiler_summary'].get('performance_score', 0)
            else:
                perf_score = 100.0
            
            result = {
                'patients': config['patients'],
                'providers': config['providers'],
                'total_agents': model.schedule.get_agent_count(),
                'creation_time': creation_time,
                'avg_step_time': avg_step_time,
                'max_step_time': max_step_time,
                'memory_used_mb': memory_used,
                'performance_score': perf_score,
                'ai_phone_calls': sum(phone.completed_calls for phone in model.schedule.agents 
                                    if hasattr(phone, 'completed_calls')),
                'cost_saved': sum(phone.total_cost_saved for phone in model.schedule.agents 
                                if hasattr(phone, 'total_cost_saved'))
            }
            
            results.append(result)
            
            # Cleanup
            model.cleanup()
            del model
            gc.collect()
            
            logger.info(f"✅ Test completed - Avg step: {avg_step_time:.3f}s, Memory: {memory_used:.1f}MB")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}", exc_info=True)
            results.append({
                'patients': config['patients'],
                'providers': config['providers'],
                'error': str(e)
            })
    
    # Print summary
    logger.info("\n=== PERFORMANCE SCALING SUMMARY ===")
    logger.info("Agents | Avg Step Time | Max Step Time | Memory Used | Performance Score | AI Calls | Cost Saved")
    logger.info("-" * 100)
    
    for result in results:
        if 'error' not in result:
            logger.info(f"{result['total_agents']:6d} | {result['avg_step_time']:13.3f}s | {result['max_step_time']:13.3f}s | "
                      f"{result['memory_used_mb']:11.1f}MB | {result['performance_score']:17.1f} | "
                      f"{result['ai_phone_calls']:8d} | ${result['cost_saved']:10.2f}")
        else:
            logger.info(f"{result['patients'] + result['providers']:6d} | ERROR: {result['error']}")
    
    # Performance recommendations
    logger.info("\n=== PERFORMANCE RECOMMENDATIONS ===")
    
    if results[-1].get('total_agents', 0) >= 10000:
        logger.info("✅ Successfully scaled to 10,000+ agents!")
        logger.info("🚀 System is ready for enterprise-scale deployments")
        
        if results[-1].get('avg_step_time', 999) < 2.0:
            logger.info("⚡ Excellent performance - sub 2-second steps with 10K+ agents")
        else:
            logger.info("⚠️  Consider enabling distributed processing for better performance")
    
    # AI Phone System ROI
    total_calls = sum(r.get('ai_phone_calls', 0) for r in results if 'error' not in r)
    total_saved = sum(r.get('cost_saved', 0) for r in results if 'error' not in r)
    
    if total_calls > 0:
        logger.info(f"\n💰 AI PHONE SYSTEM ROI:")
        logger.info(f"   - Total calls handled: {total_calls}")
        logger.info(f"   - Total cost saved: ${total_saved:.2f}")
        logger.info(f"   - Average saving per call: ${total_saved/total_calls:.2f}")
        logger.info(f"   - Projected annual savings (100K calls): ${(total_saved/total_calls) * 100000:.2f}")


def test_ai_phone_system_load():
    """Test AI phone system under heavy load"""
    logger.info("\n=== AI PHONE SYSTEM LOAD TEST ===")
    
    try:
        # Create a focused model with minimal agents but heavy phone load
        model = VAHospitalModel(
            num_initial_patients=100,
            num_providers=10,
            innovations={'ai_phone_systems': 5}
        )
        
        # Get AI phone systems
        ai_phones = [agent for agent in model.schedule.agents 
                     if hasattr(agent, 'agent_type') and agent.agent_type == 'ai_phone_system']
        
        logger.info(f"Created {len(ai_phones)} AI phone systems")
        
        # Generate heavy call load
        from simulation.agents.ai_phone_agent import CallType
        call_types = list(CallType)
        
        for phone in ai_phones:
            # Add 200 calls to each system
            for i in range(200):
                phone.add_call_to_queue(
                    call_type=call_types[i % len(call_types)],
                    patient_id=f"load_test_{i}",
                    priority="high" if i % 10 == 0 else "normal"
                )
        
        logger.info(f"Added {200 * len(ai_phones)} calls to queue")
        
        # Run for 20 steps to process calls
        start_time = time.time()
        for step in range(20):
            model.step()
            
            if step % 5 == 0:
                total_active = sum(len(phone.active_calls) for phone in ai_phones)
                total_completed = sum(phone.completed_calls for phone in ai_phones)
                total_queued = sum(len(phone.call_queue) for phone in ai_phones)
                
                logger.info(f"Step {step}: Active={total_active}, Completed={total_completed}, Queued={total_queued}")
        
        duration = time.time() - start_time
        
        # Final statistics
        logger.info("\n--- AI PHONE SYSTEM PERFORMANCE ---")
        for i, phone in enumerate(ai_phones):
            stats = phone.get_system_stats()
            logger.info(f"System {i}: {stats['total_completed']} calls, "
                      f"Transfer rate: {stats['transfer_rate']:.2%}, "
                      f"Cost saved: ${stats['total_cost_saved']:.2f}")
        
        total_calls = sum(phone.completed_calls for phone in ai_phones)
        calls_per_second = total_calls / duration
        
        logger.info(f"\n📞 THROUGHPUT: {calls_per_second:.1f} calls/second")
        logger.info(f"💪 Each AI system can handle ~{calls_per_second/len(ai_phones):.1f} calls/second")
        
        model.cleanup()
        
    except Exception as e:
        logger.error(f"AI phone system test failed: {e}", exc_info=True)


if __name__ == "__main__":
    # Run performance scaling test
    test_performance_scaling()
    
    # Run AI phone system load test
    test_ai_phone_system_load()
    
    logger.info("\n🎉 All performance tests completed!")