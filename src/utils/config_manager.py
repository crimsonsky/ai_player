"""
Configuration Manager - Handles loading and managing system configurations.
"""

import yaml
import json
from typing import Dict, Any
from pathlib import Path


class ConfigManager:
    """
    Manages configuration files for the AI Player system.
    """
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to main configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Module-specific configs
        self.perception_config = self.config.get('perception', {})
        self.state_config = self.config.get('state', {})
        self.model_config = self.config.get('model', {})
        self.action_config = self.config.get('action', {})
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                        return yaml.safe_load(f)
                    elif self.config_path.suffix.lower() == '.json':
                        return json.load(f)
            
            # Return default configuration if file doesn't exist
            return self._get_default_config()
            
        except Exception as e:
            print(f"Error loading config from {self.config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'system': {
                'project_name': 'ai_player',
                'version': '1.0.0',
                'debug_mode': True
            },
            'perception': {
                'confidence_threshold': 0.8,
                'template_library_path': 'data/templates',
                'screenshot_archive_path': 'data/screenshots'
            },
            'state': {
                'history_frames': 4,
                'state_size': 26,
                'normalize_coordinates': True
            },
            'model': {
                'algorithm': 'PPO',
                'training_mode': True,
                'state_size': 104,  # 26 * 4 frames
                'action_size': 3,
                'learning_rate': 3e-4,
                'n_steps': 2048,
                'batch_size': 64,
                'n_epochs': 10,
                'gamma': 0.99,
                'gae_lambda': 0.95,
                'clip_range': 0.2,
                'ent_coef': 0.01,
                'vf_coef': 0.5,
                'verbose': 1
            },
            'action': {
                'smooth_mouse_movement': True,
                'movement_steps': 10,
                'click_delay': 0.01,
                'key_press_delay': 0.01
            },
            'game': {
                'name': 'Dune Legacy',
                'app_path': '/Applications/Dune Legacy.app',
                'startup_delay': 3.0
            },
            'logging': {
                'level': 'INFO',
                'log_file': 'data/logs/ai_player.log',
                'tensorboard_dir': 'data/logs/tensorboard'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, path: str = None) -> bool:
        """Save current configuration to file."""
        try:
            save_path = Path(path) if path else self.config_path
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w') as f:
                if save_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
                elif save_path.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving config to {save_path}: {e}")
            return False