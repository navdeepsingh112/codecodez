import tensorflow as tf
import numpy as np
import pandas as pd
from typing import Any

def predict(new_data: pd.Series, 
            anomaly_detector: Any, 
            scaler: Any, 
            model: tf.keras.Model, 
            sequence_length: int) -> np.ndarray:
    """
    Process new data through anomaly removal and generate forecasts.
    
    Steps:
    1. Detect and remove anomalies from input data
    2. Scale the cleaned data using provided scaler
    3. Pad/truncate data to required sequence length
    4. Create input sequence for the model
    5. Generate forecast using the trained model
    6. Inverse transform prediction to original scale
    
    Args:
        new_data: Input time series data as pandas Series
        anomaly_detector: Object with remove_anomalies method for data cleaning
        scaler: Scaler object with transform/inverse_transform methods
        model: Trained TensorFlow Keras forecasting model
        sequence_length: Required input sequence length for the model
        
    Returns:
        Forecasted values as 1D numpy array
    """
    # Step 1: Remove anomalies
    cleaned_series = anomaly_detector.remove_anomalies(new_data)
    
    # Convert to 2D array for scaling
    cleaned_values = cleaned_series.values.reshape(-1, 1)
    
    # Step 2: Apply scaling
    scaled_data = scaler.transform(cleaned_values)
    
    # Step 3: Pad/truncate to sequence_length
    if len(scaled_data) > sequence_length:
        # Take the most recent sequence
        input_sequence = scaled_data[-sequence_length:]
    else:
        # Pad beginning with zeros
        padding = np.zeros((sequence_length - len(scaled_data), 1))
        input_sequence = np.concatenate([padding, scaled_data])
    
    # Step 4: Create model input (add batch dimension)
    model_input = input_sequence.reshape(1, sequence_length, 1)
    
    # Step 5: Generate forecast
    prediction = model.predict(model_input)
    
    # Step 6: Inverse transform prediction
    # Reshape prediction to 2D (samples, features)
    prediction_2d = prediction.reshape(-1, 1)
    prediction_inv = scaler.inverse_transform(prediction_2d)
    
    return prediction_inv.flatten()