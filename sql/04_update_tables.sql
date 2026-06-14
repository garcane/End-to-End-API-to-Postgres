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