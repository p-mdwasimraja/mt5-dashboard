"""
Helper functions for data loading
"""
import json
import pandas as pd
from pathlib import Path

def load_stats():
    """Load summary statistics"""
    stats_path = Path('data/processed/summary/stats.json')
    if stats_path.exists():
        with open(stats_path, 'r') as f:
            return json.load(f)
    return None

def load_accounts():
    """Load latest account data"""
    accounts_path = Path('data/processed/summary/all_accounts_latest.csv')
    if accounts_path.exists():
        return pd.read_csv(accounts_path)
    return pd.DataFrame()

def load_transactions():
    """Load latest transaction data"""
    transactions_path = Path('data/processed/summary/all_transactions_latest.csv')
    if transactions_path.exists():
        df = pd.read_csv(transactions_path)
        # Convert time columns to datetime
        if 'TimeOpen' in df.columns:
            df['TimeOpen'] = pd.to_datetime(df['TimeOpen'], errors='coerce')
        if 'TimeClose' in df.columns:
            df['TimeClose'] = pd.to_datetime(df['TimeClose'], errors='coerce')
        return df
    return pd.DataFrame()

def load_deposits():
    """Load latest deposit data"""
    deposits_path = Path('data/processed/summary/all_deposits_latest.csv')
    if deposits_path.exists():
        df = pd.read_csv(deposits_path)
        if 'TimeOpen' in df.columns:
            df['TimeOpen'] = pd.to_datetime(df['TimeOpen'], errors='coerce')
        return df
    return pd.DataFrame()