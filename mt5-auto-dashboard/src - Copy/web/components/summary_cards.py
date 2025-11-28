
"""Summary cards component"""
import dash_bootstrap_components as dbc
from dash import html
from web.helpers import load_stats

def create_summary_cards():
    stats = load_stats()

    if not stats:
        return html.Div("No data available", className="text-center text-muted")

    cards = []

    cards.append(
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-users fa-2x text-primary mb-2"),
                        html.H4(stats.get('total_eas', 0), className="mb-0"),
                        html.P("Expert Advisors", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], className="shadow-sm")
        ], width=12, md=6, lg=3, className="mb-4")
    )

    cards.append(
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-dollar-sign fa-2x text-success mb-2"),
                        html.H4(stats.get('total_deposits', 0), className="mb-0"),
                        html.P("Total Deposits", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], className="shadow-sm")
        ], width=12, md=6, lg=3, className="mb-4")
    )

    cards.append(
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-exchange-alt fa-2x text-info mb-2"),
                        html.H4(stats.get('total_transactions', 0), className="mb-0"),
                        html.P("Transactions", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], className="shadow-sm")
        ], width=12, md=6, lg=3, className="mb-4")
    )

    cards.append(
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-bar fa-2x text-warning mb-2"),
                        html.H4(stats.get('total_open_positions', 0), className="mb-0"),
                        html.P("Open Positions", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], className="shadow-sm")
        ], width=12, md=6, lg=3, className="mb-4")
    )

    return dbc.Row(cards)
