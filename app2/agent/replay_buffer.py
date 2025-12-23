import random
from collections import deque
import threading
from typing import Deque, List, Tuple, Any, Optional
import numpy as np
import torch

class ReplayBuffer:
    def __init__(self, capacity: int, batch_size: int) -> None:
        """
        Experience replay buffer for storing and sampling transitions.
        
        Args:
            capacity: Maximum number of transitions stored in the buffer
            batch_size: Number of transitions to sample in each batch
        """
        self.capacity = capacity
        self.batch_size = batch_size
        self.buffer: Deque[Tuple[Any, ...]] = deque(maxlen=capacity)
        self.lock = threading.Lock()

    def add(self, state: np.ndarray, action: np.ndarray, reward: float, next_state: np.ndarray, done: bool) -> None:
        """
        Add a new experience to the buffer.
        
        Args:
            state: Current state observation
            action: Action taken
            reward: Reward received
            next_state: Next state observation
            done: Terminal state flag
        """
        with self.lock:
            self.buffer.append((state, action, reward, next_state, done))

    def sample(self) -> Tuple[torch.Tensor, ...]:
        """
        Sample a batch of experiences from the buffer.
        
        Returns:
            Tuple containing:
                states: Tensor of shape (batch_size, *state_shape)
                actions: Tensor of shape (batch_size, *action_shape)
                rewards: Tensor of shape (batch_size, 1)
                next_states: Tensor of shape (batch_size, *state_shape)
                dones: Tensor of shape (batch_size, 1)
        
        Raises:
            ValueError: If not enough samples are available in the buffer
        """
        with self.lock:
            if len(self.buffer) < self.batch_size:
                raise ValueError(f"Not enough samples in buffer ({len(self.buffer)} available, {self.batch_size} needed)")
            
            batch = random.sample(self.buffer, self.batch_size)
            states, actions, rewards, next_states, dones = zip(*batch)

            states_tensor = torch.tensor(np.array(states), dtype=torch.float32)
            actions_tensor = torch.tensor(np.array(actions))
            rewards_tensor = torch.tensor(np.array(rewards), dtype=torch.float32).unsqueeze(-1)
            next_states_tensor = torch.tensor(np.array(next_states), dtype=torch.float32)
            dones_tensor = torch.tensor(np.array(dones, dtype=np.float32), dtype=torch.float32).unsqueeze(-1)

            return (states_tensor, actions_tensor, rewards_tensor, next_states_tensor, dones_tensor)

    def __len__(self) -> int:
        """Return the current number of stored transitions."""
        with self.lock:
            return len(self.buffer)