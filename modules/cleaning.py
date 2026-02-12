import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, List, Dict, Any, Union

def impute_values(df: pd.DataFrame, column: str, strategy: str) -> Tuple[pd.DataFrame, str, int]:
    """
    Imputes missing values in a specified column using a strategy.
    
    Args:
        df: DataFrame to clean.
        column: Target column.
        strategy: One of 'Mean', 'Median', 'Mode', or 'Drop'.
        
    Returns:
        (cleaned_df, details, rows_affected)
    """
    initial_rows = len(df)
    rows_affected = df[column].isna().sum()
    
    if rows_affected == 0:
        return df, f"No missing values in '{column}'.", 0
    
    if strategy == "Drop":
        df = df.dropna(subset=[column])
        details = f"Dropped {rows_affected} rows with missing '{column}'."
    elif strategy == "Mean":
        val = df[column].mean()
        df[column] = df[column].fillna(val)
        details = f"Imputed missing '{column}' with Mean: {val:.2f}"
    elif strategy == "Median":
        val = df[column].median()
        df[column] = df[column].fillna(val)
        details = f"Imputed missing '{column}' with Median: {val:.2f}"
    elif strategy == "Mode":
        val = df[column].mode()[0]
        df[column] = df[column].fillna(val)
        details = f"Imputed missing '{column}' with Mode: {val}"
    
    return df, details, rows_affected

def standardize_dates(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, str, int]:
    """
    Standardizes a date column to datetime objects.
    
    Args:
        df: DataFrame to clean.
        column: Target date column.
        
    Returns:
        (cleaned_df, details, rows_affected)
    """
    initial_nulls = df[column].isna().sum()
    # Attempt to convert to datetime
    df[column] = pd.to_datetime(df[column], errors='coerce')
    final_nulls = df[column].isna().sum()
    
    rows_affected = len(df) - initial_nulls # All non-null rows processed
    # If conversion created more nulls, it means some values were invalid
    invalid_dates = final_nulls - initial_nulls
    
    details = f"Standardized '{column}' to datetime. "
    if invalid_dates > 0:
        details += f"Caution: {invalid_dates} invalid date formats were coerced to Null."
        
    return df, details, rows_affected

def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> Tuple[pd.DataFrame, str, int]:
    """Removes duplicate rows."""
    initial_rows = len(df)
    df = df.drop_duplicates(subset=subset)
    rows_affected = initial_rows - len(df)
    details = f"Removed {rows_affected} duplicates based on {subset if subset else 'all columns'}"
    return df, details, rows_affected

def drop_missing_values(df: pd.DataFrame, columns: List[str] = None) -> Tuple[pd.DataFrame, str, int]:
    """Drops rows with missing values in specified columns."""
    initial_rows = len(df)
    df = df.dropna(subset=columns) if columns else df.dropna()
    rows_dropped = initial_rows - len(df)
    details = f"Dropped {rows_dropped} rows with nulls."
    return df, details, rows_dropped
