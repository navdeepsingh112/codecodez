"""
Application configuration module

This module contains constants used throughout the application.
"""

# Maximum allowed value for 'n' parameter to prevent excessive computation
MAX_N: int = 10000

# Default error message when 'n' exceeds MAX_N
DEFAULT_MAX_N_MESSAGE: str = (
    f"Requested value exceeds maximum allowed limit of {MAX_N}. "
    "Please provide a smaller value."
)