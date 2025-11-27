# MT5 Portfolio Dashboard (FastAPI, Lightweight)

Pure FastAPI + Jinja + Plotly web app that merges all enabled MT5 sources
into a single portfolio and gives you:

- Portfolio overview (profit, trades, win rate, best/worst EA & symbol)
- EA performance table (merged across accounts)
- Symbol performance table (merged across accounts)
- Debug page to see which MT5 folders + CSVs are detected

## 1. Folder Structure

Place this inside your main project, e.g.:

    mt5_auto_dashboard/
        config/
            settings.yaml            # your existing YAML
        mt5_fastapi_portfolio/
            app/
            config/                  # copy settings.yaml here too OR edit config.py
            requirements.txt
            start_fastapi.bat
            ...

The app expects:

    mt5_fastapi_portfolio/config/settings.yaml

by default (CONFIG_PATH in `app/core/config.py`).

## 2. Install Dependencies (recommended: venv)

From inside `mt5_fastapi_portfolio`:

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

## 3. Configure settings.yaml

Copy your existing MT5 dashboard config:

    copy ..\config\settings.yaml config\settings.yaml

Ensure you have valid `mt5_sources` entries with correct MT5_Data paths.

## 4. Start the Server

Use the batch script (runs on port 8010 to avoid port 8000 conflicts):

    start_fastapi.bat

Then open in your browser:

- http://127.0.0.1:8010/                 → Portfolio overview
- http://127.0.0.1:8010/ea/performance   → EA performance
- http://127.0.0.1:8010/symbols/performance → Symbol performance
- http://127.0.0.1:8010/debug_paths      → See which MT5 paths + CSVs were found
