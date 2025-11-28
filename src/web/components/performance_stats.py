"""Performance Stats Components (Enhanced, Power-BI style)"""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta

from web.helpers import load_transactions


def _get_tx():
    tx = load_transactions()
    if tx is None or tx.empty:
        return pd.DataFrame()
    return tx


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


def _kpi_card(title, value, subtitle, icon_class, color_class):
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


def create_yearly_stats(transactions=None):
    if transactions is None:
        tx = _get_tx()
    else:
        tx = transactions.copy()

    current_year = datetime.now().year
    years = [current_year - 2, current_year - 1, current_year]

    if tx.empty:
        return dbc.Row(
            dbc.Col(html.Div("No yearly data available", className="text-muted"), width=12)
        )

    tx["Year"] = tx["TimeOpen"].dt.year
    eas = sorted(tx["EA_Name"].dropna().unique())

    result = pd.DataFrame(index=years, columns=eas).fillna(0.0)
    grouped = tx.groupby(["Year", "EA_Name"])["Profit"].sum()

    for (yr, ea), profit in grouped.items():
        if yr in years:
            result.loc[yr, ea] = float(profit)

    ea_totals = result.sum(axis=0)
    total_profit = float(ea_totals.sum()) if not ea_totals.empty else 0.0
    best_ea = ea_totals.idxmax() if not ea_totals.empty else "-"
    best_ea_val = float(ea_totals.max()) if not ea_totals.empty else 0.0
    worst_ea = ea_totals.idxmin() if not ea_totals.empty else "-"
    worst_ea_val = float(ea_totals.min()) if not ea_totals.empty else 0.0

    this_year_val = float(result.loc[current_year].sum()) if current_year in result.index else 0.0
    prev_year_val = float(result.loc[current_year - 1].sum()) if (current_year - 1) in result.index else 0.0
    if prev_year_val != 0:
        yoy = (this_year_val - prev_year_val) / abs(prev_year_val) * 100.0
    else:
        yoy = 0.0

    max_profit_val = 0.0
    max_loss_val = 0.0
    if "Profit" in tx.columns and not tx["Profit"].empty:
        max_profit_val = float(tx["Profit"].max())
        max_loss_val = float(tx["Profit"].min())

    fig = go.Figure()
    for ea in eas:
        fig.add_trace(
            go.Bar(
                x=[str(y) for y in years],
                y=result[ea].values,
                name=ea,
            )
        )

    fig.update_layout(
        title="Yearly Profit by EA (Stacked)",
        barmode="stack",
        template="plotly_white",
        xaxis_title="Year",
        yaxis_title="Profit ($)",
        height=420,
        legend_title="EA",
    )

    table_df = result.copy().T
    table_df["Total"] = table_df.sum(axis=1)
    table_df.index.name = "EA"
    table_df = table_df.reset_index()

    display_df = table_df.copy()
    for c in display_df.columns[1:]:
        display_df[c] = display_df[c].map(lambda v: f"{v:,.0f}")

    table_component = _make_table(display_df)

    cards = html.Div(
        [
            _kpi_card(
                "Best EA (3Y)",
                f"{best_ea}",
                f"Total: ${best_ea_val:,.0f}",
                "fas fa-trophy",
                "insight-card-green",
            ),
            _kpi_card(
                "Worst EA (3Y)",
                f"{worst_ea}",
                f"Total: ${worst_ea_val:,.0f}",
                "fas fa-exclamation-triangle",
                "insight-card-red",
            ),
            _kpi_card(
                "Total Profit (3Y)",
                f"${total_profit:,.0f}",
                f"Latest year: ${this_year_val:,.0f}",
                "fas fa-dollar-sign",
                "insight-card-blue",
            ),
            _kpi_card(
                "YoY Growth",
                f"{yoy:,.1f}%",
                f"{current_year-1} → {current_year}",
                "fas fa-chart-line",
                "insight-card-yellow",
            ),
            _kpi_card(
                "Max Profit Trade",
                f"${max_profit_val:,.0f}",
                "Across all years",
                "fas fa-arrow-up",
                "insight-card-purple",
            ),
            _kpi_card(
                "Max Loss Trade",
                f"${max_loss_val:,.0f}",
                "Across all years",
                "fas fa-arrow-down",
                "insight-card-dark",
            ),
        ]
    )

    right_panel = html.Div(
        [
            cards,
            html.Div(
                html.Small("EA profit breakdown by year", className="text-muted mt-2")
            ),
            table_component,
        ]
    )

    return dbc.Row(
        [
            dbc.Col(dcc.Graph(figure=fig), width=8),
            dbc.Col(right_panel, width=4),
        ],
        class_name="mt-2",
    )


