#!/usr/bin/env python3
"""
M4-M6 INTEGRATION VALIDATION TEST
===============================

Tests the integration between M4 State Vectorizer and M6 Data Manager
for RL training pipeline compatibility.

Author: Agent B
Version: 1.0
"""

import sys
import os
import time
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.state.state_vectorizer import StateVectorizer, VectorConfiguration
    from src.mlops.data_manager import ExperienceReplayBuffer, NumericalIOManager
    from src.perception.semantic_map import create_semantic_map, create_detected_element, ElementLabel, ScreenContext
    print("✅ Successfully imported M4 and M6 modules")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)


def create_test_semantic_map():
    """Create test semantic map"""
    elements = [
        create_detected_element(
            label=ElementLabel.BUTTON,
            semantic_value="Single Player",
            bbox=[0.3, 0.2, 0.2, 0.1],
            confidence=0.95
        ),
        create_detected_element(
            label=ElementLabel.RESOURCE_COUNTER,
            semantic_value="450",
            bbox=[0.1, 0.9, 0.1, 0.05],
            confidence=0.88
        )
    ]
    
    return create_semantic_map(
        screen_context=ScreenContext.IN_GAME,
        elements=elements,
        screen_resolution=(800, 600)
    )


def test_m4_m6_integration():
    """Test M4 State Vectorizer integration with M6 Data Manager"""
    
    print("🧪 Testing M4-M6 Integration for RL Pipeline...")
    
    try:
        # Initialize M4 State Vectorizer
        vectorizer = StateVectorizer()
        print(f"✅ M4 StateVectorizer initialized (vector size: {vectorizer.config.base_vector_size})")
        
        # Initialize M6 Experience Replay Buffer
        state_shape = (vectorizer.config.base_vector_size,)
        buffer = ExperienceReplayBuffer(capacity=1000, state_shape=state_shape)
        print(f"✅ M6 ExperienceReplayBuffer initialized (capacity: 1000, state_shape: {state_shape})")
        
        # Generate test data for RL training pipeline
        print("\n🔄 Generating RL training data...")
        
        for episode in range(10):
            for step in range(20):
                # Create semantic map (simulating M3 output)
                semantic_map = create_test_semantic_map()
                
                # M4: Transform to state vector
                state_vector = vectorizer.semantic_to_vector(semantic_map)
                
                # Simulate RL action and reward
                action = np.random.randint(0, 4)  # 4 possible actions
                reward = np.random.random() - 0.5  # Random reward [-0.5, 0.5]
                
                # Create next state
                next_semantic_map = create_test_semantic_map() 
                next_state_vector = vectorizer.semantic_to_vector(next_semantic_map)
                
                # Episode termination
                done = (step == 19)  # Last step of episode
                
                # M6: Store experience in replay buffer
                buffer.add_experience(state_vector, action, reward, next_state_vector, done)
                
        print(f"✅ Generated training data: {buffer.total_added} experiences")
        
        # Test M6 batch sampling for RL training
        if buffer.is_ready(32):
            batch = buffer.sample_batch(32)
            print(f"✅ M6 batch sampling: {[(k, v.shape) for k, v in batch.items()]}")
            
            # Validate batch compatibility with M4 vectors
            states_batch = batch['states']
            assert states_batch.shape == (32, vectorizer.config.base_vector_size), "Batch shape mismatch"
            assert np.all(states_batch >= 0) and np.all(states_batch <= 1), "Invalid state values"
            print("✅ Batch validation: Compatible with M4 state vectors")
            
        # Test M4 reverse mapping on batch data
        sample_vector = batch['states'][0]
        decoded_info = vectorizer.vector_to_semantic_map(sample_vector)
        print(f"✅ M4 reverse mapping: Decoded {len(decoded_info['sections'])} sections from batch vector")
        
        # Test M6 high-speed I/O with M4 vectors
        test_vectors = np.array([vectorizer.semantic_to_vector(create_test_semantic_map()) for _ in range(100)])
        
        # Save and load test
        NumericalIOManager.save_state_vector('test_vectors.h5', test_vectors, 
                                           metadata={'source': 'M4_vectorizer', 'count': 100})
        
        loaded_vectors, metadata = NumericalIOManager.load_state_vector('test_vectors.h5')
        
        assert np.allclose(test_vectors, loaded_vectors), "Vector I/O inconsistency"
        assert metadata['source'] == 'M4_vectorizer', "Metadata mismatch"
        print(f"✅ M6 I/O validation: {loaded_vectors.shape} vectors saved/loaded successfully")
        
        # Cleanup
        if os.path.exists('test_vectors.h5'):
            os.remove('test_vectors.h5')
            
        # Performance validation for real-time RL
        print(f"\n⏱️  Performance validation:")
        
        # Test M4 transformation speed
        semantic_map = create_test_semantic_map()
        start_time = time.time()
        for _ in range(1000):
            _ = vectorizer.semantic_to_vector(semantic_map)
        m4_time = time.time() - start_time
        m4_rate = 1000 / m4_time
        
        # Test M6 buffer operations
        test_vector = vectorizer.semantic_to_vector(semantic_map)
        start_time = time.time()
        for _ in range(1000):
            buffer.add_experience(test_vector, 0, 0.0, test_vector, False)
        m6_time = time.time() - start_time
        m6_rate = 1000 / m6_time
        
        print(f"   M4 vectorization: {m4_rate:.1f} ops/sec")
        print(f"   M6 buffer ops: {m6_rate:.1f} ops/sec")
        
        # Real-time requirements check
        assert m4_rate > 1000, f"M4 too slow for real-time RL: {m4_rate:.1f} ops/sec"
        assert m6_rate > 5000, f"M6 too slow for real-time RL: {m6_rate:.1f} ops/sec"
        
        print("✅ Performance requirements met for real-time RL training")
        
        # Buffer statistics
        stats = buffer.get_statistics()
        print(f"\n📊 M6 Buffer Statistics:")
        print(f"   Capacity: {stats['capacity']}")
        print(f"   Current size: {stats['current_size']}")
        print(f"   Utilization: {stats['utilization']:.1%}")
        print(f"   Total added: {stats['total_added']}")
        print(f"   Total sampled: {stats['total_sampled']}")
        
        print(f"\n🎉 M4-M6 INTEGRATION: ALL TESTS PASSED!")
        print(f"✅ State vectorization pipeline ready for M5 RL training")
        print(f"✅ Data management pipeline ready for production ML")
        print(f"✅ Real-time performance validated")
        
        return True
        
    except Exception as e:
        print(f"❌ M4-M6 Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_m4_m6_integration()
    
    if success:
        try:
            os.system('say "M4 M6 integration testing completed successfully"')
        except:
            pass
    
    sys.exit(0 if success else 1)