# CLAUDE.md - AI Assistant Guide for MT5 Dashboard Repository

**Last Updated**: 2025-11-28
**Repository**: mt5-dashboard
**Purpose**: MetaTrader 5 trading performance dashboard and analytics system

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Architecture](#architecture)
3. [Component Details](#component-details)
4. [Development Setup](#development-setup)
5. [Key Conventions](#key-conventions)
6. [Common Tasks](#common-tasks)
7. [File Locations](#file-locations)
8. [Data Flow](#data-flow)
9. [Important Gotchas](#important-gotchas)

---

## Repository Overview

### Purpose
This is a monorepo containing multiple dashboard implementations for visualizing MetaTrader 5 (MT5) trading performance. The system reads MT5 trading data exported as CSV files and provides interactive web dashboards to analyze trading performance across multiple Expert Advisors (EAs), trading pairs, and accounts.

### Target Users
- Forex/CFD traders using MT5 Expert Advisors
- Traders managing multiple MT5 accounts
- Quantitative traders needing performance analytics

### Key Features
- Multi-account portfolio aggregation
- Per-EA performance analysis
- Symbol/trading pair analytics
- Equity curve visualization
- Risk metrics and insights
- Automated data export from MT5

---

## Architecture

### Monorepo Structure

```
mt5-dashboard/
├── fastapi_app/          # Lightweight FastAPI dashboard
├── mt5-auto-dashboard/   # Feature-rich Dash dashboard
└── mt5-dashboard-api/    # Placeholder (empty/future API component)
```

### Component Comparison

| Feature | fastapi_app | mt5-auto-dashboard |
|---------|-------------|-------------------|
| Framework | FastAPI + Jinja2 | Plotly Dash |
| UI Complexity | Simple, template-based | Rich, interactive components |
| Port | 8010 | 8050 |
| Best For | Quick overview, minimal resources | Deep analysis, advanced features |
| Dependencies | Minimal | Bootstrap components, advanced charts |
| Tabs/Views | 3 (Portfolio, EA, Symbols) | 6 (Overview, Analysis, Stats, EA, Pairs, Date Range) |

### Data Flow

```
MT5 Trading Terminal
    ↓
MQL5 Export Scripts (AdvancedAutoExport.mq5 / QuickExport.mq5)
    ↓
CSV Files (Terminal/MQL5/Files/MT5_Data/)
    ↓
Data Processor (Python - reads and normalizes)
    ↓
Processed Data (data/processed/ - organized by EA)
    ↓
Dashboard (FastAPI or Dash - visualizes)
    ↓
User Browser (http://localhost:8010 or :8050)
```

---

## Component Details

### 1. fastapi_app (Lightweight Dashboard)

**Technology Stack**:
- FastAPI 0.110.0+ (web framework)
- Uvicorn (ASGI server)
- Jinja2 (templating)
- Pandas + Plotly (data + visualization)

**Directory Structure**:
```
fastapi_app/
├── app/
│   ├── core/
│   │   ├── config.py       # YAML config loader
│   │   └── loader.py       # CSV data loader & normalizer
│   ├── routers/
│   │   ├── portfolio.py    # Portfolio routes
│   │   ├── ea.py          # EA performance routes
│   │   └── symbols.py     # Symbol performance routes
│   ├── services/
│   │   ├── portfolio_service.py  # Business logic: portfolio stats
│   │   ├── ea_service.py         # Business logic: EA analytics
│   │   └── symbol_service.py     # Business logic: symbol analytics
│   ├── templates/          # Jinja2 HTML templates
│   ├── static/            # CSS, JS assets
│   └── main.py            # FastAPI app entry point
├── config/
│   └── settings.yaml      # Configuration
├── requirements.txt
├── setup_fastapi.bat      # Windows setup
└── start_fastapi.bat      # Windows startup (port 8010)
```

**Entry Point**: `app/main.py`
- Creates FastAPI app
- Mounts static files at `/static`
- Includes routers for portfolio, EA, symbols
- Health check at `/health`

**Configuration**: `config/settings.yaml`
```yaml
app:
  name: "MT5 Trading Dashboard"
  version: "1.0.0"
  debug: true

paths:
  raw_data: "data/raw"
  processed_data: "data/processed"
  backup_data: "data/backup"
  logs: "logs"

mt5_sources:
  - name: "Terminal1"
    path: "path/to/MT5/Terminal/MQL5/Files/MT5_Data"
    enabled: true
    description: "Main Trading Account"
```

**API Endpoints**:
- `GET /` - Portfolio overview with equity curve
- `GET /debug_paths` - Debug MT5 data source paths
- `GET /debug_first_rows` - View sample data
- `GET /ea/performance` - EA performance table
- `GET /symbols/performance` - Symbol performance table

**Startup Command**:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8010 --workers 1
```

---

### 2. mt5-auto-dashboard (Feature-Rich Dashboard)

**Technology Stack**:
- Dash 2.14.0+ (interactive web apps)
- dash-bootstrap-components (UI)
- dash-table (data tables)
- Pandas + Plotly (data + charts)

**Directory Structure**:
```
mt5-auto-dashboard/
├── MQL5/                      # MetaTrader scripts
│   ├── Experts/
│   │   └── AdvancedAutoExport.mq5  # Auto-export EA
│   └── Scripts/
│       └── QuickExport.mq5         # Manual export script
├── config/
│   └── settings.yaml          # Main configuration
├── src/
│   ├── core/
│   │   └── data_processor.py  # MT5 data processing pipeline
│   ├── web/
│   │   ├── dashboard.py       # Main Dash app
│   │   ├── callbacks/
│   │   │   └── main_callbacks.py  # Interactive callbacks
│   │   ├── layout/
│   │   │   ├── navbar.py
│   │   │   └── tabs.py        # Tab layouts
│   │   └── components/        # UI components (11 files)
│   │       ├── summary_cards.py
│   │       ├── profit_chart.py
│   │       ├── ea_performance.py
│   │       └── ...
│   └── utils/
│       ├── config.py          # Config loader
│       └── helpers.py
├── data/
│   ├── processed/             # Processed data output
│   └── Dummy_Data_dir/        # Sample MT5 data
├── requirements.txt
├── start_dashboard.py         # Main entry point
├── setup_windows.bat          # Windows setup
├── start_dashboard.bat        # Windows startup
├── setup.sh                   # Linux setup
├── DEPLOYMENT_GUIDE.md        # Production deployment
└── WINDOWS_QUICKSTART.md      # Quick start guide
```

**Entry Point**: `start_dashboard.py`
```python
# Sets environment variable
os.environ['JUPYTER_PLATFORM_DIRS'] = '0'

# 1. Process MT5 data
processor = MT5DataProcessor(config_path)
processor.run()

# 2. Launch dashboard
from src.web.dashboard import app
app.run_server(host=host, port=port, debug=debug)
```

**Dashboard Tabs**:
1. **Overview**: Summary cards, EA table, cumulative profit, risk insights
2. **Analysis**: Date range filter, EA/Symbol filters, equity curves, trade table
3. **Performance Stats**: Yearly/monthly performance breakdown, recent 14-day stats
4. **EA Performance**: Per-EA filtering, statistics, equity curves, win/loss charts
5. **Trading Pair Performance**: Per-symbol analysis, profit breakdown
6. **Date Range Performance**: Custom date range with KPIs and filtered data

**Auto-Refresh**:
- UI refresh: 5 seconds (configurable)
- Data reprocessing: 5 minutes (configurable)

**Data Processor** (`src/core/data_processor.py`):
- Reads 3 CSV file types: `*_Account.csv`, `*_History.csv`, `*_Positions.csv`
- Separates deposits (Type='BALANCE') from actual trades
- Outputs organized by EA name to `data/processed/`
- Creates summary files: `all_transactions_latest.csv`, `stats.json`, etc.

**MQL5 Scripts**:

**AdvancedAutoExport.mq5** (Expert Advisor):
- Runs continuously on MT5 chart
- Auto-exports at intervals (default: 30 minutes)
- Configurable EA name, export path, intervals
- Exports: account info, positions, complete history

**QuickExport.mq5** (Script):
- One-time manual export
- Drag onto chart to execute
- Useful for immediate data refresh

**CSV Format**:
- Separator: `;` (semicolon)
- History columns: `EA_Name;TimeOpen;TimeClose;DealOpen;DealClose;Symbol;Type;Volume;PriceOpen;PriceClose;Profit;Swap;Commission;Duration;Comment`
- Account columns: `EA_Name;Timestamp;Balance;Equity;Margin;FreeMargin;MarginLevel;Profit;Currency;Server;Leverage`

---

### 3. mt5-dashboard-api (Future Component)

**Status**: Empty/placeholder - not actively developed
**Purpose**: Likely intended for REST/GraphQL API layer

---

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- MT5 Terminal (for data generation)
- Windows or Linux OS

### Setup Process (Windows)

**FastAPI Dashboard**:
```bash
# 1. Setup
setup_fastapi.bat

# 2. Configure MT5 paths
# Edit: fastapi_app/config/settings.yaml

# 3. Start dashboard
start_fastapi.bat

# 4. Access
# http://localhost:8010
```

**Dash Dashboard**:
```bash
# 1. Setup
cd mt5-auto-dashboard
setup_windows.bat

# 2. Configure MT5 paths
# Edit: config/settings.yaml

# 3. Start dashboard
start_dashboard.bat

# 4. Access
# http://localhost:8050
```

### Setup Process (Linux/VPS)

```bash
# 1. Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 2. Choose component and navigate
cd mt5-auto-dashboard  # or fastapi_app

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Configure
nano config/settings.yaml  # Edit MT5 source paths

# 7. Run
python start_dashboard.py  # or uvicorn app.main:app --host 127.0.0.1 --port 8010
```

### Configuration File (settings.yaml)

**Critical Settings**:
```yaml
mt5_sources:
  - name: "MyAccount"
    path: "/path/to/MT5/Terminal/MQL5/Files/MT5_Data"
    enabled: true
    description: "Main account description"
```

**Path Notes**:
- Absolute paths recommended
- Windows: `C:/Users/.../Terminal/MQL5/Files/MT5_Data`
- Linux/Wine: `/home/user/.wine/drive_c/.../Terminal/MQL5/Files/MT5_Data`
- Multiple sources supported (array of objects)

---

## Key Conventions

### Code Style

**Python**:
- Follow PEP 8 conventions
- Use absolute imports from project root
- Type hints encouraged but not enforced
- Docstrings for complex functions

**Imports Organization**:
```python
# 1. Standard library
import os
from pathlib import Path

# 2. Third-party
import pandas as pd
from fastapi import FastAPI

# 3. Local modules
from app.core.config import load_config
from app.services.portfolio_service import PortfolioService
```

### Data Standards

**CSV Format**:
- **Separator**: Always `;` (semicolon)
- **Encoding**: UTF-8
- **Date Format**: `YYYY.MM.DD HH:MM:SS`
- **Decimal Places**: 2 for money, 5 for prices

**Trade Types**:
- `BUY` / `SELL`: Regular trades
- `BALANCE`: Deposits/withdrawals
- `CREDIT`: Broker credits
- Filter out non-trades (BALANCE, CREDIT) for P&L calculations

**Column Names** (standardized):
- `EA_Name`: Expert Advisor identifier
- `Symbol`: Trading pair (e.g., EURUSD)
- `Type`: Trade type
- `Profit`: Net profit (includes swap + commission)
- `TimeOpen` / `TimeClose`: Trade timestamps

### Error Handling

**Pattern**:
```python
try:
    # File operations
    df = pd.read_csv(file_path, sep=';')
except FileNotFoundError:
    logger.warning(f"File not found: {file_path}")
    return pd.DataFrame()  # Return empty DataFrame
except Exception as e:
    logger.error(f"Error processing {file_path}: {e}")
    return pd.DataFrame()
```

**Principles**:
- Graceful degradation (return empty data, not crash)
- Log errors for debugging
- Use fallback defaults
- Validate data before processing

### Configuration Management

**Loading Pattern**:
```python
from pathlib import Path
import yaml

config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
```

**Access Pattern**:
```python
app_name = config.get('app', {}).get('name', 'MT5 Dashboard')
mt5_sources = config.get('mt5_sources', [])
```

### Logging

**Setup**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**Usage**:
- `logger.debug()`: Detailed diagnostic info
- `logger.info()`: General informational messages
- `logger.warning()`: Warning but not critical
- `logger.error()`: Error that affects functionality

---

## Common Tasks

### Task 1: Add a New Endpoint (FastAPI)

1. **Create route function** in `fastapi_app/app/routers/`:
```python
# app/routers/new_feature.py
from fastapi import APIRouter
from app.services.new_service import NewService

router = APIRouter()

@router.get("/new-feature")
async def get_new_feature():
    service = NewService()
    data = service.get_data()
    return {"data": data}
```

2. **Create service** in `fastapi_app/app/services/`:
```python
# app/services/new_service.py
class NewService:
    def get_data(self):
        # Business logic
        return processed_data
```

3. **Register router** in `app/main.py`:
```python
from app.routers import new_feature

app.include_router(new_feature.router, prefix="/api", tags=["new"])
```

### Task 2: Add a New Dashboard Tab (Dash)

1. **Create layout** in `mt5-auto-dashboard/src/web/layout/tabs.py`:
```python
def create_new_tab_layout():
    return dbc.Container([
        dbc.Row([...]),
        # Your components
    ])
```

2. **Create component** in `src/web/components/new_component.py`:
```python
def create_new_component(data):
    return dbc.Card([...])
```

3. **Add callback** in `src/web/callbacks/main_callbacks.py`:
```python
@app.callback(
    Output('new-output-id', 'children'),
    Input('new-input-id', 'value')
)
def update_new_component(input_value):
    # Process and return updated component
    return updated_component
```

4. **Register tab** in `src/web/dashboard.py`:
```python
from src.web.layout.tabs import create_new_tab_layout

tabs = dbc.Tabs([
    # Existing tabs...
    dbc.Tab(create_new_tab_layout(), label="New Feature", tab_id="new-tab"),
])
```

### Task 3: Add Support for New MT5 Data File Type

1. **Update data processor** (`src/core/data_processor.py`):
```python
def process_new_file_type(self):
    pattern = f"*_NewType.csv"
    files = list(source_path.glob(pattern))

    for file in files:
        df = pd.read_csv(file, sep=';')
        # Process data
        output_path = self.processed_dir / "new_type" / f"{ea_name}_new.csv"
        df.to_csv(output_path, sep=';', index=False)
```

2. **Call in main run method**:
```python
def run(self):
    self.process_accounts()
    self.process_history()
    self.process_positions()
    self.process_new_file_type()  # Add this
```

3. **Update loader** to read new data type in dashboards

### Task 4: Add New Calculated Metric

**Example: Sharpe Ratio**

1. **Add calculation** in service layer:
```python
# app/services/portfolio_service.py (or mt5-auto-dashboard equivalent)
def calculate_sharpe_ratio(self, df, risk_free_rate=0.0):
    """Calculate Sharpe ratio from trade data"""
    if df.empty:
        return 0

    # Daily returns
    df['Date'] = pd.to_datetime(df['TimeClose']).dt.date
    daily_returns = df.groupby('Date')['Profit'].sum()

    # Sharpe calculation
    mean_return = daily_returns.mean()
    std_return = daily_returns.std()

    if std_return == 0:
        return 0

    sharpe = (mean_return - risk_free_rate) / std_return
    return round(sharpe, 2)
```

2. **Use in view/template**:
```python
# FastAPI
sharpe = service.calculate_sharpe_ratio(trade_data)
return templates.TemplateResponse("portfolio.html", {
    "sharpe_ratio": sharpe
})

# Dash
sharpe = calculate_sharpe_ratio(df)
dbc.Card([
    html.H4("Sharpe Ratio"),
    html.P(f"{sharpe}")
])
```

### Task 5: Debugging Data Loading Issues

**Steps**:

1. **Check MT5 source paths**:
```bash
# FastAPI
curl http://localhost:8010/debug_paths

# Or check logs
tail -f logs_fastapi.txt
```

2. **Verify CSV files exist**:
```bash
ls -la "/path/to/MT5/Terminal/MQL5/Files/MT5_Data/"
# Should see: *_Account.csv, *_History.csv, *_Positions.csv
```

3. **Check CSV format**:
```bash
head -n 2 Terminal/MQL5/Files/MT5_Data/*_History.csv
# Verify semicolon separator and expected columns
```

4. **Test data loading**:
```python
# In Python REPL
import pandas as pd
df = pd.read_csv('path/to/file.csv', sep=';')
print(df.head())
print(df.columns)
```

5. **Enable debug mode**:
```yaml
# config/settings.yaml
app:
  debug: true
```

---

## File Locations

### Configuration Files
- **FastAPI**: `/home/user/mt5-dashboard/fastapi_app/config/settings.yaml`
- **Dash**: `/home/user/mt5-dashboard/mt5-auto-dashboard/config/settings.yaml`

### Entry Points
- **FastAPI**: `/home/user/mt5-dashboard/fastapi_app/app/main.py`
- **Dash**: `/home/user/mt5-dashboard/mt5-auto-dashboard/start_dashboard.py`

### Data Processing
- **Dash Processor**: `/home/user/mt5-dashboard/mt5-auto-dashboard/src/core/data_processor.py`
- **FastAPI Loader**: `/home/user/mt5-dashboard/fastapi_app/app/core/loader.py`

### Templates (FastAPI)
- **Base**: `/home/user/mt5-dashboard/fastapi_app/app/templates/base.html`
- **Portfolio**: `/home/user/mt5-dashboard/fastapi_app/app/templates/portfolio.html`
- **EA**: `/home/user/mt5-dashboard/fastapi_app/app/templates/ea_performance.html`
- **Symbols**: `/home/user/mt5-dashboard/fastapi_app/app/templates/symbol_performance.html`

### MQL5 Scripts
- **Auto Export EA**: `/home/user/mt5-dashboard/mt5-auto-dashboard/MQL5/Experts/AdvancedAutoExport.mq5`
- **Manual Export**: `/home/user/mt5-dashboard/mt5-auto-dashboard/MQL5/Scripts/QuickExport.mq5`

### Documentation
- **Deployment Guide**: `/home/user/mt5-dashboard/mt5-auto-dashboard/DEPLOYMENT_GUIDE.md`
- **Windows Quick Start**: `/home/user/mt5-dashboard/mt5-auto-dashboard/WINDOWS_QUICKSTART.md`
- **FastAPI README**: `/home/user/mt5-dashboard/fastapi_app/README.md`
- **Dash README**: `/home/user/mt5-dashboard/mt5-auto-dashboard/README.md`

### Requirements
- **FastAPI**: `/home/user/mt5-dashboard/fastapi_app/requirements.txt`
- **Dash**: `/home/user/mt5-dashboard/mt5-auto-dashboard/requirements.txt`

---

## Data Flow

### 1. Data Generation (MT5 Terminal)

**Automated** (AdvancedAutoExport.mq5):
```
MT5 Terminal (running EA)
    → Every 30 minutes (configurable)
    → Exports to: Terminal/MQL5/Files/MT5_Data/
    → Creates: {EA_Name}_Account.csv, {EA_Name}_History.csv, {EA_Name}_Positions.csv
```

**Manual** (QuickExport.mq5):
```
User drags script to chart
    → One-time export
    → Same location and format as automated
    → Includes timestamp in filename
```

### 2. Data Processing (Python)

**Dash Dashboard**:
```python
# start_dashboard.py calls:
processor = MT5DataProcessor(config_path)
processor.run()

# Which does:
1. Reads all *_History.csv from configured MT5 sources
2. Separates deposits (Type='BALANCE') from trades
3. Normalizes timestamps and data types
4. Saves to data/processed/:
   - accounts/{EA_Name}_account.csv
   - deposits/{EA_Name}_deposits.csv
   - transactions/{EA_Name}_transactions.csv
   - positions/{EA_Name}_positions.csv
   - summary/all_transactions_latest.csv
   - summary/stats.json
```

**FastAPI Dashboard**:
```python
# app/core/loader.py:
def load_trade_data():
    # Reads directly from MT5 source paths
    # Merges multiple sources
    # Returns normalized DataFrame
```

### 3. Data Consumption (Dashboard)

**On Page Load**:
```
User accesses dashboard
    → Dashboard loads processed data
    → Calculates metrics (win rate, profit, etc.)
    → Generates charts (Plotly)
    → Renders HTML/components
```

**Auto Refresh** (Dash only):
```
Every 5 seconds:
    → UI refresh (reload data from files)

Every 5 minutes:
    → Re-run data processor
    → Pick up new MT5 exports
```

---

## Important Gotchas

### 1. Port Conflicts
- **FastAPI uses port 8010** (not 8000) to avoid conflicts
- **Dash uses port 8050**
- If port in use: `OSError: [Errno 98] Address already in use`
- **Solution**: Change port in config or kill existing process

### 2. CSV Separator
- **ALWAYS use semicolon** (`;`) not comma
- MT5 exports use `;` because prices/comments may contain commas
- **Wrong**: `pd.read_csv(file)`
- **Correct**: `pd.read_csv(file, sep=';')`

### 3. BALANCE vs TRADE Types
- `Type='BALANCE'` are deposits/withdrawals, NOT trades
- **Must filter out** for P&L calculations
- Example: `df = df[df['Type'].isin(['BUY', 'SELL'])]`
- Otherwise metrics (win rate, profit) will be wrong

### 4. Path Configuration
- **Absolute paths recommended** in `settings.yaml`
- Relative paths may fail depending on working directory
- Windows: Use forward slashes `/` or escaped backslashes `\\`
- **Bad**: `C:\Users\Trader\MT5\...`
- **Good**: `C:/Users/Trader/MT5/...` or `C:\\Users\\Trader\\MT5\\...`

### 5. Virtual Environment
- **Always activate venv** before running
- Without venv, dependencies may not be found
- Windows: `venv\Scripts\activate`
- Linux: `source venv/bin/activate`

### 6. Empty Data Handling
- Always check `if df.empty:` before calculations
- Return sensible defaults (0, empty string, etc.)
- **Don't let empty DataFrames crash calculations**

### 7. Timezone Issues
- MT5 exports are in broker timezone
- May need to convert for consistent analysis
- Document timezone assumptions in comments

### 8. File Encoding
- MT5 may export in different encodings
- If seeing weird characters: try `encoding='utf-8-sig'` or `'latin1'`
- Example: `pd.read_csv(file, sep=';', encoding='utf-8-sig')`

### 9. Profit Calculation
- `Profit` column is NET (includes swap + commission)
- Don't double-count swap/commission
- For gross profit: `Profit - Swap - Commission` (but usually want net)

### 10. Multi-Account Aggregation
- When merging multiple MT5 sources, ensure EA_Name is unique
- Or add account identifier to EA_Name
- Avoid duplicate EA names across accounts

### 11. Dashboard Not Updating
- **Dash**: Check auto-refresh interval settings
- Verify MT5 is actually exporting new data
- Check file timestamps: `ls -lt Terminal/MQL5/Files/MT5_Data/`
- Clear browser cache if stale data shown

### 12. MQL5 Script Installation
- Scripts go in: `Terminal/MQL5/Experts/` or `Terminal/MQL5/Scripts/`
- Must compile in MetaEditor (F7)
- Check MT5 logs for export errors
- Verify write permissions on MT5 Files directory

---

## Testing

### Current State
- **No unit tests** found in repository
- **No integration tests**
- Testing is manual

### Recommendations for Future Tests

**Unit Tests**:
```python
# tests/test_services.py
def test_portfolio_service_win_rate():
    df = pd.DataFrame({
        'Type': ['BUY', 'SELL', 'BUY'],
        'Profit': [100, -50, 75]
    })
    service = PortfolioService()
    win_rate = service.calculate_win_rate(df)
    assert win_rate == 66.67  # 2 wins out of 3 trades
```

**Integration Tests**:
```python
# tests/test_integration.py
def test_data_processor_end_to_end():
    # Test with dummy CSV files
    processor = MT5DataProcessor('config/test_settings.yaml')
    processor.run()

    # Verify output files created
    assert (processed_dir / 'summary' / 'stats.json').exists()
```

**API Tests** (FastAPI):
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_portfolio_endpoint():
    response = client.get("/")
    assert response.status_code == 200
```

---

## Deployment

### Development
- Run locally with `start_dashboard.bat` or `start_fastapi.bat`
- Access at `http://localhost:8050` or `http://localhost:8010`

### Production (Linux VPS)

**See**: `/home/user/mt5-dashboard/mt5-auto-dashboard/DEPLOYMENT_GUIDE.md`

**Key Steps**:
1. Install Python 3.8+
2. Create systemd service for auto-start
3. Configure NGINX reverse proxy
4. Setup SSL/TLS with Let's Encrypt
5. Configure firewall (UFW)
6. Optional: Basic auth for security

**Systemd Service Example**:
```ini
[Unit]
Description=MT5 Dashboard
After=network.target

[Service]
User=trader
WorkingDirectory=/home/trader/mt5-auto-dashboard
ExecStart=/home/trader/mt5-auto-dashboard/venv/bin/python start_dashboard.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Security Considerations

### Current Security Posture
- **No authentication** by default
- Assumes trusted network (localhost or VPN)
- Sensitive trading data exposed if publicly accessible

### Recommendations
1. **Never expose directly to internet** without auth
2. Use VPN or SSH tunnel for remote access
3. Implement basic auth (NGINX or app-level)
4. Use HTTPS/SSL in production
5. Restrict firewall rules to known IPs
6. Regularly update dependencies (security patches)

### Basic Auth (NGINX)
```nginx
location / {
    auth_basic "MT5 Dashboard";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8050;
}
```

---

## Performance Optimization

### Current Bottlenecks
- File I/O (reading large CSV files repeatedly)
- No caching layer
- Full data reprocessing every 5 minutes

### Optimization Ideas
1. **Caching**: Cache processed DataFrames in memory
2. **Database**: Migrate from CSV to PostgreSQL/SQLite
3. **Incremental Processing**: Only process new trades, not full history
4. **Compression**: Compress old data files
5. **Lazy Loading**: Load data on-demand per tab/view
6. **Workers**: Use multiple Uvicorn workers for FastAPI

---

## Future Enhancements

### Planned (Inferred from Structure)
- **mt5-dashboard-api**: REST/GraphQL API layer
- Separate backend/frontend architecture
- Real-time WebSocket updates
- Mobile-responsive design improvements

### Suggested Additions
- **Backtesting integration**: Compare live vs backtest results
- **Alerts**: Email/Telegram notifications for milestones
- **Risk management**: Position sizing recommendations
- **ML insights**: Predict EA performance trends
- **Export reports**: PDF/Excel report generation
- **Multi-currency**: Support for non-USD accounts
- **Correlation analysis**: EA and symbol correlation matrices

---

## Contact & Support

### Repository Owner
- GitHub: p-mdwasimraja/mt5-dashboard

### Issues
- Check existing documentation first
- Review DEPLOYMENT_GUIDE.md and WINDOWS_QUICKSTART.md
- File issues on GitHub with:
  - Python version
  - OS and version
  - Error logs
  - Steps to reproduce

### Contributing
- Fork repository
- Create feature branch
- Follow existing code conventions
- Test thoroughly
- Submit pull request with clear description

---

## Appendix: Quick Reference

### Startup Commands

```bash
# FastAPI Dashboard
cd /home/user/mt5-dashboard/fastapi_app
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --host 127.0.0.1 --port 8010

# Dash Dashboard
cd /home/user/mt5-dashboard/mt5-auto-dashboard
source venv/bin/activate
python start_dashboard.py
```

### Key Configuration Paths
- FastAPI: `fastapi_app/config/settings.yaml`
- Dash: `mt5-auto-dashboard/config/settings.yaml`

### Default Ports
- FastAPI: 8010
- Dash: 8050

### Data Locations
- MT5 Export: `Terminal/MQL5/Files/MT5_Data/`
- Processed: `data/processed/`
- Logs: `logs/` or `logs_fastapi.txt`

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in config or kill process: `kill $(lsof -t -i:8050)` |
| No data showing | Check MT5 source paths in settings.yaml |
| Import errors | Activate virtual environment |
| CSV parsing errors | Verify semicolon separator |
| Wrong metrics | Filter out BALANCE type trades |
| Dashboard not updating | Check MT5 export script is running |

---

**End of CLAUDE.md**

This guide should be updated whenever:
- New components are added
- Major architectural changes occur
- New conventions are established
- Common issues are discovered
- Deployment procedures change
