"""
Portfolio analysis service
Optimized for performance with minimal computations
"""
import pandas as pd
from typing import Dict, Any


def compute_portfolio_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute portfolio-level summary statistics
    Optimized to avoid redundant calculations
    """
    if df.empty:
        return {
            "total_trades": 0,
            "total_profit": 0.0,
            "win_rate": 0.0,
            "total_eas": 0,
            "total_symbols": 0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "avg_profit": 0.0,
            "avg_loss": 0.0,
        }

    # Filter out BALANCE entries
    trades_df = df[df["Type"] != "BALANCE"].copy()

    if trades_df.empty:
        return {
            "total_trades": 0,
            "total_profit": 0.0,
            "win_rate": 0.0,
            "total_eas": len(df["EA_Name"].unique()) if "EA_Name" in df.columns else 0,
            "total_symbols": len(df["Symbol"].unique()) if "Symbol" in df.columns else 0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "avg_profit": 0.0,
            "avg_loss": 0.0,
        }

    # Compute metrics
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
        "total_trades": total_trades,
        "total_profit": round(total_profit, 2),
        "win_rate": round(win_rate, 2),
        "total_eas": len(df["EA_Name"].unique()) if "EA_Name" in df.columns else 0,
        "total_symbols": len(df["Symbol"].unique()) if "Symbol" in df.columns else 0,
        "profitable_trades": profitable_count,
        "losing_trades": losing_count,
        "avg_profit": round(avg_profit, 2),
        "avg_loss": round(avg_loss, 2),
    }


def build_equity_curve(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build cumulative profit equity curve
    Returns DataFrame with Time and CumulativeProfit columns
    """
    if df.empty or "Time" not in df.columns:
        return pd.DataFrame()

    # Filter trades only
    trades_df = df[df["Type"] != "BALANCE"].copy()

    if trades_df.empty:
        return pd.DataFrame()

    # Sort by time and compute cumulative profit
    trades_df = trades_df.sort_values("Time")
    trades_df["CumulativeProfit"] = trades_df["Profit"].cumsum()

    return trades_df[["Time", "CumulativeProfit"]].copy()


def get_ea_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get profit breakdown by EA
    Returns DataFrame with EA stats
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

    # Calculate win rate per EA
    def calc_win_rate(ea_name):
        ea_trades = trades_df[trades_df["EA_Name"] == ea_name]
        wins = len(ea_trades[ea_trades["Profit"] > 0])
        total = len(ea_trades)
        return round((wins / total * 100) if total > 0 else 0, 2)

    ea_stats["Win_Rate"] = ea_stats["EA_Name"].apply(calc_win_rate)

    # Sort by total profit
    ea_stats = ea_stats.sort_values("Total_Profit", ascending=False)

    return ea_stats


def get_symbol_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get profit breakdown by trading symbol
    Returns DataFrame with symbol stats
    """
    if df.empty or "Symbol" not in df.columns:
        return pd.DataFrame()

    # Filter trades only and remove empty symbols
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

    # Calculate win rate per symbol
    def calc_win_rate(symbol):
        symbol_trades = trades_df[trades_df["Symbol"] == symbol]
        wins = len(symbol_trades[symbol_trades["Profit"] > 0])
        total = len(symbol_trades)
        return round((wins / total * 100) if total > 0 else 0, 2)

    symbol_stats["Win_Rate"] = symbol_stats["Symbol"].apply(calc_win_rate)

    # Sort by total profit
    symbol_stats = symbol_stats.sort_values("Total_Profit", ascending=False)

    return symbol_stats


def get_recent_trades(df: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    """
    Get most recent trades
    """
    if df.empty or "Time" not in df.columns:
        return pd.DataFrame()

    # Filter trades only
    trades_df = df[df["Type"] != "BALANCE"].copy()

    if trades_df.empty:
        return pd.DataFrame()

    # Sort by time and get recent
    trades_df = trades_df.sort_values("Time", ascending=False)

    # Select relevant columns
    columns = ["Time", "EA_Name", "Symbol", "Type", "Profit"]
    available_columns = [col for col in columns if col in trades_df.columns]

    return trades_df[available_columns].head(limit)
