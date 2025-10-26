"""Demo script for Smart Clash Reporter.

This script launches the backend and frontend, then optionally
opens the browser for a quick demo.
"""
import argparse
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import streamlit
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  cd backend && pip install -r requirements.txt")
        print("  cd frontend && pip install -r requirements.txt")
        return False


def start_backend(mock_mode=True):
    """Start the FastAPI backend server."""
    print("\n🚀 Starting backend server...")
    
    backend_dir = Path(__file__).parent.parent
    env = os.environ.copy()
    
    if mock_mode:
        env["USE_MOCK"] = "true"
        print("   Mode: MOCK")
    else:
        print("   Mode: LIVE (requires APS credentials)")
    
    # Start uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    process = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Wait for server to start
    print("   Waiting for backend to start...", end="", flush=True)
    for _ in range(30):
        time.sleep(1)
        print(".", end="", flush=True)
        
        try:
            import requests
            response = requests.get("http://localhost:8000/api/health", timeout=2)
            if response.status_code == 200:
                print(" ✅")
                return process
        except:
            pass
    
    print(" ❌")
    print("Backend failed to start in time")
    return None


def start_frontend():
    """Start the Streamlit frontend."""
    print("\n🎨 Starting frontend...")
    
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    
    cmd = [
        sys.executable, "-m", "streamlit",
        "run", "streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "localhost"
    ]
    
    env = os.environ.copy()
    env["API_BASE_URL"] = "http://localhost:8000"
    
    process = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    print("   Waiting for frontend to start...", end="", flush=True)
    for _ in range(20):
        time.sleep(1)
        print(".", end="", flush=True)
        
        try:
            import requests
            response = requests.get("http://localhost:8501", timeout=2)
            if response.status_code == 200:
                print(" ✅")
                return process
        except:
            pass
    
    print(" ⚠️")
    print("   Frontend may still be starting...")
    return process


def open_browser():
    """Open browser to the application."""
    print("\n🌐 Opening browser...")
    time.sleep(2)
    webbrowser.open("http://localhost:8501")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Smart Clash Reporter Demo")
    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Use mock data (default)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use live APS data (requires credentials)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open browser"
    )
    
    args = parser.parse_args()
    
    # Banner
    print("=" * 60)
    print("  Smart Clash Reporter - Demo Launcher")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Determine mode
    mock_mode = not args.live
    
    # Start services
    backend_process = start_backend(mock_mode)
    if not backend_process:
        print("\n❌ Failed to start backend")
        sys.exit(1)
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend")
        backend_process.terminate()
        sys.exit(1)
    
    # Open browser
    if not args.no_browser:
        open_browser()
    
    # Instructions
    print("\n" + "=" * 60)
    print("✅ Smart Clash Reporter is running!")
    print("=" * 60)
    print(f"Backend API:  http://localhost:8000")
    print(f"Frontend UI:  http://localhost:8501")
    print(f"API Docs:     http://localhost:8000/docs")
    print("=" * 60)
    print("\n📝 Demo Steps:")
    print("  1. View KPIs and clash statistics")
    print("  2. Filter clashes by severity, status, or discipline")
    print("  3. Click 'Générer PDF' to create a report")
    print("  4. Download and view the PDF report")
    print("\n⚠️  Press Ctrl+C to stop all services")
    print("=" * 60)
    
    # Keep running
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ All services stopped")


if __name__ == "__main__":
    main()
