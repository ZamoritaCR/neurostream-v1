"""
═══════════════════════════════════════════════════════════════════════════════
DOPAMINE.WATCH 2027 - API SERVER
FastAPI-based REST API for the dopamine.watch platform.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .routes import search, mr_dp, social, user, content, websocket, gamification, premium, wellness
from services.realtime.websocket_manager import get_websocket_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting dopamine.watch API server...")

    # Initialize WebSocket manager background tasks
    ws_manager = get_websocket_manager()
    await ws_manager.start_background_tasks()

    yield

    # Shutdown
    logger.info("Shutting down dopamine.watch API server...")
    await ws_manager.stop_background_tasks()


# Create FastAPI app
app = FastAPI(
    title="dopamine.watch API",
    description="ADHD-friendly streaming recommendation API with AI-powered curation",
    version="2027.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)


# ═══════════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════════

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.middleware("http")
async def add_adhd_headers(request: Request, call_next):
    """Add ADHD-friendly response headers."""
    response = await call_next(request)
    response.headers["X-ADHD-Optimized"] = "true"
    response.headers["X-Dopamine-Version"] = "2027"
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# EXCEPTION HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Something went wrong. Don't worry, it's not you!",
            "adhd_friendly_message": "Oops! Our servers had a brain fart. Try again?"
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

# Include routers
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(mr_dp.router, prefix="/api/mr-dp", tags=["Mr.DP AI"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
app.include_router(gamification.router, prefix="/api/gamification", tags=["Gamification"])
app.include_router(premium.router, prefix="/api/premium", tags=["Premium"])
app.include_router(wellness.router, prefix="/api/wellness", tags=["Wellness"])


# ═══════════════════════════════════════════════════════════════════════════════
# ROOT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "dopamine.watch API",
        "version": "2027.1.0",
        "status": "running",
        "message": "Welcome to dopamine.watch - Your ADHD-friendly streaming companion!",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "websocket": "running",
            "mr_dp": "available"
        }
    }


@app.get("/api/status")
async def api_status():
    """Get detailed API status."""
    ws_manager = get_websocket_manager()
    ws_stats = ws_manager.get_stats()

    return {
        "status": "operational",
        "version": "2027.1.0",
        "features": {
            "search": True,
            "mr_dp_ai": True,
            "watch_parties": True,
            "direct_messaging": True,
            "user_learning": True,
            "gamification": True,
            "premium_tiers": True,
            "wellness_sos": True,
            "focus_timer": True
        },
        "statistics": {
            "active_connections": ws_stats.get("current_connections", 0),
            "online_users": ws_stats.get("online_users", 0),
            "active_rooms": ws_stats.get("active_rooms", 0)
        }
    }
