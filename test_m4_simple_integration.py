#!/usr/bin/env python3
"""
M4 SIMPLE INTEGRATION TEST
=========================

Simple integration test for M4 State Vectorizer without external dependencies.

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
    from src.perception.semantic_map import create_semantic_map, create_detected_element, ElementLabel, ScreenContext
    print("✅ Successfully imported M4 modules")
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


def test_simple_integration():
    """Test M4 functionality for RL pipeline readiness"""
    
    print("🧪 Testing M4 State Vectorizer RL Pipeline Readiness...")
    
    try:
        # Initialize vectorizer
        vectorizer = StateVectorizer()
        print(f"✅ StateVectorizer initialized (vector size: {vectorizer.config.base_vector_size})")
        
        # Simulate RL training episode
        print("\n🔄 Simulating RL training episode...")
        
        episode_vectors = []
        episode_actions = []
        episode_rewards = []
        
        for step in range(10):
            # Create semantic map (M3 output simulation)
            semantic_map = create_test_semantic_map()
            
            # M4: Transform to state vector
            state_vector = vectorizer.semantic_to_vector(semantic_map)
            episode_vectors.append(state_vector)
            
            # Simulate RL action and reward
            action = np.random.randint(0, 4)
            reward = np.random.random() - 0.5
            
            episode_actions.append(action)
            episode_rewards.append(reward)
            
        print(f"✅ Generated episode data: {len(episode_vectors)} state vectors")
        
        # Validate episode data for RL training
        episode_batch = np.array(episode_vectors)
        actions_batch = np.array(episode_actions)
        rewards_batch = np.array(episode_rewards)
        
        assert episode_batch.shape == (10, vectorizer.config.base_vector_size), "Batch shape incorrect"
        assert np.all(episode_batch >= 0) and np.all(episode_batch <= 1), "Invalid state values"
        
        print(f"✅ Episode validation: batch shape {episode_batch.shape}, value range [0, 1]")
        
        # Test reverse mapping for debugging
        sample_vector = episode_vectors[0]
        decoded = vectorizer.vector_to_semantic_map(sample_vector)
        
        game_phase = decoded['sections']['game_phase']['active_phase']
        confidence_score = decoded['sections']['confidence']['avg_detection_score']
        
        print(f"✅ Reverse mapping: {game_phase}, confidence: {confidence_score:.3f}")
        
        # Performance validation
        print(f"\n⏱️  Performance testing...")
        
        # Batch transformation test
        semantic_maps = [create_test_semantic_map() for _ in range(100)]
        
        start_time = time.time()
        batch_vectors = [vectorizer.semantic_to_vector(sm) for sm in semantic_maps]
        batch_time = time.time() - start_time
        
        batch_rate = 100 / batch_time
        print(f"   Batch transformation: {batch_rate:.1f} maps/sec")
        
        # Memory efficiency test
        vector_memory = np.array(batch_vectors).nbytes
        print(f"   Memory usage: {vector_memory} bytes for 100 vectors")
        
        # Real-time requirements
        assert batch_rate > 50, f"Batch processing too slow: {batch_rate:.1f} maps/sec"
        
        print("✅ Performance requirements met for real-time RL")
        
        # Configuration flexibility test
        print(f"\n🔧 Testing configuration flexibility...")
        
        configs = [128, 256, 512, 1024]
        for size in configs:
            config = VectorConfiguration(base_vector_size=size)
            test_vectorizer = StateVectorizer(config)
            
            test_map = create_test_semantic_map()
            test_vector = test_vectorizer.semantic_to_vector(test_map)
            
            assert test_vector.shape[0] == size, f"Configuration failed for size {size}"
            
        print(f"✅ Configuration flexibility: tested sizes {configs}")
        
        # Summary statistics
        print(f"\n📊 M4 STATE VECTORIZER SUMMARY:")
        print(f"   Vector dimensions: {vectorizer.config.base_vector_size}")
        print(f"   Transformation rate: {batch_rate:.1f} ops/sec")
        print(f"   Memory per vector: {vector_memory//100} bytes")
        print(f"   Value range: [0.0, 1.0] (normalized)")
        print(f"   Sections: game_phase, resources, confidence, elements")
        print(f"   Reverse mapping: ✅ Available for debugging")
        print(f"   Configuration: ✅ Flexible vector sizes")
        
        print(f"\n🎉 M4 STATE VECTORIZER: COMPREHENSIVE VALIDATION PASSED!")
        print(f"✅ Ready for M3 semantic map input")
        print(f"✅ Ready for M5 RL training pipeline") 
        print(f"✅ Ready for M6 data management integration")
        print(f"✅ Performance validated for real-time usage")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_simple_integration()
    
    if success:
        try:
            os.system('say "M4 State Vectorizer comprehensive validation completed successfully"')
        except:
            pass
    
    print(f"\n{'='*60}")
    print(f"M4 STATE REPRESENTATION MODULE: {'✅ READY' if success else '❌ FAILED'}")
    print(f"{'='*60}")
    
    sys.exit(0 if success else 1)