"""
CrisisShield AI — Agent Bridge
Thread-safe shared state between uAgents and FastAPI.
"""

import threading
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque


class SharedState:
    """Thread-safe shared state bridging agents to the API layer."""

    def __init__(self):
        self._lock = threading.Lock()
        self._signals: List[Dict] = []
        self._risk_zones: List[Dict] = []
        self._alerts: List[Dict] = []
        self._rescue_units: List[Dict] = []
        self._resource_inventory: Dict = {}
        self._resource_allocations: List[Dict] = []
        self._agent_statuses: Dict[str, Dict] = {}
        self._event_log: deque = deque(maxlen=200)

    # --- Signals ---
    def add_signal(self, signal: Dict):
        with self._lock:
            self._signals = [s for s in self._signals if s.get("region_id") != signal.get("region_id") or s.get("disaster_type") != signal.get("disaster_type")]
            self._signals.append(signal)
            self._event_log.append({"type": "signal", "data": signal, "ts": datetime.utcnow().isoformat()})

    def get_signals(self) -> List[Dict]:
        with self._lock:
            return list(self._signals)

    # --- Risk Zones ---
    def set_risk_zones(self, zones: List[Dict]):
        with self._lock:
            self._risk_zones = zones
            self._event_log.append({"type": "risk_update", "count": len(zones), "ts": datetime.utcnow().isoformat()})

    def get_risk_zones(self) -> List[Dict]:
        with self._lock:
            return list(self._risk_zones)

    # --- Alerts ---
    def add_alert(self, alert: Dict):
        with self._lock:
            self._alerts.insert(0, alert)
            if len(self._alerts) > 100:
                self._alerts = self._alerts[:100]
            self._event_log.append({"type": "alert", "data": alert, "ts": datetime.utcnow().isoformat()})

    def get_alerts(self, limit: int = 50) -> List[Dict]:
        with self._lock:
            return list(self._alerts[:limit])

    # --- Rescue Units ---
    def set_rescue_units(self, units: List[Dict]):
        with self._lock:
            self._rescue_units = units

    def get_rescue_units(self) -> List[Dict]:
        with self._lock:
            return list(self._rescue_units)

    # --- Resources ---
    def set_inventory(self, inventory: Dict):
        with self._lock:
            self._resource_inventory = inventory

    def get_inventory(self) -> Dict:
        with self._lock:
            return dict(self._resource_inventory)

    def add_allocation(self, allocation: Dict):
        with self._lock:
            self._resource_allocations.insert(0, allocation)
            if len(self._resource_allocations) > 50:
                self._resource_allocations = self._resource_allocations[:50]

    def get_allocations(self, limit: int = 20) -> List[Dict]:
        with self._lock:
            return list(self._resource_allocations[:limit])

    # --- Agent Status ---
    def update_agent_status(self, name: str, status: Dict):
        with self._lock:
            self._agent_statuses[name] = {**status, "last_updated": datetime.utcnow().isoformat()}

    def get_agent_statuses(self) -> Dict[str, Dict]:
        with self._lock:
            return dict(self._agent_statuses)

    def get_agent_status(self, name: str) -> Optional[Dict]:
        with self._lock:
            return self._agent_statuses.get(name)

    # --- Events ---
    def get_events(self, limit: int = 50) -> List[Dict]:
        with self._lock:
            return list(self._event_log)[-limit:]

    # --- Dashboard Overview ---
    def get_overview(self) -> Dict:
        with self._lock:
            active_alerts = [a for a in self._alerts if not a.get("acknowledged")]
            deployed_units = [u for u in self._rescue_units if u.get("status") in ("deployed", "en_route", "on_site")]
            high_risk = [z for z in self._risk_zones if z.get("risk_level") in ("HIGH", "CRITICAL")]
            people_notified = sum(a.get("people_notified", 0) for a in self._alerts)
            active_agents = sum(1 for s in self._agent_statuses.values() if s.get("state") in ("active", "processing"))

            return {
                "total_signals": len(self._signals),
                "active_alerts": len(active_alerts),
                "regions_at_risk": len(high_risk),
                "rescue_units_deployed": len(deployed_units),
                "people_notified": people_notified,
                "resources_allocated": len(self._resource_allocations),
                "agents_active": active_agents,
                "timestamp": datetime.utcnow().isoformat(),
            }


# Singleton
shared_state = SharedState()
