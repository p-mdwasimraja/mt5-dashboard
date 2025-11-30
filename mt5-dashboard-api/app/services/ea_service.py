"""
EA (Expert Advisor) analysis service
"""
import pandas as pd
from typing import Dict, Any, List


def calculate_consecutive_losses(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate consecutive loss streaks
    Returns max consecutive losses and current streak
    """
    if df.empty or "Time" not in df.columns:
        return {
            "max_consecutive_losses": 0,
            "current_streak": 0,
            "max_streak_loss_amount": 0.0
        }

    # Filter trades only and sort by time
    trades_df = df[df["Type"] != "BALANCE"].copy()
    if trades_df.empty:
        return {
            "max_consecutive_losses": 0,
            "current_streak": 0,
            "max_streak_loss_amount": 0.0
        }

    trades_df = trades_df.sort_values("Time")

    max_consecutive = 0
    current_consecutive = 0
    max_streak_amount = 0.0
    current_streak_amount = 0.0

    for profit in trades_df["Profit"]:
        if profit < 0:
            current_consecutive += 1
            current_streak_amount += profit
            if current_consecutive > max_consecutive:
                max_consecutive = current_consecutive
                max_streak_amount = current_streak_amount
        else:
            current_consecutive = 0
            current_streak_amount = 0.0

    # Check if currently in a losing streak
    last_trades = trades_df.tail(10)
    current_streak = 0
    for profit in reversed(last_trades["Profit"].tolist()):
        if profit < 0:
            current_streak += 1
        else:
            break

    return {
        "max_consecutive_losses": max_consecutive,
        "current_streak": current_streak,
        "max_streak_loss_amount": round(max_streak_amount, 2)
    }


def compute_ea_stats(df: pd.DataFrame, ea_name: str) -> Dict[str, Any]:
    """
    Compute statistics for a specific EA
    """
    if df.empty:
        return {
            "ea_name": ea_name,
            "total_trades": 0,
            "total_profit": 0.0,
            "win_rate": 0.0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "avg_profit": 0.0,
            "avg_loss": 0.0,
            "max_profit": 0.0,
            "max_loss": 0.0,
        }

    # Filter trades only (exclude BALANCE)
    trades_df = df[df["Type"] != "BALANCE"].copy()

    if trades_df.empty:
        return {
            "ea_name": ea_name,
            "total_trades": 0,
            "total_profit": 0.0,
            "win_rate": 0.0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "avg_profit": 0.0,
            "avg_loss": 0.0,
            "max_profit": 0.0,
            "max_loss": 0.0,
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
    max_profit = trades_df["Profit"].max() if total_trades > 0 else 0.0
    max_loss = trades_df["Profit"].min() if total_trades > 0 else 0.0

    # Calculate consecutive losses
    consecutive_stats = calculate_consecutive_losses(df)

    return {
        "ea_name": ea_name,
        "total_trades": total_trades,
        "total_profit": round(total_profit, 2),
        "win_rate": round(win_rate, 2),
        "profitable_trades": profitable_count,
        "losing_trades": losing_count,
        "avg_profit": round(avg_profit, 2),
        "avg_loss": round(avg_loss, 2),
        "max_profit": round(max_profit, 2),
        "max_loss": round(max_loss, 2),
        "max_consecutive_losses": consecutive_stats["max_consecutive_losses"],
        "current_loss_streak": consecutive_stats["current_streak"],
        "max_streak_loss_amount": consecutive_stats["max_streak_loss_amount"],
    }


def get_ea_equity_curve(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build equity curve for specific EA
    """
    if df.empty or "Time" not in df.columns:
        return pd.DataFrame()

    # Filter trades only
    trades_df = df[df["Type"] != "BALANCE"].copy()

    if trades_df.empty:
        return pd.DataFrame()

    # Sort and calculate cumulative profit
    trades_df = trades_df.sort_values("Time")
    trades_df["CumulativeProfit"] = trades_df["Profit"].cumsum()

    return trades_df[["Time", "CumulativeProfit"]].copy()


def get_all_eas_summary(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Get summary stats for all EAs
    """
    if df.empty or "EA_Name" not in df.columns:
        return []

    ea_names = df["EA_Name"].unique()
    summaries = []

    for ea_name in ea_names:
        ea_df = df[df["EA_Name"] == ea_name]
        stats = compute_ea_stats(ea_df, ea_name)
        summaries.append(stats)

    # Sort by total profit descending
    summaries.sort(key=lambda x: x["total_profit"], reverse=True)

    return summaries


def get_ea_symbol_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get performance breakdown by symbol for this EA
    """
    if df.empty or "Symbol" not in df.columns:
        return pd.DataFrame()

    # Filter trades only
    trades_df = df[
        (df["Type"] != "BALANCE") &
        (df["Symbol"].notna()) &
        (df["Symbol"] != "")
    ].copy()

    if trades_df.empty:
        return pd.DataFrame()

    # Group by symbol
    symbol_stats = trades_df.groupby("Symbol").agg({
        "Profit": ["sum", "count", "mean"],
    }).round(2)

    symbol_stats.columns = ["Total_Profit", "Trades", "Avg_Profit"]
    symbol_stats = symbol_stats.reset_index()

    # Sort by profit
    symbol_stats = symbol_stats.sort_values("Total_Profit", ascending=False)

    return symbol_stats
