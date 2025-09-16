#!/usr/bin/env python3
"""
Parser Engine Runner
Simple script to start the Parser Engine with proper setup and error handling.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ ERROR: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'polars',
        'pydantic',
        'beautifulsoup4',
        'lxml',
        'pyyaml'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing dependencies...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", 
                "parsingEngine/requirements.txt"
            ])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    print("✅ All dependencies are available")
    return True

def check_directories():
    """Check if required directories exist."""
    required_dirs = [
        "storage/input",
        "storage/transformed", 
        "storage/logs",
        "storage/parsing_error"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Created directory: {dir_path}")
        else:
            print(f"✅ Directory exists: {dir_path}")
    
    return True

def check_modules():
    """Check if Parser Engine modules can be imported."""
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        import parsingEngine.app.main
        print("✅ Parser Engine modules can be imported")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Parser Engine modules: {e}")
        return False

def start_server():
    """Start the Parser Engine server."""
    print("\n" + "="*60)
    print("🚀 Starting Parser Engine Server")
    print("="*60)
    print("📁 Input directory: storage/input")
    print("📁 Output directory: storage/transformed")
    print("📁 Logs directory: storage/logs")
    print("🌐 API Documentation: http://localhost:8002/docs")
    print("🌐 Server URL: http://localhost:8002")
    print("="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        # Import uvicorn and start the server directly
        import uvicorn
        
        # Add current directory to Python path for module discovery
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Start the server with uvicorn
        uvicorn.run(
            "parsingEngine.app.main:app",
            host="0.0.0.0",
            port=8002,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main function to run the Parser Engine."""
    print("Parser Engine Startup Check")
    print("="*30)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check directories
    if not check_directories():
        return 1
    
    # Check modules
    if not check_modules():
        return 1
    
    print("\n✅ All checks passed! Starting Parser Engine...")
    time.sleep(1)
    
    # Start the server
    if start_server():
        return 0
    else:
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
