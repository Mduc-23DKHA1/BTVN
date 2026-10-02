import pandas as pd
import sqlite3

csv_path = "HCM_AQI_2023_2026.csv"
df = pd.read_csv(csv_path)

db_path = "AirQualityIndex.db"
conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS AQI (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    date TEXT NOT NULL,

    aqi REAL,
    pm25 REAL,
    pm10 REAL,
    co REAL,
    so2 REAL,
    no2 REAL,
    o3 REAL,

    avgtemp_c REAL,
    avghumidity REAL,
    maxwind_kph REAL,
    totalprecip_mm REAL,
    uv REAL,
    pm_ratio REAL
)
"""
)

for _, row in df.iterrows():

    cursor.execute(
        """
        INSERT INTO AQI (
            date,
            aqi,
            pm25,
            pm10,
            co,
            so2,
            no2,
            o3,
            avgtemp_c,
            avghumidity,
            maxwind_kph,
            totalprecip_mm,
            uv,
            pm_ratio
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            row["date"],
            row["aqi"],
            row["pm25"],
            row["pm10"],
            row["co"],
            row["so2"],
            row["no2"],
            row["o3"],
            row["avgtemp_c"],
            row["avghumidity"],
            row["maxwind_kph"],
            row["totalprecip_mm"],
            row["uv"],
            row["pm_ratio"],
        ),
    )

conn.commit()

cursor.execute(
    """
    SELECT *
    FROM aqi_data
    LIMIT 5
"""
)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
