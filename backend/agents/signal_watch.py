"""
CrisisShield AI — SignalWatch Agent
Monitors environmental data sources and detects early warning signals.
"""

import asyncio
import time
import uuid
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REGIONS, RISK_THRESHOLDS, SIGNAL_WATCH_INTERVAL
from services.data_simulator import simulator
from services.agent_bridge import shared_state


class SignalWatchAgent:
    """
    Autonomous agent that continuously monitors simulated environmental data
    and detects early warning signals for potential disasters.
    """

    def __init__(self):
        self.name = "SignalWatch"
        self.messages_processed = 0
        self.start_time = time.time()

    def _analyze_weather(self, region: dict, weather: dict) -> list:
        """Analyze weather data against risk thresholds to detect disaster signals."""
        signals = []

        # Flood detection
        flood_thresh = RISK_THRESHOLDS["flood"]
        if weather["rainfall_mm"] > flood_thresh["rainfall_mm"] * 0.6 or weather["river_level_m"] > flood_thresh["river_level_m"] * 0.7:
            confidence = 0
            if weather["rainfall_mm"] > flood_thresh["rainfall_mm"]:
                confidence += 45
            elif weather["rainfall_mm"] > flood_thresh["rainfall_mm"] * 0.6:
                confidence += 25
            if weather["river_level_m"] > flood_thresh["river_level_m"]:
                confidence += 45
            elif weather["river_level_m"] > flood_thresh["river_level_m"] * 0.7:
                confidence += 20
            if weather["humidity_pct"] > 80:
                confidence += 10

            if confidence > 20:
                signals.append({
                    "id": f"SIG-{uuid.uuid4().hex[:8].upper()}",
                    "region_id": region["id"],
                    "region_name": region["name"],
                    "disaster_type": "flood",
                    "confidence": min(100, confidence),
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": f"Flood risk: rainfall={weather['rainfall_mm']}mm, river={weather['river_level_m']}m",
                    "weather_snapshot": weather,
                })

        # Cyclone detection
        cyclone_thresh = RISK_THRESHOLDS["cyclone"]
        if weather["wind_speed_kmh"] > cyclone_thresh["wind_speed_kmh"] * 0.5 and weather["pressure_hpa"] < cyclone_thresh["pressure_hpa"] + 15:
            confidence = 0
            if weather["wind_speed_kmh"] > cyclone_thresh["wind_speed_kmh"]:
                confidence += 50
            elif weather["wind_speed_kmh"] > cyclone_thresh["wind_speed_kmh"] * 0.7:
                confidence += 30
            if weather["pressure_hpa"] < cyclone_thresh["pressure_hpa"]:
                confidence += 40
            elif weather["pressure_hpa"] < cyclone_thresh["pressure_hpa"] + 10:
                confidence += 20

            if confidence > 25:
                signals.append({
                    "id": f"SIG-{uuid.uuid4().hex[:8].upper()}",
                    "region_id": region["id"],
                    "region_name": region["name"],
                    "disaster_type": "cyclone",
                    "confidence": min(100, confidence),
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": f"Cyclone risk: wind={weather['wind_speed_kmh']}km/h, pressure={weather['pressure_hpa']}hPa",
                    "weather_snapshot": weather,
                })

        # Wildfire detection
        fire_thresh = RISK_THRESHOLDS["wildfire"]
        if weather["temperature_c"] > fire_thresh["temperature_c"] * 0.8 and weather["humidity_pct"] < fire_thresh["humidity_pct"] * 2:
            confidence = 0
            if weather["temperature_c"] > fire_thresh["temperature_c"]:
                confidence += 40
            elif weather["temperature_c"] > fire_thresh["temperature_c"] * 0.85:
                confidence += 25
            if weather["humidity_pct"] < fire_thresh["humidity_pct"]:
                confidence += 40
            elif weather["humidity_pct"] < fire_thresh["humidity_pct"] * 1.5:
                confidence += 20
            if weather["wind_speed_kmh"] > fire_thresh["wind_speed_kmh"]:
                confidence += 20

            if confidence > 25:
                signals.append({
                    "id": f"SIG-{uuid.uuid4().hex[:8].upper()}",
                    "region_id": region["id"],
                    "region_name": region["name"],
                    "disaster_type": "wildfire",
                    "confidence": min(100, confidence),
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": f"Wildfire risk: temp={weather['temperature_c']}°C, humidity={weather['humidity_pct']}%",
                    "weather_snapshot": weather,
                })

        # Earthquake detection
        eq_thresh = RISK_THRESHOLDS["earthquake"]
        if weather["seismic_magnitude"] > eq_thresh["magnitude"] * 0.6:
            confidence = min(100, int((weather["seismic_magnitude"] / eq_thresh["magnitude"]) * 70))
            if confidence > 20:
                signals.append({
                    "id": f"SIG-{uuid.uuid4().hex[:8].upper()}",
                    "region_id": region["id"],
                    "region_name": region["name"],
                    "disaster_type": "earthquake",
                    "confidence": confidence,
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": f"Seismic activity: magnitude={weather['seismic_magnitude']}",
                    "weather_snapshot": weather,
                })

        return signals

    async def run_cycle(self):
        """Execute one monitoring cycle across all regions."""
        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "processing",
            "messages_processed": self.messages_processed,
            "current_action": "Scanning environmental data sources",
            "uptime_seconds": time.time() - self.start_time,
        })

        all_signals = []
        for region in REGIONS:
            weather = simulator.get_weather(region["id"])
            social = simulator.get_social_signals(region["id"])

            signals = self._analyze_weather(region, weather)

            # Boost confidence if social signals are strong
            for sig in signals:
                if social["keyword_hits"] > 50:
                    boost = min(15, social["keyword_hits"] // 20)
                    sig["confidence"] = min(100, sig["confidence"] + boost)
                    sig["social_signal"] = social

            all_signals.extend(signals)

        # Push signals to shared state
        for sig in all_signals:
            shared_state.add_signal(sig)
            self.messages_processed += 1

        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "active",
            "messages_processed": self.messages_processed,
            "current_action": f"Detected {len(all_signals)} signals across {len(REGIONS)} regions",
            "uptime_seconds": time.time() - self.start_time,
        })

        return all_signals

    async def start(self):
        """Start continuous monitoring loop."""
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
            await asyncio.sleep(SIGNAL_WATCH_INTERVAL)


signal_watch_agent = SignalWatchAgent()
