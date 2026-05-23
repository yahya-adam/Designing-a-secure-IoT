import asyncio
import json
import paho.mqtt.client as mqtt
from config.settings import MQTT_BROKER, MQTT_PORT, MQTT_TLS_CA, MQTT_TLS_CERT, MQTT_TLS_KEY
from models.sensor_data import RawSensorPayload
from edge.data_minimizer import minimise_and_anonymize
from storage.db_handler import Database

class EdgeValidator:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
        self._setup_tls()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.db = Database()

    def _setup_tls(self):
        if MQTT_TLS_CA and MQTT_TLS_CERT and MQTT_TLS_KEY:
            self.client.tls_set(ca_certs=MQTT_TLS_CA, certfile=MQTT_TLS_CERT, keyfile=MQTT_TLS_KEY)
            self.client.tls_insecure_set(True)
        else:
            print("[!] No TLS certificates provided – connecting without encryption (test only)")

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("[+] Edge gateway connected. Subscribing to raw topics...")
            self.client.subscribe("privenergy/sensors/+/raw", qos=1)
        else:
            print(f"[-] Connection failed: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            raw_json = json.loads(msg.payload.decode())
            validated = RawSensorPayload(**raw_json)
            self.db.insert_raw(validated)
            minimised = minimise_and_anonymize(validated)
            self.db.insert_minimised(minimised)
            print(f"[✓] Processed device {validated.device} at {validated.ts}")
        except Exception as e:
            print(f"[❌] Error: {e}")

    async def run(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()
            self.db.close()
