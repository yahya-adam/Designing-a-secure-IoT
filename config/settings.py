import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CERTS_DIR = BASE_DIR / "certs"

# ✅ Read DB_KEY directly from Docker environment
DB_KEY = os.getenv("DB_KEY", "~/sss-project/.ven")
print(f"DEBUG: DB_KEY is set" if DB_KEY else "DEBUG: DB_KEY is empty")

# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_TLS_CA = os.getenv("MQTT_TLS_CA", str(CERTS_DIR / "ca.cert.pem"))
MQTT_TLS_CERT = os.getenv("MQTT_TLS_CERT", "")
MQTT_TLS_KEY = os.getenv("MQTT_TLS_KEY", "")

# Storage 
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "telemetry.db"))

# Privacy & Simulation
DP_EPSILON = float(os.getenv("DP_EPSILON", "1.0"))
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "30"))
SIMULATE_SENSORS = os.getenv("SIMULATE_SENSORS", "true").lower() == "true"
SENSOR_READ_INTERVAL_SEC = int(os.getenv("SENSOR_READ_INTERVAL_SEC", "2"))




