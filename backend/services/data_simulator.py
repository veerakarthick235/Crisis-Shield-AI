"""
CrisisShield AI — Simulated Environmental Data Generator
Produces realistic weather, seismic, and social media signals.
"""

import math
import random
import time
from datetime import datetime
from typing import Dict, List

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REGIONS, DISASTER_TYPES


class DataSimulator:
    """Generates realistic simulated environmental data with escalating disaster cycles."""

    def __init__(self):
        self._start_time = time.time()
        self._cycle_duration = 180  # 3-minute disaster cycle
        self._active_disaster: Dict = {}
        self._rng = random.Random(42)
        self._trigger_new_disaster()

    def _trigger_new_disaster(self):
        """Select a random disaster type and target regions."""
        dtype = self._rng.choice(DISASTER_TYPES)
        target_regions = self._rng.sample(REGIONS, k=min(3, len(REGIONS)))
        self._active_disaster = {
            "type": dtype,
            "target_region_ids": [r["id"] for r in target_regions],
            "started_at": time.time(),
            "intensity": self._rng.uniform(0.5, 1.0),
        }

    def _cycle_phase(self) -> float:
        """Returns 0.0-1.0 indicating position in current disaster cycle."""
        elapsed = (time.time() - self._active_disaster.get("started_at", self._start_time))
        phase = (elapsed % self._cycle_duration) / self._cycle_duration
        # Reset disaster at cycle boundary
        if elapsed > self._cycle_duration:
            self._trigger_new_disaster()
        return phase

    def get_weather(self, region_id: str) -> Dict:
        """Generate weather data for a region."""
        phase = self._cycle_phase()
        disaster = self._active_disaster
        is_target = region_id in disaster.get("target_region_ids", [])
        intensity = disaster.get("intensity", 0.5) if is_target else 0.1

        # Base values with sinusoidal variation
        t = time.time()
        base_temp = 28 + 5 * math.sin(t / 100)
        base_humidity = 60 + 10 * math.sin(t / 80)
        base_rainfall = max(0, 5 + 3 * math.sin(t / 60))
        base_wind = 12 + 4 * math.sin(t / 90)
        base_pressure = 1013 - 2 * math.sin(t / 120)
        base_river = 3.0 + 0.5 * math.sin(t / 70)

        # Escalate if target region during disaster
        escalation = phase * intensity
        dtype = disaster.get("type", "flood")

        if dtype == "flood" and is_target:
            base_rainfall += escalation * 200
            base_river += escalation * 12
            base_humidity = min(100, base_humidity + escalation * 30)
        elif dtype == "cyclone" and is_target:
            base_wind += escalation * 120
            base_pressure -= escalation * 50
            base_rainfall += escalation * 150
        elif dtype == "wildfire" and is_target:
            base_temp += escalation * 18
            base_humidity = max(5, base_humidity - escalation * 50)
            base_wind += escalation * 40
        elif dtype == "earthquake" and is_target:
            pass  # Earthquake handled separately

        # Add noise
        noise = lambda v, pct: v + self._rng.uniform(-v * pct, v * pct) if v != 0 else 0
        return {
            "region_id": region_id,
            "timestamp": datetime.utcnow().isoformat(),
            "temperature_c": round(noise(base_temp, 0.05), 1),
            "humidity_pct": round(max(0, min(100, noise(base_humidity, 0.05))), 1),
            "rainfall_mm": round(max(0, noise(base_rainfall, 0.1)), 1),
            "wind_speed_kmh": round(max(0, noise(base_wind, 0.08)), 1),
            "pressure_hpa": round(noise(base_pressure, 0.002), 1),
            "river_level_m": round(max(0, noise(base_river, 0.05)), 2),
            "seismic_magnitude": round(
                (escalation * 7.5 + self._rng.uniform(0, 0.5))
                if (dtype == "earthquake" and is_target and phase > 0.3)
                else self._rng.uniform(0, 1.5),
                1
            ),
        }

    def get_social_signals(self, region_id: str) -> Dict:
        """Generate simulated social media disaster signals."""
        disaster = self._active_disaster
        phase = self._cycle_phase()
        is_target = region_id in disaster.get("target_region_ids", [])

        if is_target and phase > 0.2:
            keyword_hits = int(phase * disaster["intensity"] * 500 + self._rng.randint(0, 50))
            sentiment = round(-0.3 - phase * 0.6 + self._rng.uniform(-0.1, 0.1), 2)
        else:
            keyword_hits = self._rng.randint(0, 15)
            sentiment = round(self._rng.uniform(-0.1, 0.3), 2)

        return {
            "region_id": region_id,
            "timestamp": datetime.utcnow().isoformat(),
            "keyword_hits": keyword_hits,
            "sentiment_score": max(-1, min(1, sentiment)),
            "source": self._rng.choice(["twitter", "facebook", "news", "whatsapp"]),
        }

    def get_all_regions_data(self) -> List[Dict]:
        """Get weather + social data for all regions."""
        result = []
        for region in REGIONS:
            weather = self.get_weather(region["id"])
            social = self.get_social_signals(region["id"])
            result.append({
                "region": region,
                "weather": weather,
                "social": social,
            })
        return result


# Singleton
simulator = DataSimulator()
