
"""Navbar layout for MT5 Auto Dashboard"""
import dash_bootstrap_components as dbc
from dash import html

def create_navbar():
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.I(className="fas fa-chart-line me-2"),
                    dbc.NavbarBrand("MT5 Auto Dashboard", className="ms-2")
                ], width="auto"),
            ], align="center", className="g-0"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-sync-alt me-2"),
                        html.Span(id="last-update", children="Loading...")
                    ], className="text-light")
                ], width="auto"),
            ], align="center"),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    )
