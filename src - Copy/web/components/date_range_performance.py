"""Date Range Performance Tab Components"""

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


def _compute_synthetic_equity(tx: pd.DataFrame):
    """Return daily equity series and daily profit for the filtered date range.

    Equity is computed as:
      starting_equity = first deposit (Type == 'Deposit', Profit column)
      equity(t) = starting_equity + cumulative closed profit up to t
    """
    tx_all = _get_tx()
    if tx_all.empty:
        return pd.Series(dtype=float), pd.Series(dtype=float)

    deposits = tx_all[tx_all.get("Type", "") == "Deposit"]
    if not deposits.empty:
        start_equity = float(deposits.iloc[0]["Profit"])
    else:
        start_equity = 0.0

    if tx.empty:
        return pd.Series(dtype=float), pd.Series(dtype=float)

    time_col = "TimeClose" if "TimeClose" in tx.columns else "TimeOpen"
    tx = tx.sort_values(time_col)

    tx["Date"] = tx[time_col].dt.date
    daily_profit = tx.groupby("Date")["Profit"].sum().sort_index()

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


def _max_drawdown(equity: pd.Series):
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


def _kpi_card(title, value, subtitle, color_class, icon_class):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(className=f"{icon_class} me-2"),
                        html.Span(title, className="fw-semibold"),
                    ],
                    className="small mb-1",
                ),
                html.H4(value, className="mb-0"),
                html.Div(subtitle, className="text-white-50 small mt-1"),
            ]
        ),
        class_name=f"mb-2 insight-card {color_class}",
    )


def _make_table(df):
    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        size="sm",
        responsive=True,
        class_name="mt-2 mb-0 insight-table",
    )


def build_date_range_layout_components(start_date, end_date, ea_filter, symbol_filter):
    tx = _get_tx()
    if tx.empty:
        return (
            html.Div("No data available for selected range.", className="text-muted"),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            html.Div(""),
        )

    if start_date:
        start_dt = datetime.fromisoformat(start_date).date()
    else:
        start_dt = tx["TimeOpen"].dt.date.min()
    if end_date:
        end_dt = datetime.fromisoformat(end_date).date()
    else:
        end_dt = tx["TimeOpen"].dt.date.max()

    tx["Date"] = tx["TimeOpen"].dt.date
    mask = (tx["Date"] >= start_dt) & (tx["Date"] <= end_dt)

    if ea_filter and ea_filter != "all" and "EA_Name" in tx.columns:
        mask &= tx["EA_Name"] == ea_filter

    if symbol_filter and symbol_filter != "all" and "Symbol" in tx.columns:
        mask &= tx["Symbol"] == symbol_filter

    tx_range = tx.loc[mask].copy()
    if tx_range.empty:
        return (
            html.Div("No trades in selected range.", className="text-muted"),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            html.Div(""),
        )

    profits = tx_range["Profit"]
    total_profit = float(profits.sum())
    total_loss = float(profits[profits < 0].sum())
    total_trades = int(len(profits))
    wins = int((profits > 0).sum())
    win_rate = (wins / total_trades * 100.0) if total_trades > 0 else 0.0

    best_ea = worst_ea = "-"
    best_sym = worst_sym = "-"
    if "EA_Name" in tx_range.columns:
        ea_group = tx_range.groupby("EA_Name")["Profit"].sum()
        if not ea_group.empty:
            best_ea = ea_group.idxmax()
            worst_ea = ea_group.idxmin()
    if "Symbol" in tx_range.columns:
        sym_group = tx_range.groupby("Symbol")["Profit"].sum()
        if not sym_group.empty:
            best_sym = sym_group.idxmax()
            worst_sym = sym_group.idxmin()

    daily_profit = tx_range.groupby("Date")["Profit"].sum().sort_index()
    profit_per_day = daily_profit.mean() if not daily_profit.empty else 0.0

    equity_series, _ = _compute_synthetic_equity(tx_range)
    max_dd, max_dd_abs = _max_drawdown(equity_series)
    recovery = (total_profit / max_dd_abs) if max_dd_abs > 0 else 0.0

    kpi_cards = html.Div(
        [
            _kpi_card(
                "Total Profit",
                f"${total_profit:,.0f}",
                f"From {start_dt} to {end_dt}",
                "insight-card-green",
                "fas fa-dollar-sign",
            ),
            _kpi_card(
                "Total Loss",
                f"${total_loss:,.0f}",
                "Closed losses only",
                "insight-card-red",
                "fas fa-arrow-down",
            ),
            _kpi_card(
                "Win Rate",
                f"{win_rate:,.1f}%",
                f"{wins}/{total_trades} trades",
                "insight-card-blue",
                "fas fa-bullseye",
            ),
            _kpi_card(
                "Profit / Day",
                f"${profit_per_day:,.0f}",
                "Average in range",
                "insight-card-yellow",
                "fas fa-calendar-day",
            ),
            _kpi_card(
                "Max Drawdown",
                f"${max_dd_abs:,.0f}",
                "Equity-based",
                "insight-card-purple",
                "fas fa-chart-line",
            ),
            _kpi_card(
                "Recovery Factor",
                f"{recovery:,.2f}",
                "Total profit / Max DD",
                "insight-card-dark",
                "fas fa-sync",
            ),
            _kpi_card(
                "Best EA",
                best_ea,
                "Highest net profit",
                "insight-card-green",
                "fas fa-trophy",
            ),
            _kpi_card(
                "Worst EA",
                worst_ea,
                "Lowest net profit",
                "insight-card-red",
                "fas fa-exclamation-circle",
            ),
            _kpi_card(
                "Best Symbol",
                best_sym,
                "Highest net profit",
                "insight-card-green",
                "fas fa-chart-bar",
            ),
            _kpi_card(
                "Worst Symbol",
                worst_sym,
                "Lowest net profit",
                "insight-card-red",
                "fas fa-chart-bar",
            ),
        ]
    )

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
        title="Profit by EA",
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
        title="Profit by Symbol",
        template="plotly_white",
        xaxis_title="Symbol",
        yaxis_title="Profit",
    )

    cols = []
    for c in ["TimeOpen", "Symbol", "EA_Name", "Profit", "Lots", "Result"]:
        if c in tx_range.columns:
            cols.append(c)
    if not cols:
        cols = list(tx_range.columns)[:8]

    table_df = tx_range[cols].copy()
    if "TimeOpen" in table_df.columns:
        table_df["TimeOpen"] = table_df["TimeOpen"].dt.strftime("%Y-%m-%d %H:%M")

    table_component = _make_table(table_df)

    return kpi_cards, equity_fig, ppd_fig, pea_fig, psym_fig, table_component