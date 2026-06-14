WITH hourly_change AS (
    SELECT 
        location_name,
        time,
        temperature_2m,
        LAG(temperature_2m) OVER (PARTITION BY location_name ORDER BY time) AS prev_temp
    FROM weather_forecast
)
SELECT 
    location_name,
    time,
    temperature_2m,
    prev_temp,
    ROUND((temperature_2m - prev_temp)::numeric, 1) AS temp_change_1h
FROM hourly_change
WHERE prev_temp IS NOT NULL
ORDER BY ABS(temperature_2m - prev_temp) DESC
LIMIT 10;