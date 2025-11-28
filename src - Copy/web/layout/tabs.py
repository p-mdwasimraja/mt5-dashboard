from datetime import datetime, timedelta
from dash import html, dcc
import dash_bootstrap_components as dbc

def overview_tab():
    return html.Div(
        [
            html.Br(),
            dbc.Row([dbc.Col(html.Div(id="summary-cards"), md=12)], className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(html.Div(id="ea-overview"), md=6),
                    dbc.Col(dcc.Graph(id="profit-chart"), md=6),
                ],
                className="mb-3",
            ),
            dbc.Row([dbc.Col(html.Div(id="transaction-table"), md=12)]),
        ],
        className="p-2",
    )


def analysis_tab():
    return html.Div(
        [
            html.Br(),
            html.Div(id="ea-analysis"),
        ],
        className="p-2",
    )


def performance_stats_tab():
    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Label("Year", className="fw-bold small"),
                                            dcc.Dropdown(
                                                id="perf-year-filter",
                                                options=[],
                                                value="all",
                                                clearable=False,
                                                placeholder="All years",
                                                className="perf-filter-dropdown",
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label("Month", className="fw-bold small"),
                                            dcc.Dropdown(
                                                id="perf-month-filter",
                                                options=[],
                                                value="all",
                                                clearable=False,
                                                placeholder="All months",
                                                className="perf-filter-dropdown",
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label("EA", className="fw-bold small"),
                                            dcc.Dropdown(
                                                id="perf-ea-filter",
                                                options=[],
                                                value="all",
                                                clearable=False,
                                                placeholder="All EAs",
                                                className="perf-filter-dropdown",
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label("Symbol", className="fw-bold small"),
                                            dcc.Dropdown(
                                                id="perf-symbol-filter",
                                                options=[],
                                                value="all",
                                                clearable=False,
                                                placeholder="All symbols",
                                                className="perf-filter-dropdown",
                                            ),
                                        ],
                                        md=3,
                                    ),
                                ],
                                className="g-2",
                            ),
                        ]
                    )
                ],
                className="shadow-sm mb-4 mt-3",
            ),
            html.H4("Yearly Performance", className="mt-3 mb-2"),
            html.Div(id="yearly-stats"),
            html.H4("Monthly Performance", className="mt-4 mb-2"),
            html.Div(id="monthly-stats"),
            html.H4("Recent Daily Performance (Last 14 Days)", className="mt-4 mb-2"),
            html.Div(id="week-stats"),
        ],
        className="p-2",
    )


def ea_performance_tab():
    return html.Div(
        [
            html.Br(),
            html.P("EA Performance dashboard coming soon.", className="text-muted"),
        ],
        className="p-2",
    )


def trading_pair_performance_tab():
    return html.Div(
        [
            html.Br(),
            html.P(
                "Trading Pair Performance dashboard coming soon.",
                className="text-muted",
            ),
        ],
        className="p-2",
    )


def date_range_performance_tab():
    today = datetime.now().date()
    start_default = today - timedelta(days=30)

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Label(
                                                "Date Range", className="fw-bold small"
                                            ),
                                            dcc.DatePickerRange(
                                                id="drp-date-range",
                                                start_date=start_default,
                                                end_date=today,
                                                display_format="YYYY-MM-DD",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label(
                                                "EA", className="fw-bold small"
                                            ),
                                            dcc.Dropdown(
                                                id="drp-ea-filter",
                                                options=[],
                                                value="all",
                                                clearable=False,
                                                placeholder="All EAs",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Label(
                                                "Symbol", className="fw-bold small"
                                            ),
                                            dcc.Dropdown(
                                                id="drp-symbol-filter",
                                                options=[],
                                                value="all",
                                                clearable=False,
                                                placeholder="All symbols",
                                            ),
                                        ],
                                        md=4,
                                    ),
                                ],
                                className="g-2",
                            ),
                        ]
                    )
                ],
                className="shadow-sm mb-4 mt-3",
            ),
            html.Div(id="drp-kpi-cards"),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="drp-equity-curve"), md=8),
                    dbc.Col(dcc.Graph(id="drp-profit-per-day"), md=4),
                ],
                className="mt-4",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="drp-profit-by-ea"), md=6),
                    dbc.Col(dcc.Graph(id="drp-profit-by-symbol"), md=6),
                ],
                className="mt-4",
            ),
            html.H5("Trades in Date Range", className="mt-4 mb-2"),
            html.Div(id="drp-trade-table"),
        ],
        className="p-2",
    )


def create_tabs():
    return dcc.Tabs(
        id="main-tabs",
        value="overview",
        children=[
            dcc.Tab(label="Overview", value="overview", children=overview_tab()),
            dcc.Tab(label="Analysis", value="analysis", children=analysis_tab()),
            dcc.Tab(
                label="Performance Stats",
                value="performance",
                children=performance_stats_tab(),
            ),
            dcc.Tab(
                label="EA Performance",
                value="ea-performance",
                children=ea_performance_tab(),
            ),
            dcc.Tab(
                label="Trading Pair Performance",
                value="trading-pair-performance",
                children=trading_pair_performance_tab(),
            ),
            dcc.Tab(
                label="Date Range Performance",
                value="date-range-performance",
                children=date_range_performance_tab(),
            ),
        ],
    )