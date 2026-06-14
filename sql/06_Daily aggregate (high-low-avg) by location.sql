SELECT 
    location_name,
    DATE(time) AS forecast_day,
    ROUND(AVG(temperature_2m)::numeric, 1) AS daily_avg_temp,
    MIN(temperature_2m) AS daily_min_temp,
    MAX(temperature_2m) AS daily_max_temp,
    ROUND(AVG(wind_speed_10m)::numeric, 1) AS daily_avg_wind_kmh,
    SUM(precipitation) AS daily_precip_mm
FROM weather_forecast
GROUP BY location_name, DATE(time)
ORDER BY location_name, forecast_day;