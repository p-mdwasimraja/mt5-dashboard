"""Trading Pair Performance tab components.

Provides:
- Symbol performance summary table
- Equity-style cumulative profit for selected symbol or all
- Win/Loss distribution
- Monthly profit per symbol
- Trades table
"""

from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd

from web.helpers import load_transactions


def _get_tx():
    tx = load_transactions()
    if tx is None or tx.empty:
        return pd.DataFrame()
    return tx


def _max_drawdown_from_series(equity: pd.Series):
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


def _build_symbol_summary(tx: pd.DataFrame):
    if tx.empty or "Symbol" not in tx.columns:
        return html.Div("No symbol data available.", className="text-muted")

    rows = []
    for sym, sub in tx.groupby("Symbol"):
        profits = sub["Profit"].astype(float)
        total_profit = float(profits.sum())
        wins = int((profits > 0).sum())
        losses = int((profits < 0).sum())
        win_rate = (wins / (wins + losses) * 100.0) if (wins + losses) > 0 else 0.0

        cum_profit = profits.cumsum()
        dd_val, dd_abs = _max_drawdown_from_series(cum_profit)
        recovery = (total_profit / dd_abs) if dd_abs > 0 and total_profit > 0 else 0.0

        rows.append(
            {
                "Symbol": sym,
                "Profit / Loss": total_profit,
                "Win Rate (%)": win_rate,
                "Max Drawdown": dd_val,
                "Recovery Factor": recovery,
            }
        )

    df = pd.DataFrame(rows)
    df = df.sort_values("Profit / Loss", ascending=False)

    disp = df.copy()
    disp["Profit / Loss"] = disp["Profit / Loss"].map(lambda v: f"${v:,.0f}")
    disp["Win Rate (%)"] = disp["Win Rate (%)"].map(lambda v: f"{v:,.1f}%")
    disp["Max Drawdown"] = disp["Max Drawdown"].map(lambda v: f"${v:,.0f}")
    disp["Recovery Factor"] = disp["Recovery Factor"].map(lambda v: f"{v:,.2f}" if v != 0 else "-")

    header = html.H5("Trading Pair Performance Summary (Overall)", className="mt-2 mb-2")
    return html.Div([header, _make_table(disp)])


def build_pair_performance_components(symbol_filter: str):
    tx = _get_tx()
    if tx.empty:
        empty_fig = go.Figure()
        msg = html.Div("No data available.", className="text-muted")
        return msg, empty_fig, empty_fig, empty_fig, msg

    tx = tx.copy()
    time_col = "TimeClose" if "TimeClose" in tx.columns else "TimeOpen"

    # Summary table (all symbols)
    summary_table = _build_symbol_summary(tx)

    # Filter for selected symbol
    tx_sel = tx
    if symbol_filter and symbol_filter != "all" and "Symbol" in tx.columns:
        tx_sel = tx[tx["Symbol"] == symbol_filter].copy()

    # Equity-style cumulative profit curve (for selected symbol or all)
    equity_fig = go.Figure()
    if not tx_sel.empty:
        tx_sel = tx_sel.sort_values(time_col)
        profits = tx_sel["Profit"].astype(float)
        cum_profit = profits.cumsum()
        x_vals = tx_sel[time_col]
        equity_fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=cum_profit,
                mode="lines+markers",
                name="Cumulative Profit",
            )
        )
    equity_fig.update_layout(
        title="Cumulative Profit (Selected Symbol / All)",
        template="plotly_white",
        xaxis_title="Time",
        yaxis_title="Cumulative Profit",
    )

    # Win/Loss distribution
    winloss_fig = go.Figure()
    if not tx_sel.empty:
        profits = tx_sel["Profit"].astype(float)
        win_count = int((profits > 0).sum())
        loss_count = int((profits < 0).sum())
        breakeven_count = int((profits == 0).sum())
        labels = ["Win", "Loss", "Breakeven"]
        values = [win_count, loss_count, breakeven_count]
        winloss_fig.add_trace(
            go.Pie(labels=labels, values=values, hole=0.4)
        )
    winloss_fig.update_layout(
        title="Win / Loss Distribution",
        template="plotly_white",
    )

    # Monthly profit bar chart
    monthly_fig = go.Figure()
    if not tx_sel.empty and "TimeOpen" in tx_sel.columns:
        tx_sel["Month"] = tx_sel["TimeOpen"].dt.to_period("M").astype(str)
        monthly = tx_sel.groupby("Month")["Profit"].sum().sort_index()
        monthly_fig.add_trace(
            go.Bar(
                x=list(monthly.index),
                y=list(monthly.values),
                name="Monthly Profit",
            )
        )
    monthly_fig.update_layout(
        title="Monthly Profit (Selected Symbol / All)",
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Profit",
        xaxis={"tickangle": -45},
    )

    # Trades table
    if tx_sel.empty:
        trades_table = html.Div("No trades for selected symbol.", className="text-muted")
    else:
        cols = []
        for c in ["TimeOpen", "Symbol", "EA_Name", "Profit", "Lots", "Result"]:
            if c in tx_sel.columns:
                cols.append(c)
        if not cols:
            cols = list(tx_sel.columns)[:8]
        table_df = tx_sel[cols].copy()
        if "TimeOpen" in table_df.columns:
            table_df["TimeOpen"] = table_df["TimeOpen"].dt.strftime("%Y-%m-%d %H:%M")
        trades_table = _make_table(table_df)

    return summary_table, equity_fig, winloss_fig, monthly_fig, trades_table