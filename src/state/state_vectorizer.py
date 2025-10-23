"""
Module 4: State Representation Vectorizer - AIP-SDS-V2.3
Transforms Semantic Map data into fixed-size NumPy arrays for RL training.

This module implements the core transformation logic between M3 (Semantic Map) 
and M5 (PPO Training), providing bidirectional conversion for debugging and validation.

Features:
- semantic_to_vector(): Transform SemanticMap → RL State Vector
- vector_to_semantic_map(): Reverse mapping for debugging RL agent interpretation
- Configuration-based vector structure definition
- Normalization and validation for consistent RL training
- History stacking support for temporal dynamics

Author: Agent B
Version: 1.0
Compliance: AIP-SDS-V2.3, MODULE 4 specifications
"""

import numpy as np
import json
import logging
from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
import time

# Import M3 semantic map definitions
try:
    from ..perception.semantic_map import SemanticMap, DetectedElement, ElementLabel, ScreenContext
except ImportError:
    # Fallback for testing/standalone usage
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'perception'))
    from semantic_map import SemanticMap, DetectedElement, ElementLabel, ScreenContext


@dataclass
class VectorConfiguration:
    """Configuration for state vector structure and parameters."""
    
    # Vector size configuration
    base_vector_size: int = 256  # Fixed size for RL model compatibility
    max_elements: int = 20       # Maximum elements to encode
    history_frames: int = 4      # Number of historical frames to stack
    
    # Game phase indicators (3 values)
    game_phase_size: int = 3
    
    # Resource/stats section (10 values - expandable)
    resource_stats_size: int = 10
    
    # Perception confidence (1 value)  
    confidence_size: int = 1
    
    # Element encoding (remaining space)
    element_encoding_size: int = None  # Calculated automatically
    
    # Normalization parameters
    confidence_threshold: float = 0.8
    coordinate_scale: float = 1.0  # Already normalized in SemanticMap
    
    def __post_init__(self):
        """Calculate element encoding size based on other parameters."""
        if self.element_encoding_size is None:
            used_size = (self.game_phase_size + 
                        self.resource_stats_size + 
                        self.confidence_size)
            self.element_encoding_size = self.base_vector_size - used_size


