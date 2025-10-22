"""
RL Model - Module 3: DECISION
Implements PPO reinforcement learning model using Stable Baselines3 and PyTorch.
"""

import torch
import numpy as np
from typing import Dict, Any, Optional, Tuple
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
import gymnasium as gym
from gymnasium import spaces


class RLModel:
    """
    Reinforcement Learning model using PPO algorithm.
    Implements decision-making for the AI Player system.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the RL Model.
        
        Args:
            config: Configuration dictionary for model settings
        """
        self.config = config
        self.device = self._setup_device()
        self.is_training = config.get('training_mode', True)
        
        # Model parameters
        self.state_size = config.get('state_size', 104)  # 26 * 4 frames
        self.action_size = config.get('action_size', 3)   # No-op, Click, Key press
        
        # Initialize action and observation spaces
        self.action_space = spaces.Discrete(self.action_size)
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(self.state_size,), 
            dtype=np.float32
        )
        
        # PPO model
        self.model = None
        self.current_episode_data = []
        
        self._initialize_model()
    
    def _setup_device(self) -> torch.device:
        """Setup PyTorch device with MPS support for Apple Silicon."""
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            print("Using Metal Performance Shaders (MPS) for GPU acceleration")
        elif torch.cuda.is_available():
            device = torch.device("cuda")
            print("Using CUDA for GPU acceleration")
        else:
            device = torch.device("cpu")
            print("Using CPU for computation")
        
        return device
    
    def _initialize_model(self) -> None:
        """Initialize the PPO model with specified parameters."""
        try:
            # PPO hyperparameters from config
            model_params = {
                'learning_rate': self.config.get('learning_rate', 3e-4),
                'n_steps': self.config.get('n_steps', 2048),
                'batch_size': self.config.get('batch_size', 64),
                'n_epochs': self.config.get('n_epochs', 10),
                'gamma': self.config.get('gamma', 0.99),
                'gae_lambda': self.config.get('gae_lambda', 0.95),
                'clip_range': self.config.get('clip_range', 0.2),
                'ent_coef': self.config.get('ent_coef', 0.01),
                'vf_coef': self.config.get('vf_coef', 0.5),
                'verbose': self.config.get('verbose', 1)
            }
            
            # Create a dummy environment for PPO initialization
            env = DummyEnv(self.observation_space, self.action_space)
            
            # Initialize PPO model
            self.model = PPO(
                "MlpPolicy",
                env,
                device=self.device,
                **model_params
            )
            
            print(f"PPO model initialized successfully on device: {self.device}")
            
        except Exception as e:
            print(f"Error initializing PPO model: {e}")
            self.model = None
    
    def predict(self, state: np.ndarray, deterministic: bool = False) -> int:
        """
        Predict action given current state.
        
        Args:
            state: Current state vector
            deterministic: Whether to use deterministic policy
            
        Returns:
            int: Action ID to execute
        """
        try:
            if self.model is None:
                print("Model not initialized, returning random action")
                return np.random.randint(0, self.action_size)
            
            # Ensure state is properly shaped
            if state.shape[0] != self.state_size:
                print(f"Warning: State size mismatch. Expected {self.state_size}, got {state.shape[0]}")
                state = np.resize(state, self.state_size)
            
            # Get action from model
            action, _ = self.model.predict(state, deterministic=deterministic)
            
            return int(action)
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return 0  # Default to no-op action
    
    def step(self, state: np.ndarray, action: int, reward: float, done: bool, 
             next_state: Optional[np.ndarray] = None) -> None:
        """
        Store experience for training.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            done: Whether episode is finished
            next_state: Next state (optional for PPO)
        """
        if self.is_training:
            experience = {
                'state': state.copy(),
                'action': action,
                'reward': reward,
                'done': done
            }
            
            if next_state is not None:
                experience['next_state'] = next_state.copy()
            
            self.current_episode_data.append(experience)
    
    def train(self, total_timesteps: int = 10000) -> Dict[str, float]:
        """
        Train the model for specified timesteps.
        
        Args:
            total_timesteps: Number of timesteps to train
            
        Returns:
            Dict containing training statistics
        """
        if not self.is_training or self.model is None:
            print("Training not enabled or model not initialized")
            return {}
        
        try:
            print(f"Starting training for {total_timesteps} timesteps...")
            
            # Create training environment (this would be the actual game environment)
            # For now, use dummy environment
            env = DummyEnv(self.observation_space, self.action_space)
            self.model.set_env(env)
            
            # Train the model
            self.model.learn(total_timesteps=total_timesteps)
            
            print("Training completed successfully")
            
            # Return training stats
            return {
                'total_timesteps': total_timesteps,
                'training_completed': True
            }
            
        except Exception as e:
            print(f"Error during training: {e}")
            return {'error': str(e)}
    
    def save_model(self, path: str) -> bool:
        """
        Save the trained model.
        
        Args:
            path: Path to save the model
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if self.model is not None:
                self.model.save(path)
                print(f"Model saved to {path}")
                return True
            else:
                print("No model to save")
                return False
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self, path: str) -> bool:
        """
        Load a trained model.
        
        Args:
            path: Path to load the model from
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            self.model = PPO.load(path, device=self.device)
            print(f"Model loaded from {path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dict containing model information
        """
        if self.model is None:
            return {'model_initialized': False}
        
        return {
            'model_initialized': True,
            'device': str(self.device),
            'state_size': self.state_size,
            'action_size': self.action_size,
            'is_training': self.is_training,
            'policy_type': 'MlpPolicy',
            'algorithm': 'PPO'
        }


class DummyEnv(gym.Env):
    """
    Dummy environment for PPO initialization.
    Will be replaced with actual game environment wrapper.
    """
    
    def __init__(self, observation_space, action_space):
        super(DummyEnv, self).__init__()
        self.observation_space = observation_space
        self.action_space = action_space
    
    def step(self, action):
        obs = self.observation_space.sample()
        reward = np.random.random()
        done = np.random.random() > 0.95
        info = {}
        return obs, reward, done, False, info
    
    def reset(self, seed=None, options=None):
        obs = self.observation_space.sample()
        return obs, {}
    
    def render(self, mode='human'):
        pass
    
    def close(self):
        pass