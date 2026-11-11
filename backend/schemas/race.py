from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class SessionMetadata:
    session_id: str
    event_name: str
    session_type: str
    event_date: date
    circuit: str
    source: str


@dataclass(frozen=True)
class LapRecord:
    session_id: str
    driver: str
    lap_number: int
    lap_time_s: float
    sector1_s: Optional[float] = None
    sector2_s: Optional[float] = None
    sector3_s: Optional[float] = None
    compound: Optional[str] = None
    tyre_age_laps: Optional[int] = None


@dataclass(frozen=True)
class TelemetrySample:
    session_id: str
    driver: str
    timestamp_s: float
    lap_number: int
    distance_m: Optional[float] = None
    speed_kph: Optional[float] = None
    throttle_pct: Optional[float] = None
    brake_pct: Optional[float] = None
    gear: Optional[int] = None
