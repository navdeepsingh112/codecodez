import yaml
from typing import Dict

def load_config(config_path: str) -> Dict:
    """
    Load project configuration parameters from a YAML file.
    
    Args:
        config_path: Path to the YAML configuration file.
    
    Returns:
        Dictionary containing the configuration parameters.
    
    Raises:
        FileNotFoundError: If the specified configuration file doesn't exist.
        ValueError: If the configuration file is empty or doesn't contain a dictionary.
        yaml.YAMLError: If there's an error parsing the YAML content.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            
            if config is None:
                return {}
            if not isinstance(config, dict):
                raise ValueError(f"Configuration file '{config_path}' must contain a dictionary at the top level.")
            return config
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at path: '{config_path}'")