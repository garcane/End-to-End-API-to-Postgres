# %%
# =============================================================================
# ETL Pipeline — Open-Meteo Weather API → PostgreSQL
# No API key required. Non-commercial use, up to 10,000 calls/day.
# Docs: https://open-meteo.com/en/docs
# =============================================================================

import os
import json
import logging
import requests
import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import sql
from datetime import datetime, timezone
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

print("Packages loaded successfully.")

# %%
# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
load_dotenv()

DB_HOST     = os.getenv("POSTGRES_HOST")
DB_PORT     = os.getenv("POSTGRES_PORT", "5432")
DB_NAME     = os.getenv("POSTGRES_DB")
DB_USER     = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Locations to fetch — extend this list freely.
LOCATIONS = [
    {"name": "London",     "latitude": 51.5085, "longitude": -0.1257},
    {"name": "Manchester", "latitude": 53.4808, "longitude": -2.2426},
    {"name": "Edinburgh",  "latitude": 55.9533, "longitude": -3.1883},
]

# Hourly weather variables to request from Open-Meteo.
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
    "weather_code",
    "surface_pressure",
]

# %%
# =============================================================================
# EXTRACT
# =============================================================================

BASE_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather(location: dict) -> dict:
    """
    Fetch hourly weather forecast for a single location from Open-Meteo.
    Returns the raw JSON response dict, enriched with the location name.
    """
    params = {
        "latitude":  location["latitude"],
        "longitude": location["longitude"],
        "hourly":    ",".join(HOURLY_VARIABLES),
        "timezone":  "Europe/London",
        "forecast_days": 7,
    }

    logger.info("Fetching weather for %s (lat=%.4f, lon=%.4f)",
                location["name"], location["latitude"], location["longitude"])

    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    data["_location_name"] = location["name"]
    logger.info("  → %d hourly records returned.", len(data["hourly"]["time"]))
    return data


def extract_all(locations: list[dict]) -> list[dict]:
    """Fetch weather data for all locations. Returns a list of raw API dicts."""
    raw_responses = []
    for loc in locations:
        try:
            raw_responses.append(fetch_weather(loc))
        except requests.RequestException as exc:
            logger.error("Failed to fetch data for %s: %s", loc["name"], exc)
    return raw_responses


# %%
# =============================================================================
# TRANSFORM
# =============================================================================

def transform(raw_responses: list[dict]) -> pd.DataFrame:
    """
    Flatten all raw API responses into a single tidy DataFrame.

    Think of this step like ironing — the raw JSON is a crumpled
    nested structure; we press it flat so every row is one hour,
    one location, one set of measurements.
    """
    frames = []

    for resp in raw_responses:
        location_name = resp["_location_name"]
        hourly = resp["hourly"]

        df = pd.DataFrame(hourly)

        # Attach metadata
        df["location_name"] = location_name
        df["latitude"]      = resp["latitude"]
        df["longitude"]     = resp["longitude"]
        df["elevation_m"]   = resp.get("elevation", np.nan)
        df["fetched_at"]    = datetime.now(timezone.utc)

        frames.append(df)

    if not frames:
        raise ValueError("No data was extracted — check your API calls and network connection.")

    combined = pd.concat(frames, ignore_index=True)

    # ---- Column cleanup ----
    combined.columns = (
        combined.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_", regex=False)
    )

    # ---- Type casting ----
    combined["time"] = pd.to_datetime(combined["time"], utc=True, errors="coerce")

    float_cols = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "wind_direction_10m",
        "surface_pressure",
        "elevation_m",
        "latitude",
        "longitude",
    ]
    for col in float_cols:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")

    int_cols = ["weather_code"]
    for col in int_cols:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").astype("Int64")

    # ---- Deduplication ----
    before = len(combined)
    combined = combined.drop_duplicates(subset=["time", "location_name"])
    after = len(combined)
    if before != after:
        logger.info("Dropped %d duplicate rows.", before - after)

    # ---- Null audit ----
    null_summary = combined.isnull().sum()
    null_summary = null_summary[null_summary > 0]
    if not null_summary.empty:
        logger.warning("Columns with nulls after transform:\n%s", null_summary.to_string())

    logger.info("Transform complete — %d rows, %d columns.", *combined.shape)
    return combined


