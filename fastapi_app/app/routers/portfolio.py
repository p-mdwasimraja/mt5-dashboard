print('>>> USING portfolio router:', __file__)

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import plotly.graph_objs as go

from app.core.loader import load_portfolio_data
from app.services.portfolio_service import compute_portfolio_summary, build_equity_curve


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/")
async def portfolio_overview(request: Request):
    df = load_portfolio_data()
    summary = compute_portfolio_summary(df)

    equity_df = build_equity_curve(df)
    fig = go.Figure()
    if not equity_df.empty:
        fig.add_trace(
            go.Scatter(
                x=equity_df["Time"],
                y=equity_df["CumulativeProfit"],
                mode="lines",
                name="Portfolio Equity",
            )
        )
        fig.update_layout(
            title="Portfolio Cumulative Profit",
            template="plotly_white",
            xaxis_title="Time",
            yaxis_title="Cumulative Profit ($)",
        )
    else:
        fig.update_layout(
            title="Portfolio Cumulative Profit (no data)",
            template="plotly_white",
        )

    equity_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    return templates.TemplateResponse(
        "portfolio.html",
        {
            "request": request,
            "summary": summary,
            "equity_html": equity_html,
        },
    )


@router.get("/debug_paths")
async def debug_paths():
    import os
    from app.core.config import get_settings

    settings = get_settings()

    results = []
    for src in settings.enabled_sources():
        path = src.get("path")
        exists = os.path.exists(path)

        if exists:
            csvs = [f for f in os.listdir(path) if f.lower().endswith(".csv")]
        else:
            csvs = []

        results.append({
            "account": src.get("name"),
            "path": path,
            "exists": exists,
            "csv_files_found": csvs,
        })

    return results



@router.get("/debug_first_rows")
async def debug_first_rows():
    df = load_portfolio_data()
    if df.empty:
        return {"error": "DF is empty"}

    return {
        "columns": list(df.columns),
        "sample": df.head(10).to_dict(orient="records")
    }
