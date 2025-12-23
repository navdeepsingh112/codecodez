import pandas as pd
from sklearn.preprocessing import RobustScaler
from typing import Tuple, Any

def preprocess_data(data: pd.Series, config: dict) -> Tuple[pd.Series, Any]:
    """
    Preprocess time-series data by handling missing values and normalizing.
    
    Steps:
    1. Linearly interpolate missing values
    2. Initialize and fit RobustScaler
    3. Transform data using fitted scaler
    4. Return scaled data and scaler object
    
    Args:
        data: Input time-series data as pandas Series
        config: Configuration dictionary (currently unused but included for future extensibility)
    
    Returns:
        Tuple containing:
            - Scaled data as pandas Series
            - Fitted RobustScaler object
    
    Raises:
        TypeError: If input data is not a pandas Series
        ValueError: If data contains non-numeric values or insufficient data points
    """
    if not isinstance(data, pd.Series):
        raise TypeError("Input data must be a pandas Series")
    
    if data.empty:
        return data, None
    
    # Handle missing values via linear interpolation
    interpolated = data.interpolate(method='linear', limit_direction='both')
    
    # Check for remaining NaNs (e.g., if all values were NaN initially)
    if interpolated.isna().any():
        raise ValueError("Data interpolation failed - insufficient valid points")
    
    # Reshape data for scaler (1D array to 2D column vector)
    values = interpolated.values.reshape(-1, 1)
    
    # Initialize and fit RobustScaler
    scaler = RobustScaler()
    scaled_values = scaler.fit_transform(values)
    
    # Convert back to pandas Series with original index
    scaled_series = pd.Series(
        scaled_values.flatten(), 
        index=interpolated.index, 
        name=interpolated.name
    )
    
    return scaled_series, scaler

import numpy as np
from typing import Tuple

def create_sequences(data: np.ndarray, sequence_length: int, forecast_horizon: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate input-output sequences using sliding window approach.
    
    This function creates input sequences of fixed length (sequence_length) and corresponding 
    output sequences of fixed length (forecast_horizon) by sliding a window over the input data.
    The temporal order of the data is preserved in the generated sequences.
    
    Parameters:
        data (np.ndarray): Input time series data as a 2D numpy array (timesteps, features)
        sequence_length (int): Number of timesteps in each input sequence
        forecast_horizon (int): Number of future timesteps to predict (output sequence length)
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: 
            X - Input sequences array of shape (num_sequences, sequence_length, num_features)
            y - Output sequences array of shape (num_sequences, forecast_horizon, num_features)
            
    Raises:
        ValueError: If input data has insufficient length or invalid dimensions
    """
    # Validate input data
    if not isinstance(data, np.ndarray):
        raise TypeError("Input data must be a numpy array")
    if data.ndim != 2:
        raise ValueError("Input data must be a 2D array (timesteps, features)")
    if len(data) < sequence_length + forecast_horizon:
        raise ValueError(f"Insufficient data length. Requires at least {sequence_length + forecast_horizon} timesteps, got {len(data)}")
    if sequence_length <= 0 or forecast_horizon <= 0:
        raise ValueError("Sequence length and forecast horizon must be positive integers")
    
    num_samples = len(data) - sequence_length - forecast_horizon + 1
    X = np.zeros((num_samples, sequence_length, data.shape[1]))
    y = np.zeros((num_samples, forecast_horizon, data.shape[1]))
    
    for i in range(num_samples):
        start_idx = i
        end_idx = i + sequence_length
        X[i] = data[start_idx:end_idx]
        y[i] = data[end_idx:end_idx + forecast_horizon]
        
    return X, y

import numpy as np
from typing import Dict, Tuple

def temporal_split(X: np.ndarray, y: np.ndarray, split_ratios: Tuple[float, float, float]) -> Dict[str, np.ndarray]:
    """
    Split sequences into training, validation, and test sets while preserving temporal order.
    
    Args:
        X: Input features array of shape (n_samples, ...) in temporal order.
        y: Target values array of shape (n_samples, ...) in temporal order.
        split_ratios: Tuple of three floats (train_ratio, val_ratio, test_ratio) that sum to 1.0.
    
    Returns:
        Dictionary containing:
            'X_train': Training features
            'X_val': Validation features
            'X_test': Test features
            'y_train': Training targets
            'y_val': Validation targets
            'y_test': Test targets
    
    Raises:
        ValueError: If split_ratios doesn't have exactly three elements, 
                    if ratios don't sum to 1.0, 
                    or if X and y have different sample counts.
    """
    if len(split_ratios) != 3:
        raise ValueError("split_ratios must contain exactly three elements")
    
    if not np.isclose(sum(split_ratios), 1.0, atol=1e-7):
        raise ValueError(f"split_ratios must sum to 1.0, got {sum(split_ratios)}")
    
    n_samples = X.shape[0]
    if y.shape[0] != n_samples:
        raise ValueError(f"X and y have different sample counts: {n_samples} vs {y.shape[0]}")
    
    if n_samples == 0:
        empty_X = np.empty((0, *X.shape[1:]), dtype=X.dtype)
        empty_y = np.empty((0, *y.shape[1:]), dtype=y.dtype)
        return {
            'X_train': empty_X,
            'X_val': empty_X,
            'X_test': empty_X,
            'y_train': empty_y,
            'y_val': empty_y,
            'y_test': empty_y
        }
    
    train_size = int(split_ratios[0] * n_samples)
    val_size = int(split_ratios[1] * n_samples)
    test_size = n_samples - train_size - val_size
    
    X_train = X[:train_size]
    X_val = X[train_size:train_size + val_size]
    X_test = X[train_size + val_size:]
    
    y_train = y[:train_size]
    y_val = y[train_size:train_size + val_size]
    y_test = y[train_size + val_size:]
    
    return {
        'X_train': X_train,
        'X_val': X_val,
        'X_test': X_test,
        'y_train': y_train,
        'y_val': y_val,
        'y_test': y_test
    }