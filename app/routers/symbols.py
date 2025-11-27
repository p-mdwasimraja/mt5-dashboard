from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.core.loader import load_portfolio_data
from app.services.symbol_service import compute_symbol_performance


templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/symbols", tags=["symbols"])


@router.get("/performance")
async def symbol_performance(request: Request):
    df = load_portfolio_data()
    sym_df = compute_symbol_performance(df)
    records = sym_df.to_dict(orient="records") if not sym_df.empty else []
    return templates.TemplateResponse(
        "symbol_performance.html",
        {"request": request, "rows": records},
    )
