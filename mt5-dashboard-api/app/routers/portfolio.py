"""
Portfolio API endpoints
Optimized for VPS performance with caching
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import plotly.graph_objs as go

from app.core.loader import load_portfolio_data
from app.services.portfolio_service import (
    compute_portfolio_summary,
    build_equity_curve,
    get_ea_breakdown,
    get_symbol_breakdown,
    get_recent_trades,
)

router = APIRouter(tags=["Portfolio"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def portfolio_dashboard(request: Request):
    """
    Main portfolio dashboard page
    Server-side rendered for better VPS performance
    """
    # Load data (cached)
    df = load_portfolio_data()

    # Compute summary stats
    summary = compute_portfolio_summary(df)

    # Build equity curve chart
    equity_df = build_equity_curve(df)
    equity_chart_html = ""

    if not equity_df.empty:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=equity_df["Time"],
                y=equity_df["CumulativeProfit"],
                mode="lines",
                name="Cumulative Profit",
                line=dict(color="#2ecc71", width=2),
            )
        )
        fig.update_layout(
            title="Portfolio Equity Curve",
            template="plotly_white",
            xaxis_title="Date",
            yaxis_title="Cumulative Profit ($)",
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
        )
        equity_chart_html = fig.to_html(
            full_html=False,
            include_plotlyjs="cdn",
            config={"displayModeBar": False}
        )

    # Get EA breakdown
    ea_breakdown = get_ea_breakdown(df)
    ea_breakdown_html = ea_breakdown.to_html(
        classes="table table-striped table-sm",
        index=False
    ) if not ea_breakdown.empty else ""

    # Get symbol breakdown
    symbol_breakdown = get_symbol_breakdown(df)
    symbol_breakdown_html = symbol_breakdown.to_html(
        classes="table table-striped table-sm",
        index=False
    ) if not symbol_breakdown.empty else ""

    # Get recent trades
    recent_trades = get_recent_trades(df, limit=15)
    recent_trades_html = recent_trades.to_html(
        classes="table table-striped table-sm",
        index=False
    ) if not recent_trades.empty else ""

    return templates.TemplateResponse(
        "portfolio.html",
        {
            "request": request,
            "summary": summary,
            "equity_chart": equity_chart_html,
            "ea_breakdown": ea_breakdown_html,
            "symbol_breakdown": symbol_breakdown_html,
            "recent_trades": recent_trades_html,
        }
    )


@router.get("/api/summary")
async def api_portfolio_summary():
    """
    API endpoint for portfolio summary
    Returns JSON data
    """
    df = load_portfolio_data()
    summary = compute_portfolio_summary(df)
    return summary


@router.get("/api/equity-curve")
async def api_equity_curve():
    """
    API endpoint for equity curve data
    Returns JSON array
    """
    df = load_portfolio_data()
    equity_df = build_equity_curve(df)

    if equity_df.empty:
        return []

    # Convert to JSON-friendly format
    return equity_df.to_dict(orient="records")


@router.get("/api/ea-breakdown")
async def api_ea_breakdown():
    """
    API endpoint for EA breakdown
    Returns JSON array
    """
    df = load_portfolio_data()
    ea_breakdown = get_ea_breakdown(df)

    if ea_breakdown.empty:
        return []

    return ea_breakdown.to_dict(orient="records")


@router.get("/api/symbol-breakdown")
async def api_symbol_breakdown():
    """
    API endpoint for symbol breakdown
    Returns JSON array
    """
    df = load_portfolio_data()
    symbol_breakdown = get_symbol_breakdown(df)

    if symbol_breakdown.empty:
        return []

    return symbol_breakdown.to_dict(orient="records")


@router.get("/api/recent-trades")
async def api_recent_trades(limit: int = 20):
    """
    API endpoint for recent trades
    Returns JSON array
    """
    df = load_portfolio_data()
    recent = get_recent_trades(df, limit=limit)

    if recent.empty:
        return []

    # Convert timestamps to strings for JSON
    result = recent.copy()
    if "Time" in result.columns:
        result["Time"] = result["Time"].astype(str)

    return result.to_dict(orient="records")
