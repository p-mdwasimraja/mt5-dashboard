"""Analysis tab components: filters, daily/weekly equity curves, full trade table."""

from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd

from web.helpers import load_transactions


def _get_tx():
    tx = load_transactions()
    if tx is None or tx.empty:
        return pd.DataFrame()
    return tx.copy()


def _filter_tx(tx: pd.DataFrame, start_date, end_date, ea_val, symbol_val):
    if tx.empty:
        return tx

    time_col = "TimeClose" if "TimeClose" in tx.columns else "TimeOpen"

    if time_col in tx.columns:
        if start_date is not None:
            tx = tx[tx[time_col] >= pd.to_datetime(start_date)]
        if end_date is not None:
            tx = tx[tx[time_col] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]

    if ea_val and ea_val != "all" and "EA_Name" in tx.columns:
        tx = tx[tx["EA_Name"] == ea_val]

    if symbol_val and symbol_val != "all" and "Symbol" in tx.columns:
        tx = tx[tx["Symbol"] == symbol_val]

    return tx


def _build_daily_equity(tx: pd.DataFrame):
    fig = go.Figure()
    if tx.empty:
        fig.update_layout(
            title="Daily Equity Curve",
            template="plotly_white",
            xaxis_title="Date",
            yaxis_title="Cumulative Profit",
        )
        return fig

    time_col = "TimeClose" if "TimeClose" in tx.columns else "TimeOpen"
    tx = tx.sort_values(time_col)
    tx["Date"] = tx[time_col].dt.date
    daily = tx.groupby("Date")["Profit"].sum().cumsum()

    fig.add_trace(
        go.Scatter(
            x=list(daily.index),
            y=list(daily.values),
            mode="lines+markers",
            name="Daily Equity",
        )
    )
    fig.update_layout(
        title="Daily Equity Curve",
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Cumulative Profit",
    )
    return fig


def _build_weekly_equity(tx: pd.DataFrame):
    fig = go.Figure()
    if tx.empty:
        fig.update_layout(
            title="Weekly Equity Curve",
            template="plotly_white",
            xaxis_title="Week",
            yaxis_title="Cumulative Profit",
        )
        return fig

    time_col = "TimeClose" if "TimeClose" in tx.columns else "TimeOpen"
    tx = tx.sort_values(time_col)
    tx["Week"] = tx[time_col].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = tx.groupby("Week")["Profit"].sum().cumsum()

    fig.add_trace(
        go.Scatter(
            x=list(weekly.index),
            y=list(weekly.values),
            mode="lines+markers",
            name="Weekly Equity",
        )
    )
    fig.update_layout(
        title="Weekly Equity Curve",
        template="plotly_white",
        xaxis_title="Week Start",
        yaxis_title="Cumulative Profit",
    )
    return fig


def _build_trade_table(tx: pd.DataFrame):
    if tx.empty:
        return html.Div("No trades in selected range.", className="text-muted")

    cols = []
    preferred = ["Ticket", "TimeOpen", "TimeClose", "Symbol", "EA_Name", "Lots", "Profit", "Result"]
    for c in preferred:
        if c in tx.columns:
            cols.append(c)
    if not cols:
        cols = list(tx.columns)[:10]

    df = tx[cols].copy()
    if "TimeOpen" in df.columns:
        df["TimeOpen"] = df["TimeOpen"].dt.strftime("%Y-%m-%d %H:%M")
    if "TimeClose" in df.columns:
        df["TimeClose"] = df["TimeClose"].dt.strftime("%Y-%m-%d %H:%M")

    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        size="sm",
        responsive=True,
        class_name="mt-2 mb-0",
    )


def build_analysis_components(start_date, end_date, ea_val, symbol_val):
    tx = _get_tx()
    tx_f = _filter_tx(tx, start_date, end_date, ea_val, symbol_val)

    daily_fig = _build_daily_equity(tx_f)
    weekly_fig = _build_weekly_equity(tx_f)
    table_comp = _build_trade_table(tx_f)

    return daily_fig, weekly_fig, table_comp