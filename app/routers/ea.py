from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.core.loader import load_portfolio_data
from app.services.ea_service import compute_ea_performance


templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/ea", tags=["ea"])


@router.get("/performance")
async def ea_performance(request: Request):
    df = load_portfolio_data()
    ea_df = compute_ea_performance(df)
    records = ea_df.to_dict(orient="records") if not ea_df.empty else []
    return templates.TemplateResponse(
        "ea_performance.html",
        {"request": request, "rows": records},
    )
