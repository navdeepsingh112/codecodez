import tensorflow as tf
from typing import Tuple, Dict, Any

def train_model(model: tf.keras.Model, 
                train_data: Tuple[tf.Tensor, tf.Tensor], 
                val_data: Tuple[tf.Tensor, tf.Tensor], 
                config: Dict[str, Any]) -> tf.keras.callbacks.History:
    """
    Compiles and trains a GRU model using TensorFlow Dataset pipeline.
    
    Args:
        model: Compiled or uncompiled Keras model
        train_data: Tuple of (train_features, train_labels) as tensors
        val_data: Tuple of (val_features, val_labels) as tensors
        config: Configuration dictionary containing:
            - 'batch_size': Batch size for training
            - 'epochs': Number of training epochs
            - 'patience': EarlyStopping patience
            - 'model_save_path': Path to save best model weights
    
    Returns:
        Training history object
    
    Raises:
        ValueError: If required config keys are missing or invalid data provided
    """
    # Validate config parameters
    required_keys = {'batch_size', 'epochs', 'patience', 'model_save_path'}
    if not required_keys.issubset(config.keys()):
        raise ValueError(f"Config missing required keys: {required_keys - set(config.keys())}")
    
    # Unpack and validate data
    X_train, y_train = train_data
    X_val, y_val = val_data
    
    if X_train.shape[0] == 0 or X_val.shape[0] == 0:
        raise ValueError("Training or validation data is empty")
    
    # Create TensorFlow Datasets
    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    val_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val))
    
    # Shuffle and batch datasets
    train_dataset = train_dataset.shuffle(buffer_size=1024).batch(config['batch_size'])
    val_dataset = val_dataset.batch(config['batch_size'])
    
    # Compile model (if not already compiled)
    if not model.optimizer:
        model.compile(
            optimizer=tf.keras.optimizers.Adam(),
            loss=tf.keras.losses.Huber(),
            metrics=['mae']
        )
    
    # Configure callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=config['patience'],
            restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=config['model_save_path'],
            monitor='val_loss',
            save_best_only=True,
            save_weights_only=True
        )
    ]
    
    # Train model
    history = model.fit(
        train_dataset,
        epochs=config['epochs'],
        validation_data=val_dataset,
        callbacks=callbacks
    )
    
    return history