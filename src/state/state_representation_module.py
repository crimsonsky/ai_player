"""
STATE REPRESENTATION MODULE - Module 4: Semantic Map to RL State Vector Conversion
Bridge Between AI Perception and Reinforcement Learning Decision Making

This module converts rich hierarchical SemanticMap data from M3 YOLOv8 detection
into fixed-length numerical state vectors required for RL algorithms (M5 PPO).

Pipeline Integration:
M3 (YOLOv8) → SemanticMap → M4 (State Vector) → M5 (RL Decision) → M6 (Experience Replay)

Features:
- Fixed-length state vector generation (consistent dimensions)
- Resource encoding with min-max normalization  
- Categorical data encoding with one-hot representation
- Spatial encoding for bounding box information
- Top-N detection selection with zero-padding
- Agent B ExperienceReplayBuffer integration ready
- Complete RL pipeline orchestration

Author: Agent A
Version: 1.0
Compliance: AIP-SDS-V2.3, MODULE 4 specifications  
Integration: Agent B MLOps pipeline (ExperienceReplayBuffer + DLAT)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum
import time
import json

# Import M3 perception components
from ..perception.semantic_map import SemanticMap, DetectedElement, ElementLabel
from ..perception.screen_capture import GameScreenCapture  
from ..perception.yolo_detection_engine import YOLODetectionEngine, run_complete_perception_pipeline

# Agent B MLOps integration
try:
    from ..mlops.data_manager import ExperienceReplayBuffer
    MLOPS_AVAILABLE = True
except ImportError:
    MLOPS_AVAILABLE = False
    logging.warning("Agent B MLOps not available - using placeholder integration")


@dataclass
class StateVectorConfig:
    """Configuration for state vector dimensions and encoding parameters."""
    
    # Core dimensions
    MAX_DETECTIONS = 10  # Maximum objects tracked in state vector
    RESOURCE_DIMS = 8    # Normalized resource values (spice, power, health, etc.)
    CONTEXT_DIMS = 12    # One-hot encoded screen contexts  
    SPATIAL_DIMS = 40    # Bounding box coordinates (MAX_DETECTIONS * 4)
    CONFIDENCE_DIMS = 10 # Confidence scores for detections
    TEMPORAL_DIMS = 20   # Previous state history for dynamics
    
    @property
    def total_dimensions(self) -> int:
        """Calculate total state vector length."""
        return (self.RESOURCE_DIMS + self.CONTEXT_DIMS + self.SPATIAL_DIMS + 
                self.CONFIDENCE_DIMS + self.TEMPORAL_DIMS)
    
    # Normalization ranges for resources
    RESOURCE_RANGES = {
        'spice_count': (0, 10000),
        'power_level': (0, 1000), 
        'unit_health': (0, 100),
        'building_count': (0, 50),
        'enemy_units': (0, 100),
        'map_control': (0, 100),
        'tech_level': (0, 10),
        'time_elapsed': (0, 3600)  # Max 1 hour game time
    }
    
    # Screen context categories for one-hot encoding
    SCREEN_CONTEXTS = [
        'main_menu', 'single_player_menu', 'multiplayer_menu', 'options_menu',
        'game_setup', 'loading_screen', 'in_game_hud', 'minimap_view',
        'construction_menu', 'unit_selection', 'resource_overlay', 'unknown'
    ]


class ScreenContext(Enum):
    """Enumeration of possible game screen contexts."""
    MAIN_MENU = 0
    SINGLE_PLAYER_MENU = 1
    MULTIPLAYER_MENU = 2
    OPTIONS_MENU = 3
    GAME_SETUP = 4
    LOADING_SCREEN = 5
    IN_GAME_HUD = 6
    MINIMAP_VIEW = 7
    CONSTRUCTION_MENU = 8
    UNIT_SELECTION = 9
    RESOURCE_OVERLAY = 10
    UNKNOWN = 11


class StateRepresentationModule:
    """
    Core state representation engine for RL integration.
    
    Converts hierarchical SemanticMap data into fixed-length numerical vectors
    suitable for PPO and other RL algorithms.
    """
    
    def __init__(self, config: Optional[StateVectorConfig] = None):
        """
        Initialize state representation module.
        
        Args:
            config: State vector configuration (uses default if None)
        """
        self.config = config or StateVectorConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize perception components
        self.screen_capture = GameScreenCapture()
        self.detection_engine = YOLODetectionEngine()
        
        # Agent B MLOps integration
        if MLOPS_AVAILABLE:
            self.experience_buffer = ExperienceReplayBuffer(capacity=100000)
            self.logger.info("Agent B ExperienceReplayBuffer integration active")
        
        # State history for temporal encoding
        self.state_history: List[np.ndarray] = []
        self.max_history_length = 5
        
        # Performance tracking
        self.conversion_stats = {
            'total_conversions': 0,
            'average_conversion_time': 0.0,
            'last_state_vector_size': 0
        }
        
        self.logger.info(f"StateRepresentationModule initialized - Vector size: {self.config.total_dimensions}")
    
    def convert_to_state_vector(self, semantic_map: SemanticMap) -> np.ndarray:
        """
        Core function: Convert SemanticMap to fixed-length state vector.
        
        Args:
            semantic_map: Rich hierarchical game state from M3 YOLOv8
            
        Returns:
            np.ndarray: Fixed-length state vector for RL algorithms
        """
        start_time = time.time()
        
        try:
            # Initialize state vector with zeros
            state_vector = np.zeros(self.config.total_dimensions, dtype=np.float32)
            current_idx = 0
            
            # 1. RESOURCE ENCODING (normalized to [0,1])
            resource_vector = self._encode_resources(semantic_map)
            state_vector[current_idx:current_idx + self.config.RESOURCE_DIMS] = resource_vector
            current_idx += self.config.RESOURCE_DIMS
            
            # 2. CONTEXT ENCODING (one-hot)
            context_vector = self._encode_screen_context(semantic_map)
            state_vector[current_idx:current_idx + self.config.CONTEXT_DIMS] = context_vector
            current_idx += self.config.CONTEXT_DIMS
            
            # 3. SPATIAL ENCODING (bounding boxes)
            spatial_vector = self._encode_spatial_information(semantic_map)
            state_vector[current_idx:current_idx + self.config.SPATIAL_DIMS] = spatial_vector
            current_idx += self.config.SPATIAL_DIMS
            
            # 4. CONFIDENCE ENCODING (detection confidence scores)
            confidence_vector = self._encode_confidence_scores(semantic_map)
            state_vector[current_idx:current_idx + self.config.CONFIDENCE_DIMS] = confidence_vector
            current_idx += self.config.CONFIDENCE_DIMS
            
            # 5. TEMPORAL ENCODING (state history for dynamics)
            temporal_vector = self._encode_temporal_history()
            state_vector[current_idx:current_idx + self.config.TEMPORAL_DIMS] = temporal_vector
            
            # Update performance stats
            conversion_time = time.time() - start_time
            self._update_conversion_stats(conversion_time, len(state_vector))
            
            # Add to state history for temporal encoding
            self._update_state_history(state_vector.copy())
            
            self.logger.debug(f"State vector conversion completed in {conversion_time:.3f}s "
                            f"- Vector size: {len(state_vector)}")
            
            return state_vector
            
        except Exception as e:
            self.logger.error(f"State vector conversion failed: {e}")
            # Return zero vector on error to maintain consistency
            return np.zeros(self.config.total_dimensions, dtype=np.float32)
    
    def _encode_resources(self, semantic_map: SemanticMap) -> np.ndarray:
        """
        Encode resource information with min-max normalization.
        
        Extracts numerical values from detected elements and normalizes to [0,1].
        """
        resource_vector = np.zeros(self.config.RESOURCE_DIMS, dtype=np.float32)
        
        try:
            # Extract resource information from detected elements
            detected_resources = {
                'spice_count': 0,
                'power_level': 0, 
                'unit_health': 0,
                'building_count': 0,
                'enemy_units': 0,
                'map_control': 0,
                'tech_level': 0,
                'time_elapsed': 0
            }
            
            # Parse semantic map for resource data
            for element in semantic_map.elements:
                if element.element_label == ElementLabel.COUNTER:
                    # Resource counter detection
                    if 'spice' in element.semantic_value.lower():
                        detected_resources['spice_count'] = self._extract_numeric_value(element.semantic_value)
                    elif 'power' in element.semantic_value.lower():
                        detected_resources['power_level'] = self._extract_numeric_value(element.semantic_value)
                
                elif element.element_label == ElementLabel.ICON:
                    # Count different types of game objects
                    if 'unit' in element.semantic_value.lower():
                        detected_resources['unit_health'] += element.confidence_score * 100
                    elif 'building' in element.semantic_value.lower():
                        detected_resources['building_count'] += 1
                    elif 'enemy' in element.semantic_value.lower():
                        detected_resources['enemy_units'] += 1
            
            # Estimate map control and tech level from detected elements
            detected_resources['map_control'] = min(len(semantic_map.elements) * 5, 100)
            detected_resources['tech_level'] = min(detected_resources['building_count'] // 5, 10)
            detected_resources['time_elapsed'] = semantic_map.timestamp % 3600
            
            # Apply min-max normalization
            for i, (resource_key, raw_value) in enumerate(detected_resources.items()):
                if i < self.config.RESOURCE_DIMS:
                    min_val, max_val = self.config.RESOURCE_RANGES[resource_key]
                    normalized_value = (raw_value - min_val) / (max_val - min_val)
                    resource_vector[i] = np.clip(normalized_value, 0.0, 1.0)
            
            return resource_vector
            
        except Exception as e:
            self.logger.warning(f"Resource encoding failed: {e}")
            return np.zeros(self.config.RESOURCE_DIMS, dtype=np.float32)
    
    def _encode_screen_context(self, semantic_map: SemanticMap) -> np.ndarray:
        """
        Encode screen context using one-hot representation.
        
        Determines current game screen/menu context from detected elements.
        """
        context_vector = np.zeros(self.config.CONTEXT_DIMS, dtype=np.float32)
        
        try:
            # Analyze semantic map to determine screen context
            detected_context = self._classify_screen_context(semantic_map)
            
            # Set one-hot encoding
            if detected_context.value < len(context_vector):
                context_vector[detected_context.value] = 1.0
            
            return context_vector
            
        except Exception as e:
            self.logger.warning(f"Context encoding failed: {e}")
            # Default to unknown context
            context_vector[ScreenContext.UNKNOWN.value] = 1.0
            return context_vector
    
    def _encode_spatial_information(self, semantic_map: SemanticMap) -> np.ndarray:
        """
        Encode spatial information from bounding boxes.
        
        Uses top-N most confident detections with zero-padding.
        """
        spatial_vector = np.zeros(self.config.SPATIAL_DIMS, dtype=np.float32)
        
        try:
            # Sort elements by confidence score (highest first)
            sorted_elements = sorted(semantic_map.elements, 
                                   key=lambda x: x.confidence_score, reverse=True)
            
            # Take top MAX_DETECTIONS elements
            top_elements = sorted_elements[:self.config.MAX_DETECTIONS]
            
            # Encode bounding boxes (normalized coordinates)
            screen_width, screen_height = semantic_map.screen_resolution
            for i, element in enumerate(top_elements):
                base_idx = i * 4  # 4 coordinates per bounding box
                if base_idx + 3 < self.config.SPATIAL_DIMS:
                    x1, y1, x2, y2 = element.bounding_box
                    
                    # Normalize coordinates to [0,1]
                    spatial_vector[base_idx] = x1 / screen_width
                    spatial_vector[base_idx + 1] = y1 / screen_height  
                    spatial_vector[base_idx + 2] = x2 / screen_width
                    spatial_vector[base_idx + 3] = y2 / screen_height
            
            return spatial_vector
            
        except Exception as e:
            self.logger.warning(f"Spatial encoding failed: {e}")
            return np.zeros(self.config.SPATIAL_DIMS, dtype=np.float32)
    
    def _encode_confidence_scores(self, semantic_map: SemanticMap) -> np.ndarray:
        """
        Encode detection confidence scores.
        
        Top-N confidence values for RL decision confidence weighting.
        """
        confidence_vector = np.zeros(self.config.CONFIDENCE_DIMS, dtype=np.float32)
        
        try:
            # Sort by confidence and take top N
            sorted_elements = sorted(semantic_map.elements,
                                   key=lambda x: x.confidence_score, reverse=True)
            
            for i, element in enumerate(sorted_elements[:self.config.CONFIDENCE_DIMS]):
                confidence_vector[i] = element.confidence_score
            
            return confidence_vector
            
        except Exception as e:
            self.logger.warning(f"Confidence encoding failed: {e}")
            return np.zeros(self.config.CONFIDENCE_DIMS, dtype=np.float32)
    
    def _encode_temporal_history(self) -> np.ndarray:
        """
        Encode temporal state history for dynamic understanding.
        
        Provides recent state information for temporal patterns in RL.
        """
        temporal_vector = np.zeros(self.config.TEMPORAL_DIMS, dtype=np.float32)
        
        try:
            if self.state_history:
                # Use recent state history (flattened partial vectors)
                history_length = min(len(self.state_history), self.config.TEMPORAL_DIMS // 4)
                
                for i in range(history_length):
                    # Take subset of previous state vectors
                    prev_state = self.state_history[-(i+1)]
                    start_idx = i * 4
                    end_idx = min(start_idx + 4, self.config.TEMPORAL_DIMS)
                    
                    # Use first few dimensions of previous state
                    subset_length = end_idx - start_idx
                    if len(prev_state) >= subset_length:
                        temporal_vector[start_idx:end_idx] = prev_state[:subset_length]
            
            return temporal_vector
            
        except Exception as e:
            self.logger.warning(f"Temporal encoding failed: {e}")
            return np.zeros(self.config.TEMPORAL_DIMS, dtype=np.float32)
    
    def get_current_rl_state(self) -> np.ndarray:
        """
        M5 INTEGRATION: Complete RL-ready pipeline orchestrator.
        
        Executes full perception → state vector pipeline for RL algorithms.
        
        Returns:
            np.ndarray: Ready-to-use state vector for PPO/DQN algorithms
        """
        try:
            # Complete M3 → M4 pipeline execution
            start_time = time.time()
            
            # 1. M3A: Screen capture
            screen_image = self.screen_capture.capture_game_window()
            if screen_image is None:
                self.logger.error("Screen capture failed - returning zero state")
                return np.zeros(self.config.total_dimensions, dtype=np.float32)
            
            # 2. M3B/C: YOLOv8 detection and semantic mapping
            semantic_map = run_complete_perception_pipeline(screen_image, self.detection_engine)
            
            # 3. M4: State vector conversion
            state_vector = self.convert_to_state_vector(semantic_map)
            
            # 4. Agent B MLOps integration (Experience storage)
            if MLOPS_AVAILABLE and hasattr(self, 'experience_buffer'):
                # Store state for future SARSA tuple generation
                experience_data = {
                    'state_vector': state_vector,
                    'semantic_map': semantic_map,
                    'screen_capture': np.array(screen_image),
                    'timestamp': time.time()
                }
                # Note: Full SARSA integration will be completed in M5
            
            pipeline_time = time.time() - start_time
            self.logger.info(f"Complete RL state pipeline executed in {pipeline_time:.3f}s "
                           f"- State vector ready for M5")
            
            return state_vector
            
        except Exception as e:
            self.logger.error(f"RL state pipeline failed: {e}")
            return np.zeros(self.config.total_dimensions, dtype=np.float32)
    
    def _classify_screen_context(self, semantic_map: SemanticMap) -> ScreenContext:
        """
        Classify current screen context from detected elements.
        """
        try:
            # Analyze detected elements for context clues
            menu_indicators = []
            game_indicators = []
            
            for element in semantic_map.elements:
                semantic_value = element.semantic_value.lower()
                
                if 'menu' in semantic_value or 'button' in semantic_value:
                    menu_indicators.append(semantic_value)
                elif 'single' in semantic_value and 'player' in semantic_value:
                    return ScreenContext.SINGLE_PLAYER_MENU
                elif 'multiplayer' in semantic_value:
                    return ScreenContext.MULTIPLAYER_MENU
                elif 'option' in semantic_value:
                    return ScreenContext.OPTIONS_MENU
                elif 'dune' in semantic_value or 'legacy' in semantic_value:
                    return ScreenContext.MAIN_MENU
                elif 'resource' in semantic_value or 'spice' in semantic_value:
                    game_indicators.append(semantic_value)
            
            # Context classification logic
            if len(game_indicators) > 2:
                return ScreenContext.IN_GAME_HUD
            elif len(menu_indicators) > 0:
                return ScreenContext.MAIN_MENU
            else:
                return ScreenContext.UNKNOWN
                
        except Exception as e:
            self.logger.warning(f"Screen context classification failed: {e}")
            return ScreenContext.UNKNOWN
    
    def _extract_numeric_value(self, text: str) -> float:
        """Extract numeric value from text (e.g., 'Spice: 2500' → 2500.0)"""
        try:
            import re
            numbers = re.findall(r'\d+', text)
            return float(numbers[0]) if numbers else 0.0
        except:
            return 0.0
    
    def _update_state_history(self, state_vector: np.ndarray):
        """Update temporal state history for dynamics."""
        self.state_history.append(state_vector)
        if len(self.state_history) > self.max_history_length:
            self.state_history.pop(0)
    
    def _update_conversion_stats(self, conversion_time: float, vector_size: int):
        """Update performance statistics."""
        self.conversion_stats['total_conversions'] += 1
        total = self.conversion_stats['total_conversions']
        current_avg = self.conversion_stats['average_conversion_time']
        self.conversion_stats['average_conversion_time'] = (
            (current_avg * (total - 1) + conversion_time) / total
        )
        self.conversion_stats['last_state_vector_size'] = vector_size
    
    def get_state_vector_info(self) -> Dict[str, Any]:
        """
        Get comprehensive state vector configuration and statistics.
        
        Returns:
            Dict with vector dimensions, performance stats, and configuration
        """
        return {
            'vector_dimensions': self.config.total_dimensions,
            'component_breakdown': {
                'resources': self.config.RESOURCE_DIMS,
                'context': self.config.CONTEXT_DIMS,
                'spatial': self.config.SPATIAL_DIMS,
                'confidence': self.config.CONFIDENCE_DIMS,
                'temporal': self.config.TEMPORAL_DIMS
            },
            'performance_stats': self.conversion_stats,
            'mlops_integration': MLOPS_AVAILABLE,
            'max_detections_tracked': self.config.MAX_DETECTIONS,
            'supported_contexts': [ctx.name for ctx in ScreenContext]
        }


# Factory function for easy instantiation
def create_state_representation_module(config: Optional[StateVectorConfig] = None) -> StateRepresentationModule:
    """
    Factory function for creating state representation module.
    
    Args:
        config: Optional custom configuration
        
    Returns:
        Configured StateRepresentationModule instance
    """
    return StateRepresentationModule(config=config)


# Convenience function for direct state vector generation
def convert_semantic_map_to_rl_state(semantic_map: SemanticMap) -> np.ndarray:
    """
    Direct conversion function for external use.
    
    Args:
        semantic_map: SemanticMap from M3 YOLOv8 pipeline
        
    Returns:
        np.ndarray: Fixed-length state vector for RL
    """
    module = create_state_representation_module()
    return module.convert_to_state_vector(semantic_map)