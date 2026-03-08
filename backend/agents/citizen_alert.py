"""
CrisisShield AI — CitizenAlert Agent
Generates and dispatches citizen alerts based on risk zone data.
"""

import asyncio
import time
import uuid
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REGIONS, CITIZEN_ALERT_INTERVAL
from services.agent_bridge import shared_state


class CitizenAlertAgent:
    """
    Monitors risk zones and automatically generates human-readable alerts
    for citizens and authorities. Logs alerts to dashboard.
    """

    def __init__(self):
        self.name = "CitizenAlert"
        self.messages_processed = 0
        self.start_time = time.time()
        self._region_lookup = {r["id"]: r for r in REGIONS}
        self._sent_alert_keys = set()  # Prevent duplicate alerts within cycle

    def _generate_alert_message(self, zone: dict) -> str:
        """Generate human-readable alert message."""
        templates = {
            "flood": {
                "CRITICAL": "⛔ CRITICAL FLOOD WARNING\n{region_name}: Severe flooding expected within {hours}h.\nIMMMEDIATE EVACUATION REQUIRED.\nNearest shelter: Government School, Ward 4\nEmergency: 112",
                "HIGH": "🔴 FLOOD ALERT — HIGH RISK\n{region_name}: Significant flood risk within {hours}h.\nPrepare for evacuation. Move to higher ground.\nEmergency: 112",
                "MODERATE": "🟡 FLOOD ADVISORY\n{region_name}: Moderate flood risk. Monitor water levels.\nPrepare emergency supplies.\nStay tuned for updates.",
            },
            "earthquake": {
                "CRITICAL": "⛔ EARTHQUAKE WARNING\n{region_name}: Strong seismic activity detected.\nDROP, COVER, HOLD ON.\nMove away from buildings. Await aftershocks.\nEmergency: 112",
                "HIGH": "🔴 SEISMIC ALERT\n{region_name}: Elevated seismic activity.\nSecure heavy objects. Identify safe zones.\nEmergency: 112",
                "MODERATE": "🟡 SEISMIC ADVISORY\n{region_name}: Minor seismic activity detected.\nNo immediate action required. Stay alert.",
            },
            "wildfire": {
                "CRITICAL": "⛔ WILDFIRE EMERGENCY\n{region_name}: Wildfire approaching within {hours}h.\nEVACUATE IMMEDIATELY via designated routes.\nAvoid smoke inhalation.\nEmergency: 112",
                "HIGH": "🔴 WILDFIRE WARNING\n{region_name}: High wildfire risk.\nPrepare for possible evacuation.\nClear vegetation around property.\nEmergency: 112",
                "MODERATE": "🟡 FIRE WEATHER ADVISORY\n{region_name}: Elevated fire conditions.\nAvoid outdoor burning. Report any smoke.",
            },
            "cyclone": {
                "CRITICAL": "⛔ CYCLONE EMERGENCY\n{region_name}: Severe cyclone expected within {hours}h.\nSEEK IMMEDIATE SHELTER. Board windows.\nAvoid coastal areas.\nEmergency: 112",
                "HIGH": "🔴 CYCLONE WARNING\n{region_name}: Cyclone approaching.\nSecure loose items. Stock emergency supplies.\nPrepare for power outages.\nEmergency: 112",
                "MODERATE": "🟡 CYCLONE WATCH\n{region_name}: Tropical disturbance detected.\nMonitor weather updates. Prepare emergency kit.",
            },
        }

        dtype = zone.get("disaster_type", "flood")
        level = zone.get("risk_level", "MODERATE")

        if level == "LOW":
            return f"ℹ️ {dtype.upper()} WATCH — {zone.get('region_name', 'Region')}: Low risk detected. Continue normal activities. Stay informed."

        template_group = templates.get(dtype, templates["flood"])
        template = template_group.get(level, template_group.get("MODERATE", "Alert for {region_name}"))

        return template.format(
            region_name=zone.get("region_name", "Unknown Region"),
            hours=zone.get("estimated_impact_time_hours", "N/A"),
        )

    async def run_cycle(self):
        """Process risk zones and generate alerts."""
        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "processing",
            "messages_processed": self.messages_processed,
            "current_action": "Generating citizen alerts from risk zones",
            "uptime_seconds": time.time() - self.start_time,
        })

        risk_zones = shared_state.get_risk_zones()
        alertable = [z for z in risk_zones if z.get("risk_level") in ("MODERATE", "HIGH", "CRITICAL")]

        new_alerts = 0
        for zone in alertable:
            # De-duplicate: one alert per region+type per cycle
            alert_key = f"{zone['region_id']}_{zone['disaster_type']}_{zone['risk_level']}"
            if alert_key in self._sent_alert_keys:
                continue

            region = self._region_lookup.get(zone["region_id"], {})
            population = region.get("population", 10000)
            notified = int(population * 0.6)  # Assume 60% reachable

            channels = ["dashboard"]
            if zone["risk_level"] == "CRITICAL":
                channels = ["sms", "whatsapp", "app", "dashboard", "radio"]
            elif zone["risk_level"] == "HIGH":
                channels = ["sms", "app", "dashboard"]
            else:
                channels = ["app", "dashboard"]

            alert = {
                "id": f"ALT-{uuid.uuid4().hex[:8].upper()}",
                "region_id": zone["region_id"],
                "region_name": zone.get("region_name", ""),
                "disaster_type": zone["disaster_type"],
                "risk_level": zone["risk_level"],
                "message": self._generate_alert_message(zone),
                "channels": channels,
                "timestamp": datetime.utcnow().isoformat(),
                "acknowledged": False,
                "people_notified": notified,
            }

            shared_state.add_alert(alert)
            self._sent_alert_keys.add(alert_key)
            new_alerts += 1
            self.messages_processed += 1

        # Clean old keys periodically
        if len(self._sent_alert_keys) > 200:
            self._sent_alert_keys.clear()

        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "active",
            "messages_processed": self.messages_processed,
            "current_action": f"Dispatched {new_alerts} alerts across {len(set(z['region_id'] for z in alertable))} regions",
            "uptime_seconds": time.time() - self.start_time,
        })

    async def start(self):
        """Start continuous alerting loop."""
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
            await asyncio.sleep(CITIZEN_ALERT_INTERVAL)


citizen_alert_agent = CitizenAlertAgent()
