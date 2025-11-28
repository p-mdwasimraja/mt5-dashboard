from __future__ import annotations

from typing import Dict, Any

import pandas as pd


def compute_portfolio_summary(df: pd.DataFrame) -> Dict[str, Any]:
    if df is None or df.empty:
        return {
            "total_profit": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "best_ea": None,
            "worst_ea": None,
            "best_symbol": None,
            "worst_symbol": None,
        }

    trade_df = df.copy()

    if "Type" in trade_df.columns and trade_df["Type"].dtype == "object":
        trade_df = trade_df[trade_df["Type"].str.lower() != "deposit"]

    total_profit = float(trade_df["Profit"].sum())
    total_trades = int(len(trade_df))

    wins = (trade_df["Profit"] > 0).sum()
    win_rate = float(wins / total_trades * 100) if total_trades > 0 else 0.0

    best_ea = None
    worst_ea = None
    best_symbol = None
    worst_symbol = None

    if "EA_Name" in trade_df.columns:
        ea_group = trade_df.groupby("EA_Name")["Profit"].sum()
        if not ea_group.empty:
            best_ea = ea_group.idxmax()
            worst_ea = ea_group.idxmin()

    if "Symbol" in trade_df.columns:
        sym_group = trade_df.groupby("Symbol")["Profit"].sum()
        if not sym_group.empty:
            best_symbol = sym_group.idxmax()
            worst_symbol = sym_group.idxmin()

    return {
        "total_profit": total_profit,
        "total_trades": total_trades,
        "win_rate": win_rate,
        "best_ea": best_ea,
        "worst_ea": worst_ea,
        "best_symbol": best_symbol,
        "worst_symbol": worst_symbol,
    }


def build_equity_curve(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["Time", "CumulativeProfit"])

    df_sorted = df.sort_values("__Time")
    df_sorted["CumulativeProfit"] = df_sorted["Profit"].cumsum()
    return df_sorted[["__Time", "CumulativeProfit"]].rename(columns={"__Time": "Time"})

def _filter_trade_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter out non-trade rows (deposits/balance/credit) for trade analytics.
    """
    if df is None or df.empty:
        return df

    if "Type" not in df.columns:
        return df

    type_lower = df["Type"].astype(str).str.lower()
    # This will catch 'BALANCE', 'Balance', etc.
    mask = ~type_lower.isin(["balance", "deposit", "credit"])
    return df[mask].copy()
