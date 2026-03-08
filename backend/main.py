"""
CrisisShield AI — Main Application Entry Point
FastAPI server with background agent orchestration.
"""

import asyncio
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.dashboard import router as dashboard_router
from routes.alerts import router as alerts_router
from routes.agents import router as agents_router

from agents.signal_watch import signal_watch_agent
from agents.risk_predict import risk_predict_agent
from agents.citizen_alert import citizen_alert_agent
from agents.rescue_coordinator import rescue_coordinator_agent
from agents.resource_supply import resource_supply_agent


app = FastAPI(
    title="CrisisShield AI",
    description="Autonomous Multi-Agent Disaster Detection & Response Coordination System",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(dashboard_router)
app.include_router(alerts_router)
app.include_router(agents_router)

# Serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


@app.get("/")
async def serve_index():
    """Serve the main dashboard page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# Mount static files
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
    if os.path.exists(os.path.join(FRONTEND_DIR, "assets")):
        app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")


async def run_agents():
    """Start all agents as concurrent tasks."""
    await asyncio.gather(
        signal_watch_agent.start(),
        risk_predict_agent.start(),
        citizen_alert_agent.start(),
        rescue_coordinator_agent.start(),
        resource_supply_agent.start(),
    )


@app.on_event("startup")
async def startup_event():
    """Launch agent system on server startup."""
    asyncio.create_task(run_agents())
    print("\n" + "=" * 60)
    print("  🛡️  CrisisShield AI — System Online")
    print("  🤖 5 Autonomous Agents Activated")
    print("  📡 Dashboard: http://localhost:8000")
    print("  📋 API Docs:  http://localhost:8000/docs")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
