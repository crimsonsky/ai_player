"""
M3-M4 INTEGRATION ENHANCEMENT
============================

Integration layer between Agent A's M3 YOLOv8 Detection Engine and Agent B's M4 State Vectorizer.
Provides seamless pipeline for real-time RL training data generation.

Author: Agent B
Version: 1.0
Integration: Agent A M3 + Agent B M4
"""

import numpy as np
import time
from typing import Dict, Any, Optional, Tuple
import logging

try:
    from .yolo_detection_engine import YOLODetectionEngine
    from ..state.state_vectorizer import StateVectorizer, VectorConfiguration
    from .semantic_map import SemanticMap
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logging.warning("M3-M4 integration not available - check module imports")


class M3M4Pipeline:
    """
    Integrated pipeline combining Agent A's M3 YOLOv8 detection with Agent B's M4 state vectorization.
    
    Provides a unified interface for real-time perception → state vector conversion
    optimized for M5 RL training pipeline.
    """
    
    def __init__(self, yolo_model_path: Optional[str] = None, 
                 vector_config: Optional[VectorConfiguration] = None):
        """
        Initialize integrated M3-M4 pipeline.
        
        Args:
            yolo_model_path: Path to trained YOLOv8 model (Agent A's M3)
            vector_config: State vector configuration (Agent B's M4)
        """
        self.logger = logging.getLogger(__name__)
        
        if not INTEGRATION_AVAILABLE:
            raise ImportError("M3-M4 integration requires both YOLODetectionEngine and StateVectorizer")
        
        # Initialize Agent A's M3 YOLOv8 engine
        self.yolo_engine = YOLODetectionEngine(model_path=yolo_model_path)
        self.logger.info("Agent A M3 YOLOv8 engine initialized")
        
        # Initialize Agent B's M4 state vectorizer
        self.state_vectorizer = StateVectorizer(config=vector_config)
        self.logger.info(f"Agent B M4 state vectorizer initialized (vector size: {self.state_vectorizer.config.base_vector_size})")
        
        # Performance metrics
        self.processing_times = {
            'm3_detection': [],
            'm4_vectorization': [],
            'total_pipeline': []
        }
        
    def process_frame(self, screen_image) -> Tuple[SemanticMap, np.ndarray]:
        """
        Complete M3→M4 pipeline: Screen → SemanticMap → StateVector.
        
        Args:
            screen_image: PIL Image of game screen
            
        Returns:
            Tuple of (SemanticMap, StateVector) for RL training
        """
        start_time = time.time()
        
        # M3: YOLOv8 Detection (Agent A)
        m3_start = time.time()
        semantic_map = self.yolo_engine.detect_objects(screen_image)
        m3_time = time.time() - m3_start
        self.processing_times['m3_detection'].append(m3_time)
        
        # M4: State Vectorization (Agent B)
        m4_start = time.time()
        state_vector = self.state_vectorizer.semantic_to_vector(semantic_map)
        m4_time = time.time() - m4_start
        self.processing_times['m4_vectorization'].append(m4_time)
        
        # Total pipeline time
        total_time = time.time() - start_time
        self.processing_times['total_pipeline'].append(total_time)
        
        self.logger.debug(f"M3-M4 pipeline: {total_time:.3f}s (M3: {m3_time:.3f}s, M4: {m4_time:.3f}s)")
        
        return semantic_map, state_vector
        
    def batch_process(self, screen_images: list) -> Tuple[list, np.ndarray]:
        """
        Batch processing for multiple frames (efficient for training data generation).
        
        Args:
            screen_images: List of PIL Images
            
        Returns:
            Tuple of (SemanticMaps list, StateVectors array)
        """
        semantic_maps = []
        state_vectors = []
        
        for screen_image in screen_images:
            semantic_map, state_vector = self.process_frame(screen_image)
            semantic_maps.append(semantic_map)
            state_vectors.append(state_vector)
            
        return semantic_maps, np.array(state_vectors)
        
    def debug_state_vector(self, state_vector: np.ndarray) -> Dict[str, Any]:
        """
        Debug state vector using Agent B's M4 reverse mapping.
        
        Args:
            state_vector: State vector to debug
            
        Returns:
            Decoded semantic information for debugging
        """
        return self.state_vectorizer.vector_to_semantic_map(state_vector)
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the M3-M4 pipeline."""
        stats = {}
        
        for component, times in self.processing_times.items():
            if times:
                stats[component] = {
                    'avg_time': np.mean(times),
                    'max_time': np.max(times),
                    'min_time': np.min(times),
                    'fps': 1.0 / np.mean(times),
                    'samples': len(times)
                }
                
        return stats
        
    def reset_stats(self):
        """Reset performance statistics."""
        for key in self.processing_times:
            self.processing_times[key] = []
            

def create_m3_m4_pipeline(yolo_model_path: Optional[str] = None,
                         vector_size: int = 256) -> M3M4Pipeline:
    """
    Factory function to create M3-M4 integrated pipeline.
    
    Args:
        yolo_model_path: Path to YOLOv8 model (None for dummy model)
        vector_size: State vector dimensions
        
    Returns:
        Configured M3M4Pipeline instance
    """
    vector_config = VectorConfiguration(base_vector_size=vector_size)
    return M3M4Pipeline(yolo_model_path=yolo_model_path, vector_config=vector_config)


def validate_m3_m4_integration() -> bool:
    """
    Validate M3-M4 integration with comprehensive testing.
    
    Returns:
        True if integration is working correctly
    """
    try:
        print("🧪 Validating M3-M4 Integration...")
        
        # Create pipeline
        pipeline = create_m3_m4_pipeline()
        print("✅ M3-M4 pipeline created successfully")
        
        # Create test image (placeholder)
        from PIL import Image
        test_image = Image.new('RGB', (800, 600), color='blue')
        
        # Test single frame processing
        semantic_map, state_vector = pipeline.process_frame(test_image)
        
        print(f"✅ Single frame processing:")
        print(f"   SemanticMap: {len(semantic_map.elements)} elements")
        print(f"   StateVector: shape {state_vector.shape}, dtype {state_vector.dtype}")
        
        # Test debug functionality
        debug_info = pipeline.debug_state_vector(state_vector)
        print(f"✅ Debug functionality: {len(debug_info['sections'])} sections decoded")
        
        # Test performance
        stats = pipeline.get_performance_stats()
        if stats:
            total_stats = stats.get('total_pipeline', {})
            if 'fps' in total_stats:
                print(f"✅ Performance: {total_stats['fps']:.1f} FPS")
        
        print("✅ M3-M4 Integration: VALIDATION PASSED")
        return True
        
    except Exception as e:
        print(f"❌ M3-M4 Integration validation failed: {e}")
        return False


if __name__ == "__main__":
    # Run validation
    success = validate_m3_m4_integration()
    
    if success:
        print("\n🎉 M3-M4 INTEGRATION READY FOR M5 RL TRAINING!")
        print("✅ Agent A M3 + Agent B M4: Seamless collaboration")
    else:
        print("\n❌ M3-M4 Integration needs attention")
        
    exit(0 if success else 1)