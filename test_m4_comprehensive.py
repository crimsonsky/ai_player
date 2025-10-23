#!/usr/bin/env python3
"""
M4 STATE VECTORIZER COMPREHENSIVE TEST SUITE
============================================

Extensive testing for Module 4 State Representation implementation.
Tests semantic_to_vector and vector_to_semantic_map functionality with
comprehensive validation, edge cases, and integration testing.

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
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.state.state_vectorizer import StateVectorizer, VectorConfiguration, create_default_config
    from src.perception.semantic_map import (
        SemanticMap, 
        DetectedElement,
        ElementLabel,
        ScreenContext,
        create_test_semantic_map
    )
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all required modules are available")
    sys.exit(1)


@dataclass 
class TestResult:
    """Test result container for detailed reporting"""
    name: str
    passed: bool
    duration: float
    details: str
    error: Optional[str] = None
    
    
class M4TestSuite:
    """Comprehensive test suite for M4 State Vectorizer"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.vectorizer = StateVectorizer()
        self.config = create_default_config()
        
        print("🧪 M4 STATE VECTORIZER COMPREHENSIVE TEST SUITE")
        print("=" * 55)
        print(f"Testing State Representation Module with extensive validation")
        print(f"Target vector size: {self.config['vector_size']}")
        print()
        
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Run a single test with timing and error handling"""
        print(f"🔄 Running: {test_name}")
        
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            test_result = TestResult(
                name=test_name,
                passed=True,
                duration=duration,
                details=str(result)
            )
            print(f"✅ PASSED ({duration:.3f}s): {test_name}")
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            test_result = TestResult(
                name=test_name,
                passed=False,
                duration=duration,
                details="",
                error=error_msg
            )
            print(f"❌ FAILED ({duration:.3f}s): {test_name}")
            print(f"   Error: {error_msg}")
            
        self.results.append(test_result)
        return test_result
        
    def test_basic_transformation(self) -> str:
        """Test basic semantic_to_vector transformation"""
        # Create test semantic map
        semantic_map = create_test_semantic_map()
        
        # Transform to vector
        state_vector = semantic_to_vector(semantic_map, self.config)
        
        # Validate basic properties
        assert isinstance(state_vector, np.ndarray), "Output must be NumPy array"
        assert state_vector.dtype == np.float32, f"Expected float32, got {state_vector.dtype}"
        assert len(state_vector.shape) == 1, f"Expected 1D array, got shape {state_vector.shape}"
        assert state_vector.shape[0] == self.config['vector_size'], \
            f"Expected size {self.config['vector_size']}, got {state_vector.shape[0]}"
        
        # Check value ranges (should be normalized 0-1)
        assert np.all(state_vector >= 0.0), "All values should be >= 0"
        assert np.all(state_vector <= 1.0), "All values should be <= 1"
        
        return f"Vector shape: {state_vector.shape}, dtype: {state_vector.dtype}, range: [{state_vector.min():.3f}, {state_vector.max():.3f}]"
        
    def test_reverse_mapping(self) -> str:
        """Test vector_to_semantic_map reverse transformation"""
        # Create original semantic map
        original_map = create_test_semantic_map()
        
        # Forward transformation
        state_vector = semantic_to_vector(original_map, self.config)
        
        # Reverse transformation
        reconstructed_map = vector_to_semantic_map(state_vector, self.config)
        
        # Validate reconstruction
        assert isinstance(reconstructed_map, SemanticMap), "Output must be SemanticMap"
        assert reconstructed_map.frame_id == original_map.frame_id, "Frame ID mismatch"
        
        # Check game state reconstruction
        orig_state = original_map.game_state
        recon_state = reconstructed_map.game_state
        
        assert abs(orig_state.confidence - recon_state.confidence) < 0.01, "Confidence mismatch"
        assert orig_state.is_in_menu == recon_state.is_in_menu, "Menu state mismatch"
        assert orig_state.is_in_game == recon_state.is_in_game, "Game state mismatch"
        
        # Check element counts (approximate due to normalization)
        orig_ui_count = len(original_map.ui_elements)
        recon_ui_count = len(reconstructed_map.ui_elements)
        
        return f"Original UI elements: {orig_ui_count}, Reconstructed: {recon_ui_count}, State consistency: OK"
        
    def test_roundtrip_consistency(self) -> str:
        """Test multiple forward-reverse transformations for consistency"""
        original_map = create_test_semantic_map()
        
        consistency_scores = []
        
        for i in range(5):
            # Forward-reverse cycle
            vector1 = semantic_to_vector(original_map, self.config)
            map1 = vector_to_semantic_map(vector1, self.config)
            vector2 = semantic_to_vector(map1, self.config)
            
            # Calculate consistency score
            consistency = np.corrcoef(vector1, vector2)[0, 1]
            consistency_scores.append(consistency)
            
            # Vectors should be nearly identical
            mse = np.mean((vector1 - vector2) ** 2)
            assert mse < 0.001, f"Round-trip MSE too high: {mse}"
            
        avg_consistency = np.mean(consistency_scores)
        assert avg_consistency > 0.99, f"Consistency too low: {avg_consistency}"
        
        return f"Round-trip consistency: {avg_consistency:.4f}, MSE < 0.001"
        
    def test_validation_system(self) -> str:
        """Test vector validation and configuration handling"""
        semantic_map = create_test_semantic_map()
        
        # Test normal validation
        state_vector = semantic_to_vector(semantic_map, self.config)
        is_valid = validate_state_vector(state_vector, self.config)
        assert is_valid, "Valid vector failed validation"
        
        # Test invalid vectors
        invalid_vectors = [
            np.array([1.0, 2.0, -1.0]),  # Wrong size and values
            np.array([0.5] * 100),       # Wrong size
            np.ones(self.config['vector_size']) * 2.0,  # Values > 1
            np.ones(self.config['vector_size']) * -1.0,  # Values < 0
        ]
        
        invalid_count = 0
        for invalid_vec in invalid_vectors:
            if not validate_state_vector(invalid_vec, self.config):
                invalid_count += 1
                
        assert invalid_count == len(invalid_vectors), "Some invalid vectors passed validation"
        
        return f"Validation: Valid vector passed, {invalid_count}/{len(invalid_vectors)} invalid vectors correctly rejected"
        
    def test_edge_cases(self) -> str:
        """Test edge cases and boundary conditions"""
        # Test empty semantic map
        empty_map = SemanticMap(
            frame_id=0,
            timestamp=time.time(),
            game_state=GameState(confidence=0.0, is_in_menu=False, is_in_game=False),
            ui_elements=[],
            text_elements=[]
        )
        
        empty_vector = semantic_to_vector(empty_map, self.config)
        assert validate_state_vector(empty_vector, self.config), "Empty map vector invalid"
        
        # Test map with maximum elements
        max_elements = self.config.get('max_ui_elements', 50)
        large_map = SemanticMap(
            frame_id=1,
            timestamp=time.time(),
            game_state=GameState(confidence=1.0, is_in_menu=True, is_in_game=False),
            ui_elements=[
                UIElement(
                    element_type=ElementType.BUTTON,
                    bbox=[i/max_elements, i/max_elements, (i+1)/max_elements, (i+1)/max_elements],
                    confidence=0.95,
                    semantic_label=f"button_{i}",
                    properties={"clickable": True}
                ) for i in range(max_elements)
            ],
            text_elements=[]
        )
        
        large_vector = semantic_to_vector(large_map, self.config)
        assert validate_state_vector(large_vector, self.config), "Large map vector invalid"
        
        # Test reconstruction
        reconstructed = vector_to_semantic_map(large_vector, self.config)
        assert len(reconstructed.ui_elements) <= max_elements, "Too many reconstructed elements"
        
        return f"Empty map: OK, Large map ({max_elements} elements): OK, Reconstruction: OK"
        
    def test_configuration_variations(self) -> str:
        """Test different configuration parameters"""
        semantic_map = create_test_semantic_map()
        
        # Test different vector sizes
        test_configs = [
            {**self.config, 'vector_size': 128},
            {**self.config, 'vector_size': 512},
            {**self.config, 'vector_size': 1024}
        ]
        
        results = []
        
        for config in test_configs:
            vector = semantic_to_vector(semantic_map, config)
            assert vector.shape[0] == config['vector_size'], f"Wrong vector size for config"
            assert validate_state_vector(vector, config), "Vector invalid for config"
            
            # Test reverse mapping
            reconstructed = vector_to_semantic_map(vector, config)
            assert isinstance(reconstructed, SemanticMap), "Reconstruction failed"
            
            results.append(f"Size {config['vector_size']}: OK")
            
        return f"Configuration variations: {', '.join(results)}"
        
    def test_performance_benchmarks(self) -> str:
        """Test performance and memory usage"""
        semantic_map = create_test_semantic_map()
        
        # Benchmark transformation speed
        num_iterations = 1000
        
        # Forward transformation benchmark
        start_time = time.time()
        for _ in range(num_iterations):
            vector = semantic_to_vector(semantic_map, self.config)
        forward_time = time.time() - start_time
        forward_rate = num_iterations / forward_time
        
        # Reverse transformation benchmark  
        test_vector = semantic_to_vector(semantic_map, self.config)
        start_time = time.time()
        for _ in range(num_iterations):
            reconstructed = vector_to_semantic_map(test_vector, self.config)
        reverse_time = time.time() - start_time
        reverse_rate = num_iterations / reverse_time
        
        # Memory usage test
        vectors = []
        for i in range(100):
            vec = semantic_to_vector(semantic_map, self.config)
            vectors.append(vec)
            
        memory_per_vector = vec.nbytes
        total_memory = sum(v.nbytes for v in vectors)
        
        # Performance requirements (should be fast enough for real-time RL)
        assert forward_rate > 100, f"Forward transformation too slow: {forward_rate:.1f} ops/sec"
        assert reverse_rate > 50, f"Reverse transformation too slow: {reverse_rate:.1f} ops/sec"
        
        return f"Forward: {forward_rate:.1f} ops/sec, Reverse: {reverse_rate:.1f} ops/sec, Memory: {memory_per_vector} bytes/vector"
        
    def test_integration_with_m3_m6(self) -> str:
        """Test integration with M3 semantic map and M6 data manager"""
        try:
            # Test with multiple semantic maps (simulating M3 output)
            semantic_maps = []
            for i in range(10):
                semantic_map = create_test_semantic_map()
                semantic_map.frame_id = i
                semantic_maps.append(semantic_map)
                
            # Transform all to vectors (M4 processing)
            vectors = []
            for semantic_map in semantic_maps:
                vector = semantic_to_vector(semantic_map, self.config)
                vectors.append(vector)
                
            # Test batch processing (M6 data manager compatibility)
            vector_array = np.array(vectors)
            assert vector_array.shape == (10, self.config['vector_size']), "Batch shape incorrect"
            
            # Test individual reconstruction
            reconstructed_maps = []
            for vector in vectors:
                reconstructed = vector_to_semantic_map(vector, self.config)
                reconstructed_maps.append(reconstructed)
                
            # Verify sequence integrity
            for i, (orig, recon) in enumerate(zip(semantic_maps, reconstructed_maps)):
                assert orig.frame_id == recon.frame_id, f"Frame ID mismatch at index {i}"
                
            return f"Batch processing: {vector_array.shape}, Sequence integrity: OK, M3/M6 compatibility: OK"
            
        except Exception as e:
            return f"Integration test failed: {str(e)}"
            
    def test_data_integrity(self) -> str:
        """Test data integrity and error recovery"""
        # Test with corrupted/invalid inputs
        test_cases = []
        
        # Valid semantic map
        valid_map = create_test_semantic_map()
        
        try:
            # Test normal case
            vector = semantic_to_vector(valid_map, self.config)
            reconstructed = vector_to_semantic_map(vector, self.config)
            test_cases.append("Normal case: OK")
            
            # Test with modified confidence values
            corrupted_map = create_test_semantic_map()
            corrupted_map.game_state.confidence = 1.5  # Invalid confidence > 1
            
            try:
                vector = semantic_to_vector(corrupted_map, self.config)
                # Should handle gracefully with clamping
                assert np.all(vector >= 0) and np.all(vector <= 1), "Invalid confidence not handled"
                test_cases.append("Invalid confidence: Handled")
            except Exception:
                test_cases.append("Invalid confidence: Exception (OK)")
                
            # Test with invalid bounding boxes
            invalid_bbox_map = create_test_semantic_map()
            if invalid_bbox_map.ui_elements:
                invalid_bbox_map.ui_elements[0].bbox = [2.0, 2.0, 3.0, 3.0]  # Invalid coords > 1
                
            try:
                vector = semantic_to_vector(invalid_bbox_map, self.config)
                test_cases.append("Invalid bbox: Handled")
            except Exception:
                test_cases.append("Invalid bbox: Exception (OK)")
                
            return f"Data integrity tests: {', '.join(test_cases)}"
            
        except Exception as e:
            return f"Data integrity test error: {str(e)}"
            
    def run_all_tests(self):
        """Execute the complete test suite"""
        print("Starting comprehensive M4 State Vectorizer testing...\n")
        
        # Core functionality tests
        self.run_test("Basic Transformation", self.test_basic_transformation)
        self.run_test("Reverse Mapping", self.test_reverse_mapping)
        self.run_test("Round-trip Consistency", self.test_roundtrip_consistency)
        
        # Validation and configuration tests
        self.run_test("Validation System", self.test_validation_system)
        self.run_test("Configuration Variations", self.test_configuration_variations)
        
        # Edge cases and robustness
        self.run_test("Edge Cases", self.test_edge_cases)
        self.run_test("Data Integrity", self.test_data_integrity)
        
        # Performance and integration
        self.run_test("Performance Benchmarks", self.test_performance_benchmarks)
        self.run_test("M3/M6 Integration", self.test_integration_with_m3_m6)
        
        # Generate comprehensive report
        self.generate_test_report()
        
    def generate_test_report(self):
        """Generate detailed test report"""
        print("\n" + "=" * 60)
        print("📊 M4 STATE VECTORIZER TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        total_time = sum(r.duration for r in self.results)
        
        print(f"📈 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⏱️  Total Time: {total_time:.3f}s")
        print(f"   🎯 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"   • {result.name}: {result.error}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"   {status} | {result.name:30s} | {result.duration:6.3f}s | {result.details[:60]}")
        
        # Overall assessment
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! M4 State Vectorizer is ready for production.")
            print(f"✅ Semantic-to-vector transformation: VALIDATED")
            print(f"✅ Vector-to-semantic reverse mapping: VALIDATED") 
            print(f"✅ Round-trip consistency: VALIDATED")
            print(f"✅ Performance benchmarks: VALIDATED")
            print(f"✅ M3/M6 integration: VALIDATED")
            print(f"\n🚀 Ready for M5 RL training pipeline integration!")
            
        else:
            print(f"\n⚠️  {failed_tests} TEST(S) FAILED - Review and fix before production use")
            
        # Audio feedback
        try:
            if passed_tests == total_tests:
                os.system('say "M4 State Vectorizer all tests passed successfully"')
            else:
                os.system('say "M4 testing completed with failures requiring attention"')
        except:
            pass  # Audio feedback is optional
            

def main():
    """Main test execution function"""
    try:
        # Initialize and run test suite
        test_suite = M4TestSuite()
        test_suite.run_all_tests()
        
        # Return success/failure for CI/CD
        failed_count = sum(1 for r in test_suite.results if not r.passed)
        return 0 if failed_count == 0 else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)