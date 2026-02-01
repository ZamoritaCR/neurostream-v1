"""
═══════════════════════════════════════════════════════════════════════════════
DOPAMINE.WATCH 2027 - UNIFIED SERVER
Serves both the static frontend and FastAPI backend.
═══════════════════════════════════════════════════════════════════════════════

Run with:
    python server.py

Then open:
    http://localhost:8000        - Frontend
    http://localhost:8000/api/docs - API Documentation
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from contextlib import asynccontextmanager
import logging

# Import all API routers
from api.routes import search, mr_dp, social, user, content, gamification, premium, wellness

# Try to import websocket (may have additional dependencies)
try:
    from api.routes import websocket
    from services.realtime.websocket_manager import get_websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("⚠️  WebSocket not available (missing dependencies)")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting dopamine.watch server...")

    if WEBSOCKET_AVAILABLE:
        ws_manager = get_websocket_manager()
        await ws_manager.start_background_tasks()

    yield

    logger.info("👋 Shutting down dopamine.watch server...")
    if WEBSOCKET_AVAILABLE:
        await ws_manager.stop_background_tasks()


# Create FastAPI app
app = FastAPI(
    title="dopamine.watch",
    description="ADHD-friendly streaming recommendation platform",
    version="2027.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)


# ═══════════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(mr_dp.router, prefix="/api/mr-dp", tags=["Mr.DP AI"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(gamification.router, prefix="/api/gamification", tags=["Gamification"])
app.include_router(premium.router, prefix="/api/premium", tags=["Premium"])
app.include_router(wellness.router, prefix="/api/wellness", tags=["Wellness"])

if WEBSOCKET_AVAILABLE:
    app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2027.1.0",
        "websocket": WEBSOCKET_AVAILABLE
    }


@app.get("/api/status")
async def api_status():
    """Get detailed API status."""
    return {
        "status": "operational",
        "version": "2027.1.0",
        "features": {
            "search": True,
            "mr_dp_ai": True,
            "gamification": True,
            "premium_tiers": True,
            "wellness_sos": True,
            "focus_timer": True,
            "websocket": WEBSOCKET_AVAILABLE
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STATIC FILE SERVING
# ═══════════════════════════════════════════════════════════════════════════════

# Get the parent directory (Neuronav) for static files
PARENT_DIR = Path(__file__).parent.parent


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main index.html."""
    index_path = PARENT_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the dashboard for logged-in users."""
    dashboard_path = Path(__file__).parent / "static" / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>dopamine.watch</title>
        <style>
            body { font-family: system-ui; background: #0f0f14; color: white;
                   display: flex; justify-content: center; align-items: center;
                   height: 100vh; margin: 0; }
            .container { text-align: center; }
            h1 { font-size: 3rem; margin-bottom: 1rem; }
            a { color: #7c3aed; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 dopamine.watch</h1>
            <p>Server is running!</p>
            <p><a href="/api/docs">View API Documentation</a></p>
            <p><a href="/test">Test GUI</a></p>
        </div>
    </body>
    </html>
    """)


@app.get("/test", response_class=HTMLResponse)
async def serve_test_page():
    """Serve test page with instructions to use Streamlit."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>dopamine.watch - Test GUI</title>
        <style>
            body { font-family: system-ui; background: #0f0f14; color: white;
                   padding: 40px; max-width: 800px; margin: 0 auto; }
            h1 { color: #7c3aed; }
            code { background: #1a1a24; padding: 2px 8px; border-radius: 4px; }
            pre { background: #1a1a24; padding: 20px; border-radius: 8px; overflow-x: auto; }
            .card { background: #16161d; padding: 20px; border-radius: 12px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>🧪 Test GUI</h1>
        <div class="card">
            <h3>Run the Streamlit Test GUI:</h3>
            <pre>cd /Users/zamorita/Desktop/Neuronav/dopamine_2027
streamlit run test_app.py</pre>
        </div>
        <div class="card">
            <h3>API Endpoints Available:</h3>
            <ul>
                <li><a href="/api/docs" style="color: #7c3aed;">/api/docs</a> - Interactive API Documentation</li>
                <li><a href="/api/health" style="color: #7c3aed;">/api/health</a> - Health Check</li>
                <li><a href="/api/status" style="color: #7c3aed;">/api/status</a> - Full Status</li>
            </ul>
        </div>
        <p><a href="/" style="color: #7c3aed;">← Back to Home</a></p>
    </body>
    </html>
    """)


# Serve static files from parent directory
@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files from parent directory."""
    # Security: only allow certain file extensions
    allowed_extensions = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', '.woff', '.woff2'}

    file = PARENT_DIR / file_path
    if file.exists() and file.is_file():
        if file.suffix.lower() in allowed_extensions:
            return FileResponse(file)

    # Return 404 for unknown paths
    return JSONResponse(status_code=404, content={"error": "Not found"})


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    import os

    # Railway uses PORT env var
    port = int(os.environ.get("PORT", 8000))
    is_production = os.environ.get("RAILWAY_ENVIRONMENT") is not None

    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║           🧠 dopamine.watch 2027 - API Server                 ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  Port: {port}                                                   ║
    ║  Docs: /api/docs                                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,
        log_level="info"
    )
