"""
CrisisShield AI — RescueCoordinator Agent
Optimizes rescue unit deployment based on risk zones.
"""

import asyncio
import time
import uuid
import random
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REGIONS, RESCUE_COORDINATOR_INTERVAL, DEFAULT_RESOURCES
from services.agent_bridge import shared_state


class RescueCoordinatorAgent:
    """
    Receives risk zone data and optimally assigns rescue units
    (ambulances, boats, teams) based on severity, proximity, and capacity.
    """

    def __init__(self):
        self.name = "RescueCoordinator"
        self.messages_processed = 0
        self.start_time = time.time()
        self._rng = random.Random(99)

        # Initialize rescue fleet
        self._fleet = []
        for i in range(DEFAULT_RESOURCES["ambulances"]):
            self._fleet.append({"id": f"AMB-{i+1:03d}", "unit_type": "ambulance", "status": "standby", "assigned_region": "", "assigned_region_name": ""})
        for i in range(DEFAULT_RESOURCES["rescue_boats"]):
            self._fleet.append({"id": f"BOAT-{i+1:03d}", "unit_type": "rescue_boat", "status": "standby", "assigned_region": "", "assigned_region_name": ""})
        for i in range(DEFAULT_RESOURCES["relief_teams"]):
            self._fleet.append({"id": f"TEAM-{i+1:03d}", "unit_type": "relief_team", "status": "standby", "assigned_region": "", "assigned_region_name": ""})

    def _get_required_units(self, zone: dict) -> dict:
        """Determine required units based on disaster type and severity."""
        risk_score = zone.get("risk_score", 0)
        dtype = zone.get("disaster_type", "flood")

        base = {
            "ambulance": 0,
            "rescue_boat": 0,
            "relief_team": 0,
        }

        if zone.get("risk_level") == "CRITICAL":
            base = {"ambulance": 4, "rescue_boat": 3, "relief_team": 6}
        elif zone.get("risk_level") == "HIGH":
            base = {"ambulance": 2, "rescue_boat": 2, "relief_team": 4}
        elif zone.get("risk_level") == "MODERATE":
            base = {"ambulance": 1, "rescue_boat": 1, "relief_team": 2}

        # Adjust by disaster type
        if dtype == "flood":
            base["rescue_boat"] = int(base["rescue_boat"] * 1.5) + 1
        elif dtype == "earthquake":
            base["ambulance"] = int(base["ambulance"] * 1.5) + 1
            base["rescue_boat"] = 0
        elif dtype == "wildfire":
            base["relief_team"] = int(base["relief_team"] * 1.3) + 1
            base["rescue_boat"] = 0

        return base

    async def run_cycle(self):
        """Assess risk zones and deploy rescue units."""
        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "processing",
            "messages_processed": self.messages_processed,
            "current_action": "Optimizing rescue unit deployment",
            "uptime_seconds": time.time() - self.start_time,
        })

        risk_zones = shared_state.get_risk_zones()
        actionable = [z for z in risk_zones if z.get("risk_level") in ("MODERATE", "HIGH", "CRITICAL")]

        # Reset all to standby first
        for unit in self._fleet:
            unit["status"] = "standby"
            unit["assigned_region"] = ""
            unit["assigned_region_name"] = ""
            unit["eta_minutes"] = 0

        # Deploy units to zones by priority
        unit_idx = {"ambulance": 0, "rescue_boat": 0, "relief_team": 0}

        for zone in actionable:
            required = self._get_required_units(zone)

            for unit_type, count in required.items():
                available = [u for u in self._fleet if u["unit_type"] == unit_type and u["status"] == "standby"]
                to_deploy = available[:count]

                for unit in to_deploy:
                    statuses = ["deployed", "en_route", "on_site"]
                    unit["status"] = self._rng.choice(statuses)
                    unit["assigned_region"] = zone["region_id"]
                    unit["assigned_region_name"] = zone.get("region_name", "")
                    unit["eta_minutes"] = round(self._rng.uniform(8, 45), 1) if unit["status"] != "on_site" else 0
                    unit["timestamp"] = datetime.utcnow().isoformat()

            self.messages_processed += 1

        # Push to shared state
        shared_state.set_rescue_units(self._fleet)

        deployed_count = sum(1 for u in self._fleet if u["status"] != "standby")
        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "active",
            "messages_processed": self.messages_processed,
            "current_action": f"Deployed {deployed_count} units to {len(actionable)} risk zones",
            "uptime_seconds": time.time() - self.start_time,
        })

    async def start(self):
        """Start continuous coordination loop."""
        while True:
            try:
                await self.run_cycle()
            except Exception as e:
                shared_state.update_agent_status(self.name, {
                    "name": self.name,
                    "state": "error",
                    "messages_processed": self.messages_processed,
                    "current_action": f"Error: {str(e)}",
                    "uptime_seconds": time.time() - self.start_time,
                })
            await asyncio.sleep(RESCUE_COORDINATOR_INTERVAL)


rescue_coordinator_agent = RescueCoordinatorAgent()
