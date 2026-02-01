"""
Run the FastAPI backend server.

Usage:
    python run_api.py

Or with uvicorn directly:
    uvicorn api.main:app --reload --port 8000
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
