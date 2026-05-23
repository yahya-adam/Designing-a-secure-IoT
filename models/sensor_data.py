from pydantic import BaseModel, confloat, constr
from typing import Optional
from datetime import datetime

class RawSensorPayload(BaseModel):
    ts: int
    device: constr(min_length=1)
    co: confloat(ge=0, le=100)
    humidity: confloat(ge=0, le=100)
    light: bool
    lpg: confloat(ge=0, le=100)
    motion: bool
    smoke: confloat(ge=0, le=100)
    temp: confloat(ge=-20, le=80)

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.ts)

class MinimisedReport(BaseModel):
    region_hash: str
    avg_co_24h: Optional[float]
    avg_lpg_24h: Optional[float]
    avg_smoke_24h: Optional[float]
    avg_temp_24h: Optional[float]
    peak_light_hour: Optional[int]
    motion_count_24h: Optional[int]
    timestamp_bucket: int
