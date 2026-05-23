
from pysqlcipher3 import dbapi2 as sqlite3
import threading
from config.settings import DB_PATH, DB_KEY

class Database:
    def __init__(self):
        self._local = threading.local()
        self._init_db()

    def _get_conn(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(DB_PATH)
            if DB_KEY:
                self._local.conn.execute(f"PRAGMA key = '{DB_KEY}'")
            self._init_tables(self._local.conn)
        return self._local.conn

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        if DB_KEY:
            conn.execute(f"PRAGMA key = '{DB_KEY}'")
        self._init_tables(conn)
        conn.close()

    def _init_tables(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER, device TEXT, co REAL, humidity REAL,
                light INTEGER, lpg REAL, motion INTEGER, smoke REAL,
                temp REAL, received_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS minimised_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_hash TEXT, avg_co_24h REAL, avg_lpg_24h REAL,
                avg_smoke_24h REAL, avg_temp_24h REAL, peak_light_hour INTEGER,
                motion_count_24h INTEGER, timestamp_bucket INTEGER,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        conn.commit()

    def insert_raw(self, data):
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO raw_sensor_data (ts, device, co, humidity, light, lpg, motion, smoke, temp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data.ts, data.device, data.co, data.humidity, int(data.light),
              data.lpg, int(data.motion), data.smoke, data.temp))
        conn.commit()

    def insert_minimised(self, report):  # ✅ Fixed variable name
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO minimised_reports 
            (region_hash, avg_co_24h, avg_lpg_24h, avg_smoke_24h, avg_temp_24h,
             peak_light_hour, motion_count_24h, timestamp_bucket)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (report.region_hash, report.avg_co_24h, report.avg_lpg_24h,
              report.avg_smoke_24h, report.avg_temp_24h, report.peak_light_hour,
              report.motion_count_24h, report.timestamp_bucket))
        conn.commit()

    def close(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.close()