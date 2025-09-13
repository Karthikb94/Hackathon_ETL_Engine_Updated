#!/usr/bin/env python3
"""
Startup script for Transformation Engine
"""

import uvicorn
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting Transformation Engine...")
    print("📁 Input directory: ../storage/input")
    print("📁 Output directory: ../storage/transformed")
    print("📁 Logs directory: ../storage/logs")
    print("🌐 API Documentation: http://localhost:8001/docs")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
