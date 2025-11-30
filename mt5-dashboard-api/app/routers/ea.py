"""
EA (Expert Advisor) API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import plotly.graph_objs as go

from app.core.loader import load_ea_data, get_available_eas, load_portfolio_data
from app.services.ea_service import (
    compute_ea_stats,
    get_ea_equity_curve,
    get_ea_symbol_performance,
    get_all_eas_summary,
)

router = APIRouter(prefix="/ea", tags=["EA"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def ea_list(request: Request):
    """
    List all available EAs
    """
    eas = get_available_eas()

    return templates.TemplateResponse(
        "ea_list.html",
        {
            "request": request,
            "eas": eas,
        }
    )


@router.get("/overview/all", response_class=HTMLResponse)
async def ea_all_overview(request: Request):
    """
    Overview of all EAs with key metrics
    """
    df = load_portfolio_data()
    all_eas = get_all_eas_summary(df)

    return templates.TemplateResponse(
        "ea_all_overview.html",
        {
            "request": request,
            "eas": all_eas,
            "total_eas": len(all_eas),
        }
    )


@router.get("/{ea_name}", response_class=HTMLResponse)
async def ea_dashboard(request: Request, ea_name: str):
    """
    Dashboard for specific EA
    """
    # Load EA data
    df = load_ea_data(ea_name)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"EA '{ea_name}' not found")

    # Compute stats
    stats = compute_ea_stats(df, ea_name)

    # Build equity curve
    equity_df = get_ea_equity_curve(df)
    equity_chart_html = ""

    if not equity_df.empty:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=equity_df["Time"],
                y=equity_df["CumulativeProfit"],
                mode="lines",
                name="Cumulative Profit",
                line=dict(color="#3498db", width=2),
            )
        )
        fig.update_layout(
            title=f"{ea_name} - Equity Curve",
            template="plotly_white",
            xaxis_title="Date",
            yaxis_title="Cumulative Profit ($)",
            height=400,
        )
        equity_chart_html = fig.to_html(
            full_html=False,
            include_plotlyjs="cdn",
            config={"displayModeBar": False}
        )

    # Symbol performance
    symbol_perf = get_ea_symbol_performance(df)
    symbol_perf_html = symbol_perf.to_html(
        classes="table table-striped table-sm",
        index=False
    ) if not symbol_perf.empty else ""

    return templates.TemplateResponse(
        "ea_detail.html",
        {
            "request": request,
            "ea_name": ea_name,
            "stats": stats,
            "equity_chart": equity_chart_html,
            "symbol_performance": symbol_perf_html,
        }
    )


@router.get("/api/list")
async def api_ea_list():
    """
    API: Get list of all EAs
    """
    return {"eas": get_available_eas()}


@router.get("/api/{ea_name}/stats")
async def api_ea_stats(ea_name: str):
    """
    API: Get stats for specific EA
    """
    df = load_ea_data(ea_name)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"EA '{ea_name}' not found")

    stats = compute_ea_stats(df, ea_name)
    return stats


@router.get("/api/{ea_name}/equity")
async def api_ea_equity(ea_name: str):
    """
    API: Get equity curve for specific EA
    """
    df = load_ea_data(ea_name)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"EA '{ea_name}' not found")

    equity_df = get_ea_equity_curve(df)

    if equity_df.empty:
        return []

    # Convert to JSON
    result = equity_df.copy()
    if "Time" in result.columns:
        result["Time"] = result["Time"].astype(str)

    return result.to_dict(orient="records")
