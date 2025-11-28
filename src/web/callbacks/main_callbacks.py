from datetime import datetime

from dash.dependencies import Input, Output

from web.helpers import load_transactions
from web.components import (
    create_summary_cards,
    create_ea_overview,
    create_transaction_table,
    create_profit_chart,
    create_yearly_stats,
    create_monthly_stats,
    create_week_stats,
    create_ea_analysis_table,
)
from web.components.date_range_performance import build_date_range_layout_components
from web.components.ea_performance import build_ea_performance_components
from web.components.trading_pair_performance import build_pair_performance_components
from web.components.risk_insights import create_ea_risk_insights
from web.components.analysis_performance import build_analysis_components


def register_callbacks(app):

    # Populate Performance Stats filters
    @app.callback(
        [
            Output("perf-year-filter", "options"),
            Output("perf-year-filter", "value"),
            Output("perf-month-filter", "options"),
            Output("perf-month-filter", "value"),
            Output("perf-ea-filter", "options"),
            Output("perf-ea-filter", "value"),
            Output("perf-symbol-filter", "options"),
            Output("perf-symbol-filter", "value"),
        ],
        Input("interval-component", "n_intervals"),
    )
    def populate_performance_filters(n):
        tx = load_transactions()

        year_options = [{"label": "All", "value": "all"}]
        month_options = [{"label": "All", "value": "all"}]
        ea_options = [{"label": "All", "value": "all"}]
        symbol_options = [{"label": "All", "value": "all"}]

        if tx is not None and not tx.empty:
            if "TimeOpen" in tx.columns:
                years = sorted(tx["TimeOpen"].dt.year.unique())
                year_options += [{"label": str(y), "value": str(y)} for y in years]

                months = sorted(tx["TimeOpen"].dt.to_period("M").astype(str).unique())
                month_options += [{"label": m, "value": m} for m in months]

            if "EA_Name" in tx.columns:
                eas = sorted(tx["EA_Name"].dropna().unique())
                ea_options += [{"label": ea, "value": ea} for ea in eas]

            if "Symbol" in tx.columns:
                symbols = sorted(tx["Symbol"].dropna().unique())
                symbol_options += [{"label": s, "value": s} for s in symbols]

        return (
            year_options,
            "all",
            month_options,
            "all",
            ea_options,
            "all",
            symbol_options,
            "all",
        )

    # Populate Date Range Performance EA/Symbol filters
    @app.callback(
        [
            Output("drp-ea-filter", "options"),
            Output("drp-ea-filter", "value"),
            Output("drp-symbol-filter", "options"),
            Output("drp-symbol-filter", "value"),
        ],
        Input("interval-component", "n_intervals"),
    )
    def populate_date_range_filters(n):
        tx = load_transactions()

        ea_options = [{"label": "All", "value": "all"}]
        symbol_options = [{"label": "All", "value": "all"}]

        if tx is not None and not tx.empty:
            if "EA_Name" in tx.columns:
                eas = sorted(tx["EA_Name"].dropna().unique())
                ea_options += [{"label": ea, "value": ea} for ea in eas]

            if "Symbol" in tx.columns:
                symbols = sorted(tx["Symbol"].dropna().unique())
                symbol_options += [{"label": s, "value": s} for s in symbols]

        return ea_options, "all", symbol_options, "all"

    # Populate EA Performance EA filter
    @app.callback(
        [
            Output("ea-perf-ea-filter", "options"),
            Output("ea-perf-ea-filter", "value"),
        ],
        Input("interval-component", "n_intervals"),
    )
    def populate_ea_performance_filter(n):
        tx = load_transactions()
        ea_options = [{"label": "All", "value": "all"}]

        if tx is not None and not tx.empty and "EA_Name" in tx.columns:
            eas = sorted(tx["EA_Name"].dropna().unique())
            ea_options += [{"label": ea, "value": ea} for ea in eas]

        return ea_options, "all"

    # Populate Trading Pair Performance symbol filter
    @app.callback(
        [
            Output("pair-perf-symbol-filter", "options"),
            Output("pair-perf-symbol-filter", "value"),
        ],
        Input("interval-component", "n_intervals"),
    )
    def populate_pair_performance_filter(n):
        tx = load_transactions()
        symbol_options = [{"label": "All", "value": "all"}]

        if tx is not None and not tx.empty and "Symbol" in tx.columns:
            symbols = sorted(tx["Symbol"].dropna().unique())
            symbol_options += [{"label": s, "value": s} for s in symbols]

        return symbol_options, "all"

    # Populate Analysis tab EA/Symbol filters
    @app.callback(
        [
            Output("ana-ea-filter", "options"),
            Output("ana-ea-filter", "value"),
            Output("ana-symbol-filter", "options"),
            Output("ana-symbol-filter", "value"),
        ],
        Input("interval-component", "n_intervals"),
    )
    def populate_analysis_filters(n):
        tx = load_transactions()
        ea_options = [{"label": "All", "value": "all"}]
        symbol_options = [{"label": "All", "value": "all"}]

        if tx is not None and not tx.empty:
            if "EA_Name" in tx.columns:
                eas = sorted(tx["EA_Name"].dropna().unique())
                ea_options += [{"label": ea, "value": ea} for ea in eas]
            if "Symbol" in tx.columns:
                symbols = sorted(tx["Symbol"].dropna().unique())
                symbol_options += [{"label": s, "value": s} for s in symbols]

        return ea_options, "all", symbol_options, "all"

    # Main dashboard sections (Overview / Analysis Summary / Performance Stats)
    @app.callback(
        [
            Output("summary-cards", "children"),
            Output("ea-overview", "children"),
            Output("ea-risk-insights", "children"),
            Output("ea-analysis", "children"),
            Output("profit-chart", "figure"),
            Output("yearly-stats", "children"),
            Output("monthly-stats", "children"),
            Output("week-stats", "children"),
            Output("last-update", "children"),
        ],
        [
            Input("interval-component", "n_intervals"),
            Input("perf-year-filter", "value"),
            Input("perf-month-filter", "value"),
            Input("perf-ea-filter", "value"),
            Input("perf-symbol-filter", "value"),
        ],
    )
    def update_dashboard(n, year_val, month_val, ea_val, symbol_val):
        tx = load_transactions()
        tx_filtered = tx.copy() if tx is not None and not tx.empty else tx

        if tx_filtered is not None and not tx_filtered.empty:
            if year_val and year_val != "all" and "TimeOpen" in tx_filtered.columns:
                year_int = int(year_val)
                tx_filtered = tx_filtered[tx_filtered["TimeOpen"].dt.year == year_int]

            if month_val and month_val != "all" and "TimeOpen" in tx_filtered.columns:
                tx_filtered = tx_filtered[
                    tx_filtered["TimeOpen"].dt.to_period("M").astype(str) == month_val
                ]

            if ea_val and ea_val != "all" and "EA_Name" in tx_filtered.columns:
                tx_filtered = tx_filtered[tx_filtered["EA_Name"] == ea_val]

            if symbol_val and symbol_val != "all" and "Symbol" in tx_filtered.columns:
                tx_filtered = tx_filtered[tx_filtered["Symbol"] == symbol_val]

        yearly_section = (
            create_yearly_stats(tx_filtered)
            if tx_filtered is not None
            else create_yearly_stats()
        )
        monthly_section = (
            create_monthly_stats(tx_filtered)
            if tx_filtered is not None
            else create_monthly_stats()
        )
        week_section = (
            create_week_stats(tx_filtered)
            if tx_filtered is not None
            else create_week_stats()
        )

        risk_insights = create_ea_risk_insights(tx_filtered)

        return (
            create_summary_cards(),
            create_ea_overview(),
            risk_insights,
            create_ea_analysis_table(),
            create_profit_chart(),
            yearly_section,
            monthly_section,
            week_section,
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )

    # Analysis tab charts + trade table
    @app.callback(
        [
            Output("ana-daily-equity", "figure"),
            Output("ana-weekly-equity", "figure"),
            Output("ana-trade-table", "children"),
        ],
        [
            Input("interval-component", "n_intervals"),
            Input("ana-date-range", "start_date"),
            Input("ana-date-range", "end_date"),
            Input("ana-ea-filter", "value"),
            Input("ana-symbol-filter", "value"),
        ],
    )
    def update_analysis_tab(n, start_date, end_date, ea_val, symbol_val):
        daily_fig, weekly_fig, table_comp = build_analysis_components(
            start_date, end_date, ea_val, symbol_val
        )
        return daily_fig, weekly_fig, table_comp

    # Date Range Performance tab (EA summary table + charts)
    @app.callback(
        [
            Output("drp-kpi-cards", "children"),
            Output("drp-equity-curve", "figure"),
            Output("drp-profit-per-day", "figure"),
            Output("drp-profit-by-ea", "figure"),
            Output("drp-profit-by-symbol", "figure"),
            Output("drp-trade-table", "children"),
        ],
        [
            Input("interval-component", "n_intervals"),
            Input("drp-date-range", "start_date"),
            Input("drp-date-range", "end_date"),
            Input("drp-ea-filter", "value"),
            Input("drp-symbol-filter", "value"),
        ],
    )
    def update_date_range_tab(n, start_date, end_date, ea_val, symbol_val):
        (
            ea_summary,
            equity_fig,
            ppd_fig,
            pea_fig,
            psym_fig,
            table_comp,
        ) = build_date_range_layout_components(start_date, end_date, ea_val, symbol_val)

        return ea_summary, equity_fig, ppd_fig, pea_fig, psym_fig, table_comp

    # EA Performance tab
    @app.callback(
        [
            Output("ea-perf-summary-table", "children"),
            Output("ea-perf-equity-curve", "figure"),
            Output("ea-perf-winloss-distribution", "figure"),
            Output("ea-perf-monthly-profit", "figure"),
            Output("ea-perf-trade-table", "children"),
        ],
        [
            Input("interval-component", "n_intervals"),
            Input("ea-perf-ea-filter", "value"),
        ],
    )
    def update_ea_performance_tab(n, ea_val):
        (
            summary_table,
            equity_fig,
            winloss_fig,
            monthly_fig,
            trades_table,
        ) = build_ea_performance_components(ea_val)

        return summary_table, equity_fig, winloss_fig, monthly_fig, trades_table

    # Trading Pair Performance tab
    @app.callback(
        [
            Output("pair-perf-summary-table", "children"),
            Output("pair-perf-equity-curve", "figure"),
            Output("pair-perf-winloss-distribution", "figure"),
            Output("pair-perf-monthly-profit", "figure"),
            Output("pair-perf-trade-table", "children"),
        ],
        [
            Input("interval-component", "n_intervals"),
            Input("pair-perf-symbol-filter", "value"),
        ],
    )
    def update_pair_performance_tab(n, symbol_val):
        (
            summary_table,
            equity_fig,
            winloss_fig,
            monthly_fig,
            trades_table,
        ) = build_pair_performance_components(symbol_val)

        return summary_table, equity_fig, winloss_fig, monthly_fig, trades_table