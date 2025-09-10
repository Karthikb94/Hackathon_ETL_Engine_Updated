#!/usr/bin/env python3
"""
Startup script for the ETL Engine
"""
import uvicorn
import os

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.environ.get("ETL_HOST", "0.0.0.0")
    port = int(os.environ.get("ETL_PORT", "8000"))
    reload = os.environ.get("ETL_RELOAD", "true").lower() == "true"
    
    print(f"Starting ETL Engine on {host}:{port}")
    print(f"Reload mode: {reload}")
    print(f"Output directory: {os.environ.get('ETL_OUTPUT_DIR', 'output')}")
    print(f"Logs directory: {os.environ.get('ETL_LOGS_DIR', 'logs')}")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
