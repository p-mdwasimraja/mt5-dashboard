from __future__ import annotations

import pandas as pd


def compute_ea_performance(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or "EA_Name" not in df.columns:
        return pd.DataFrame(columns=["EA_Name", "Trades", "WinRate", "TotalProfit"])

    grouped = df.groupby("EA_Name")
    stats = grouped["Profit"].agg(["count", "sum"])
    stats = stats.rename(columns={"count": "Trades", "sum": "TotalProfit"})

    win_rate = grouped.apply(lambda x: (x["Profit"] > 0).sum() / len(x) * 100 if len(x) > 0 else 0.0)
    stats["WinRate"] = win_rate

    stats = stats.reset_index()
    stats = stats.sort_values("TotalProfit", ascending=False)
    return stats[["EA_Name", "Trades", "WinRate", "TotalProfit"]]
