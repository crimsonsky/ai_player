"""
AI Player - Main Entry Point
Implements the core RL loop as specified in the design document.
"""

from src.perception.perception_module import PerceptionModule
from src.state.state_representation import StateRepresentation
from src.decision.rl_model import RLModel
from src.action.action_module import ActionModule
from src.utils.config_manager import ConfigManager
from src.utils.logger import Logger

import time
import numpy as np


class AIPlayer:
    """
    Main AI Player class implementing the closed-loop RL system.
    
    Architecture:
    PERCEPTION -> STATE REPRESENTATION -> DECISION -> ACTION -> LEARNING
    """
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        """Initialize all modules and components."""
        self.config = ConfigManager(config_path)
        self.logger = Logger()
        
        # Initialize all modules
        self.perception = PerceptionModule(self.config.perception_config)
        self.state_rep = StateRepresentation(self.config.state_config)
        self.rl_model = RLModel(self.config.model_config)
        self.action_module = ActionModule(self.config.action_config)
        
        self.logger.info("AI Player initialized successfully")
    
    def run_episode(self, max_steps: int = 1000) -> dict:
        """
        Run a single episode of the RL loop.
        
        Returns:
            dict: Episode statistics and results
        """
        episode_stats = {
            'total_reward': 0.0,
            'steps': 0,
            'success': False
        }
        
        # Reset environment
        state = self._reset_environment()
        
        for step in range(max_steps):
            # PERCEPTION: Capture screen and extract features
            raw_screen = self.perception.capture_screen()
            features = self.perception.extract_features(raw_screen)
            
            # STATE REPRESENTATION: Convert to state vector
            state_vector = self.state_rep.create_state_vector(features)
            
            # DECISION: Get action from RL model
            action = self.rl_model.predict(state_vector)
            
            # ACTION: Execute the action
            success = self.action_module.execute_action(action)
            
            # Get reward and check if done
            reward = self._calculate_reward(features, action, success)
            done = self._is_episode_done(features)
            
            # LEARNING: Update model if training
            if self.rl_model.is_training:
                self.rl_model.step(state_vector, action, reward, done)
            
            episode_stats['total_reward'] += reward
            episode_stats['steps'] = step + 1
            
            if done:
                episode_stats['success'] = True
                break
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.1)
        
        self.logger.info(f"Episode completed: {episode_stats}")
        return episode_stats
    
    def _reset_environment(self) -> np.ndarray:
        """Reset the game environment and return initial state."""
        # This will be implemented in M1 - Game Launch POC
        pass
    
    def _calculate_reward(self, features: dict, action: int, success: bool) -> float:
        """Calculate reward based on current game state and action results."""
        # This will be implemented based on the reward function in design spec
        reward = -1.0  # Time step penalty
        
        if not success:
            reward -= 50.0  # Invalid action penalty
        
        # Add success rewards based on game state
        if features.get('is_in_game', False):
            reward += 100.0  # Successfully entered game
        
        return reward
    
    def _is_episode_done(self, features: dict) -> bool:
        """Check if the current episode should terminate."""
        return features.get('is_game_over', False) or features.get('is_in_game', False)


if __name__ == "__main__":
    # Initialize and run AI Player
    player = AIPlayer()
    
    # Run a test episode
    stats = player.run_episode()
    print(f"Episode completed with stats: {stats}")