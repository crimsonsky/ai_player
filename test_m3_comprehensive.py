"""
COMPREHENSIVE M3 PIPELINE VALIDATION SUITE
Extensive testing for YOLOv8 Detection Engine and complete perception pipeline

Test Categories:
1. Unit Tests - Individual component validation
2. Integration Tests - Cross-module functionality  
3. Performance Tests - Benchmark and optimization validation
4. Error Handling Tests - Robustness and edge cases
5. Agent B Integration Tests - MLOps pipeline compatibility
6. Multi-Resolution Tests - Various screen sizes and formats
7. Memory and Resource Tests - Resource usage validation

Author: Agent A
Compliance: AIP-SDS-V2.3 Module 3 comprehensive validation
"""

import sys
from pathlib import Path
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import psutil
import gc
import traceback
from typing import List, Dict, Tuple, Any
import threading
import random

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from src.perception.screen_capture import GameScreenCapture
    from src.perception.yolo_detection_engine import YOLODetectionEngine, run_complete_perception_pipeline
    from src.perception.semantic_map import SemanticMap, DetectedElement, ElementLabel
    MODULES_AVAILABLE = True
    print("✅ All M3 modules imported successfully")
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    MODULES_AVAILABLE = False


class M3TestSuite:
    """Comprehensive test suite for M3 YOLOv8 pipeline validation"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.error_log = []
        self.start_time = time.time()
        
    def log_result(self, test_name: str, passed: bool, details: str = "", metrics: Dict = None):
        """Log test result with details"""
        self.test_results[test_name] = {
            'passed': passed,
            'details': details,
            'timestamp': time.time(),
            'metrics': metrics or {}
        }
        
        status = "✅ PASS" if passed else "❌ FAIL" 
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")
        if metrics:
            for key, value in metrics.items():
                print(f"   {key}: {value}")
    
    def log_error(self, test_name: str, error: Exception):
        """Log error with full traceback"""
        error_info = {
            'test': test_name,
            'error': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': time.time()
        }
        self.error_log.append(error_info)
        print(f"❌ ERROR in {test_name}: {error}")
    
    def create_test_images(self) -> List[Tuple[str, Image.Image]]:
        """Create diverse test images for comprehensive validation"""
        test_images = []
        
        # 1. Standard game resolution (1920x1080)
        img1 = self._create_standard_game_ui()
        test_images.append(("standard_1920x1080", img1))
        
        # 2. High resolution (2560x1440) 
        img2 = self._create_high_res_ui()
        test_images.append(("high_res_2560x1440", img2))
        
        # 3. Windowed mode (1280x720)
        img3 = self._create_windowed_ui()
        test_images.append(("windowed_1280x720", img3))
        
        # 4. Complex UI with many elements
        img4 = self._create_complex_ui()
        test_images.append(("complex_ui_elements", img4))
        
        # 5. Minimal UI (edge case)
        img5 = self._create_minimal_ui()
        test_images.append(("minimal_ui", img5))
        
        # 6. Dark theme variant
        img6 = self._create_dark_theme_ui()
        test_images.append(("dark_theme", img6))
        
        return test_images
    
    def _create_standard_game_ui(self) -> Image.Image:
        """Create standard 1920x1080 Dune Legacy UI"""
        img = Image.new('RGB', (1920, 1080), color=(40, 45, 60))
        draw = ImageDraw.Draw(img)
        
        # Title bar
        draw.rectangle([0, 0, 1920, 80], fill=(20, 25, 35))
        draw.text((860, 30), "DUNE LEGACY", fill=(255, 215, 100))
        
        # Version
        draw.text((950, 90), "v0.96.4", fill=(180, 180, 200))
        
        # Main menu buttons
        buttons = [
            (760, 200, 1160, 260, "Single Player"),
            (760, 280, 1160, 340, "Multiplayer"),
            (760, 360, 1160, 420, "Campaign"), 
            (760, 440, 1160, 500, "Custom Game"),
            (760, 520, 1160, 580, "Options"),
            (760, 600, 1160, 660, "Exit")
        ]
        
        for x1, y1, x2, y2, text in buttons:
            draw.rectangle([x1, y1, x2, y2], fill=(70, 90, 130), outline=(150, 180, 255), width=3)
            draw.text((x1 + 30, y1 + 20), text, fill=(255, 255, 255))
        
        # Resource display
        draw.rectangle([50, 50, 300, 120], fill=(80, 60, 30), outline=(160, 120, 60), width=2)
        draw.text((70, 70), "Credits: 5000", fill=(255, 255, 150))
        draw.text((70, 95), "Spice: 2500", fill=(255, 200, 100))
        
        return img
    
    def _create_high_res_ui(self) -> Image.Image:
        """Create high resolution 2560x1440 UI"""
        img = Image.new('RGB', (2560, 1440), color=(35, 40, 55))
        draw = ImageDraw.Draw(img)
        
        # Scale everything up proportionally
        draw.rectangle([0, 0, 2560, 100], fill=(15, 20, 30))
        draw.text((1180, 40), "DUNE LEGACY - HIGH RES", fill=(255, 220, 120))
        
        # Larger buttons for high res
        buttons = [
            (1080, 300, 1480, 380, "Single Player"),
            (1080, 400, 1480, 480, "Multiplayer"),
            (1080, 500, 1480, 580, "Options")
        ]
        
        for x1, y1, x2, y2, text in buttons:
            draw.rectangle([x1, y1, x2, y2], fill=(80, 100, 140), outline=(160, 200, 255), width=4)
            draw.text((x1 + 40, y1 + 25), text, fill=(255, 255, 255))
        
        return img
    
    def _create_windowed_ui(self) -> Image.Image:
        """Create windowed mode 1280x720 UI"""
        img = Image.new('RGB', (1280, 720), color=(50, 55, 70))
        draw = ImageDraw.Draw(img)
        
        # Compact layout for smaller window
        draw.text((540, 50), "DUNE LEGACY", fill=(255, 200, 80))
        
        buttons = [
            (440, 150, 840, 200, "Single Player"),
            (440, 220, 840, 270, "Multiplayer"),
            (440, 290, 840, 340, "Exit")
        ]
        
        for x1, y1, x2, y2, text in buttons:
            draw.rectangle([x1, y1, x2, y2], fill=(60, 80, 120), outline=(140, 170, 240), width=2)
            draw.text((x1 + 20, y1 + 15), text, fill=(255, 255, 255))
        
        return img
    
    def _create_complex_ui(self) -> Image.Image:
        """Create UI with many elements for stress testing"""
        img = Image.new('RGB', (1920, 1080), color=(30, 35, 50))
        draw = ImageDraw.Draw(img)
        
        # Many UI elements
        for i in range(20):
            x = 100 + (i % 5) * 300
            y = 100 + (i // 5) * 150
            draw.rectangle([x, y, x + 200, y + 80], fill=(random.randint(50, 100), random.randint(70, 120), random.randint(90, 140)))
            draw.text((x + 10, y + 30), f"Element {i+1}", fill=(255, 255, 255))
        
        return img
    
    def _create_minimal_ui(self) -> Image.Image:
        """Create minimal UI (edge case)"""
        img = Image.new('RGB', (800, 600), color=(20, 20, 25))
        draw = ImageDraw.Draw(img)
        
        # Just one element
        draw.rectangle([300, 250, 500, 300], fill=(60, 60, 80))
        draw.text((350, 270), "MENU", fill=(200, 200, 200))
        
        return img
    
    def _create_dark_theme_ui(self) -> Image.Image:
        """Create dark theme UI variant"""
        img = Image.new('RGB', (1920, 1080), color=(10, 10, 15))
        draw = ImageDraw.Draw(img)
        
        # Dark theme styling
        draw.rectangle([760, 200, 1160, 260], fill=(25, 25, 30), outline=(80, 80, 90), width=2)
        draw.text((880, 225), "Dark Theme", fill=(180, 180, 190))
        
        return img
    
    def test_unit_yolo_engine_initialization(self):
        """Test YOLOv8 engine initialization with various configurations"""
        try:
            # Test default initialization
            engine1 = YOLODetectionEngine()
            assert engine1 is not None, "Engine initialization failed"
            
            # Test with specific device configuration
            engine2 = YOLODetectionEngine(use_mps=False)  # Force CPU for Intel
            assert engine2.device.type in ['cpu', 'cuda'], f"Unexpected device: {engine2.device}"
            
            # Test device detection
            device_info = {
                'device_type': engine1.device.type,
                'device_available': True
            }
            
            self.log_result("unit_yolo_initialization", True, 
                          f"Engine initialized successfully on {engine1.device}", device_info)
            
        except Exception as e:
            self.log_error("unit_yolo_initialization", e)
            self.log_result("unit_yolo_initialization", False, str(e))
    
    def test_unit_inference_functionality(self):
        """Test core inference functionality with various inputs"""
        try:
            engine = YOLODetectionEngine()
            test_images = self.create_test_images()
            
            inference_results = {}
            
            for name, img in test_images:
                start_time = time.time()
                results = engine.run_yolo_inference(img)
                inference_time = time.time() - start_time
                
                # Validate result structure
                assert 'boxes' in results, "Missing 'boxes' in results"
                assert 'labels' in results, "Missing 'labels' in results" 
                assert 'scores' in results, "Missing 'scores' in results"
                assert 'image_size' in results, "Missing 'image_size' in results"
                
                inference_results[name] = {
                    'inference_time': inference_time,
                    'detections': len(results['boxes']),
                    'resolution': img.size
                }
            
            avg_inference_time = np.mean([r['inference_time'] for r in inference_results.values()])
            
            self.log_result("unit_inference_functionality", True,
                          f"All inference tests passed - Avg time: {avg_inference_time:.3f}s",
                          inference_results)
            
        except Exception as e:
            self.log_error("unit_inference_functionality", e)
            self.log_result("unit_inference_functionality", False, str(e))
    
    def test_unit_semantic_mapping(self):
        """Test semantic mapping functionality"""
        try:
            engine = YOLODetectionEngine()
            test_img = self.create_test_images()[0][1]  # Use standard image
            
            # Get raw detections
            raw_results = engine.run_yolo_inference(test_img)
            
            # Test semantic mapping
            semantic_map = engine.process_detections(raw_results, test_img)
            
            # Validate SemanticMap structure
            assert isinstance(semantic_map, SemanticMap), "Must return SemanticMap instance"
            assert hasattr(semantic_map, 'elements'), "Missing elements attribute"
            assert hasattr(semantic_map, 'timestamp'), "Missing timestamp"
            assert semantic_map.screen_resolution == test_img.size, "Resolution mismatch"
            
            # Validate DetectedElement structure
            for element in semantic_map.elements:
                assert isinstance(element, DetectedElement), "Invalid element type"
                assert hasattr(element, 'bounding_box'), "Missing bounding_box"
                assert hasattr(element, 'confidence_score'), "Missing confidence_score"
                assert 0 <= element.confidence_score <= 1, "Invalid confidence range"
            
            mapping_metrics = {
                'total_elements': len(semantic_map.elements),
                'avg_confidence': np.mean([e.confidence_score for e in semantic_map.elements]) if semantic_map.elements else 0,
                'element_types': list(set([str(e.element_label) for e in semantic_map.elements]))
            }
            
            self.log_result("unit_semantic_mapping", True,
                          f"Semantic mapping successful - {len(semantic_map.elements)} elements",
                          mapping_metrics)
            
        except Exception as e:
            self.log_error("unit_semantic_mapping", e)
            self.log_result("unit_semantic_mapping", False, str(e))
    
    def test_performance_benchmarks(self):
        """Comprehensive performance testing"""
        try:
            engine = YOLODetectionEngine()
            test_images = self.create_test_images()
            
            # Warmup
            warmup_img = test_images[0][1]
            for _ in range(3):
                engine.run_yolo_inference(warmup_img)
            
            # Performance benchmark
            performance_data = {}
            
            for name, img in test_images:
                times = []
                fps_list = []
                
                # Run multiple inferences for statistical accuracy
                for _ in range(10):
                    start = time.time()
                    results = engine.run_yolo_inference(img)
                    inference_time = time.time() - start
                    times.append(inference_time)
                    fps_list.append(1.0 / inference_time if inference_time > 0 else 0)
                
                performance_data[name] = {
                    'min_time': min(times),
                    'max_time': max(times),
                    'avg_time': np.mean(times),
                    'std_time': np.std(times),
                    'avg_fps': np.mean(fps_list),
                    'resolution': img.size,
                    'pixels': img.size[0] * img.size[1]
                }
            
            # Overall performance metrics
            all_times = [metrics['avg_time'] for metrics in performance_data.values()]
            all_fps = [metrics['avg_fps'] for metrics in performance_data.values()]
            
            overall_metrics = {
                'overall_avg_fps': np.mean(all_fps),
                'min_fps': min(all_fps),
                'max_fps': max(all_fps),
                'target_fps': 30.0,
                'meets_target': min(all_fps) >= 30.0
            }
            
            self.log_result("performance_benchmarks", True,
                          f"Performance test complete - Avg FPS: {overall_metrics['overall_avg_fps']:.1f}",
                          {**overall_metrics, 'detailed_results': performance_data})
            
        except Exception as e:
            self.log_error("performance_benchmarks", e)
            self.log_result("performance_benchmarks", False, str(e))
    
    def test_error_handling_robustness(self):
        """Test error handling and edge cases"""
        try:
            engine = YOLODetectionEngine()
            error_test_results = {}
            
            # Test 1: Invalid image formats
            try:
                # Corrupted image
                corrupt_img = Image.new('RGB', (100, 100))
                corrupt_img.putpixel((50, 50), (999, 999, 999))  # Invalid values should be handled
                results = engine.run_yolo_inference(corrupt_img)
                error_test_results['corrupt_image'] = 'handled_gracefully'
            except Exception as e:
                error_test_results['corrupt_image'] = f'failed: {e}'
            
            # Test 2: Very small images
            try:
                tiny_img = Image.new('RGB', (10, 10), color=(128, 128, 128))
                results = engine.run_yolo_inference(tiny_img)
                error_test_results['tiny_image'] = 'handled_gracefully'
            except Exception as e:
                error_test_results['tiny_image'] = f'failed: {e}'
            
            # Test 3: Very large images
            try:
                large_img = Image.new('RGB', (4000, 3000), color=(64, 64, 64))
                results = engine.run_yolo_inference(large_img)
                error_test_results['large_image'] = 'handled_gracefully'
            except Exception as e:
                error_test_results['large_image'] = f'failed: {e}'
            
            # Test 4: Unusual aspect ratios
            try:
                wide_img = Image.new('RGB', (3000, 100), color=(100, 100, 100))
                results = engine.run_yolo_inference(wide_img)
                error_test_results['wide_aspect'] = 'handled_gracefully'
            except Exception as e:
                error_test_results['wide_aspect'] = f'failed: {e}'
            
            passed_tests = sum(1 for result in error_test_results.values() if 'handled_gracefully' in result)
            total_tests = len(error_test_results)
            
            self.log_result("error_handling_robustness", passed_tests == total_tests,
                          f"Passed {passed_tests}/{total_tests} error handling tests",
                          error_test_results)
            
        except Exception as e:
            self.log_error("error_handling_robustness", e)
            self.log_result("error_handling_robustness", False, str(e))
    
    def test_memory_resource_usage(self):
        """Test memory usage and resource management"""
        try:
            # Baseline memory usage
            gc.collect()
            baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            engine = YOLODetectionEngine()
            
            # Memory after engine initialization
            engine_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Run inference loop to test memory leaks
            test_img = self.create_test_images()[0][1]
            
            memory_samples = []
            for i in range(20):
                results = engine.run_yolo_inference(test_img)
                semantic_map = engine.process_detections(results, test_img)
                
                if i % 5 == 0:  # Sample every 5 iterations
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)
            
            # Final memory check
            gc.collect()
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            memory_metrics = {
                'baseline_mb': baseline_memory,
                'engine_init_mb': engine_memory,
                'final_memory_mb': final_memory,
                'memory_increase_mb': final_memory - baseline_memory,
                'max_memory_mb': max(memory_samples),
                'memory_stable': abs(memory_samples[-1] - memory_samples[0]) < 50,  # < 50MB drift
                'samples': memory_samples
            }
            
            # Memory usage should be reasonable and stable
            memory_reasonable = memory_metrics['memory_increase_mb'] < 500  # < 500MB increase
            
            self.log_result("memory_resource_usage", memory_reasonable and memory_metrics['memory_stable'],
                          f"Memory usage: {memory_metrics['memory_increase_mb']:.1f}MB increase",
                          memory_metrics)
            
        except Exception as e:
            self.log_error("memory_resource_usage", e)
            self.log_result("memory_resource_usage", False, str(e))
    
    def test_agent_b_integration(self):
        """Test integration with Agent B's MLOps infrastructure"""
        try:
            integration_results = {}
            
            # Test MLOps imports
            try:
                from src.mlops.data_manager import ExperienceReplayBuffer
                integration_results['mlops_import'] = 'success'
            except ImportError:
                integration_results['mlops_import'] = 'not_available'
            
            try:
                from src.mlops.dlat_annotation_tool import BoundingBox
                integration_results['dlat_import'] = 'success'
            except ImportError:
                integration_results['dlat_import'] = 'not_available'
            
            # Test YOLOv8 engine MLOps integration
            engine = YOLODetectionEngine()
            if hasattr(engine, 'experience_buffer'):
                integration_results['experience_buffer'] = 'integrated'
            else:
                integration_results['experience_buffer'] = 'not_integrated'
            
            # Test data compatibility
            test_img = self.create_test_images()[0][1]
            results = engine.run_yolo_inference(test_img)
            semantic_map = engine.process_detections(results, test_img)
            
            # Verify data can be serialized for MLOps pipeline
            try:
                json_data = {
                    'timestamp': semantic_map.timestamp,
                    'resolution': semantic_map.screen_resolution,
                    'elements': len(semantic_map.elements)
                }
                json.dumps(json_data)  # Test serialization
                integration_results['data_serialization'] = 'compatible'
            except:
                integration_results['data_serialization'] = 'incompatible'
            
            integration_score = sum(1 for result in integration_results.values() if result in ['success', 'integrated', 'compatible'])
            total_checks = len(integration_results)
            
            self.log_result("agent_b_integration", integration_score >= 2,
                          f"Integration check: {integration_score}/{total_checks} components ready",
                          integration_results)
            
        except Exception as e:
            self.log_error("agent_b_integration", e)
            self.log_result("agent_b_integration", False, str(e))
    
    def test_multi_resolution_compatibility(self):
        """Test compatibility across multiple screen resolutions"""
        try:
            engine = YOLODetectionEngine()
            
            # Test various resolutions
            resolutions = [
                (800, 600, "SVGA"),
                (1024, 768, "XGA"),
                (1280, 720, "HD"),
                (1366, 768, "WXGA"),
                (1920, 1080, "FHD"),
                (2560, 1440, "QHD"),
                (3840, 2160, "4K")
            ]
            
            resolution_results = {}
            
            for width, height, name in resolutions:
                try:
                    # Create test image for this resolution
                    test_img = Image.new('RGB', (width, height), color=(50, 60, 80))
                    draw = ImageDraw.Draw(test_img)
                    
                    # Add some UI elements scaled to resolution
                    scale = min(width, height) / 1080
                    button_width = int(200 * scale)
                    button_height = int(50 * scale)
                    
                    draw.rectangle([
                        width//2 - button_width//2,
                        height//2 - button_height//2,
                        width//2 + button_width//2,
                        height//2 + button_height//2
                    ], fill=(100, 120, 160))
                    
                    # Test inference
                    start_time = time.time()
                    results = engine.run_yolo_inference(test_img)
                    inference_time = time.time() - start_time
                    
                    # Test semantic mapping
                    semantic_map = engine.process_detections(results, test_img)
                    
                    resolution_results[name] = {
                        'resolution': f"{width}x{height}",
                        'inference_time': inference_time,
                        'fps': 1.0 / inference_time,
                        'detections': len(semantic_map.elements),
                        'success': True
                    }
                    
                except Exception as e:
                    resolution_results[name] = {
                        'resolution': f"{width}x{height}",
                        'success': False,
                        'error': str(e)
                    }
            
            successful_resolutions = sum(1 for r in resolution_results.values() if r.get('success', False))
            total_resolutions = len(resolutions)
            
            avg_fps = np.mean([r['fps'] for r in resolution_results.values() if r.get('success', False)])
            
            self.log_result("multi_resolution_compatibility", successful_resolutions == total_resolutions,
                          f"Compatible with {successful_resolutions}/{total_resolutions} resolutions - Avg FPS: {avg_fps:.1f}",
                          resolution_results)
            
        except Exception as e:
            self.log_error("multi_resolution_compatibility", e)
            self.log_result("multi_resolution_compatibility", False, str(e))
    
    def test_concurrent_processing(self):
        """Test concurrent/threaded processing capability"""
        try:
            engine = YOLODetectionEngine()
            test_images = self.create_test_images()[:3]  # Use first 3 test images
            
            concurrent_results = {}
            
            def process_image(name, img):
                try:
                    start_time = time.time()
                    results = engine.run_yolo_inference(img)
                    semantic_map = engine.process_detections(results, img)
                    processing_time = time.time() - start_time
                    
                    return {
                        'name': name,
                        'success': True,
                        'processing_time': processing_time,
                        'detections': len(semantic_map.elements)
                    }
                except Exception as e:
                    return {
                        'name': name,
                        'success': False,
                        'error': str(e)
                    }
            
            # Test sequential processing
            sequential_start = time.time()
            sequential_results = []
            for name, img in test_images:
                result = process_image(name, img)
                sequential_results.append(result)
            sequential_time = time.time() - sequential_start
            
            # Test concurrent processing (if safe)
            concurrent_start = time.time()
            threads = []
            thread_results = []
            
            def thread_worker(name, img):
                result = process_image(name, img)
                thread_results.append(result)
            
            for name, img in test_images:
                thread = threading.Thread(target=thread_worker, args=(name, img))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            concurrent_time = time.time() - concurrent_start
            
            # Analyze results
            sequential_success = sum(1 for r in sequential_results if r.get('success', False))
            concurrent_success = sum(1 for r in thread_results if r.get('success', False))
            
            concurrency_metrics = {
                'sequential_time': sequential_time,
                'concurrent_time': concurrent_time,
                'speedup_ratio': sequential_time / concurrent_time if concurrent_time > 0 else 0,
                'sequential_success': f"{sequential_success}/{len(test_images)}",
                'concurrent_success': f"{concurrent_success}/{len(test_images)}",
                'thread_safe': concurrent_success == sequential_success
            }
            
            self.log_result("concurrent_processing", concurrent_success == sequential_success,
                          f"Concurrency test - Speedup: {concurrency_metrics['speedup_ratio']:.2f}x",
                          concurrency_metrics)
            
        except Exception as e:
            self.log_error("concurrent_processing", e)
            self.log_result("concurrent_processing", False, str(e))
    
    def run_all_tests(self):
        """Execute complete validation test suite"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE M3 YOLOV8 PIPELINE VALIDATION SUITE")
        print("Agent A - Extensive Testing and Validation")
        print("=" * 80)
        
        if not MODULES_AVAILABLE:
            print("❌ Cannot run tests - module imports failed")
            return False
        
        # Execute all test categories
        test_methods = [
            self.test_unit_yolo_engine_initialization,
            self.test_unit_inference_functionality,
            self.test_unit_semantic_mapping,
            self.test_performance_benchmarks,
            self.test_error_handling_robustness,
            self.test_memory_resource_usage,
            self.test_agent_b_integration,
            self.test_multi_resolution_compatibility,
            self.test_concurrent_processing
        ]
        
        for test_method in test_methods:
            print(f"\n--- Running {test_method.__name__} ---")
            try:
                test_method()
            except Exception as e:
                self.log_error(test_method.__name__, e)
        
        # Generate comprehensive report
        self.generate_final_report()
        
        return self.calculate_overall_success_rate()
    
    def calculate_overall_success_rate(self) -> float:
        """Calculate overall test success rate"""
        if not self.test_results:
            return 0.0
        
        passed_tests = sum(1 for result in self.test_results.values() if result['passed'])
        total_tests = len(self.test_results)
        
        return (passed_tests / total_tests) * 100.0
    
    def generate_final_report(self):
        """Generate comprehensive final validation report"""
        total_time = time.time() - self.start_time
        success_rate = self.calculate_overall_success_rate()
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE VALIDATION REPORT")
        print("=" * 80)
        
        # Test results summary
        passed_tests = sum(1 for result in self.test_results.values() if result['passed'])
        failed_tests = len(self.test_results) - passed_tests
        
        print(f"📊 TEST SUMMARY:")
        print(f"   Total Tests: {len(self.test_results)}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Runtime: {total_time:.2f} seconds")
        
        # Performance summary
        performance_metrics = []
        for test_name, result in self.test_results.items():
            if 'metrics' in result and result['metrics']:
                if 'avg_fps' in result['metrics']:
                    performance_metrics.append(result['metrics']['avg_fps'])
        
        if performance_metrics:
            print(f"\n🚀 PERFORMANCE SUMMARY:")
            print(f"   Average FPS: {np.mean(performance_metrics):.1f}")
            print(f"   Min FPS: {min(performance_metrics):.1f}")
            print(f"   Max FPS: {max(performance_metrics):.1f}")
            print(f"   Target FPS (30): {'✅ ACHIEVED' if min(performance_metrics) >= 30 else '⚠️ BELOW TARGET'}")
        
        # Error analysis
        if self.error_log:
            print(f"\n⚠️  ERROR ANALYSIS:")
            print(f"   Total Errors: {len(self.error_log)}")
            for error in self.error_log[-3:]:  # Show last 3 errors
                print(f"   • {error['test']}: {error['error']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("   ✅ EXCELLENT - M3 pipeline is production ready")
        elif success_rate >= 75:
            print("   ✅ GOOD - M3 pipeline is functional with minor issues")
        elif success_rate >= 50:
            print("   ⚠️  ACCEPTABLE - M3 pipeline works but needs optimization")
        else:
            print("   ❌ NEEDS WORK - Significant issues found")
        
        # Next steps
        print(f"\n📋 NEXT STEPS:")
        if success_rate >= 75:
            print("   • Ready for M4 State Representation integration")
            print("   • Consider PyTorch optimization for production")
            print("   • Integrate with Agent B's DLAT training pipeline")
        else:
            print("   • Address failed test cases")
            print("   • Optimize performance bottlenecks") 
            print("   • Review error handling")
        
        print("=" * 80)


def main():
    """Execute comprehensive M3 validation suite"""
    test_suite = M3TestSuite()
    success = test_suite.run_all_tests()
    
    # Return appropriate exit code
    exit_code = 0 if success >= 75 else 1
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)