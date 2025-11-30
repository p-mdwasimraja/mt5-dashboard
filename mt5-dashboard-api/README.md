# MT5 Dashboard API

Lightweight, high-performance MT5 trading dashboard built with FastAPI. Optimized for VPS deployment with minimal resource usage.

## Features

- **Performance Optimized**: Built-in caching reduces CSV read operations
- **Lightweight**: Minimal resource footprint compared to Dash
- **Fast API**: RESTful API endpoints for programmatic access
- **Server-Side Rendering**: Reduces client-side load
- **VPS Ready**: Optimized for low-resource environments
- **Auto-Discovery**: Automatically detects MT5 CSV files
- **Multi-Terminal Support**: Aggregates data from multiple MT5 terminals

## Key Improvements Over Dash

1. **5-10x Lower Memory Usage**: No WebSocket overhead
2. **Faster Page Loads**: Server-side rendering with caching
3. **Better Concurrency**: Async FastAPI handles more concurrent users
4. **API Access**: Programmatic access to all metrics
5. **Simple Deployment**: Single command startup, systemd service included

## Quick Start

### 1. Installation

```bash
# Clone or extract the project
cd mt5-dashboard-api

# Run installation script
chmod +x install.sh
./install.sh
```

### 2. Configuration

Edit `config/settings.yaml` with your MT5 data paths:

```yaml
mt5_sources:
  - name: "Terminal1"
    enabled: true
    path: "/path/to/MT5/MQL5/Files"
```

### 3. Run

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

Access the dashboard at: `http://localhost:8000`

## VPS Deployment

### Using systemd (Linux)

1. Edit `mt5-dashboard.service` with your paths and username
2. Copy to systemd directory:
   ```bash
   sudo cp mt5-dashboard.service /etc/systemd/system/
   ```
3. Enable and start:
   ```bash
   sudo systemctl enable mt5-dashboard
   sudo systemctl start mt5-dashboard
   ```
4. Check status:
   ```bash
   sudo systemctl status mt5-dashboard
   ```

### Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## API Endpoints

### Portfolio
- `GET /` - Portfolio dashboard (HTML)
- `GET /api/summary` - Portfolio summary (JSON)
- `GET /api/equity-curve` - Equity curve data (JSON)
- `GET /api/ea-breakdown` - Performance by EA (JSON)
- `GET /api/symbol-breakdown` - Performance by symbol (JSON)

### EAs
- `GET /ea/` - List all EAs
- `GET /ea/{ea_name}` - EA dashboard
- `GET /ea/api/{ea_name}/stats` - EA statistics (JSON)

### Symbols
- `GET /symbols/` - List all symbols
- `GET /symbols/{symbol}` - Symbol dashboard
- `GET /symbols/api/{symbol}/stats` - Symbol statistics (JSON)

### System
- `GET /system/health` - Health check
- `GET /system/info` - System metrics
- `GET /system/cache/stats` - Cache statistics
- `POST /system/cache/clear` - Clear cache
- `POST /system/config/reload` - Reload configuration

## Performance Tuning

### Cache Settings (.env)

```env
CACHE_TTL=300          # Cache duration in seconds
CACHE_MAX_SIZE=100     # Max items in cache
MAX_WORKERS=2          # Uvicorn workers (keep low on VPS)
```

### Manual Cache Clear

After updating MT5 data, clear cache:
```bash
curl -X POST http://localhost:8000/system/cache/clear
```

## Project Structure

```
mt5-dashboard-api/
├── app/
│   ├── core/           # Core modules (config, loader, cache)
│   ├── routers/        # API endpoints
│   ├── services/       # Business logic
│   ├── templates/      # HTML templates
│   ├── static/         # CSS, JS, images
│   └── main.py         # Application entry point
├── config/
│   └── settings.yaml   # MT5 data source configuration
├── data/               # Data directory
├── logs/               # Application logs
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── start.sh            # Startup script (Linux)
├── start.bat           # Startup script (Windows)
└── README.md           # This file
```

## Monitoring

View system metrics at `/system/info`:
- CPU and memory usage
- Disk space
- Cache statistics
- Data source counts

## Troubleshooting

### No data showing
1. Check `config/settings.yaml` paths are correct
2. Verify MT5 CSV files exist in configured paths
3. Check logs at `logs/app.log`
4. Visit `/system/info` for diagnostics

### High memory usage
1. Reduce `CACHE_MAX_SIZE` in `.env`
2. Reduce `MAX_WORKERS` to 1
3. Lower `CACHE_TTL` to reduce cache retention

### Slow performance
1. Increase `CACHE_TTL` for longer caching
2. Ensure MT5 data is on fast storage (SSD)
3. Check system resources at `/system/info`

## Development

### Run in development mode

```bash
# With auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Visit `/docs` for interactive Swagger API documentation.

## License

MIT License - See LICENSE file

## Support

For issues or questions, check the logs at `logs/app.log`
