"""
Startup script for the FastAPI application.

This script provides an easy way to start the FastAPI server.
"""

import uvicorn
import sys
import os

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, src_path)

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )
