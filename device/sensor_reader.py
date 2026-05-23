import csv
import time
import random
from pathlib import Path
from models.sensor_data import RawSensorPayload

class SensorReader:
    def __init__(self, device_id: str, simulate: bool = True):
        self.device_id = device_id
        self.simulate = simulate

    def read(self) -> RawSensorPayload:
        if self.simulate:
            return self._simulate_read()
        else:
            return self._hardware_read()

    def _simulate_read(self) -> RawSensorPayload:
        return RawSensorPayload(
            ts=int(time.time()),
            device=self.device_id,
            co=round(random.uniform(0.002, 0.006), 6),
            humidity=round(random.uniform(40, 80), 1),
            light=random.choice([True, False]),
            lpg=round(random.uniform(0.005, 0.008), 6),
            motion=random.choice([True, False]),
            smoke=round(random.uniform(0.013, 0.021), 6),
            temp=round(random.uniform(19, 28), 1)
        )

    def _hardware_read(self) -> RawSensorPayload:
        raise NotImplementedError("Hardware reading not implemented")

class CsvReplayReader:
    def __init__(self, device_id: str, csv_path: str):
        self.device_id = device_id
        self.csv_path = Path(csv_path)
        self.rows = self._load_rows_for_device()
        self.index = 0
        self.last_ts = None

    def _load_rows_for_device(self):
        rows = []
        with open(self.csv_path, 'r', encoding='utf-8-sig') as f:   # BOM is removed
            reader = csv.DictReader(f)
            # Also strip any whitespace from column names
            if reader.fieldnames:
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
            for row in reader:
                if row['device'] == self.device_id:
                    rows.append(row)
        if not rows:
            raise ValueError(f"No data for device {self.device_id} in CSV")
        return rows

    def read(self) -> RawSensorPayload:
        if self.index >= len(self.rows):
            self.index = 0  # loop
        row = self.rows[self.index]
        orig_ts = int(float(row['ts']))
        now = int(time.time())
        if self.last_ts is not None:
            delta = orig_ts - self.last_ts
            if delta > 0 and delta < 60:
                time.sleep(delta)  # simulate real-time delay
        self.last_ts = orig_ts
        payload = RawSensorPayload(
            ts=now,  # use current time to simulate live
            device=self.device_id,
            co=float(row['co']),
            humidity=float(row['humidity']),
            light=row['light'].upper() == 'TRUE',
            lpg=float(row['lpg']),
            motion=row['motion'].upper() == 'TRUE',
            smoke=float(row['smoke']),
            temp=float(row['temp'])
        )
        self.index += 1
        return payload
