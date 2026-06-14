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