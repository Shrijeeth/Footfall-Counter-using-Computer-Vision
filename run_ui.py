#!/usr/bin/env python3
"""
Startup script to run both FastAPI backend and Streamlit frontend
"""

import signal
import subprocess
import sys
import time
from threading import Thread


def run_fastapi():
    """Run FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ FastAPI server failed: {e}")
    except KeyboardInterrupt:
        print("🛑 FastAPI server stopped")


def run_streamlit():
    """Run Streamlit app"""
    print("🎨 Starting Streamlit UI...")
    time.sleep(3)  # Wait for FastAPI to start
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "streamlit_app.py",
                "--server.port",
                "8501",
                "--server.address",
                "0.0.0.0",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit app failed: {e}")
    except KeyboardInterrupt:
        print("🛑 Streamlit app stopped")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down services...")
    sys.exit(0)


def main():
    """Main function to run both services"""
    print("🏃‍♂️ Starting Footfall Counter Application...")
    print("📡 FastAPI will be available at: http://localhost:8000")
    print("🎨 Streamlit UI will be available at: http://localhost:8501")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both services\n")

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Start FastAPI in a separate thread
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Start Streamlit in main thread
    try:
        run_streamlit()
    except KeyboardInterrupt:
        print("\n🛑 Application stopped")


if __name__ == "__main__":
    main()
