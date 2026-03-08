"""
CrisisShield AI — Agent Status API Routes
"""

from fastapi import APIRouter

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.agent_bridge import shared_state

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/status")
async def get_all_agent_statuses():
    """Get status of all agents."""
    statuses = shared_state.get_agent_statuses()
    return {"agents": statuses}


@router.get("/{agent_name}")
async def get_agent_detail(agent_name: str):
    """Get detailed status of a specific agent."""
    status = shared_state.get_agent_status(agent_name)
    if status is None:
        return {"error": f"Agent '{agent_name}' not found", "available": list(shared_state.get_agent_statuses().keys())}
    return {"agent": status}


@router.get("/rescue/units")
async def get_rescue_units():
    """Get current rescue unit deployment status."""
    units = shared_state.get_rescue_units()
    deployed = [u for u in units if u.get("status") != "standby"]
    return {
        "total_units": len(units),
        "deployed": len(deployed),
        "units": units,
    }


@router.get("/resources/inventory")
async def get_resource_inventory():
    """Get current resource inventory."""
    return {"inventory": shared_state.get_inventory()}


@router.get("/resources/allocations")
async def get_resource_allocations():
    """Get resource allocation history."""
    return {"allocations": shared_state.get_allocations()}
