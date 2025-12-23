import pandas as pd
from typing import Optional

def load_data(file_path: str, datetime_col: str, value_col: str) -> pd.DataFrame:
    """
    Load and preprocess time-series energy data from a CSV file.
    
    Steps:
    1. Read CSV file using pandas
    2. Parse specified datetime column to datetime objects
    3. Set datetime column as DataFrame index
    4. Extract specified value column
    5. Handle datetime parsing errors by coercing invalid dates to NaT
    6. Drop rows with NaT in datetime index
    7. Sort DataFrame by datetime index
    
    Args:
        file_path: Path to the CSV file
        datetime_col: Name of the datetime column in the CSV
        value_col: Name of the value column to extract
    
    Returns:
        pd.DataFrame: Preprocessed DataFrame with datetime index and single value column
    
    Raises:
        FileNotFoundError: If specified file_path doesn't exist
        KeyError: If specified datetime_col or value_col doesn't exist in CSV
        ValueError: For general data parsing issues
    
    Example:
        df = load_data('data/raw/energy_data.csv', 'timestamp', 'consumption')
    """
    try:
        # Read CSV with datetime parsing for specified column
        df = pd.read_csv(
            file_path,
            parse_dates=[datetime_col],
            infer_datetime_format=True,
            usecols=[datetime_col, value_col]
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Data file not found at {file_path}") from e
    except ValueError as e:
        # Handle missing columns
        raise KeyError(f"One or more specified columns missing in {file_path}") from e
    
    # Verify required columns exist
    if datetime_col not in df.columns:
        raise KeyError(f"Datetime column '{datetime_col}' not found in DataFrame")
    if value_col not in df.columns:
        raise KeyError(f"Value column '{value_col}' not found in DataFrame")
    
    # Set datetime index and handle invalid dates
    df[datetime_col] = pd.to_datetime(df[datetime_col], errors='coerce')
    df = df.dropna(subset=[datetime_col])
    df.set_index(datetime_col, inplace=True)
    
    # Extract value column and sort
    result_df = df[[value_col]].copy()
    result_df.sort_index(inplace=True)
    
    return result_df