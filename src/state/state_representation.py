"""
State Representation Module - Module 2: FEATURES -> State Vector
Converts visual features into compact numerical state vectors for RL.
"""

import numpy as np
from typing import Dict, Any, List


class StateRepresentation:
    """
    Handles conversion of perception features into state vectors for RL model.
    Implements state vector structure from design specification Section 3.1.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the State Representation module.
        
        Args:
            config: Configuration dictionary for state settings
        """
        self.config = config
        self.history_frames = config.get('history_frames', 4)
        self.state_history = []
        self.state_size = self._calculate_state_size()
    
    def _calculate_state_size(self) -> int:
        """Calculate the total size of the state vector."""
        # Based on design spec Section 3.1:
        # - Game Phase Indicators: 3 (is_in_main_menu, is_in_game, is_game_over)
        # - Resources/Stats: 2 (current_minerals, power_consumption)  
        # - Perception Confidence: 1 (avg_confidence_score)
        # - Element positions: Variable, assume max 10 elements * 2 coords = 20
        base_size = 3 + 2 + 1 + 20
        return base_size
    
    def create_state_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Convert perception features into a state vector.
        
        Args:
            features: Features extracted from perception module
            
        Returns:
            np.ndarray: Normalized state vector for RL model
        """
        try:
            # Create base state vector
            state = np.zeros(self.state_size, dtype=np.float32)
            
            # Game Phase Indicators (positions 0-2)
            state[0] = float(features.get('is_in_main_menu', False))
            state[1] = float(features.get('is_in_game', False))
            state[2] = float(features.get('is_game_over', False))
            
            # Resources/Stats (positions 3-4)
            # Normalize resources to reasonable ranges
            state[3] = self._normalize_resource(features.get('current_minerals', 0), max_val=10000)
            state[4] = self._normalize_resource(features.get('power_consumption', 0), max_val=1000)
            
            # Perception Confidence (position 5)
            state[5] = features.get('avg_confidence_score', 0.0)
            
            # Element positions (positions 6-25)
            elements = features.get('elements', [])
            element_start_idx = 6
            max_elements = 10
            
            for i, element in enumerate(elements[:max_elements]):
                if i < max_elements:
                    idx = element_start_idx + (i * 2)
                    state[idx] = element.get('x', 0.0)      # Normalized x coordinate
                    state[idx + 1] = element.get('y', 0.0)  # Normalized y coordinate
            
            # Add to history and return stacked state
            self.state_history.append(state)
            
            # Keep only the last N frames
            if len(self.state_history) > self.history_frames:
                self.state_history.pop(0)
            
            # Create history-stacked state
            stacked_state = self._create_stacked_state()
            
            return stacked_state
            
        except Exception as e:
            print(f"Error creating state vector: {e}")
            return np.zeros(self.state_size * self.history_frames, dtype=np.float32)
    
    def _normalize_resource(self, value: int, max_val: int) -> float:
        """
        Normalize a resource value to [0, 1] range.
        
        Args:
            value: Raw resource value
            max_val: Maximum expected value for normalization
            
        Returns:
            float: Normalized value between 0 and 1
        """
        return min(float(value) / max_val, 1.0)
    
    def _create_stacked_state(self) -> np.ndarray:
        """
        Create history-stacked state vector.
        
        Returns:
            np.ndarray: Stacked state vector with temporal information
        """
        # Pad with zeros if we don't have enough history
        while len(self.state_history) < self.history_frames:
            self.state_history.insert(0, np.zeros(self.state_size, dtype=np.float32))
        
        # Stack the last N frames
        stacked = np.concatenate(self.state_history[-self.history_frames:])
        
        return stacked
    
    def reset_history(self) -> None:
        """Reset the state history for a new episode."""
        self.state_history = []
    
    def get_state_info(self) -> Dict[str, Any]:
        """
        Get information about the state representation.
        
        Returns:
            Dict containing state configuration info
        """
        return {
            'base_state_size': self.state_size,
            'history_frames': self.history_frames,
            'total_state_size': self.state_size * self.history_frames,
            'current_history_length': len(self.state_history)
        }
    
    def validate_state_vector(self, state: np.ndarray) -> Dict[str, Any]:
        """
        Validate state vector for anomalous values.
        
        Args:
            state: State vector to validate
            
        Returns:
            Dict containing validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check for NaN or infinite values
            if np.any(np.isnan(state)) or np.any(np.isinf(state)):
                validation['valid'] = False
                validation['errors'].append("State contains NaN or infinite values")
            
            # Check coordinate bounds (should be [0, 1])
            element_coords = state[6:26]  # Element positions
            if np.any(element_coords < 0) or np.any(element_coords > 1):
                validation['warnings'].append("Element coordinates outside [0, 1] range")
            
            # Check game state consistency
            game_states = state[:3]  # Game phase indicators
            if np.sum(game_states) > 1:
                validation['warnings'].append("Multiple game states active simultaneously")
            
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Validation error: {e}")
        
        return validation