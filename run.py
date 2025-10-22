#!/usr/bin/env python3
"""
Startup script for the Footfall Counter FastAPI application.
"""

import os
from pathlib import Path

import uvicorn

# Ensure required directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Copy example env file if .env doesn't exist
if not Path(".env").exists() and Path(".env.example").exists():
    import shutil

    shutil.copy(".env.example", ".env")
    print("Created .env file from .env.example")
    print("Please update the SECRET_KEY and other settings in .env file")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
