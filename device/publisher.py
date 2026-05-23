import asyncio
import json
import paho.mqtt.client as mqtt
from config.settings import MQTT_BROKER, MQTT_PORT, MQTT_TLS_CA, MQTT_TLS_CERT, MQTT_TLS_KEY, SENSOR_READ_INTERVAL_SEC
from device.sensor_reader import SensorReader, CsvReplayReader

class SecurePublisher:
    def __init__(self, device_id: str, mode: str = 'simulate', csv_path: str = None):
        self.device_id = device_id
        self.mode = mode
        if mode == 'csv':
            if not csv_path:
                raise ValueError("csv_path required for csv mode")
            self.reader = CsvReplayReader(device_id, csv_path)
        else:
            simulate = (mode == 'simulate')
            self.reader = SensorReader(device_id, simulate=simulate)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
        self._setup_tls()
        self.client.on_connect = self._on_connect

    def _setup_tls(self):
        if MQTT_TLS_CA and MQTT_TLS_CERT and MQTT_TLS_KEY:
            self.client.tls_set(ca_certs=MQTT_TLS_CA, certfile=MQTT_TLS_CERT, keyfile=MQTT_TLS_KEY)
            self.client.tls_insecure_set(True)
        else:
            print("[!] No TLS certificates provided – connecting without encryption (test only)")

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"[+] Device {self.device_id} connected to broker")
        else:
            print(f"[-] Connection failed: {rc}")

    async def publish_loop(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()
        try:
            while True:
                data = self.reader.read()
                payload = data.model_dump()
                topic = f"privenergy/sensors/{self.device_id}/raw"
                self.client.publish(topic, json.dumps(payload), qos=1)
                print(f"[✓] Published from {self.device_id}: {payload['ts']}")
                await asyncio.sleep(SENSOR_READ_INTERVAL_SEC)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()
