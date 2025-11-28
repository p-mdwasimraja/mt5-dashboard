"""Date Range Performance Tab Components (EA summary table + charts)."""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

from web.helpers import load_transactions


def _get_tx():
    tx = load_transactions()
    if tx is None or tx.empty:
        return pd.DataFrame()
    return tx


def _get_start_equity():
    """Starting equity based on first Deposit (Type == 'Deposit', Profit column)."""
    tx_all = _get_tx()
    if tx_all.empty or "Type" not in tx_all.columns or "Profit" not in tx_all.columns:
        return 0.0
    deposits = tx_all[tx_all["Type"] == "Deposit"]
    if deposits.empty:
        return 0.0
    try:
        return float(deposits.iloc[0]["Profit"])
    except Exception:
        return 0.0


def _max_drawdown_from_series(equity: pd.Series):
    """Return (dd_value, dd_abs) from an equity curve series."""
    if equity.empty:
        return 0.0, 0.0
    peak = equity.iloc[0]
    max_dd = 0.0
    for v in equity:
        if v > peak:
            peak = v
        dd = v - peak
        if dd < max_dd:
            max_dd = dd
    return max_dd, abs(max_dd)


def _make_table(df):
    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        size="sm",
        responsive=True,
        class_name="mt-2 mb-0",
    )


def _compute_account_equity_and_daily_profit(tx_range: pd.DataFrame):
    """Compute synthetic account-level equity curve & daily profit for charts (not per EA)."""
    tx_all = _get_tx()
    if tx_all.empty or tx_range.empty:
        return pd.Series(dtype=float), pd.Series(dtype=float)

    start_equity = _get_start_equity()

    time_col = "TimeClose" if "TimeClose" in tx_range.columns else "TimeOpen"
    tx_r = tx_range.sort_values(time_col).copy()
    tx_r["Date"] = tx_r[time_col].dt.date
    daily_profit = tx_r.groupby("Date")["Profit"].sum().sort_index()

    start_date = daily_profit.index.min()
    tx_all = tx_all.copy()
    if time_col in tx_all.columns:
        tx_all["Date"] = tx_all[time_col].dt.date
    else:
        tx_all["Date"] = tx_all["TimeOpen"].dt.date

    before_mask = tx_all["Date"] < start_date
    before_profit = tx_all.loc[before_mask, "Profit"].sum() if "Profit" in tx_all.columns else 0.0
    equity_start = start_equity + float(before_profit)

    cum_profit = daily_profit.cumsum()
    equity_series = equity_start + cum_profit

    return equity_series, daily_profit


def _build_ea_summary_table(tx_range: pd.DataFrame, start_equity: float):
    """Return a striped table summarising EA performance inside the filtered range.

    Columns:
      EA Name | Profit/Loss | Win Rate | Max Drawdown | Recovery Factor | % Return
    """
    if tx_range.empty or "EA_Name" not in tx_range.columns:
        return html.Div("No EA data in selected range.", className="text-muted")

    time_col = "TimeClose" if "TimeClose" in tx_range.columns else "TimeOpen"

    rows = []
    for ea, sub in tx_range.groupby("EA_Name"):
        if sub.empty:
            continue

        sub = sub.sort_values(time_col)
        profits = sub["Profit"].astype(float)

        total_profit = float(profits.sum())
        wins = int((profits > 0).sum())
        losses = int((profits < 0).sum())
        win_rate = (wins / (wins + losses) * 100.0) if (wins + losses) > 0 else 0.0

        # EA-specific equity curve (starting at 0 for that EA)
        cum_profit = profits.cumsum()
        dd_val, dd_abs = _max_drawdown_from_series(cum_profit)

        if dd_abs > 0 and total_profit > 0:
            recovery = total_profit / dd_abs
        else:
            recovery = 0.0

        if start_equity > 0:
            pct_return = total_profit / start_equity * 100.0
        else:
            pct_return = 0.0

        rows.append(
            {
                "EA Name": ea,
                "Profit / Loss": total_profit,
                "Win Rate (%)": win_rate,
                "Max Drawdown": dd_val,  # keep signed value
                "Recovery Factor": recovery,
                "% Return": pct_return,
            }
        )

    if not rows:
        return html.Div("No EA data in selected range.", className="text-muted")

    df = pd.DataFrame(rows)

    # Sort by Profit descending
    df = df.sort_values("Profit / Loss", ascending=False)

    # Format for display
    disp = df.copy()
    disp["Profit / Loss"] = disp["Profit / Loss"].map(lambda v: f"${v:,.0f}")
    disp["Win Rate (%)"] = disp["Win Rate (%)"].map(lambda v: f"{v:,.1f}%")
    disp["Max Drawdown"] = disp["Max Drawdown"].map(lambda v: f"${v:,.0f}")
    disp["Recovery Factor"] = disp["Recovery Factor"].map(lambda v: f"{v:,.2f}" if v != 0 else "-")
    disp["% Return"] = disp["% Return"].map(lambda v: f"{v:,.2f}%" if v != 0 else "0.00%")

    header = html.H5("EA Performance Summary (Date Range)", className="mt-2 mb-2")

    return html.Div(
        [
            header,
            _make_table(disp),
        ]
    )


