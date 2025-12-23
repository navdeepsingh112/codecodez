import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import tensorflow as tf

def evaluate_model(model: tf.keras.Model, X_test: np.ndarray, y_test: np.ndarray, scaler: object) -> dict:
    """
    Evaluate model performance, inverse scale predictions and actuals, calculate metrics, and create a comparison plot.

    Args:
        model: Trained Keras model for prediction.
        X_test: Test input features as numpy array.
        y_test: Test target values as numpy array.
        scaler: Scaler object with inverse_transform method used during preprocessing.

    Returns:
        Dictionary containing:
            'mae': Mean Absolute Error
            'rmse': Root Mean Squared Error
            'figure': Matplotlib figure object of the time-series comparison plot

    Raises:
        ValueError: If inputs are empty or incompatible.
        AttributeError: If scaler lacks inverse_transform method.
        RuntimeError: If inverse transformation fails.
    """
    # Validate inputs
    if X_test.size == 0 or y_test.size == 0:
        raise ValueError("X_test and y_test must not be empty.")
    if not hasattr(scaler, 'inverse_transform'):
        raise AttributeError("Scaler must have an inverse_transform method.")
    
    # Generate predictions
    predictions = model.predict(X_test)
    if predictions.size == 0:
        raise RuntimeError("Model returned empty predictions.")
    
    # Check feature dimension compatibility
    if predictions.shape[-1] != y_test.shape[-1]:
        raise ValueError(
            f"Last dimension mismatch: predictions ({predictions.shape[-1]}) vs y_test ({y_test.shape[-1]})"
        )
    
    # Reshape to 2D for inverse transform
    original_pred_shape = predictions.shape
    original_y_shape = y_test.shape
    predictions_2d = predictions.reshape(-1, original_pred_shape[-1])
    y_test_2d = y_test.reshape(-1, original_y_shape[-1])
    
    # Apply inverse transform
    try:
        predictions_inv = scaler.inverse_transform(predictions_2d).reshape(original_pred_shape)
        actuals_inv = scaler.inverse_transform(y_test_2d).reshape(original_y_shape)
    except Exception as e:
        raise RuntimeError(f"Inverse transform failed: {str(e)}")
    
    # Calculate metrics
    mae = mean_absolute_error(actuals_inv, predictions_inv)
    rmse = np.sqrt(mean_squared_error(actuals_inv, predictions_inv))
    
    # Prepare data for plotting
    plot_actuals = actuals_inv.reshape(-1, actuals_inv.shape[-1])
    plot_preds = predictions_inv.reshape(-1, predictions_inv.shape[-1])
    
    # If multiple features, use first feature for plotting
    if plot_actuals.shape[1] > 1:
        plot_actuals = plot_actuals[:, 0]
        plot_preds = plot_preds[:, 0]
    else:
        plot_actuals = plot_actuals.squeeze()
        plot_preds = plot_preds.squeeze()
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(plot_actuals, label='Actual', alpha=0.7)
    ax.plot(plot_preds, label='Predicted', alpha=0.7, linestyle='--')
    ax.set_title("Actual vs Predicted Values")
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Value")
    ax.legend()
    plt.tight_layout()
    
    return {
        'mae': mae,
        'rmse': rmse,
        'figure': fig
    }