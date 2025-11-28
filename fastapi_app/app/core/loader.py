from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from .config import get_settings


def _parse_ea_from_filename(csv_path: Path) -> str:
    """
    Fallback EA name from filename if EA_Name column is missing.
    e.g.  'Ultimate-Timebomb_History.csv' -> 'Ultimate-Timebomb'
    """
    stem = csv_path.stem  # 'Ultimate-Timebomb_History'
    if "_" in stem:
        return stem.split("_", 1)[0]
    return stem


def _normalize_history_df(
    df: pd.DataFrame,
    csv_path: Path,
    account_label: str,
) -> pd.DataFrame:
    """
    Normalize a single *_History.csv DataFrame into a common format.
    Your current format:

    EA_Name;TimeOpen;TimeClose;DealOpen;DealClose;Symbol;Type;Volume;
            PriceOpen;PriceClose;Profit;Swap;Commission;Duration;Comment
    """
    df = df.copy()

    # --- EA name ---
    if "EA_Name" in df.columns:
        df["EA_Name"] = df["EA_Name"].astype(str)
    else:
        df["EA_Name"] = _parse_ea_from_filename(csv_path)

    # Tag terminal / source account (the mt5_sources.name)
    df["Account"] = account_label

    # --- Time columns ---
    # Convert your TimeOpen / TimeClose into datetimes
    if "TimeOpen" in df.columns:
        df["TimeOpen"] = pd.to_datetime(df["TimeOpen"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    if "TimeClose" in df.columns:
        df["TimeClose"] = pd.to_datetime(df["TimeClose"], format="%Y.%m.%d %H:%M:%S", errors="coerce")

    # We use close time if present, else open time
    if "TimeClose" in df.columns:
        df["__Time"] = df["TimeClose"]
    else:
        df["__Time"] = df.get("TimeOpen")

    # --- Profit column ---
    if "Profit" in df.columns:
        df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0.0)
    else:
        df["Profit"] = 0.0

    # --- Symbol ---
    if "Symbol" in df.columns:
        df["Symbol"] = df["Symbol"].astype(str)
    else:
        df["Symbol"] = ""

    # --- Type (BUY/SELL/BALANCE/etc.) ---
    if "Type" in df.columns:
        df["Type"] = df["Type"].astype(str)
    else:
        df["Type"] = ""

    return df


def load_portfolio_data() -> pd.DataFrame:
    """
    Load and MERGE ALL MT5 terminals into a single portfolio DataFrame.

    Rules:
      - Only use *_History.csv files
      - CSVs are semicolon-separated ';'
      - EA name read from EA_Name column (preferred) or filename
    """
    settings = get_settings()
    frames: List[pd.DataFrame] = []

    for src in settings.enabled_sources():
        src_path_str = src.get("path")
        if not src_path_str:
            continue

        src_path = Path(src_path_str)
        if not src_path.exists():
            continue

        account_label = src.get("name") or src_path.name

        history_files = sorted(src_path.glob("*_History.csv"))

        for csv_path in history_files:
            try:
                # Your files use ';' as separator
                df = pd.read_csv(csv_path, sep=";")
            except Exception:
                continue

            if df.empty:
                continue

            df_norm = _normalize_history_df(df, csv_path=csv_path, account_label=account_label)
            frames.append(df_norm)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)

    # Sort by time if available
    if "__Time" in combined.columns:
        combined = combined.sort_values("__Time")

    return combined
