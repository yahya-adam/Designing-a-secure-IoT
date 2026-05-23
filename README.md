# Privacy‑Centric IoT System for Home Environment

This project implements a secure, privacy‑preserving IoT telemetry pipeline. Sensor data is transmitted over TLS‑encrypted MQTT, validated, minimised (with differential privacy), stored in an SQLCipher‑encrypted database, and finally visualised via Grafana through a secure API layer.

## Architecture Overview

![System Architecture](./images/architecture.png "Click to enlarge")

## Components

### 1. MQTT Broker (Mosquitto)
- Listens on port **8883** (TLS).
- Server certificate: `broker.cert.pem` + `broker.key.pem`.
- Client certificates are **accepted but not required** (`require_certificate false`).  
  Devices and the edge gateway can present their own certificates for identification.

### 2. IoT Devices (Publishers)
- Simulated devices read from CSV files (or generate random data) and publish to topic `privenergy/sensors/<MAC>/raw`.
- Each device uses a **client certificate** and the **CA certificate** to authenticate the broker.
- **No database access** – devices only publish.

### 3. Edge Gateway (Subscriber + Processor)
- Subscribes to `privenergy/sensors/+/raw` over TLS.
- **Validates** incoming payloads against a Pydantic schema.
- **Minimises & anonymises** data:  
  - Applies Laplace mechanism (differential privacy) to numerical values.  
  - Aggregates into 1‑hour buckets (can be extended to 24h).
- **Stores** raw and minimised data into an **SQLCipher‑encrypted SQLite** database.

### 4. Encrypted Database (SQLCipher)
- SQLite database encrypted with AES‑256 via `pysqlcipher3`.
- The encryption key (`DB_KEY`) is passed as an environment variable to the **edge** and **API** containers.
- Without the correct key, the database is unreadable.

### 5. FastAPI Gateway (Secure API)
- Runs a REST API that:
  - Decrypts the database using the same `DB_KEY`.
  - Requires an **API key** (`X-API-Key` header) for all requests.
- Endpoints:
  - `GET /health` – status check.
  - `GET /api/latest?limit=N` – last N sensor readings.
  - `GET /api/devices` – list of all device MACs.
  - `GET /api/timeseries?device=...&from_ts=...&to_ts=...` – historical data.
- Listens on port **8000** (internal network only, not exposed to host unless needed).

### 6. Grafana (Visualisation)
- Uses the **Infinity** data source plugin to query the FastAPI gateway.
- Dashboards display real‑time and historical sensor values (temperature, CO, LPG, etc.).
- Secured with admin credentials (change from default).


## Security Measures

| Layer               | Protection                                      |
|---------------------|-------------------------------------------------|
| MQTT transport      | TLS 1.2/1.3 (port 8883)                         |
| Broker authentication| Client certificates (optional) + username       |
| Database at rest    | SQLCipher (AES‑256)                             |
| API access          | API key (`X-API-Key` header)                    |
| Data minimisation   | Differential privacy (Laplace noise)            |
| Network isolation   | All containers on a dedicated Docker bridge    |

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development, optional)
- OpenSSL (to generate certificates)

### 1. Generate Certificates (if not already present)
```bash
# Create CA, broker, gateway, and device certificates
# See `gen_certs.sh` script (or use your own PKI)

2. Prepare CSV Data

Place CSV files for each device in ./data/ with columns:
ts,device,co,humidity,light,lpg,motion,smoke,temp

3. Configure Environment
DB_KEY=your-strong-sqlcipher-key
API_KEY=your-grafana-api-key

4. Build & Run
docker compose up --build

5. Verify

    MQTT broker: openssl s_client -connect localhost:8883 -CAfile certs/ca.cert.pem

    API health: curl -H "X-API-Key: $API_KEY" http://localhost:8000/health

    Grafana: http://localhost:3000 (admin/admin)


Visualisation in Grafana

    Install Infinity plugin in Grafana.

    Add data source:

        URL: http://api:8000

        Header: X-API-Key = your API key.

    Create dashboards using the API endpoints:

        Table of latest values: /api/latest?limit=100

        Time series of temperature: /api/timeseries?device=$device&from_ts=$__from_ms/1000&to_ts=$__to_ms/1000

    Add a device variable querying /api/devices.

File Structure
.
├── api/                  # FastAPI application
├── certs/                # CA, server, client certificates
├── config/               # Python settings module
├── data/                 # CSV files for devices
├── device/               # Device publisher logic
├── edge/                 # Edge gateway (validator, minimiser)
├── models/               # Pydantic data models
├── storage/              # Database handler (SQLCipher)
├── mosquitto/config/     # Mosquitto configuration
├── private/              # Private keys (keep secure!)
├── docker-compose.yml
├── Dockerfile.*          # Device, edge, api, mosquitto
├── requirements-*.txt
└── .env                  # Secrets (DB_KEY, API_KEY)


Limitations & Future Work

    Client certificate enforcement – currently optional; can be enabled by setting require_certificate true in mosquitto.conf.

    24‑hour aggregation – currently uses per‑reading noise; implement true daily aggregates.

    Key rotation – SQLCipher supports REKEY, but not yet implemented.

    Scaling – SQLite is single‑writer; for multiple edges, switch to PostgreSQL + encryption at application level.

