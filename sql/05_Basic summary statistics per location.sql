SELECT 
    location_name,
    COUNT(*) AS total_hours,
    ROUND(AVG(temperature_2m)::numeric, 1) AS avg_temp_c,
    ROUND(MIN(temperature_2m)::numeric, 1) AS min_temp_c,
    ROUND(MAX(temperature_2m)::numeric, 1) AS max_temp_c,
    ROUND(AVG(relative_humidity_2m)::numeric, 1) AS avg_humidity_pct,
    ROUND(SUM(precipitation)::numeric, 2) AS total_precip_mm
FROM weather_forecast
GROUP BY location_name
ORDER BY location_name;