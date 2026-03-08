"""
CrisisShield AI — Pydantic Data Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DisasterType(str, Enum):
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    WILDFIRE = "wildfire"
    CYCLONE = "cyclone"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentState(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"


# --- Weather / Sensor Data ---

class WeatherData(BaseModel):
    region_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    temperature_c: float = 0.0
    humidity_pct: float = 0.0
    rainfall_mm: float = 0.0
    wind_speed_kmh: float = 0.0
    pressure_hpa: float = 1013.0
    river_level_m: float = 0.0
    seismic_magnitude: float = 0.0


class SocialSignal(BaseModel):
    region_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    keyword_hits: int = 0
    sentiment_score: float = 0.0  # -1 to 1
    source: str = "twitter"


# --- Agent Outputs ---

class DisasterSignal(BaseModel):
    id: str
    region_id: str
    region_name: str = ""
    disaster_type: DisasterType
    confidence: float = 0.0  # 0-100
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    weather_snapshot: Optional[WeatherData] = None
    social_signal: Optional[SocialSignal] = None
    summary: str = ""


class RiskZone(BaseModel):
    id: str
    region_id: str
    region_name: str = ""
    disaster_type: DisasterType
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = 0.0  # 0-100
    population_at_risk: int = 0
    estimated_impact_time_hours: float = 0.0
    recommended_action: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Alert(BaseModel):
    id: str
    region_id: str
    region_name: str = ""
    disaster_type: DisasterType
    risk_level: RiskLevel
    message: str = ""
    channels: List[str] = Field(default_factory=lambda: ["sms", "app", "dashboard"])
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    people_notified: int = 0


class RescueUnit(BaseModel):
    id: str
    unit_type: str  # ambulance, boat, relief_team
    assigned_region: str = ""
    assigned_region_name: str = ""
    status: str = "standby"  # standby, deployed, en_route, on_site
    eta_minutes: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResourceInventory(BaseModel):
    region_id: str = "HQ"
    region_name: str = "Central HQ"
    food_packets: int = 0
    medical_kits: int = 0
    shelter_capacity: int = 0
    water_liters: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResourceAllocation(BaseModel):
    id: str
    region_id: str
    region_name: str = ""
    food_packets: int = 0
    medical_kits: int = 0
    water_liters: int = 0
    shelter_assigned: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentStatus(BaseModel):
    name: str
    state: AgentState = AgentState.IDLE
    last_run: Optional[datetime] = None
    messages_processed: int = 0
    current_action: str = ""
    uptime_seconds: float = 0.0


# --- API Responses ---

class DashboardOverview(BaseModel):
    total_signals: int = 0
    active_alerts: int = 0
    regions_at_risk: int = 0
    rescue_units_deployed: int = 0
    people_notified: int = 0
    resources_allocated: int = 0
    agents_active: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