def create_monthly_stats(transactions=None):
    if transactions is None:
        tx = _get_tx()
    else:
        tx = transactions.copy()

    today = datetime.now()
    months = pd.date_range(today - pd.DateOffset(months=11), today, freq="MS").to_period("M")
    month_labels = [m.strftime("%Y-%m") for m in months]

    if tx.empty:
        return dbc.Row(
            dbc.Col(html.Div("No monthly data available", className="text-muted"), width=12)
        )

    tx["Month"] = tx["TimeOpen"].dt.to_period("M").astype(str)
    eas = sorted(tx["EA_Name"].dropna().unique())

    result = pd.DataFrame(index=month_labels, columns=eas).fillna(0.0)
    grouped = tx.groupby(["Month", "EA_Name"])["Profit"].sum()
    for (mon, ea), profit in grouped.items():
        if mon in month_labels:
            result.loc[mon, ea] = float(profit)

    monthly_totals = result.sum(axis=1)
    total_profit = float(monthly_totals.sum()) if not monthly_totals.empty else 0.0
    best_month = monthly_totals.idxmax() if not monthly_totals.empty else "-"
    worst_month = monthly_totals.idxmin() if not monthly_totals.empty else "-"
    best_month_val = float(monthly_totals.max()) if not monthly_totals.empty else 0.0
    worst_month_val = float(monthly_totals.min()) if not monthly_totals.empty else 0.0
    avg_month_profit = float(monthly_totals.mean()) if not monthly_totals.empty else 0.0

    fig = go.Figure()
    for ea in eas:
        fig.add_trace(
            go.Bar(
                x=month_labels,
                y=result[ea].values,
                name=ea,
            )
        )

    fig.update_layout(
        title="Monthly Profit by EA (Stacked, Last 12 Months)",
        barmode="stack",
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Profit ($)",
        xaxis={"tickangle": -45},
        height=420,
        legend_title="EA",
    )

    table_df = result.copy().T
    table_df["Total"] = table_df.sum(axis=1)
    table_df.index.name = "EA"
    table_df = table_df.reset_index()

    display_df = table_df.copy()
    for c in display_df.columns[1:]:
        display_df[c] = display_df[c].map(lambda v: f"{v:,.0f}")

    table_component = _make_table(display_df)

    cards = html.Div(
        [
            _kpi_card(
                "Best Month (Total)",
                best_month,
                f"${best_month_val:,.0f}",
                "fas fa-calendar-check",
                "insight-card-green",
            ),
            _kpi_card(
                "Worst Month (Total)",
                worst_month,
                f"${worst_month_val:,.0f}",
                "fas fa-calendar-times",
                "insight-card-red",
            ),
            _kpi_card(
                "Avg Monthly Profit",
                f"${avg_month_profit:,.0f}",
                "Last 12 months",
                "fas fa-wave-square",
                "insight-card-blue",
            ),
        ]
    )

    right_panel = html.Div(
        [
            cards,
            html.Div(
                html.Small(
                    "EA profit breakdown by month (last 12)",
                    className="text-muted mt-2",
                )
            ),
            table_component,
        ]
    )

    return dbc.Row(
        [
            dbc.Col(dcc.Graph(figure=fig), width=8),
            dbc.Col(right_panel, width=4),
        ],
        class_name="mt-4",
    )


def create_week_stats(transactions=None):
    if transactions is None:
        tx = _get_tx()
    else:
        tx = transactions.copy()

    today = datetime.now().date()
    days = [(today - timedelta(days=i)) for i in range(13, -1, -1)]
    day_labels = [d.strftime("%Y-%m-%d") for d in days]

    if tx.empty:
        return dbc.Row(
            dbc.Col(
                html.Div("No recent daily data available", className="text-muted"),
                width=12,
            )
        )

    tx["Date"] = tx["TimeOpen"].dt.date.astype(str)
    eas = sorted(tx["EA_Name"].dropna().unique())

    result = pd.DataFrame(index=day_labels, columns=eas).fillna(0.0)
    grouped = tx.groupby(["Date", "EA_Name"])["Profit"].sum()
    for (d, ea), profit in grouped.items():
        if d in day_labels:
            result.loc[d, ea] = float(profit)

    daily_totals = result.sum(axis=1)
    total_profit = float(daily_totals.sum()) if not daily_totals.empty else 0.0
    best_day = daily_totals.idxmax() if not daily_totals.empty else "-"
    worst_day = daily_totals.idxmin() if not daily_totals.empty else "-"
    best_day_val = float(daily_totals.max()) if not daily_totals.empty else 0.0
    worst_day_val = float(daily_totals.min()) if not daily_totals.empty else 0.0
    avg_day_profit = float(daily_totals.mean()) if not daily_totals.empty else 0.0

    fig = go.Figure()
    for ea in eas:
        fig.add_trace(
            go.Bar(
                x=day_labels,
                y=result[ea].values,
                name=ea,
            )
        )

    fig.update_layout(
        title="Daily Profit by EA (Stacked, Last 14 Days)",
        barmode="stack",
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Profit ($)",
        xaxis={"tickangle": -45},
        height=420,
        legend_title="EA",
    )

    table_df = result.copy().T
    table_df["Total"] = table_df.sum(axis=1)
    table_df.index.name = "EA"
    table_df = table_df.reset_index()

    display_df = table_df.copy()
    for c in display_df.columns[1:]:
        display_df[c] = display_df[c].map(lambda v: f"{v:,.0f}")

    table_component = _make_table(display_df)

    cards = html.Div(
        [
            _kpi_card(
                "Best Day (Total)",
                best_day,
                f"${best_day_val:,.0f}",
                "fas fa-sun",
                "insight-card-green",
            ),
            _kpi_card(
                "Worst Day (Total)",
                worst_day,
                f"${worst_day_val:,.0f}",
                "fas fa-cloud-showers-heavy",
                "insight-card-red",
            ),
            _kpi_card(
                "Avg Daily Profit",
                f"${avg_day_profit:,.0f}",
                "Last 14 days",
                "fas fa-chart-area",
                "insight-card-blue",
            ),
            _kpi_card(
                "Total Profit (14d)",
                f"${total_profit:,.0f}",
                "All EAs combined",
                "fas fa-coins",
                "insight-card-yellow",
            ),
        ]
    )

    right_panel = html.Div(
        [
            cards,
            html.Div(
                html.Small(
                    "EA profit breakdown by day (last 14)",
                    className="text-muted mt-2",
                )
            ),
            table_component,
        ]
    )

    return dbc.Row(
        [
            dbc.Col(dcc.Graph(figure=fig), width=8),
            dbc.Col(right_panel, width=4),
        ],
        class_name="mt-4",
    )