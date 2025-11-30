"""
Symbol analysis service
"""
import pandas as pd
from typing import Dict, Any


def compute_symbol_stats(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """
    Compute statistics for a specific trading symbol
    """
    if df.empty:
        return {
            "symbol": symbol,
            "total_trades": 0,
            "total_profit": 0.0,
            "win_rate": 0.0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "avg_profit": 0.0,
            "avg_loss": 0.0,
        }

    # Filter trades only
    trades_df = df[df["Type"] != "BALANCE"].copy()

    if trades_df.empty:
        return {
            "symbol": symbol,
            "total_trades": 0,
            "total_profit": 0.0,
            "win_rate": 0.0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "avg_profit": 0.0,
            "avg_loss": 0.0,
        }

    # Calculate metrics
    total_profit = trades_df["Profit"].sum()
    profitable = trades_df[trades_df["Profit"] > 0]
    losses = trades_df[trades_df["Profit"] < 0]

    profitable_count = len(profitable)
    losing_count = len(losses)
    total_trades = len(trades_df)

    win_rate = (profitable_count / total_trades * 100) if total_trades > 0 else 0.0
    avg_profit = profitable["Profit"].mean() if profitable_count > 0 else 0.0
    avg_loss = losses["Profit"].mean() if losing_count > 0 else 0.0

    return {
        "symbol": symbol,
        "total_trades": total_trades,
        "total_profit": round(total_profit, 2),
        "win_rate": round(win_rate, 2),
        "profitable_trades": profitable_count,
        "losing_trades": losing_count,
        "avg_profit": round(avg_profit, 2),
        "avg_loss": round(avg_loss, 2),
    }


def get_symbol_ea_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get performance breakdown by EA for this symbol
    """
    if df.empty or "EA_Name" not in df.columns:
        return pd.DataFrame()

    # Filter trades only
    trades_df = df[df["Type"] != "BALANCE"].copy()

    if trades_df.empty:
        return pd.DataFrame()

    # Group by EA
    ea_stats = trades_df.groupby("EA_Name").agg({
        "Profit": ["sum", "count", "mean"],
    }).round(2)

    ea_stats.columns = ["Total_Profit", "Trades", "Avg_Profit"]
    ea_stats = ea_stats.reset_index()

    # Sort by profit
    ea_stats = ea_stats.sort_values("Total_Profit", ascending=False)

    return ea_stats
