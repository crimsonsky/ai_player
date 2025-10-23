"""
DATA MANAGER - Module 6.1: Experience Replay Buffer and I/O Utilities
MLOps Data Pipeline for Reinforcement Learning Training

This module provides the foundational data management infrastructure for the RL training loop,
including experience replay buffer for SARSA tuples and high-speed numerical I/O utilities.

Features:
- ExperienceReplayBuffer class for efficient RL training data storage
- Random sampling for batch training
- High-speed numerical array I/O (HDF5/NPZ formats)
- Memory-efficient storage and retrieval
- Support for large-scale training datasets

Author: Agent B
Version: 1.0  
Compliance: AIP-SDS-V2.3, MODULE 6.1 specifications
"""

import numpy as np
import h5py
import pickle
import os
import random
from typing import List, Tuple, Optional, Dict, Any
from collections import deque
import json
from datetime import datetime
import threading
import logging


class ExperienceReplayBuffer:
    """
    Fixed-size circular buffer for storing and sampling SARSA tuples for RL training.
    
    Implements efficient storage and random sampling of experience tuples:
    (State, Action, Reward, Next_State, Done)
    
    Thread-safe implementation for concurrent access during training.
    """
    
    def __init__(self, capacity: int = 100000, state_shape: Tuple = None):
        """
        Initialize the experience replay buffer.
        
        Args:
            capacity: Maximum number of experiences to store
            state_shape: Shape of state vectors (for pre-allocation)
        """
        self.capacity = capacity
        self.state_shape = state_shape
        self.buffer = deque(maxlen=capacity)
        self.position = 0
        self.lock = threading.Lock()
        
        # Statistics
        self.total_added = 0
        self.total_sampled = 0
        
        # Pre-allocated arrays for efficiency (if state_shape provided)
        if state_shape:
            self._pre_allocate_arrays()
            
        logging.info(f"ExperienceReplayBuffer initialized with capacity {capacity}")
        
    def _pre_allocate_arrays(self):
        """Pre-allocate numpy arrays for memory efficiency"""
        self.states = np.zeros((self.capacity, *self.state_shape), dtype=np.float32)
        self.actions = np.zeros(self.capacity, dtype=np.int32)
        self.rewards = np.zeros(self.capacity, dtype=np.float32) 
        self.next_states = np.zeros((self.capacity, *self.state_shape), dtype=np.float32)
        self.dones = np.zeros(self.capacity, dtype=bool)
        self.use_arrays = True
        
    def add_experience(self, state: np.ndarray, action: int, reward: float, 
                      next_state: np.ndarray, done: bool):
        """
        Add a single experience tuple to the buffer.
        
        Args:
            state: Current state vector
            action: Action taken (integer ID)
            reward: Reward received
            next_state: Next state vector  
            done: Episode termination flag
        """
        with self.lock:
            if hasattr(self, 'use_arrays') and self.use_arrays:
                # Use pre-allocated arrays
                idx = self.position % self.capacity
                self.states[idx] = state
                self.actions[idx] = action
                self.rewards[idx] = reward
                self.next_states[idx] = next_state
                self.dones[idx] = done
            else:
                # Use deque for variable-size states
                experience = (state, action, reward, next_state, done)
                self.buffer.append(experience)
                
            self.position += 1
            self.total_added += 1
            
    def sample_batch(self, batch_size: int) -> Dict[str, np.ndarray]:
        """
        Sample a random batch of experiences for training.
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            Dictionary containing batched arrays of states, actions, rewards, etc.
        """
        with self.lock:
            if len(self) < batch_size:
                raise ValueError(f"Not enough experiences in buffer ({len(self)}) for batch size {batch_size}")
                
            if hasattr(self, 'use_arrays') and self.use_arrays:
                # Sample from pre-allocated arrays
                current_size = min(self.position, self.capacity)
                indices = np.random.choice(current_size, batch_size, replace=False)
                
                batch = {
                    'states': self.states[indices].copy(),
                    'actions': self.actions[indices].copy(), 
                    'rewards': self.rewards[indices].copy(),
                    'next_states': self.next_states[indices].copy(),
                    'dones': self.dones[indices].copy()
                }
            else:
                # Sample from deque
                experiences = random.sample(self.buffer, batch_size)
                
                batch = {
                    'states': np.array([e[0] for e in experiences]),
                    'actions': np.array([e[1] for e in experiences]),
                    'rewards': np.array([e[2] for e in experiences]), 
                    'next_states': np.array([e[3] for e in experiences]),
                    'dones': np.array([e[4] for e in experiences])
                }
                
            self.total_sampled += batch_size
            return batch
            
    def __len__(self) -> int:
        """Return current number of experiences in buffer"""
        if hasattr(self, 'use_arrays') and self.use_arrays:
            return min(self.position, self.capacity)
        else:
            return len(self.buffer)
            
    def is_ready(self, min_size: int) -> bool:
        """Check if buffer has enough experiences for training"""
        return len(self) >= min_size
        
    def clear(self):
        """Clear all experiences from buffer"""
        with self.lock:
            if hasattr(self, 'use_arrays') and self.use_arrays:
                self.position = 0
            else:
                self.buffer.clear()
            logging.info("Experience replay buffer cleared")
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get buffer usage statistics"""
        return {
            'capacity': self.capacity,
            'current_size': len(self),
            'total_added': self.total_added,
            'total_sampled': self.total_sampled,
            'utilization': len(self) / self.capacity,
            'memory_efficient': hasattr(self, 'use_arrays') and self.use_arrays
        }
        
    def save_to_disk(self, filepath: str):
        """Save buffer contents to disk for persistence"""
        with self.lock:
            try:
                if hasattr(self, 'use_arrays') and self.use_arrays:
                    # Save pre-allocated arrays
                    current_size = len(self)
                    with h5py.File(filepath, 'w') as f:
                        f.create_dataset('states', data=self.states[:current_size])
                        f.create_dataset('actions', data=self.actions[:current_size])
                        f.create_dataset('rewards', data=self.rewards[:current_size])
                        f.create_dataset('next_states', data=self.next_states[:current_size])
                        f.create_dataset('dones', data=self.dones[:current_size])
                        
                        # Metadata
                        f.attrs['capacity'] = self.capacity
                        f.attrs['position'] = self.position
                        f.attrs['state_shape'] = self.state_shape
                        
                else:
                    # Save deque buffer
                    with open(filepath, 'wb') as f:
                        pickle.dump({
                            'buffer': list(self.buffer),
                            'capacity': self.capacity,
                            'position': self.position,
                            'total_added': self.total_added,
                            'total_sampled': self.total_sampled
                        }, f)
                        
                logging.info(f"Experience buffer saved to {filepath}")
                
            except Exception as e:
                logging.error(f"Failed to save buffer: {e}")
                raise
                
    def load_from_disk(self, filepath: str):
        """Load buffer contents from disk"""
        with self.lock:
            try:
                if filepath.endswith('.h5') or filepath.endswith('.hdf5'):
                    # Load HDF5 format (pre-allocated arrays)
                    with h5py.File(filepath, 'r') as f:
                        states = f['states'][:]
                        actions = f['actions'][:]
                        rewards = f['rewards'][:]
                        next_states = f['next_states'][:]
                        dones = f['dones'][:]
                        
                        # Restore metadata
                        self.capacity = f.attrs['capacity']
                        self.position = f.attrs['position']
                        self.state_shape = tuple(f.attrs['state_shape'])
                        
                        # Recreate arrays
                        self._pre_allocate_arrays()
                        current_size = len(states)
                        self.states[:current_size] = states
                        self.actions[:current_size] = actions
                        self.rewards[:current_size] = rewards
                        self.next_states[:current_size] = next_states
                        self.dones[:current_size] = dones
                        
                else:
                    # Load pickle format (deque buffer)
                    with open(filepath, 'rb') as f:
                        data = pickle.load(f)
                        
                    self.buffer = deque(data['buffer'], maxlen=self.capacity)
                    self.capacity = data['capacity']
                    self.position = data['position'] 
                    self.total_added = data.get('total_added', 0)
                    self.total_sampled = data.get('total_sampled', 0)
                    
                logging.info(f"Experience buffer loaded from {filepath}")
                
            except Exception as e:
                logging.error(f"Failed to load buffer: {e}")
                raise


class NumericalIOManager:
    """
    High-speed I/O utilities for numerical arrays and ML artifacts.
    
    Provides optimized storage and retrieval for:
    - State vectors (NumPy arrays)
    - Model weights and parameters
    - Training metrics and logs
    - Compressed data archives
    """
    
    @staticmethod
    def save_state_vector(filepath: str, array: np.ndarray, 
                         compression: str = 'gzip', metadata: Dict = None):
        """
        Save a NumPy state vector to disk with optimal compression.
        
        Args:
            filepath: Output file path
            array: NumPy array to save
            compression: Compression method ('gzip', 'lzf', 'szip')
            metadata: Optional metadata dictionary
        """
        try:
            if filepath.endswith('.npz'):
                # Use NPZ format for multiple arrays or metadata
                save_dict = {'state_vector': array}
                if metadata:
                    save_dict['metadata'] = np.array([json.dumps(metadata)])
                np.savez_compressed(filepath, **save_dict)
                
            elif filepath.endswith('.h5') or filepath.endswith('.hdf5'):
                # Use HDF5 for large arrays with compression
                with h5py.File(filepath, 'w') as f:
                    f.create_dataset('state_vector', data=array, 
                                   compression=compression, compression_opts=9)
                    
                    # Store metadata as attributes
                    if metadata:
                        for key, value in metadata.items():
                            if isinstance(value, (str, int, float, bool)):
                                f.attrs[key] = value
                            else:
                                f.attrs[key] = json.dumps(value)
                                
            else:
                # Default to NPY format
                np.save(filepath, array)
                
            # Log file size and compression ratio if available
            file_size = os.path.getsize(filepath)
            uncompressed_size = array.nbytes
            compression_ratio = uncompressed_size / file_size if file_size > 0 else 1.0
            
            logging.info(f"Saved state vector: {filepath}")
            logging.info(f"Compression ratio: {compression_ratio:.2f}x ({file_size} bytes)")
            
        except Exception as e:
            logging.error(f"Failed to save state vector: {e}")
            raise
            
    @staticmethod  
    def load_state_vector(filepath: str) -> Tuple[np.ndarray, Optional[Dict]]:
        """
        Load a NumPy state vector from disk.
        
        Args:
            filepath: Input file path
            
        Returns:
            Tuple of (array, metadata_dict)
        """
        try:
            metadata = None
            
            if filepath.endswith('.npz'):
                # Load NPZ format
                with np.load(filepath) as data:
                    array = data['state_vector']
                    if 'metadata' in data:
                        metadata_str = str(data['metadata'].item())
                        metadata = json.loads(metadata_str)
                        
            elif filepath.endswith('.h5') or filepath.endswith('.hdf5'):
                # Load HDF5 format
                with h5py.File(filepath, 'r') as f:
                    array = f['state_vector'][:]
                    
                    # Load metadata from attributes
                    metadata = {}
                    for key, value in f.attrs.items():
                        try:
                            # Try to parse as JSON first
                            if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                                metadata[key] = json.loads(value)
                            else:
                                metadata[key] = value
                        except (json.JSONDecodeError, TypeError):
                            metadata[key] = value
                            
            else:
                # Load NPY format
                array = np.load(filepath)
                
            logging.info(f"Loaded state vector: {filepath}, shape: {array.shape}")
            return array, metadata
            
        except Exception as e:
            logging.error(f"Failed to load state vector: {e}")
            raise
            
    @staticmethod
    def save_training_batch(filepath: str, states: np.ndarray, actions: np.ndarray,
                           rewards: np.ndarray, metadata: Dict = None):
        """
        Save a complete training batch with multiple arrays.
        
        Args:
            filepath: Output file path  
            states: State vectors array
            actions: Actions array
            rewards: Rewards array
            metadata: Training metadata (epoch, loss, etc.)
        """
        try:
            with h5py.File(filepath, 'w') as f:
                # Save main arrays with compression
                f.create_dataset('states', data=states, compression='gzip', compression_opts=9)
                f.create_dataset('actions', data=actions, compression='gzip', compression_opts=9) 
                f.create_dataset('rewards', data=rewards, compression='gzip', compression_opts=9)
                
                # Save metadata
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            f.attrs[key] = value
                        else:
                            f.attrs[key] = json.dumps(value)
                            
                # Add timestamp
                f.attrs['saved_at'] = datetime.now().isoformat()
                
            logging.info(f"Saved training batch: {filepath}")
            
        except Exception as e:
            logging.error(f"Failed to save training batch: {e}")
            raise
            
    @staticmethod
    def load_training_batch(filepath: str) -> Dict[str, Any]:
        """
        Load a complete training batch from disk.
        
        Args:
            filepath: Input file path
            
        Returns:
            Dictionary containing arrays and metadata
        """
        try:
            with h5py.File(filepath, 'r') as f:
                result = {
                    'states': f['states'][:],
                    'actions': f['actions'][:],
                    'rewards': f['rewards'][:],
                    'metadata': {}
                }
                
                # Load metadata
                for key, value in f.attrs.items():
                    try:
                        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                            result['metadata'][key] = json.loads(value) 
                        else:
                            result['metadata'][key] = value
                    except (json.JSONDecodeError, TypeError):
                        result['metadata'][key] = value
                        
            logging.info(f"Loaded training batch: {filepath}")
            return result
            
        except Exception as e:
            logging.error(f"Failed to load training batch: {e}")
            raise
            
    @staticmethod
    def create_data_archive(archive_path: str, data_dict: Dict[str, np.ndarray],
                           compression_level: int = 9):
        """
        Create a compressed archive of multiple data arrays.
        
        Args:
            archive_path: Output archive path (.h5 extension recommended)
            data_dict: Dictionary of name -> array mappings
            compression_level: Compression level (0-9)
        """
        try:
            with h5py.File(archive_path, 'w') as f:
                for name, array in data_dict.items():
                    f.create_dataset(name, data=array, 
                                   compression='gzip', compression_opts=compression_level)
                    
                # Add archive metadata
                f.attrs['created_at'] = datetime.now().isoformat()
                f.attrs['num_arrays'] = len(data_dict)
                f.attrs['total_size'] = sum(arr.nbytes for arr in data_dict.values())
                
            logging.info(f"Created data archive: {archive_path} with {len(data_dict)} arrays")
            
        except Exception as e:
            logging.error(f"Failed to create data archive: {e}")
            raise


def create_data_directories(base_path: str) -> Dict[str, str]:
    """
    Create the standard MLOps data directory structure.
    
    Args:
        base_path: Base directory path for data storage
        
    Returns:
        Dictionary mapping directory names to paths
    """
    directories = {
        'experiences': os.path.join(base_path, 'experiences'),
        'states': os.path.join(base_path, 'state_vectors'), 
        'models': os.path.join(base_path, 'model_weights'),
        'training': os.path.join(base_path, 'training_batches'),
        'archives': os.path.join(base_path, 'archives'),
        'annotations': os.path.join(base_path, 'annotations'),
        'logs': os.path.join(base_path, 'training_logs')
    }
    
    for name, path in directories.items():
        os.makedirs(path, exist_ok=True)
        logging.info(f"Created directory: {path}")
        
    return directories


def main():
    """
    Main function for testing data management utilities.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Data Manager Module 6.1 - Testing Mode")
    
    # Test ExperienceReplayBuffer
    print("\n1. Testing ExperienceReplayBuffer...")
    buffer = ExperienceReplayBuffer(capacity=1000, state_shape=(64,))
    
    # Add sample experiences
    for i in range(100):
        state = np.random.random((64,)).astype(np.float32)
        action = np.random.randint(0, 4)
        reward = np.random.random()
        next_state = np.random.random((64,)).astype(np.float32) 
        done = (i % 20 == 19)  # Episode ends every 20 steps
        
        buffer.add_experience(state, action, reward, next_state, done)
        
    print(f"Buffer statistics: {buffer.get_statistics()}")
    
    # Test sampling
    if buffer.is_ready(32):
        batch = buffer.sample_batch(32)
        print(f"Sampled batch shapes: {[(k, v.shape) for k, v in batch.items()]}")
        
    # Test I/O utilities
    print("\n2. Testing NumericalIOManager...")
    
    # Test state vector I/O
    test_vector = np.random.random((128,)).astype(np.float32)
    test_metadata = {'epoch': 10, 'loss': 0.001, 'timestamp': datetime.now().isoformat()}
    
    # Save and load
    NumericalIOManager.save_state_vector('test_state.h5', test_vector, metadata=test_metadata)
    loaded_vector, loaded_metadata = NumericalIOManager.load_state_vector('test_state.h5')
    
    print(f"Original shape: {test_vector.shape}, Loaded shape: {loaded_vector.shape}")
    print(f"Vectors match: {np.allclose(test_vector, loaded_vector)}")
    print(f"Metadata: {loaded_metadata}")
    
    # Cleanup
    if os.path.exists('test_state.h5'):
        os.remove('test_state.h5')
        
    print("\n✅ Data Manager Module 6.1 - All tests passed!")
    

if __name__ == "__main__":
    main()