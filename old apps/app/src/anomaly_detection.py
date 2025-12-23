import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict

def detect_and_remove_anomalies(data: pd.Series, config: Dict) -> pd.Series:
    """
    Identify anomalies using Isolation Forest and remove them by interpolation.
    
    Steps:
    1. Reshape 1D series to 2D array for sklearn
    2. Initialize IsolationForest with parameters from config
    3. Fit model and predict anomalies (anomalies marked as -1)
    4. Remove anomalous points by setting to NaN
    5. Interpolate missing values
    6. Return cleaned pandas Series
    
    Args:
        data: Input time series data as pandas Series
        config: Dictionary containing model parameters. Must include:
                'contamination': Expected proportion of outliers in data
                Optional: Any other IsolationForest parameters (n_estimators, max_samples, etc.)
    
    Returns:
        pd.Series: Cleaned data with anomalies removed and interpolated
    
    Raises:
        ValueError: If contamination is not in config or data contains insufficient points
    """
    # Validate input data
    if len(data) < 2:
        raise ValueError("Input data must contain at least 2 points")
    
    # Extract contamination with validation
    contamination = config.get('contamination')
    if contamination is None:
        raise ValueError("Config must contain 'contamination' parameter")
    
    # Reshape data for sklearn (n_samples, n_features)
    values = data.values.reshape(-1, 1)
    
    # Create model with config parameters (override contamination)
    model_params = {k: v for k, v in config.items() if k != 'contamination'}
    model = IsolationForest(contamination=contamination, **model_params)
    
    # Fit model and predict
    preds = model.fit_predict(values)
    
    # Create mask for normal points (1 = normal, -1 = anomaly)
    normal_mask = preds == 1
    
    # Create cleaned series with NaN for anomalies
    cleaned = data.copy()
    cleaned[~normal_mask] = np.nan
    
    # Interpolate missing values
    cleaned = cleaned.interpolate(method='linear', limit_direction='both')
    
    return cleaned