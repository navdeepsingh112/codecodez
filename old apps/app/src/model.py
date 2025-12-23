import tensorflow as tf
from typing import Tuple, Dict

def build_gru_model(input_shape: Tuple[int, ...], config: Dict) -> tf.keras.Model:
    """
    Constructs a three-layer GRU model with dropout regularization.
    
    The model architecture consists of:
    1. Three GRU layers with the first two returning full sequences
    2. Dropout layers after the first two GRU layers
    3. A final Dense output layer
    
    Automatically uses CuDNN-accelerated GRU implementation when available.

    Args:
        input_shape: Shape of the input data (timesteps, features)
        config: Configuration dictionary with keys:
            - 'gru_units': List of 3 integers - units for each GRU layer
            - 'dropout_rate': Float between 0 and 1 - dropout rate
            - 'output_units': Integer - units for Dense output layer
            - 'output_activation': String - activation for output layer

    Returns:
        tf.keras.Model: Compiled GRU model

    Raises:
        ValueError: For invalid configuration parameters
    """
    # Validate configuration
    required_keys = {'gru_units', 'dropout_rate', 'output_units', 'output_activation'}
    missing_keys = required_keys - set(config.keys())
    if missing_keys:
        raise ValueError(f"Missing required config keys: {missing_keys}")
    
    gru_units = config['gru_units']
    if len(gru_units) != 3:
        raise ValueError("gru_units must contain exactly 3 integers")
    
    for i, units in enumerate(gru_units):
        if not isinstance(units, int) or units <= 0:
            raise ValueError(f"Invalid units in gru_units[{i}]: must be positive integer")
    
    dropout_rate = config['dropout_rate']
    if not 0 <= dropout_rate < 1:
        raise ValueError("dropout_rate must be in [0, 1)")
    
    output_units = config['output_units']
    if not isinstance(output_units, int) or output_units <= 0:
        raise ValueError("output_units must be positive integer")
    
    # Build model
    model = tf.keras.Sequential()
    
    # First GRU layer
    model.add(tf.keras.layers.GRU(
        units=gru_units[0],
        return_sequences=True,
        input_shape=input_shape,
        name='gru_1'
    ))
    model.add(tf.keras.layers.Dropout(dropout_rate, name='dropout_1'))
    
    # Second GRU layer
    model.add(tf.keras.layers.GRU(
        units=gru_units[1],
        return_sequences=True,
        name='gru_2'
    ))
    model.add(tf.keras.layers.Dropout(dropout_rate, name='dropout_2'))
    
    # Third GRU layer
    model.add(tf.keras.layers.GRU(
        units=gru_units[2],
        return_sequences=False,
        name='gru_3'
    ))
    
    # Output layer
    model.add(tf.keras.layers.Dense(
        units=output_units,
        activation=config['output_activation'],
        name='output'
    ))
    
    return model