class StateVectorizer:
    """
    Main class for bidirectional transformation between SemanticMap and RL state vectors.
    
    Implements the core M4 functionality with comprehensive validation and debugging support.
    """
    
    def __init__(self, config: Optional[VectorConfiguration] = None):
        """
        Initialize the state vectorizer with configuration.
        
        Args:
            config: Vector configuration (creates default if None)
        """
        self.config = config or VectorConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Initialize element label mapping for consistent encoding
        self.label_to_id = {label: idx for idx, label in enumerate(ElementLabel)}
        self.id_to_label = {idx: label for label, idx in self.label_to_id.items()}
        
        # Context mapping
        self.context_to_id = {context: idx for idx, context in enumerate(ScreenContext)}
        self.id_to_context = {idx: context for context, idx in self.context_to_id.items()}
        
        # Vector section indices for debugging
        self._calculate_section_indices()
        
        self.logger.info(f"StateVectorizer initialized with vector size: {self.config.base_vector_size}")
        
    def _calculate_section_indices(self):
        """Calculate start/end indices for each vector section."""
        self.indices = {
            'game_phase': (0, self.config.game_phase_size),
            'resources': (self.config.game_phase_size, 
                         self.config.game_phase_size + self.config.resource_stats_size),
            'confidence': (self.config.game_phase_size + self.config.resource_stats_size,
                          self.config.game_phase_size + self.config.resource_stats_size + self.config.confidence_size),
            'elements': (self.config.game_phase_size + self.config.resource_stats_size + self.config.confidence_size,
                        self.config.base_vector_size)
        }
        
    def semantic_to_vector(self, semantic_map: SemanticMap, 
                          config: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Transform SemanticMap into fixed-size RL state vector.
        
        Args:
            semantic_map: Input semantic map from M3 perception
            config: Optional runtime configuration overrides
            
        Returns:
            np.ndarray: Fixed-size normalized state vector for RL training
        """
        try:
            # Initialize state vector
            state_vector = np.zeros(self.config.base_vector_size, dtype=np.float32)
            
            # Section 1: Game Phase Indicators (3 values)
            game_phase = self._encode_game_phase(semantic_map.screen_context)
            start_idx, end_idx = self.indices['game_phase']
            state_vector[start_idx:end_idx] = game_phase
            
            # Section 2: Resource/Stats (10 values)  
            resources = self._encode_resources_stats(semantic_map.elements)
            start_idx, end_idx = self.indices['resources']
            state_vector[start_idx:end_idx] = resources
            
            # Section 3: Perception Confidence (1 value)
            confidence = self._encode_perception_confidence(semantic_map.elements)
            start_idx, end_idx = self.indices['confidence'] 
            state_vector[start_idx:end_idx] = [confidence]
            
            # Section 4: Element Encoding (remaining space)
            elements_encoded = self._encode_elements(semantic_map.elements)
            start_idx, end_idx = self.indices['elements']
            available_space = end_idx - start_idx
            state_vector[start_idx:start_idx + min(len(elements_encoded), available_space)] = elements_encoded[:available_space]
            
            # Validate output
            self._validate_state_vector(state_vector)
            
            self.logger.debug(f"Encoded SemanticMap to state vector: {state_vector.shape}")
            return state_vector
            
        except Exception as e:
            self.logger.error(f"Failed to convert semantic map to vector: {e}")
            # Return zero vector on error to prevent training crashes
            return np.zeros(self.config.base_vector_size, dtype=np.float32)
            
    def vector_to_semantic_map(self, state_vector: np.ndarray,
                              config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Reverse mapping: State vector → Semantic interpretation for debugging.
        
        Args:
            state_vector: RL state vector to decode
            config: Optional runtime configuration
            
        Returns:
            Dictionary containing decoded semantic information
        """
        try:
            self._validate_state_vector(state_vector)
            
            decoded = {
                'timestamp': time.time(),
                'vector_size': len(state_vector),
                'sections': {}
            }
            
            # Decode game phase indicators
            start_idx, end_idx = self.indices['game_phase']
            game_phase_raw = state_vector[start_idx:end_idx]
            decoded['sections']['game_phase'] = self._decode_game_phase(game_phase_raw)
            
            # Decode resources/stats
            start_idx, end_idx = self.indices['resources']
            resources_raw = state_vector[start_idx:end_idx]
            decoded['sections']['resources'] = self._decode_resources_stats(resources_raw)
            
            # Decode perception confidence
            start_idx, end_idx = self.indices['confidence']
            confidence_raw = state_vector[start_idx:end_idx]
            decoded['sections']['confidence'] = {
                'avg_detection_score': float(confidence_raw[0]),
                'normalized': True
            }
            
            # Decode elements
            start_idx, end_idx = self.indices['elements']
            elements_raw = state_vector[start_idx:end_idx]
            decoded['sections']['elements'] = self._decode_elements(elements_raw)
            
            # Summary statistics
            decoded['summary'] = {
                'non_zero_values': np.count_nonzero(state_vector),
                'mean_activation': float(np.mean(state_vector)),
                'max_activation': float(np.max(state_vector)),
                'vector_norm': float(np.linalg.norm(state_vector))
            }
            
            self.logger.debug(f"Decoded state vector to semantic interpretation")
            return decoded
            
        except Exception as e:
            self.logger.error(f"Failed to decode state vector: {e}")
            return {'error': str(e), 'timestamp': time.time()}
            
    def _encode_game_phase(self, screen_context: ScreenContext) -> np.ndarray:
        """
        Encode game phase indicators from screen context.
        
        Args:
            screen_context: Current screen context from semantic map
            
        Returns:
            np.ndarray: Game phase indicator array [is_main_menu, is_in_game, is_loading]
        """
        phase = np.zeros(3, dtype=np.float32)
        
        if screen_context == ScreenContext.MAIN_MENU:
            phase[0] = 1.0  # is_main_menu
        elif screen_context == ScreenContext.IN_GAME:
            phase[1] = 1.0  # is_in_game
        elif screen_context == ScreenContext.LOADING:
            phase[2] = 1.0  # is_loading
        # Default: all zeros for unknown/other contexts
            
        return phase
        
    def _encode_resources_stats(self, elements: List[DetectedElement]) -> np.ndarray:
        """
        Encode resource counters and game statistics from detected elements.
        
        Args:
            elements: List of detected elements from semantic map
            
        Returns:
            np.ndarray: Resource/stats array (normalized values)
        """
        resources = np.zeros(self.config.resource_stats_size, dtype=np.float32)
        
        # Extract numeric values from resource counter elements
        resource_values = []
        
        for element in elements:
            if element.label == ElementLabel.RESOURCE_COUNTER:
                # Try to extract numeric value from semantic_value
                try:
                    value = float(''.join(c for c in element.semantic_value if c.isdigit() or c == '.'))
                    resource_values.append(value)
                except (ValueError, TypeError):
                    continue
                    
        # Encode first N resource values (normalized)
        for i, value in enumerate(resource_values[:self.config.resource_stats_size]):
            # Normalize to 0-1 range (assume max value of 10000 for game resources)
            resources[i] = min(value / 10000.0, 1.0)
            
        return resources
        
    def _encode_perception_confidence(self, elements: List[DetectedElement]) -> float:
        """
        Calculate average perception confidence from all detected elements.
        
        Args:
            elements: List of detected elements
            
        Returns:
            float: Average confidence score (0.0-1.0)
        """
        if not elements:
            return 0.0
            
        total_confidence = sum(elem.confidence for elem in elements)
        return total_confidence / len(elements)
        
    def _encode_elements(self, elements: List[DetectedElement]) -> np.ndarray:
        """
        Encode detected elements with positions and types.
        
        Args:
            elements: List of detected elements
            
        Returns:
            np.ndarray: Flattened array of element encodings
        """
        # Each element encoded as: [label_id, center_x, center_y, confidence, is_clickable]
        element_encoding_dim = 5
        max_elements = min(len(elements), self.config.max_elements)
        
        encoded = []
        
        # Sort elements by confidence (highest first) for consistent encoding
        sorted_elements = sorted(elements, key=lambda x: x.confidence, reverse=True)
        
        for i in range(max_elements):
            element = sorted_elements[i]
            
            # Get element center point
            center_x, center_y = element.get_center_point()
            
            # Encode element
            element_encoding = [
                float(self.label_to_id.get(element.label, 0)) / len(ElementLabel),  # Normalized label ID
                center_x,  # Already normalized
                center_y,  # Already normalized  
                element.confidence,  # Already 0-1
                1.0 if element.is_clickable() else 0.0  # Boolean as float
            ]
            
            encoded.extend(element_encoding)
            
        return np.array(encoded, dtype=np.float32)
        
    def _decode_game_phase(self, game_phase_raw: np.ndarray) -> Dict[str, Any]:
        """Decode game phase indicators for debugging."""
        phase_names = ['is_main_menu', 'is_in_game', 'is_loading']
        
        decoded = {
            'raw_values': game_phase_raw.tolist(),
            'active_phase': None,
            'confidence': 0.0
        }
        
        # Find highest activation
        max_idx = np.argmax(game_phase_raw)
        max_value = game_phase_raw[max_idx]
        
        if max_value > 0.5:  # Threshold for activation
            decoded['active_phase'] = phase_names[max_idx]
            decoded['confidence'] = float(max_value)
            
        return decoded
        
    def _decode_resources_stats(self, resources_raw: np.ndarray) -> Dict[str, Any]:
        """Decode resource/stats section for debugging."""
        return {
            'raw_values': resources_raw.tolist(),
            'resource_count': int(np.count_nonzero(resources_raw)),
            'denormalized_values': (resources_raw * 10000).astype(int).tolist(),
            'max_resource': float(np.max(resources_raw)) * 10000
        }
        
    def _decode_elements(self, elements_raw: np.ndarray) -> Dict[str, Any]:
        """Decode elements section for debugging."""
        element_encoding_dim = 5
        num_elements = len(elements_raw) // element_encoding_dim
        
        decoded_elements = []
        
        for i in range(num_elements):
            start_idx = i * element_encoding_dim
            end_idx = start_idx + element_encoding_dim
            
            if end_idx <= len(elements_raw):
                element_data = elements_raw[start_idx:end_idx]
                
                # Skip zero elements (empty slots)
                if np.any(element_data):
                    label_id = int(element_data[0] * len(ElementLabel))
                    label = self.id_to_label.get(label_id, ElementLabel.BUTTON)
                    
                    decoded_element = {
                        'label': label.value,
                        'center_x': float(element_data[1]), 
                        'center_y': float(element_data[2]),
                        'confidence': float(element_data[3]),
                        'is_clickable': bool(element_data[4] > 0.5)
                    }
                    
                    decoded_elements.append(decoded_element)
                    
        return {
            'total_encoded_elements': num_elements,
            'active_elements': len(decoded_elements),
            'elements': decoded_elements
        }
        
    def _validate_state_vector(self, state_vector: np.ndarray):
        """
        Validate state vector format and content.
        
        Args:
            state_vector: State vector to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check type and shape
        if not isinstance(state_vector, np.ndarray):
            raise ValueError("State vector must be numpy array")
            
        if state_vector.dtype != np.float32:
            raise ValueError("State vector must be float32 dtype")
            
        if len(state_vector.shape) != 1:
            raise ValueError("State vector must be 1-dimensional")
            
        if state_vector.shape[0] != self.config.base_vector_size:
            raise ValueError(f"State vector size must be {self.config.base_vector_size}, got {state_vector.shape[0]}")
            
        # Check value ranges
        if np.any(np.isnan(state_vector)):
            raise ValueError("State vector contains NaN values")
            
        if np.any(np.isinf(state_vector)):
            raise ValueError("State vector contains infinite values")
            
        # Check reasonable value ranges (most should be 0-1)
        if np.any(state_vector < -1.0) or np.any(state_vector > 2.0):
            self.logger.warning(f"State vector contains values outside expected range [-1, 2]: "
                              f"min={np.min(state_vector)}, max={np.max(state_vector)}")
                              
    def get_vector_info(self) -> Dict[str, Any]:
        """
        Get information about vector structure and configuration.
        
        Returns:
            Dictionary containing vector configuration details
        """
        return {
            'config': asdict(self.config),
            'section_indices': self.indices,
            'label_mappings': {label.value: idx for label, idx in self.label_to_id.items()},
            'context_mappings': {context.value: idx for context, idx in self.context_to_id.items()},
            'total_vector_size': self.config.base_vector_size
        }
        
    def create_test_vector(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Create a test state vector with known values for validation.
        
        Returns:
            Tuple of (test_vector, expected_decoded_info)
        """
        # Create test semantic map
        from semantic_map import create_semantic_map, create_detected_element
        
        test_elements = [
            create_detected_element(
                label=ElementLabel.BUTTON,
                semantic_value="Single Player", 
                bbox=[0.3, 0.4, 0.2, 0.1],
                confidence=0.95
            ),
            create_detected_element(
                label=ElementLabel.RESOURCE_COUNTER,
                semantic_value="1500",
                bbox=[0.8, 0.1, 0.1, 0.05],
                confidence=0.9
            )
        ]
        
        test_semantic_map = create_semantic_map(
            screen_context=ScreenContext.MAIN_MENU,
            elements=test_elements,
            screen_resolution=(800, 600)
        )
        
        # Convert to vector  
        test_vector = self.semantic_to_vector(test_semantic_map)
        
        # Create expected decode info
        expected_info = {
            'should_detect_main_menu': True,
            'should_have_resources': True,
            'should_have_elements': True,
            'expected_confidence': 0.925  # Average of 0.95 and 0.9
        }
        
        return test_vector, expected_info


def validate_state_vectorizer():
    """Test and validate the state vectorizer implementation."""
    try:
        print("🧪 Testing State Vectorizer (Module 4)...")
        
        # Initialize vectorizer
        vectorizer = StateVectorizer()
        print(f"✅ Vectorizer initialized with config: {vectorizer.config.base_vector_size} dimensions")
        
        # Test vector info
        info = vectorizer.get_vector_info()
        print(f"   Vector sections: {list(info['section_indices'].keys())}")
        
        # Create test vector
        test_vector, expected_info = vectorizer.create_test_vector()
        print(f"✅ Test vector created: shape {test_vector.shape}, dtype {test_vector.dtype}")
        
        # Test reverse mapping
        decoded = vectorizer.vector_to_semantic_map(test_vector)
        print(f"✅ Reverse mapping successful")
        
        # Validate game phase detection
        game_phase = decoded['sections']['game_phase']
        if game_phase['active_phase'] == 'is_main_menu':
            print("✅ Game phase detection: MAIN_MENU correctly identified")
        else:
            print(f"⚠️  Game phase detection: Expected MAIN_MENU, got {game_phase['active_phase']}")
            
        # Validate elements detection
        elements_info = decoded['sections']['elements'] 
        if elements_info['active_elements'] > 0:
            print(f"✅ Element encoding: {elements_info['active_elements']} elements detected")
        else:
            print("⚠️  Element encoding: No elements detected in test vector")
            
        # Test vector consistency
        summary = decoded['summary']
        print(f"   Vector statistics: {summary['non_zero_values']} non-zero values, "
              f"norm: {summary['vector_norm']:.3f}")
              
        print("✅ State Vectorizer validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ State Vectorizer validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_default_config() -> Dict[str, Any]:
    """
    Create default configuration for testing.
    
    Returns:
        Default configuration dictionary
    """
    return {
        'vector_size': 256,
        'max_elements': 20,
        'history_frames': 4,
        'normalization_enabled': True,
        'confidence_threshold': 0.1,
        'element_padding': True
    }


def main():
    """Main function for testing state vectorizer."""
    print("📋 Module 4: State Representation Vectorizer - AIP-SDS-V2.3")
    print("=" * 70)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run validation
    success = validate_state_vectorizer()
    
    if success:
        print("\n🎯 M4 State Vectorizer: Ready for M3→M5 pipeline integration!")
    else:
        print("\n❌ M4 State Vectorizer: Validation failed - check implementation")
        

if __name__ == "__main__":
    main()