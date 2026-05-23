#!/usr/bin/env python3
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    if len(sys.argv) < 2:
        print("Usage: run_device.py <device_mac> [--mode simulate|csv] [--csv PATH]")
        sys.exit(1)
    device_mac = sys.argv[1]
    mode = "simulate"
    csv_path = None
    if len(sys.argv) >= 3 and sys.argv[2] == "--mode":
        mode = sys.argv[3] if len(sys.argv) > 3 else "simulate"
    if mode == "csv":
        if len(sys.argv) >= 5 and sys.argv[4] == "--csv":
            csv_path = sys.argv[5]
        else:
            print("CSV mode requires --csv PATH")
            sys.exit(1)

    base_dir = Path(__file__).parent.parent
    certs_dir = base_dir / "certs"
    private_dir = base_dir / "private"

    # Only set if not already set
    if not os.getenv("MQTT_TLS_CA"):
        ca_path = certs_dir / "ca.cert.pem"
        if ca_path.exists():
            os.environ["MQTT_TLS_CA"] = str(ca_path)

    if not os.getenv("MQTT_TLS_CERT"):
        cert_path = certs_dir / f"{device_mac}.cert.pem"
        if cert_path.exists():
            os.environ["MQTT_TLS_CERT"] = str(cert_path)

    if not os.getenv("MQTT_TLS_KEY"):
        key_path = private_dir / f"{device_mac}.key.pem"
        if key_path.exists():
            os.environ["MQTT_TLS_KEY"] = str(key_path)

    os.environ["MQTT_BROKER"] = os.getenv("MQTT_BROKER", "localhost")

    from device.publisher import SecurePublisher
    publisher = SecurePublisher(device_id=device_mac, mode=mode, csv_path=csv_path)
    asyncio.run(publisher.publish_loop())

if __name__ == "__main__":
    main()
