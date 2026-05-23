#!/usr/bin/env python3
import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    base_dir = Path(__file__).parent.parent
    certs_dir = base_dir / "certs"
    private_dir = base_dir / "private"

    # Only set if not already set (respect user exports)
    if not os.getenv("MQTT_TLS_CA"):
        ca_path = certs_dir / "ca.cert.pem"
        if ca_path.exists():
            os.environ["MQTT_TLS_CA"] = str(ca_path)

    if not os.getenv("MQTT_TLS_CERT"):
        # Try gateway certificate from local certs
        cert_path = certs_dir / "gateway.cert.pem"
        if cert_path.exists():
            os.environ["MQTT_TLS_CERT"] = str(cert_path)

    if not os.getenv("MQTT_TLS_KEY"):
        key_path = private_dir / "gateway.key.pem"
        if key_path.exists():
            os.environ["MQTT_TLS_KEY"] = str(key_path)

    # Finally, if still no TLS certs, print a warning
    if not os.getenv("MQTT_TLS_CERT"):
        print("WARNING: No edge gateway certificate found. Running without TLS.")

    from edge.validator import EdgeValidator
    validator = EdgeValidator()
    asyncio.run(validator.run())

if __name__ == "__main__":
    main()
