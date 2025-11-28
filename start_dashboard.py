"""
Simple startup script for MT5 Dashboard
Sets environment variables before importing modules
"""
import os
import sys

# Set environment variables BEFORE any imports
os.environ['JUPYTER_PLATFORM_DIRS'] = '0'

# Add src to path
sys.path.insert(0, 'src')

# Now import and run
if __name__ == '__main__':
    print("\n" + "="*60)
    print("MT5 Auto Dashboard - Starting")
    print("="*60 + "\n")
    
    # Import and run data processor
    print("Processing MT5 data...")
    from core.data_processor import MT5DataProcessor
    processor = MT5DataProcessor()
    processor.process_all_sources()
    print("\n✓ Data processing complete!\n")
    
    print("="*60)
    print("Launching web dashboard...")
    print("="*60 + "\n")
    
    # Import and run dashboard
    from web.dashboard import app, config
    host = config['dashboard']['host']
    port = config['dashboard']['port']
    
    print(f"Dashboard URL: http://{host}:{port}")
    print("\nPress CTRL+C to stop the server\n")
    
    app.run(host=host, port=port, debug=False)
