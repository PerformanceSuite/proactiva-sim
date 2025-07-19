#!/usr/bin/env python3
"""
Test script for the Voice Interface and Natural Language Query system
"""
import asyncio
import json
from api.main import sim_manager, NaturalLanguageQuery

async def test_natural_language_queries():
    """Test various natural language queries"""
    
    print("🎤 Testing PROACTIVA Voice Interface System")
    print("=" * 50)
    
    # Create a test simulation
    from simulation.models.modernized_hospital_model import VAHospitalModel
    
    print("📋 Creating test simulation...")
    model = VAHospitalModel(
        num_initial_patients=100,
        num_providers=20,
        innovations={
            'vr_stations': 5,
            'telehealth_rooms': 3,
            'ai_triage_enabled': True
        }
    )
    
    # Simulate some steps to generate data
    for _ in range(10):
        model.step()
    
    # Add test simulation to manager
    sim_id = "test_voice_sim"
    sim_manager.simulations[sim_id] = {
        'id': sim_id,
        'model': model,
        'config': type('Config', (), {
            'dict': lambda: {
                'vr_stations': 5,
                'telehealth_rooms': 3,
                'ai_triage_enabled': True
            }
        })(),
        'status': 'running',
        'step_count': 10,
        'insights': [
            {
                'description': 'VR therapy reducing patient anxiety by 25%',
                'severity': 'medium',
                'timestamp': '2024-01-15T10:30:00'
            },
            {
                'description': 'Telehealth reducing wait times in primary care',
                'severity': 'high',
                'timestamp': '2024-01-15T11:00:00'
            }
        ]
    }
    
    # Test queries
    test_queries = [
        "What's the current wait time?",
        "How many patients are in the system?",
        "What insights do you have?",
        "How effective is VR therapy?",
        "Show me the telehealth utilization",
        "What's the provider utilization rate?",
        "Give me a status overview"
    ]
    
    print("🤖 Testing Natural Language Queries:")
    print("-" * 30)
    
    for query_text in test_queries:
        print(f"\n👤 User: {query_text}")
        
        query = NaturalLanguageQuery(
            query=query_text,
            include_context=True,
            voice_response=True
        )
        
        try:
            response = await sim_manager.process_natural_language_query(sim_id, query)
            print(f"🤖 AI: {response.response}")
            
            if response.metrics:
                print(f"📊 Metrics: {json.dumps(response.metrics, indent=2)}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Test voice optimization
    print(f"\n🎙️ Testing Voice-Optimized Responses:")
    print("-" * 35)
    
    voice_queries = [
        "Quick status update",
        "Are wait times good?",
        "Any urgent issues?"
    ]
    
    for query_text in voice_queries:
        print(f"\n👤 User (voice): {query_text}")
        
        query = NaturalLanguageQuery(
            query=query_text,
            include_context=False,  # Less context for voice
            voice_response=True     # Optimized for speech
        )
        
        try:
            response = await sim_manager.process_natural_language_query(sim_id, query)
            print(f"🔊 AI (speech): {response.response}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n✅ Voice Interface Testing Complete!")
    print("🎯 Key Features Demonstrated:")
    print("   - Natural language query processing")
    print("   - Context-aware responses")
    print("   - Voice-optimized output")
    print("   - Simulation data integration")
    print("   - Fallback processing (no OpenAI key required)")

if __name__ == "__main__":
    asyncio.run(test_natural_language_queries())