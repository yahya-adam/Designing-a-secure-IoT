import random
from config.settings import DP_EPSILON
from models.sensor_data import RawSensorPayload, MinimisedReport

def laplace_mechanism(value: float, sensitivity: float = 1.0) -> float:
    if value is None:
        return None
    scale = sensitivity / DP_EPSILON
    noise = random.gauss(0, scale)
    return round(value + noise, 3)

def minimise_and_anonymize(raw: RawSensorPayload) -> MinimisedReport:
    # For simplicity, we anonymise the current reading (no 24h aggregation yet)
    return MinimisedReport(
        region_hash=raw.device[:8],
        avg_co_24h=laplace_mechanism(raw.co),
        avg_lpg_24h=laplace_mechanism(raw.lpg),
        avg_smoke_24h=laplace_mechanism(raw.smoke),
        avg_temp_24h=laplace_mechanism(raw.temp),
        peak_light_hour=None,
        motion_count_24h=None,
        timestamp_bucket=int(raw.ts / 3600) * 3600
    )
