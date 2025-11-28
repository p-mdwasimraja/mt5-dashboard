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


def register_callbacks(app):

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

    @app.callback(
        [
            Output("summary-cards", "children"),
            Output("ea-overview", "children"),
            Output("ea-analysis", "children"),
            Output("profit-chart", "figure"),
            Output("transaction-table", "children"),
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

        return (
            create_summary_cards(),
            create_ea_overview(),
            create_ea_analysis_table(),
            create_profit_chart(),
            create_transaction_table(),
            yearly_section,
            monthly_section,
            week_section,
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )

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
            kpi_cards,
            equity_fig,
            ppd_fig,
            pea_fig,
            psym_fig,
            table_comp,
        ) = build_date_range_layout_components(start_date, end_date, ea_val, symbol_val)

        return kpi_cards, equity_fig, ppd_fig, pea_fig, psym_fig, table_comp