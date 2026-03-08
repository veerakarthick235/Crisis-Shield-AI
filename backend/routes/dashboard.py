"""
CrisisShield AI — Dashboard API Routes
"""

from fastapi import APIRouter

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.agent_bridge import shared_state
from services.data_simulator import simulator

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview")
async def get_overview():
    """Get aggregated dashboard overview stats."""
    return shared_state.get_overview()


@router.get("/signals")
async def get_signals():
    """Get latest disaster signals detected by SignalWatch."""
    return {"signals": shared_state.get_signals()}


@router.get("/risk-zones")
async def get_risk_zones():
    """Get current risk zone assessments from RiskPredict."""
    return {"risk_zones": shared_state.get_risk_zones()}


@router.get("/weather")
async def get_weather():
    """Get current simulated weather data for all regions."""
    return {"data": simulator.get_all_regions_data()}


@router.get("/events")
async def get_events():
    """Get recent event log."""
    return {"events": shared_state.get_events()}
