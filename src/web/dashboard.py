"""
MT5 Auto Dashboard - Modular Web Entry (Fixed Path Version)
"""

import os
os.environ['JUPYTER_PLATFORM_DIRS'] = '0'

import sys
from pathlib import Path

# ================================================================
# 🔧 FIXED PATH HANDLING — Ensures imports work ALWAYS
# ================================================================

# Current file → src/web/dashboard.py
current_file = Path(__file__).resolve()

# src/web/
web_dir = current_file.parent

# src/
src_dir = web_dir.parent

# project root → mt5_auto_dashboard/
project_root = src_dir.parent

# Make sure project root & src/ are in the Python path
for p in [project_root, src_dir]:
    p = str(p)
    if p not in sys.path:
        sys.path.insert(0, p)

# Verify Python sees 'web', 'core', 'utils'
# print("PYTHONPATH:", sys.path)   # uncomment to debug


# ================================================================
# Imports AFTER fixing sys.path
# ================================================================

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from web.layout import create_navbar, create_tabs
from web.callbacks import register_callbacks
from utils.config import config


# ================================================================
# Dash App Initialization
# ================================================================

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    dbc.icons.FONT_AWESOME
]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

app.title = "MT5 Auto Dashboard"


# ================================================================
# App Layout
# ================================================================

app.layout = html.Div([

    # Top Navigation Bar
    create_navbar(),

    # Main container
    dbc.Container([

        # Background auto-refresh (interval in settings.yaml)
        dcc.Interval(
            id='interval-component',
            interval=config.get('dashboard.update_interval', 60000),
            n_intervals=0
        ),

        # MT5 → CSV → Processor auto-refresh
        dcc.Interval(
            id='data-refresh-interval',
            interval=config.get('dashboard.data_refresh_interval', 300000),
            n_intervals=0
        ),

        # Main Application Tabs
        create_tabs(),

    ], fluid=True)
], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})


# ================================================================
# Register all callbacks
# ================================================================

register_callbacks(app)


# ================================================================
# Run Server
# ================================================================

if __name__ == "__main__":

    host = config.get("dashboard.host", "127.0.0.1")
    port = config.get("dashboard.port", 8050)
    debug = config.get("dashboard.debug", False)

    print("\n" + "=" * 60)
    print("MT5 Auto Dashboard starting...")
    print(f"📊 Dashboard URL: http://{host}:{port}")
    print("=" * 60 + "\n")

    app.run(host=host, port=port, debug=debug)
