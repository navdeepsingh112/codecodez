import logging
from src.config import load_config
from src.data_loader import load_data
from src.preprocessing import preprocess_data
from src.anomaly_detection import detect_and_remove_anomalies
from src.model import build_model
from src.train import train_model
from src.evaluate import evaluate_model
import tensorflow as tf

def main(config_path: str) -> None:
    """
    End-to-end execution of data processing, training, and evaluation pipeline.
    
    Steps:
    1. Load configuration from YAML file
    2. Set up logging
    3. Load and preprocess data
    4. Perform anomaly detection
    5. Create sequences and split data
    6. Build TensorFlow model
    7. Train model
    8. Evaluate model
    9. Save model and artifacts
    
    Args:
        config_path: Path to configuration YAML file
    
    Raises:
        FileNotFoundError: If config file is missing
        KeyError: For missing configuration sections
        ValueError: For invalid configuration values
    """
    try:
        # Load configuration
        config = load_config(config_path).get_config()
        
        # Initialize logging
        logging.basicConfig(
            level=config['logging']['level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        logger.info("Pipeline started")
        
        # Data loading
        logger.info("Loading data")
        data = load_data(config['data']['path'])
        
        # Preprocessing
        logger.info("Preprocessing data")
        processed_data = preprocess_data(data, config['preprocessing'])
        
        # Anomaly detection
        logger.info("Running anomaly detection")
        cleaned_data = detect_and_remove_anomalies(processed_data, config['anomaly_detection'])
        
        # Sequence creation and splitting
        logger.info("Creating sequences and splitting data")
        # Placeholder for sequence creation logic
        # This would typically be implemented in preprocessing or separate module
        # Example: 
        # from src.preprocessing import create_sequences, split_data
        # sequences = create_sequences(cleaned_data, **config['sequence'])
        # train_data, val_data, test_data = split_data(sequences, **config['split'])
        
        # Model building
        logger.info("Building model")
        model = build_model(config['model'])
        
        # Model training
        logger.info("Training model")
        # Placeholder for actual training call
        # Example: 
        # history = train_model(model, train_data, val_data, config['training'])
        
        # Model evaluation
        logger.info("Evaluating model")
        # Placeholder for evaluation call
        # Example: 
        # metrics = evaluate_model(model, test_data, config['evaluation'])
        
        # Save artifacts
        logger.info("Saving model and artifacts")
        # Placeholder for saving logic
        # Example: model.save(config['output']['model_path'])
        
        logger.info("Pipeline completed successfully")
        
    except FileNotFoundError as e:
        logging.error(f"Configuration file not found: {e}")
        raise
    except KeyError as e:
        logging.error(f"Missing configuration key: {e}")
        raise
    except ValueError as e:
        logging.error(f"Invalid configuration value: {e}")
        raise
    except Exception as e:
        logging.exception(f"Unexpected error in pipeline: {e}")
        raise

if __name__ == '__main__':
    main('config.yaml')

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fibonacci import router as fibonacci_router

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Fibonacci API",
        description="API for calculating Fibonacci numbers",
        version=os.getenv("APP_VERSION", "1.0.0")
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(fibonacci_router, prefix="/fib")

    @app.get("/health", tags=["Health Check"])
    async def health_check() -> dict:
        """
        Health check endpoint to verify service availability.
        
        Returns:
            dict: Status of the service
        """
        return {"status": "healthy", "version": app.version}

    return app

app = create_app()