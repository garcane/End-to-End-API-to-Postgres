SELECT 
    location_name,
    time,
    temperature_2m,
    wind_speed_10m,
    precipitation,
    weather_code
FROM weather_forecast
WHERE 
    temperature_2m > 30               OR  -- heat
    temperature_2m < 0                OR  -- freezing
    wind_speed_10m > 50               OR  -- storm force
    precipitation > 5                 OR  -- heavy rain (mm per hour)
    weather_code IN (65, 75, 95, 96)      -- severe codes: heavy rain, snow, thunder
ORDER BY time DESC;