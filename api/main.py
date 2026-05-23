import os
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pysqlcipher3 import dbapi2 as sqlite3
from contextlib import contextmanager

app = FastAPI(title="Telemetry API")
@app.get("/")
def root():
    return {"message": "Telemetry API is running"}

API_KEY = os.getenv("API_KEY", "~/sss-project/.ven")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)

DB_PATH = os.getenv("DB_PATH", "/data/telemetry.db")
DB_KEY = os.getenv("DB_KEY", "~/sss-project/.ven")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    if DB_KEY:
        conn.execute(f"PRAGMA key = '{DB_KEY}'")
    try:
        yield conn
    finally:
        conn.close()

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/latest")
def get_latest(limit: int = 100, _ = Depends(verify_api_key)):
    with get_db() as conn:
        cur = conn.execute("""
            SELECT device, ts, co, humidity, light, lpg, motion, smoke, temp
            FROM raw_sensor_data
            ORDER BY ts DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
    return [{"device": r[0], "ts": r[1], "co": r[2], "humidity": r[3],
             "light": bool(r[4]), "lpg": r[5], "motion": bool(r[6]),
             "smoke": r[7], "temp": r[8]} for r in rows]

@app.get("/api/devices")
def get_devices(_ = Depends(verify_api_key)):
    with get_db() as conn:
        cur = conn.execute("SELECT DISTINCT device FROM raw_sensor_data")
        return [{"device": r[0]} for r in cur.fetchall()]

@app.get("/api/timeseries")
def get_timeseries(device: str, from_ts: int, to_ts: int, _ = Depends(verify_api_key)):
    with get_db() as conn:
        cur = conn.execute("""
            SELECT ts, co, temp, humidity
            FROM raw_sensor_data
            WHERE device = ? AND ts BETWEEN ? AND ?
            ORDER BY ts
        """, (device, from_ts, to_ts))
        rows = cur.fetchall()
    return [{"ts": r[0], "co": r[1], "temp": r[2], "humidity": r[3]} for r in rows]
