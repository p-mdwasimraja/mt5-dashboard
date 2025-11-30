# Quick Start Guide

## One-Command Setup

### Windows
```batch
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## What the Setup Does

1. ✓ Checks Python installation
2. ✓ Creates virtual environment
3. ✓ Installs all dependencies
4. ✓ Creates necessary directories
5. ✓ Copies configuration files
6. ✓ Makes scripts executable

## After Setup

### 1. Configure MT5 Data Sources

**Windows:**
```batch
notepad config\settings.yaml
```

**Linux/Mac:**
```bash
nano config/settings.yaml
```

Update the paths to your MT5 data:
```yaml
mt5_sources:
  - name: "Terminal1"
    path: "C:/path/to/MT5/MQL5/Files"  # Windows
    # path: "/path/to/MT5/MQL5/Files"  # Linux
    enabled: true
```

### 2. Start the Server

**Windows:**
```batch
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

### 3. Access Dashboard

Open your browser:
- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs
- System Info: http://localhost:8000/system/info

## Troubleshooting

### "Python not found"
- Install Python 3.8+ from python.org
- Make sure Python is in your PATH

### "Permission denied" (Linux/Mac)
```bash
chmod +x setup.sh start.sh
```

### "Module not found"
```bash
# Re-run setup
./setup.sh  # or setup.bat on Windows
```

### No data showing
1. Check config/settings.yaml paths are correct
2. Verify MT5 CSV files exist
3. Check logs/app.log for errors

## VPS Deployment

See README.md for detailed VPS deployment instructions including:
- systemd service setup
- Nginx configuration
- Auto-start on boot
- Performance tuning

## Project Structure

```
mt5-dashboard-api/
├── setup.sh / setup.bat    ← Run this first
├── start.sh / start.bat    ← Run this to start
├── config/
│   └── settings.yaml       ← Configure your MT5 paths here
├── app/                    ← Application code
├── logs/                   ← Log files
└── venv/                   ← Virtual environment (created by setup)
```

## Common Commands

```bash
# Setup (first time only)
./setup.sh  # or setup.bat

# Start server
./start.sh  # or start.bat

# Clear cache (after updating MT5 data)
curl -X POST http://localhost:8000/system/cache/clear

# View logs
tail -f logs/app.log  # Linux/Mac
type logs\app.log     # Windows
```

## Support

- Check logs: `logs/app.log`
- System info: http://localhost:8000/system/info
- API docs: http://localhost:8000/docs
