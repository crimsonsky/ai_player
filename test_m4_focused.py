#!/usr/bin/env python3
"""
M4 STATE VECTORIZER FOCUSED TEST SUITE
=====================================

Focused testing for Module 4 State Representation implementation.
Tests the actual StateVectorizer class API with real semantic map data.

Author: Agent B
Version: 1.0
Compliance: AIP-SDS-V2.3 Module 4 specifications
"""

import sys
import os
import time
import traceback
import numpy as np
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.state.state_vectorizer import StateVectorizer, VectorConfiguration
    from src.perception.semantic_map import (
        SemanticMap, 
        DetectedElement,
        ElementLabel,
        ScreenContext,
        create_detected_element,
        create_semantic_map
    )
    print("✅ Successfully imported all required modules")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all required modules are available")
    sys.exit(1)


def create_test_semantic_map() -> SemanticMap:
    """Create a test semantic map for validation"""
    # Create test elements
    elements = [
        create_detected_element(
            label=ElementLabel.BUTTON,
            semantic_value="Single Player",
            bbox=[0.3, 0.2, 0.2, 0.1],
            confidence=0.95
        ),
        create_detected_element(
            label=ElementLabel.MENU_TITLE,
            semantic_value="DUNE LEGACY",
            bbox=[0.25, 0.05, 0.5, 0.08],
            confidence=0.98
        ),
        create_detected_element(
            label=ElementLabel.BUTTON,
            semantic_value="Options",
            bbox=[0.3, 0.35, 0.2, 0.1],
            confidence=0.92
        ),
        create_detected_element(
            label=ElementLabel.RESOURCE_COUNTER,
            semantic_value="450",
            bbox=[0.1, 0.9, 0.1, 0.05],
            confidence=0.88
        )
    ]
    
    # Create semantic map
    return create_semantic_map(
        screen_context=ScreenContext.MAIN_MENU,
        elements=elements,
        screen_resolution=(800, 600),
        capture_source="test_game_window"
    )


def test_basic_functionality():
    """Test basic StateVectorizer functionality"""
    print("\n🔄 Testing basic functionality...")
    
    try:
        # Initialize vectorizer
        vectorizer = StateVectorizer()
        print(f"✅ StateVectorizer initialized with vector size: {vectorizer.config.base_vector_size}")
        
        # Create test semantic map
        test_map = create_test_semantic_map()
        print(f"✅ Test semantic map created with {len(test_map.elements)} elements")
        
        # Test forward transformation
        state_vector = vectorizer.semantic_to_vector(test_map)
        print(f"✅ Forward transformation: {test_map.__class__.__name__} → vector shape {state_vector.shape}")
        
        # Validate vector properties
        assert isinstance(state_vector, np.ndarray), "Output must be NumPy array"
        assert state_vector.dtype == np.float32, f"Expected float32, got {state_vector.dtype}"
        assert len(state_vector.shape) == 1, f"Expected 1D array, got {state_vector.shape}"
        assert state_vector.shape[0] == vectorizer.config.base_vector_size, "Vector size mismatch"
        assert np.all(state_vector >= 0.0), "Vector values should be >= 0"
        assert np.all(state_vector <= 1.0), "Vector values should be <= 1"
        
        print(f"✅ Vector validation passed: range [{state_vector.min():.3f}, {state_vector.max():.3f}]")
        
        # Test reverse transformation
        decoded_info = vectorizer.vector_to_semantic_map(state_vector)
        print(f"✅ Reverse transformation: vector → semantic info with {len(decoded_info['sections'])} sections")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_vector_consistency():
    """Test vector consistency and round-trip accuracy"""
    print("\n🔄 Testing vector consistency...")
    
    try:
        vectorizer = StateVectorizer()
        test_map = create_test_semantic_map()
        
        # Multiple transformations
        vectors = []
        for i in range(5):
            vector = vectorizer.semantic_to_vector(test_map)
            vectors.append(vector)
            
        # Check consistency
        for i in range(1, len(vectors)):
            consistency = np.corrcoef(vectors[0], vectors[i])[0, 1]
            assert consistency > 0.99, f"Consistency too low: {consistency}"
            
        print(f"✅ Vector consistency validated across {len(vectors)} transformations")
        
        # Test round-trip
        original_vector = vectors[0]
        decoded = vectorizer.vector_to_semantic_map(original_vector)
        
        # Check decoded information makes sense
        assert 'sections' in decoded, "Missing sections in decoded output"
        assert 'game_phase' in decoded['sections'], "Missing game_phase section"
        assert 'confidence' in decoded['sections'], "Missing confidence section"
        
        print("✅ Round-trip consistency validated")
        return True
        
    except Exception as e:
        print(f"❌ Consistency test failed: {e}")
        traceback.print_exc()
        return False


