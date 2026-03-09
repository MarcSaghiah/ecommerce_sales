"""
Data Loader Module
Handles loading data from various sources (raw, processed, sample).
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def load_processed_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load processed transaction data and RFM data.
    
    Returns:
        Tuple of (transactions_df, rfm_df)
    """
    project_root = get_project_root()
    processed_path = project_root / 'data' / 'processed'
    
    transactions = pd.read_csv(processed_path / 'cleaned_transactions.csv')
    rfm = pd.read_csv(processed_path / 'customer_rfm.csv')
    
    # Convert date columns
    transactions['InvoiceDate'] = pd.to_datetime(transactions['InvoiceDate'])
    transactions['YearMonth'] = pd.to_datetime(transactions['YearMonth'].astype(str))
    
    return transactions, rfm


def load_sample_data() -> pd.DataFrame:
    """
    Load sample data for quick testing.
    
    Returns:
        Sample transactions DataFrame
    """
    project_root = get_project_root()
    sample_path = project_root / 'data' / 'sample' / 'sample_data.csv'
    
    if not sample_path.exists():
        raise FileNotFoundError(
            f"Sample data not found at {sample_path}. "
            "Run preprocessing first: python src/preprocessing.py"
        )
    
    df = pd.read_csv(sample_path)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    return df


def load_data(use_sample: bool = False) -> pd.DataFrame:
    """
    Load transaction data, using sample if specified or if processed data unavailable.
    
    Args:
        use_sample: If True, load sample data instead of full processed data
        
    Returns:
        Transactions DataFrame
    """
    project_root = get_project_root()
    
    if use_sample:
        return load_sample_data()
    
    processed_file = project_root / 'data' / 'processed' / 'cleaned_transactions.csv'
    
    if processed_file.exists():
        df = pd.read_csv(processed_file)
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        return df
    else:
        print("⚠️ Processed data not found. Loading sample data instead.")
        return load_sample_data()


def check_data_availability() -> dict:
    """
    Check which data files are available.
    
    Returns:
        Dictionary with availability status for each data source
    """
    project_root = get_project_root()
    
    return {
        'raw': (project_root / 'data' / 'raw' / 'online_retail_II.xlsx').exists(),
        'processed': (project_root / 'data' / 'processed' / 'cleaned_transactions.csv').exists(),
        'rfm': (project_root / 'data' / 'processed' / 'customer_rfm.csv').exists(),
        'sample': (project_root / 'data' / 'sample' / 'sample_data.csv').exists()
    }


def create_date_filters(df: pd.DataFrame) -> dict:
    """
    Create date range information for filtering.
    
    Returns:
        Dictionary with min/max dates and available years/months
    """
    return {
        'min_date': df['InvoiceDate'].min(),
        'max_date': df['InvoiceDate'].max(),
        'years': sorted(df['Year'].unique()),
        'months': sorted(df['Month'].unique())
    }
