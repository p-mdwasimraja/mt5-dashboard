from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from .config import get_settings


def _normalize_df(df: pd.DataFrame, account_name: str) -> pd.DataFrame:
    df = df.copy()
    df["Account"] = account_name

    for col in ("TimeClose", "Close time", "TimeOpen", "Open time"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "Profit" in df.columns:
        df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0.0)
    elif "Net profit" in df.columns:
        df["Profit"] = pd.to_numeric(df["Net profit"], errors="coerce").fillna(0.0)
    else:
        df["Profit"] = 0.0

    if "Symbol" in df.columns:
        df["Symbol"] = df["Symbol"].astype(str)
    elif "Trading Pair" in df.columns:
        df["Symbol"] = df["Trading Pair"].astype(str)
    else:
        df["Symbol"] = ""

    if "EA_Name" in df.columns:
        df["EA_Name"] = df["EA_Name"].astype(str)
    elif "EA" in df.columns:
        df["EA_Name"] = df["EA"].astype(str)
    elif "Order comment" in df.columns:
        df["EA_Name"] = df["Order comment"].astype(str)
    else:
        df["EA_Name"] = ""

    if "TimeClose" in df.columns:
        df["__Time"] = df["TimeClose"]
    elif "Close time" in df.columns:
        df["__Time"] = df["Close time"]
    elif "TimeOpen" in df.columns:
        df["__Time"] = df["TimeOpen"]
    elif "Open time" in df.columns:
        df["__Time"] = df["Open time"]
    else:
        df["__Time"] = pd.NaT

    return df


def load_portfolio_data() -> pd.DataFrame:
    settings = get_settings()
    frames: List[pd.DataFrame] = []

    for src in settings.enabled_sources():
        src_name = src.get("name", "Unknown")
        src_path_str = src.get("path")
        if not src_path_str:
            continue

        src_path = Path(src_path_str)
        if not src_path.exists():
            continue

        csv_files = sorted(src_path.glob("*.csv"))
        for csv_path in csv_files:
            try:
                df = pd.read_csv(csv_path)
            except Exception:
                continue

            if df.empty:
                continue

            df_norm = _normalize_df(df, src_name)
            frames.append(df_norm)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    return combined