def test_different_screen_contexts():
    """Test vectorizer with different screen contexts"""
    print("\n🔄 Testing different screen contexts...")
    
    try:
        vectorizer = StateVectorizer()
        
        # Test different screen contexts
        contexts = [ScreenContext.MAIN_MENU, ScreenContext.IN_GAME, ScreenContext.LOADING]
        results = []
        
        for context in contexts:
            test_map = create_test_semantic_map()
            test_map.screen_context = context
            
            vector = vectorizer.semantic_to_vector(test_map)
            decoded = vectorizer.vector_to_semantic_map(vector)
            
            game_phase = decoded['sections']['game_phase']
            results.append(f"{context.value}: {game_phase['active_phase']}")
            
        print(f"✅ Screen contexts tested: {', '.join(results)}")
        return True
        
    except Exception as e:
        print(f"❌ Screen context test failed: {e}")
        traceback.print_exc()
        return False


def test_performance():
    """Test performance benchmarks"""
    print("\n🔄 Testing performance...")
    
    try:
        vectorizer = StateVectorizer()
        test_map = create_test_semantic_map()
        
        # Forward transformation benchmark
        num_iterations = 1000
        start_time = time.time()
        
        for _ in range(num_iterations):
            vector = vectorizer.semantic_to_vector(test_map)
            
        forward_time = time.time() - start_time
        forward_rate = num_iterations / forward_time
        
        print(f"✅ Forward transformation: {forward_rate:.1f} ops/sec")
        
        # Reverse transformation benchmark
        test_vector = vectorizer.semantic_to_vector(test_map)
        start_time = time.time()
        
        for _ in range(num_iterations):
            decoded = vectorizer.vector_to_semantic_map(test_vector)
            
        reverse_time = time.time() - start_time
        reverse_rate = num_iterations / reverse_time
        
        print(f"✅ Reverse transformation: {reverse_rate:.1f} ops/sec")
        
        # Performance requirements
        assert forward_rate > 100, f"Forward transformation too slow: {forward_rate:.1f} ops/sec"
        assert reverse_rate > 50, f"Reverse transformation too slow: {reverse_rate:.1f} ops/sec"
        
        print("✅ Performance requirements met")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🔄 Testing edge cases...")
    
    try:
        vectorizer = StateVectorizer()
        
        # Test with empty semantic map
        empty_map = SemanticMap(
            timestamp=time.time(),
            screen_context=ScreenContext.UNKNOWN,
            elements=[]
        )
        
        empty_vector = vectorizer.semantic_to_vector(empty_map)
        assert isinstance(empty_vector, np.ndarray), "Empty map should produce valid vector"
        print("✅ Empty semantic map handled correctly")
        
        # Test with maximum elements
        large_map = create_test_semantic_map()
        # Add more elements to test capacity
        for i in range(20):
            # Create normalized coordinates within 0-1 range
            x = (i % 5) * 0.2  # 5 columns
            y = (i // 5) * 0.2  # 4 rows
            w = min(0.15, 1.0 - x)  # Width constraint
            h = min(0.15, 1.0 - y)  # Height constraint
            
            element = DetectedElement(
                label=ElementLabel.BUTTON,
                semantic_value=f"Button_{i}",
                bbox=[x, y, w, h],
                confidence=0.9,
                attributes={}
            )
            large_map.elements.append(element)
            
        large_vector = vectorizer.semantic_to_vector(large_map)
        assert isinstance(large_vector, np.ndarray), "Large map should produce valid vector"
        print(f"✅ Large semantic map ({len(large_map.elements)} elements) handled correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        traceback.print_exc()
        return False


def test_configuration_options():
    """Test different configuration options"""
    print("\n🔄 Testing configuration options...")
    
    try:
        # Test different vector sizes
        configs = [
            VectorConfiguration(base_vector_size=128),
            VectorConfiguration(base_vector_size=256),
            VectorConfiguration(base_vector_size=512)
        ]
        
        test_map = create_test_semantic_map()
        
        for config in configs:
            vectorizer = StateVectorizer(config)
            vector = vectorizer.semantic_to_vector(test_map)
            
            assert vector.shape[0] == config.base_vector_size, f"Vector size mismatch for config"
            print(f"✅ Configuration with vector size {config.base_vector_size}: OK")
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False


def run_comprehensive_tests():
    """Run all tests and generate report"""
    print("🧪 M4 STATE VECTORIZER COMPREHENSIVE TESTING")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Vector Consistency", test_vector_consistency),
        ("Screen Contexts", test_different_screen_contexts),
        ("Performance Benchmarks", test_performance),
        ("Edge Cases", test_edge_cases),
        ("Configuration Options", test_configuration_options),
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
        
    total_time = time.time() - start_time
    
    # Generate report
    print(f"\n{'='*60}")
    print("📊 M4 STATE VECTORIZER TEST REPORT")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"📈 SUMMARY:")
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {total - passed}")
    print(f"   ⏱️  Total Time: {total_time:.3f}s")
    print(f"   🎯 Success Rate: {(passed/total)*100:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} | {test_name}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ M4 State Vectorizer is ready for M3→M5 pipeline integration!")
        
        # Audio feedback
        try:
            os.system('say "M4 State Vectorizer all tests passed successfully"')
        except:
            pass
            
        return True
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("❌ Review implementation before production use")
        
        try:
            os.system('say "M4 testing completed with failures"')
        except:
            pass
            
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)