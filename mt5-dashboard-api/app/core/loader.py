"""
Optimized MT5 data loader with caching
Reduces I/O operations for better VPS performance
"""
from pathlib import Path
from typing import List, Optional
import pandas as pd
import logging

from .config import get_enabled_sources
from .cache import cached

logger = logging.getLogger(__name__)


def _parse_ea_from_filename(csv_path: Path) -> str:
    """
    Extract EA name from filename
    e.g. 'Ultimate-Timebomb_History.csv' -> 'Ultimate-Timebomb'
    """
    stem = csv_path.stem
    if "_" in stem:
        return stem.split("_", 1)[0]
    return stem


def _normalize_history_df(
    df: pd.DataFrame,
    csv_path: Path,
    account_label: str,
) -> pd.DataFrame:
    """
    Normalize a single *_History.csv DataFrame
    Format: EA_Name;TimeOpen;TimeClose;DealOpen;DealClose;Symbol;Type;Volume;
            PriceOpen;PriceClose;Profit;Swap;Commission;Duration;Comment
    """
    df = df.copy()

    # EA name
    if "EA_Name" in df.columns:
        df["EA_Name"] = df["EA_Name"].astype(str)
    else:
        df["EA_Name"] = _parse_ea_from_filename(csv_path)

    # Account source
    df["Account"] = account_label

    # Time columns
    if "TimeOpen" in df.columns:
        df["TimeOpen"] = pd.to_datetime(
            df["TimeOpen"],
            format="%Y.%m.%d %H:%M:%S",
            errors="coerce"
        )
    if "TimeClose" in df.columns:
        df["TimeClose"] = pd.to_datetime(
            df["TimeClose"],
            format="%Y.%m.%d %H:%M:%S",
            errors="coerce"
        )

    # Primary time column (prefer close time)
    if "TimeClose" in df.columns:
        df["Time"] = df["TimeClose"]
    else:
        df["Time"] = df.get("TimeOpen")

    # Profit column
    if "Profit" in df.columns:
        df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0.0)
    else:
        df["Profit"] = 0.0

    # Symbol
    if "Symbol" in df.columns:
        df["Symbol"] = df["Symbol"].astype(str)
    else:
        df["Symbol"] = ""

    # Type (BUY/SELL/BALANCE)
    if "Type" in df.columns:
        df["Type"] = df["Type"].astype(str)
    else:
        df["Type"] = ""

    return df


@cached
def load_portfolio_data() -> pd.DataFrame:
    """
    Load and merge all MT5 terminals into a single portfolio DataFrame
    Results are cached to improve VPS performance

    Returns:
        Combined DataFrame with all trading history
    """
    logger.info("Loading portfolio data...")
    sources = get_enabled_sources()
    frames: List[pd.DataFrame] = []

    for src in sources:
        src_path_str = src.get("path")
        if not src_path_str:
            continue

        src_path = Path(src_path_str)
        if not src_path.exists():
            logger.warning(f"Source path does not exist: {src_path}")
            continue

        account_label = src.get("name", src_path.name)
        history_files = sorted(src_path.glob("*_History.csv"))

        logger.info(f"Found {len(history_files)} history files in {account_label}")

        for csv_path in history_files:
            try:
                # MT5 CSVs use semicolon separator
                df = pd.read_csv(csv_path, sep=";")
            except Exception as e:
                logger.error(f"Error reading {csv_path}: {e}")
                continue

            if df.empty:
                continue

            df_norm = _normalize_history_df(
                df,
                csv_path=csv_path,
                account_label=account_label
            )
            frames.append(df_norm)

    if not frames:
        logger.warning("No data loaded")
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)

    # Sort by time
    if "Time" in combined.columns:
        combined = combined.sort_values("Time")

    logger.info(f"Loaded {len(combined)} total records")
    return combined


@cached
def load_ea_data(ea_name: str) -> pd.DataFrame:
    """
    Load data for a specific EA
    Cached for performance
    """
    df = load_portfolio_data()
    if df.empty:
        return df

    return df[df["EA_Name"] == ea_name].copy()


@cached
def load_symbol_data(symbol: str) -> pd.DataFrame:
    """
    Load data for a specific trading symbol
    Cached for performance
    """
    df = load_portfolio_data()
    if df.empty:
        return df

    return df[df["Symbol"] == symbol].copy()


def get_available_eas() -> List[str]:
    """Get list of all available EAs"""
    df = load_portfolio_data()
    if df.empty or "EA_Name" not in df.columns:
        return []

    return sorted(df["EA_Name"].unique().tolist())


def get_available_symbols() -> List[str]:
    """Get list of all trading symbols"""
    df = load_portfolio_data()
    if df.empty or "Symbol" not in df.columns:
        return []

    # Filter out empty symbols
    symbols = df["Symbol"].unique()
    return sorted([s for s in symbols if s and s.strip()])


def get_available_accounts() -> List[str]:
    """Get list of all accounts"""
    df = load_portfolio_data()
    if df.empty or "Account" not in df.columns:
        return []

    return sorted(df["Account"].unique().tolist())