# %%
# =============================================================================
# LOAD
# =============================================================================

DDL = """
CREATE TABLE IF NOT EXISTS weather_forecast (
    id                      SERIAL PRIMARY KEY,
    location_name           VARCHAR(100)  NOT NULL,
    latitude                FLOAT,
    longitude               FLOAT,
    elevation_m             FLOAT,
    time                    TIMESTAMPTZ   NOT NULL,
    temperature_2m          FLOAT,
    relative_humidity_2m    FLOAT,
    precipitation           FLOAT,
    wind_speed_10m          FLOAT,
    wind_direction_10m      FLOAT,
    weather_code            INTEGER,
    surface_pressure        FLOAT,
    fetched_at              TIMESTAMPTZ,
    UNIQUE (location_name, time)
);
"""

UPSERT_SQL = """
INSERT INTO weather_forecast (
    location_name, latitude, longitude, elevation_m, time,
    temperature_2m, relative_humidity_2m, precipitation,
    wind_speed_10m, wind_direction_10m, weather_code,
    surface_pressure, fetched_at
)
VALUES (
    %(location_name)s, %(latitude)s, %(longitude)s, %(elevation_m)s, %(time)s,
    %(temperature_2m)s, %(relative_humidity_2m)s, %(precipitation)s,
    %(wind_speed_10m)s, %(wind_direction_10m)s, %(weather_code)s,
    %(surface_pressure)s, %(fetched_at)s
)
ON CONFLICT (location_name, time)
DO UPDATE SET
    temperature_2m       = EXCLUDED.temperature_2m,
    relative_humidity_2m = EXCLUDED.relative_humidity_2m,
    precipitation        = EXCLUDED.precipitation,
    wind_speed_10m       = EXCLUDED.wind_speed_10m,
    wind_direction_10m   = EXCLUDED.wind_direction_10m,
    weather_code         = EXCLUDED.weather_code,
    surface_pressure     = EXCLUDED.surface_pressure,
    fetched_at           = EXCLUDED.fetched_at;
"""


def get_connection():
    """Return a live psycopg2 connection, raising clearly if env vars are missing."""
    required = {
        "POSTGRES_HOST": DB_HOST,
        "POSTGRES_DB":   DB_NAME,
        "POSTGRES_USER": DB_USER,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return psycopg2.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def load(df: pd.DataFrame) -> None:
    """
    Load the transformed DataFrame into PostgreSQL.

    Uses an upsert (INSERT … ON CONFLICT DO UPDATE) so the pipeline
    is idempotent — safe to re-run without creating duplicate rows.
    Think of it like a smart post box: if a letter with the same
    address already arrived today, it just replaces the old one
    rather than stacking duplicates.
    """
    conn = get_connection()
    logger.info("Connected to PostgreSQL at %s:%s/%s", DB_HOST, DB_PORT, DB_NAME)

    try:
        with conn:
            with conn.cursor() as cur:
                # Ensure table exists
                cur.execute(DDL)
                logger.info("Table 'weather_forecast' verified / created.")

                # Convert DataFrame to list of dicts; handle pandas NA → None
                records = df.where(pd.notnull(df), other=None).to_dict(orient="records")

                cur.executemany(UPSERT_SQL, records)
                logger.info("Upserted %d rows into 'weather_forecast'.", len(records))

    except psycopg2.Error as exc:
        logger.error("Database error during load: %s", exc)
        raise
    finally:
        conn.close()
        logger.info("Database connection closed.")


# %%
# =============================================================================
# PIPELINE ORCHESTRATION
# =============================================================================

def run_pipeline():
    logger.info("=== ETL pipeline starting ===")

    # 1. Extract
    raw = extract_all(LOCATIONS)
    logger.info("Extract complete — %d location(s) fetched.", len(raw))

    # 2. Transform
    df = transform(raw)
    print(df.head(10).to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"\nDtypes:\n{df.dtypes.to_string()}")

    # 3. Load
    load(df)

    logger.info("=== ETL pipeline complete ===")
    return df


if __name__ == "__main__":
    result_df = run_pipeline()