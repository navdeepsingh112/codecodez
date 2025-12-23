import torch
import torch.nn as nn
import torch.nn.functional as F

class DQN(nn.Module):
    """
    Deep Q-Network (DQN) model for reinforcement learning.
    
    Args:
        input_dim (int): Dimension of the input state
        output_dim (int): Dimension of the output action space
        hidden_layers (list[int]): List of integers specifying hidden layer sizes
    """
    
    def __init__(self, input_dim: int, output_dim: int, hidden_layers: list[int]):
        super().__init__()
        self.layers = nn.ModuleList()
        layer_sizes = [input_dim] + hidden_layers
        
        # Create hidden layers with ReLU activations and dropout
        for in_size, out_size in zip(layer_sizes[:-1], layer_sizes[1:]):
            self.layers.append(nn.Linear(in_size, out_size))
            self.layers.append(nn.ReLU())
            self.layers.append(nn.Dropout(p=0.2))
        
        # Output layer
        self.output_layer = nn.Linear(layer_sizes[-1], output_dim)
        self.initialize_weights()

    def initialize_weights(self):
        """Initialize weights using Xavier uniform initialization."""
        for layer in self.layers:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.constant_(layer.bias, 0.1)
        nn.init.xavier_uniform_(self.output_layer.weight)
        nn.init.constant_(self.output_layer.bias, 0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network.
        
        Args:
            x (torch.Tensor): Input state tensor
            
        Returns:
            torch.Tensor: Q-values for all possible actions
        """
        for layer in self.layers:
            x = layer(x)
        return self.output_layer(x)