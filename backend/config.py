"""
CrisisShield AI — Configuration
"""

# Server
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Agent polling intervals (seconds)
SIGNAL_WATCH_INTERVAL = 10
RISK_PREDICT_INTERVAL = 12
CITIZEN_ALERT_INTERVAL = 15
RESCUE_COORDINATOR_INTERVAL = 15
RESOURCE_SUPPLY_INTERVAL = 20

# Simulated regions
REGIONS = [
    {"id": "R1", "name": "Riverside District", "lat": 28.6139, "lon": 77.2090, "population": 125000, "type": "urban"},
    {"id": "R2", "name": "Coastal Village Alpha", "lat": 19.0760, "lon": 72.8777, "population": 8500, "type": "rural"},
    {"id": "R3", "name": "Mountain Town Beta", "lat": 34.0837, "lon": 74.7973, "population": 32000, "type": "semi-urban"},
    {"id": "R4", "name": "Delta Lowlands", "lat": 22.5726, "lon": 88.3639, "population": 45000, "type": "rural"},
    {"id": "R5", "name": "Forest Range Gamma", "lat": 15.3173, "lon": 75.7139, "population": 12000, "type": "rural"},
    {"id": "R6", "name": "Metro Central", "lat": 12.9716, "lon": 77.5946, "population": 500000, "type": "urban"},
]

# Risk thresholds
RISK_THRESHOLDS = {
    "flood": {"rainfall_mm": 120, "river_level_m": 8.5},
    "earthquake": {"magnitude": 4.5},
    "wildfire": {"temperature_c": 42, "humidity_pct": 20, "wind_speed_kmh": 45},
    "cyclone": {"wind_speed_kmh": 90, "pressure_hpa": 980},
}

# Risk levels
RISK_LEVELS = {
    "LOW": {"min": 0, "max": 30, "color": "#22c55e"},
    "MODERATE": {"min": 30, "max": 55, "color": "#f59e0b"},
    "HIGH": {"min": 55, "max": 75, "color": "#f97316"},
    "CRITICAL": {"min": 75, "max": 100, "color": "#ef4444"},
}

# Resource inventory defaults
DEFAULT_RESOURCES = {
    "ambulances": 24,
    "rescue_boats": 16,
    "relief_teams": 40,
    "food_packets": 50000,
    "medical_kits": 8000,
    "shelter_capacity": 15000,
    "water_liters": 100000,
}

# Disaster types
DISASTER_TYPES = ["flood", "earthquake", "wildfire", "cyclone"]
