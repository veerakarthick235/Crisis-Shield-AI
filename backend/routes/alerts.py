"""
CrisisShield AI — Alert API Routes
"""

from fastapi import APIRouter

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.agent_bridge import shared_state

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
async def get_alerts():
    """Get active alerts."""
    alerts = shared_state.get_alerts()
    active = [a for a in alerts if not a.get("acknowledged")]
    return {"alerts": active, "total": len(active)}


@router.get("/history")
async def get_alert_history():
    """Get all alert history."""
    return {"alerts": shared_state.get_alerts(limit=100), "total": len(shared_state.get_alerts(limit=100))}
