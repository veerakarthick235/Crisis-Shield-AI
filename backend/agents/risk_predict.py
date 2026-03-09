"""
CrisisShield AI — RiskPredict Agent
Analyzes signals to predict risk zones and severity levels.
Uses ASI:One API for intelligent disaster analysis.
"""

import asyncio
import time
import uuid
import requests
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REGIONS, RISK_PREDICT_INTERVAL
from services.agent_bridge import shared_state


class RiskPredictAgent:
    """
    Receives disaster signals from SignalWatch and performs risk assessment
    using terrain analysis, population data, and ASI:One AI reasoning.
    """

    def __init__(self):
        self.name = "RiskPredict"
        self.messages_processed = 0
        self.start_time = time.time()
        self._region_lookup = {r["id"]: r for r in REGIONS}

        # ASI:One API configuration
        self.asi_api_key = os.getenv("ASI_API_KEY")
        self.asi_url = "https://api.asi1.ai/v1/chat/completions"

        # Terrain vulnerability factors (simulated)
        self._terrain_vulnerability = {
            "urban": 0.7,
            "semi-urban": 0.85,
            "rural": 1.0,
        }

        # Disaster-type base impact hours
        self._impact_hours = {
            "flood": 6,
            "earthquake": 0.5,
            "wildfire": 12,
            "cyclone": 8,
        }

    def _ai_risk_analysis(self, signal):
        """
        Use ASI:One API to analyze disaster risk.
        """

        prompt = f"""
        Analyze the following disaster signal and provide a short risk assessment.

        Disaster Type: {signal['disaster_type']}
        Region ID: {signal['region_id']}
        Confidence Score: {signal['confidence']}

        Provide:
        - Risk severity explanation
        - Recommended emergency action
        """

        try:
            response = requests.post(
                self.asi_url,
                headers={
                    "Authorization": f"Bearer {self.asi_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "asi1-mini",
                    "messages": [
                        {"role": "system", "content": "You are an expert disaster risk analyst."},
                        {"role": "user", "content": prompt}
                    ]
                }
            )

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            return f"AI analysis unavailable: {str(e)}"

    def _calculate_risk_score(self, signal: dict) -> dict:
        """Calculate comprehensive risk score for a signal."""

        region = self._region_lookup.get(signal["region_id"], {})
        terrain_type = region.get("type", "rural")
        vulnerability = self._terrain_vulnerability.get(terrain_type, 1.0)
        population = region.get("population", 10000)

        # Base score from signal confidence
        base_score = signal["confidence"]

        # Adjust by terrain vulnerability
        adjusted_score = base_score * vulnerability

        # Population density factor
        pop_factor = min(1.3, 0.8 + (population / 500000) * 0.5)
        adjusted_score *= pop_factor

        # Cap risk score
        risk_score = min(100, round(adjusted_score, 1))

        # Determine risk level
        if risk_score >= 75:
            risk_level = "CRITICAL"
            action = f"IMMEDIATE EVACUATION — All residents within 5km radius of {region.get('name', 'affected area')}"
        elif risk_score >= 55:
            risk_level = "HIGH"
            action = f"EVACUATION ADVISORY — Prepare for evacuation in {region.get('name', 'affected area')}"
        elif risk_score >= 30:
            risk_level = "MODERATE"
            action = f"ALERT — Monitor conditions closely in {region.get('name', 'affected area')}"
        else:
            risk_level = "LOW"
            action = f"WATCH — Continue monitoring {region.get('name', 'affected area')}"

        # Impact time estimation
        base_hours = self._impact_hours.get(signal["disaster_type"], 6)
        impact_hours = max(0.5, base_hours * (1 - (risk_score / 150)))

        # AI analysis using ASI:One
        ai_analysis = self._ai_risk_analysis(signal)

        return {
            "id": f"RZ-{uuid.uuid4().hex[:8].upper()}",
            "region_id": signal["region_id"],
            "region_name": region.get("name", ""),
            "disaster_type": signal["disaster_type"],
            "risk_level": risk_level,
            "risk_score": risk_score,
            "population_at_risk": int(population * (risk_score / 100) * 0.3),
            "estimated_impact_time_hours": round(impact_hours, 1),
            "recommended_action": action,
            "ai_analysis": ai_analysis,
            "source_signal_id": signal["id"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def run_cycle(self):
        """Process latest signals and generate risk zones."""

        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "processing",
            "messages_processed": self.messages_processed,
            "current_action": "Analyzing disaster signals using AI",
            "uptime_seconds": time.time() - self.start_time,
        })

        signals = shared_state.get_signals()

        if not signals:
            shared_state.update_agent_status(self.name, {
                "name": self.name,
                "state": "active",
                "messages_processed": self.messages_processed,
                "current_action": "No signals detected",
                "uptime_seconds": time.time() - self.start_time,
            })
            return []

        risk_zones = []

        for signal in signals:
            zone = self._calculate_risk_score(signal)
            risk_zones.append(zone)
            self.messages_processed += 1

        # Sort by risk score
        risk_zones.sort(key=lambda z: z["risk_score"], reverse=True)

        shared_state.set_risk_zones(risk_zones)

        shared_state.update_agent_status(self.name, {
            "name": self.name,
            "state": "active",
            "messages_processed": self.messages_processed,
            "current_action": f"Generated {len(risk_zones)} AI risk assessments",
            "uptime_seconds": time.time() - self.start_time,
        })

        return risk_zones

    async def start(self):
        """Start continuous risk prediction loop."""

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

            await asyncio.sleep(RISK_PREDICT_INTERVAL)


risk_predict_agent = RiskPredictAgent()
