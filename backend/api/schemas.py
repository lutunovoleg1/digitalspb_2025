from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, date


class HalfHourReading(BaseModel):
    timestamp: datetime
    value: float


class DailyReading(BaseModel):
    date: date
    value: float


class VisualizationData(BaseModel):
    half_hour_readings_A_plus: List[HalfHourReading]
    half_hour_readings_P_plus: List[HalfHourReading]
    daily_readings_T0_A_plus: List[DailyReading]


class SuspiciousMeter(BaseModel):
    serial_number: str
    reason: str
    suspicion_level: float


class Report(BaseModel):
    suspicious_meters: List[SuspiciousMeter]
    visualization_data: Dict[str, VisualizationData]