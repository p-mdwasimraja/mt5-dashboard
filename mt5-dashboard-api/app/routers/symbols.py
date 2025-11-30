"""
Trading Symbol API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.loader import load_symbol_data, get_available_symbols
from app.services.symbol_service import (
    compute_symbol_stats,
    get_symbol_ea_performance,
)

router = APIRouter(prefix="/symbols", tags=["Symbols"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def symbol_list(request: Request):
    """
    List all trading symbols
    """
    symbols = get_available_symbols()

    return templates.TemplateResponse(
        "symbol_list.html",
        {
            "request": request,
            "symbols": symbols,
        }
    )


@router.get("/{symbol}", response_class=HTMLResponse)
async def symbol_dashboard(request: Request, symbol: str):
    """
    Dashboard for specific symbol
    """
    # Load symbol data
    df = load_symbol_data(symbol)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    # Compute stats
    stats = compute_symbol_stats(df, symbol)

    # EA performance
    ea_perf = get_symbol_ea_performance(df)
    ea_perf_html = ea_perf.to_html(
        classes="table table-striped table-sm",
        index=False
    ) if not ea_perf.empty else ""

    return templates.TemplateResponse(
        "symbol_detail.html",
        {
            "request": request,
            "symbol": symbol,
            "stats": stats,
            "ea_performance": ea_perf_html,
        }
    )


@router.get("/api/list")
async def api_symbol_list():
    """
    API: Get list of all symbols
    """
    return {"symbols": get_available_symbols()}


@router.get("/api/{symbol}/stats")
async def api_symbol_stats(symbol: str):
    """
    API: Get stats for specific symbol
    """
    df = load_symbol_data(symbol)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    stats = compute_symbol_stats(df, symbol)
    return stats
