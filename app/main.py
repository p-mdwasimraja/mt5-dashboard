from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import get_settings
from app.routers import portfolio, ea, symbols


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="MT5 Portfolio Dashboard (FastAPI)")


app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(portfolio.router)
app.include_router(ea.router)
app.include_router(symbols.router)


@app.get("/health")
async def health_check():
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "version": settings.version}