def build_date_range_layout_components(start_date, end_date, ea_filter, symbol_filter):
    """Build components for the Date Range Performance tab.

    Returns:
      ea_summary_table, equity_fig, ppd_fig, pea_fig, psym_fig, trades_table
    """
    tx = _get_tx()
    if tx.empty:
        msg = html.Div("No data available for selected range.", className="text-muted")
        empty_fig = go.Figure()
        return msg, empty_fig, empty_fig, empty_fig, empty_fig, html.Div("")

    # Parse dates
    if start_date:
        start_dt = datetime.fromisoformat(start_date).date()
    else:
        start_dt = tx["TimeOpen"].dt.date.min()
    if end_date:
        end_dt = datetime.fromisoformat(end_date).date()
    else:
        end_dt = tx["TimeOpen"].dt.date.max()

    # Base filter by date range
    tx["Date"] = tx["TimeOpen"].dt.date
    mask = (tx["Date"] >= start_dt) & (tx["Date"] <= end_dt)

    # EA filter
    if ea_filter and ea_filter != "all" and "EA_Name" in tx.columns:
        mask &= tx["EA_Name"] == ea_filter

    # Symbol filter
    if symbol_filter and symbol_filter != "all" and "Symbol" in tx.columns:
        mask &= tx["Symbol"] == symbol_filter

    tx_range = tx.loc[mask].copy()
    if tx_range.empty:
        msg = html.Div("No trades in selected range.", className="text-muted")
        empty_fig = go.Figure()
        return msg, empty_fig, empty_fig, empty_fig, empty_fig, html.Div("")

    # --- EA summary table (per EA) ---
    start_equity = _get_start_equity()
    ea_summary = _build_ea_summary_table(tx_range, start_equity)

    # --- Account-level equity & daily profit for charts ---
    equity_series, daily_profit = _compute_account_equity_and_daily_profit(tx_range)

    equity_fig = go.Figure()
    if not equity_series.empty:
        equity_fig.add_trace(
            go.Scatter(
                x=list(equity_series.index),
                y=list(equity_series.values),
                mode="lines+markers",
                name="Equity",
            )
        )
    equity_fig.update_layout(
        title="Synthetic Equity Curve (Closed P/L based)",
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Equity",
    )

    ppd_fig = go.Figure()
    if not daily_profit.empty:
        ppd_fig.add_trace(
            go.Bar(
                x=list(daily_profit.index),
                y=list(daily_profit.values),
                name="Daily Profit",
            )
        )
    ppd_fig.update_layout(
        title="Profit per Day",
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Profit",
    )

    pea_fig = go.Figure()
    if "EA_Name" in tx_range.columns:
        pea = tx_range.groupby("EA_Name")["Profit"].sum().sort_values(ascending=False)
        pea_fig.add_trace(
            go.Bar(
                x=list(pea.index),
                y=list(pea.values),
                name="Profit by EA",
            )
        )
    pea_fig.update_layout(
        title="Profit by EA (in range)",
        template="plotly_white",
        xaxis_title="EA",
        yaxis_title="Profit",
    )

    psym_fig = go.Figure()
    if "Symbol" in tx_range.columns:
        psym = tx_range.groupby("Symbol")["Profit"].sum().sort_values(ascending=False)
        psym_fig.add_trace(
            go.Bar(
                x=list(psym.index),
                y=list(psym.values),
                name="Profit by Symbol",
            )
        )
    psym_fig.update_layout(
        title="Profit by Symbol (in range)",
        template="plotly_white",
        xaxis_title="Symbol",
        yaxis_title="Profit",
    )

    # Trades table (filtered trades)
    cols = []
    for c in ["TimeOpen", "Symbol", "EA_Name", "Profit", "Lots", "Result"]:
        if c in tx_range.columns:
            cols.append(c)
    if not cols:
        cols = list(tx_range.columns)[:8]

    table_df = tx_range[cols].copy()
    if "TimeOpen" in table_df.columns:
        table_df["TimeOpen"] = table_df["TimeOpen"].dt.strftime("%Y-%m-%d %H:%M")

    trades_table = _make_table(table_df)

    return ea_summary, equity_fig, ppd_fig, pea_fig, psym_fig, trades_table