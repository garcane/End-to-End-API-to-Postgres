SELECT 
    location_name,
    time,
    wind_speed_10m AS wind_speed_kmh,
    wind_direction_10m,
    temperature_2m
FROM weather_forecast
ORDER BY wind_speed_10m DESC
LIMIT 5;