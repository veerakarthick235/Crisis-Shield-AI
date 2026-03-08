"""
CrisisShield AI — ResourceSupply Agent
Manages emergency supplies and routes resources to risk zones.
"""

import asyncio
import time
import uuid
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REGIONS, RESOURCE_SUPPLY_INTERVAL, DEFAULT_RESOURCES
from services.agent_bridge import shared_state


class ResourceSupplyAgent:
    """
    Tracks emergency supply inventory and automatically allocates
    resources to risk zones based on population and severity.
    """

    def __init__(self):
        self.name = "ResourceSupply"
        self.messages_processed = 0
        self.start_time = time.time()
        self._region_lookup = {r["id"]: r for r in REGIONS}

        # Central inventory
        self._inventory = {
            "food_packets": DEFAULT_RESOURCES["food_packets"],
            "medical_kits": DEFAULT_RESOURCES["medical_kits"],
            "shelter_capacity": DEFAULT_RESOURCES["shelter_capacity"],
            "water_liters": DEFAULT_RESOURCES["water_liters"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_allocation(self, zone: dict) -> dict:
        """Calculate resource allocation based on risk and population."""
        population = zone.get("population_at_risk", 1000)
        risk_score = zone.get("risk_score", 50)
        multiplier = risk_score / 100

        food = int(population * 3 * multiplier)  # 3 packets per person at full risk
        medical = int(population * 0.1 * multiplier)  # 10% need medical kits
        water = int(population * 5 * multiplier)  # 5 liters per person
        shelter = int(population * 0.5 * multiplier)  # 50% need shelter

        return {
            "food_packets": min(food, self._inventory["food_packets"]),
            "medical_kits": min(medical, self._inventory["medical_kits"]),
            "water_liters": min(water, self._inventory["water_liters"]),
            "shelter_assigned": min(shelter, self._inventory["shelter_capacity"]),
        }

    async def run_cycle(self):
        """Assess needs and allocate resources."""
        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "processing",
            "messages_processed": self.messages_processed,
            "current_action": "Calculating resource allocations for risk zones",
            "uptime_seconds": time.time() - self.start_time,
        })

        # Refresh inventory (simulate slow replenishment)
        self._inventory["food_packets"] = min(DEFAULT_RESOURCES["food_packets"], self._inventory["food_packets"] + 500)
        self._inventory["medical_kits"] = min(DEFAULT_RESOURCES["medical_kits"], self._inventory["medical_kits"] + 50)
        self._inventory["water_liters"] = min(DEFAULT_RESOURCES["water_liters"], self._inventory["water_liters"] + 2000)
        self._inventory["shelter_capacity"] = min(DEFAULT_RESOURCES["shelter_capacity"], self._inventory["shelter_capacity"] + 200)
        self._inventory["timestamp"] = datetime.utcnow().isoformat()

        risk_zones = shared_state.get_risk_zones()
        actionable = [z for z in risk_zones if z.get("risk_level") in ("MODERATE", "HIGH", "CRITICAL")]

        for zone in actionable:
            allocation = self._calculate_allocation(zone)

            # Deduct from inventory
            self._inventory["food_packets"] -= allocation["food_packets"]
            self._inventory["medical_kits"] -= allocation["medical_kits"]
            self._inventory["water_liters"] -= allocation["water_liters"]
            self._inventory["shelter_capacity"] -= allocation["shelter_assigned"]

            alloc_record = {
                "id": f"RES-{uuid.uuid4().hex[:8].upper()}",
                "region_id": zone["region_id"],
                "region_name": zone.get("region_name", ""),
                "food_packets": allocation["food_packets"],
                "medical_kits": allocation["medical_kits"],
                "water_liters": allocation["water_liters"],
                "shelter_assigned": allocation["shelter_assigned"],
                "timestamp": datetime.utcnow().isoformat(),
            }

            shared_state.add_allocation(alloc_record)
            self.messages_processed += 1

        # Update inventory in shared state
        shared_state.set_inventory(self._inventory)

        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "active",
            "messages_processed": self.messages_processed,
            "current_action": f"Allocated resources to {len(actionable)} zones — {self._inventory['food_packets']} food packets remaining",
            "uptime_seconds": time.time() - self.start_time,
        })

    async def start(self):
        """Start continuous supply management loop."""
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
            await asyncio.sleep(RESOURCE_SUPPLY_INTERVAL)


resource_supply_agent = ResourceSupplyAgent()
