#!/usr/bin/env python3
"""
Alternative startup script for the ETL Engine that bypasses uvicorn CLI issues
"""
import asyncio
import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.environ.get("ETL_HOST", "0.0.0.0")
    port = int(os.environ.get("ETL_PORT", "8001"))
    reload = os.environ.get("ETL_RELOAD", "true").lower() == "true"
    
    print(f"Starting ETL Engine on {host}:{port}")
    print(f"Reload mode: {reload}")
    print(f"Output directory: {os.environ.get('ETL_OUTPUT_DIR', 'output')}")
    print(f"Logs directory: {os.environ.get('ETL_LOGS_DIR', 'logs')}")
    print("Press Ctrl+C to stop")
    
    # Create uvicorn config and run directly
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("\nShutting down server...")
