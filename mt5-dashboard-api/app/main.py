"""
MT5 Dashboard API - Main Application
Optimized for VPS deployment with caching and minimal resource usage
"""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.routers import portfolio, ea, symbols, system, debug

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Lightweight MT5 Trading Dashboard API - Optimized for VPS",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add GZip compression middleware for better performance
if settings.enable_gzip:
    app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(portfolio.router)
app.include_router(ea.router)
app.include_router(symbols.router)
app.include_router(system.router)
app.include_router(debug.router)


@app.get("/")
async def root():
    """
    Redirect root to portfolio dashboard
    """
    return RedirectResponse(url="/")


@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks
    """
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Cache TTL: {settings.cache_ttl}s")
    logger.info(f"Cache Max Size: {settings.cache_max_size}")

    # Create logs directory if not exists
    Path("logs").mkdir(exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks
    """
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.max_workers if not settings.reload else 1,
        log_level="info",
    )
