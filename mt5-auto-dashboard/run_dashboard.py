"""
MT5 Auto Dashboard - Main Launcher
Process data and start the web dashboard
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.data_processor import MT5DataProcessor

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("MT5 Auto Dashboard - Starting")
    print("="*60 + "\n")
    
    # Step 1: Process data
    print("Step 1: Processing MT5 data...")
    print("-" * 60)
    try:
        processor = MT5DataProcessor()
        processor.process_all_sources()
        print("\n✓ Data processing complete!")
    except Exception as e:
        print(f"\n✗ Error processing data: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    
    # Step 2: Launch dashboard
    print("Step 2: Launching web dashboard...")
    print("-" * 60)
    time.sleep(1)
    
    try:
        from web.dashboard import app, config
        host = config['dashboard']['host']
        port = config['dashboard']['port']
        debug = config['dashboard']['debug']
        
        print(f"\n✓ Dashboard starting at http://{host}:{port}")
        print("\nPress CTRL+C to stop the server")
        print("="*60 + "\n")
        
        app.run_server(host=host, port=port, debug=debug)
        
    except Exception as e:
        print(f"\n✗ Error launching dashboard: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
