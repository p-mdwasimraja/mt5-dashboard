"""
Debug endpoints for troubleshooting data loading issues
"""
from fastapi import APIRouter
from pathlib import Path
import os

from app.core.config import get_mt5_config, get_enabled_sources
from app.core.loader import load_portfolio_data

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/config")
async def debug_config():
    """Show current configuration"""
    config = get_mt5_config()
    sources = get_enabled_sources()

    return {
        "config_file": "config/settings.yaml",
        "mt5_sources": sources,
        "total_sources": len(sources),
        "enabled_sources": len([s for s in sources if s.get("enabled")])
    }


@router.get("/paths")
async def debug_paths():
    """Check if configured paths exist and list CSV files"""
    sources = get_enabled_sources()
    results = []

    for src in sources:
        path_str = src.get("path")
        path = Path(path_str)

        result = {
            "name": src.get("name"),
            "path": path_str,
            "enabled": src.get("enabled"),
            "exists": path.exists(),
            "is_dir": path.is_dir() if path.exists() else False,
        }

        if path.exists() and path.is_dir():
            # List CSV files
            history_files = list(path.glob("*_History.csv"))
            account_files = list(path.glob("*_Account.csv"))
            position_files = list(path.glob("*_Positions.csv"))

            result["csv_files"] = {
                "history": [f.name for f in history_files],
                "account": [f.name for f in account_files],
                "positions": [f.name for f in position_files],
            }
            result["total_files"] = len(history_files) + len(account_files) + len(position_files)
        else:
            result["error"] = "Path does not exist or is not a directory"

        results.append(result)

    return {
        "sources_checked": len(results),
        "sources": results
    }


@router.get("/load-test")
async def debug_load_test():
    """Test data loading and show results"""
    try:
        df = load_portfolio_data()

        if df.empty:
            return {
                "success": False,
                "message": "DataFrame is empty - no data loaded",
                "rows": 0,
                "columns": []
            }

        return {
            "success": True,
            "message": "Data loaded successfully",
            "rows": len(df),
            "columns": list(df.columns),
            "sample_data": df.head(5).to_dict(orient="records"),
            "unique_eas": df["EA_Name"].unique().tolist() if "EA_Name" in df.columns else [],
            "unique_symbols": df["Symbol"].unique().tolist() if "Symbol" in df.columns else [],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.get("/csv-raw/{source_index}")
async def debug_csv_raw(source_index: int = 0):
    """Read first few lines of CSV file directly"""
    sources = get_enabled_sources()

    if source_index >= len(sources):
        return {"error": f"Invalid source index. Max: {len(sources)-1}"}

    src = sources[source_index]
    path = Path(src.get("path"))

    if not path.exists():
        return {"error": f"Path does not exist: {path}"}

    history_files = list(path.glob("*_History.csv"))

    if not history_files:
        return {"error": "No History CSV files found"}

    csv_file = history_files[0]

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = [f.readline().strip() for _ in range(10)]

        return {
            "file": str(csv_file),
            "first_10_lines": lines,
            "separator": ";" if ";" in lines[0] else ","
        }
    except Exception as e:
        return {
            "error": str(e),
            "file": str(csv_file)
        }
