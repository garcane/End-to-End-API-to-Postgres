WITH daily_avg AS (
    SELECT 
        location_name,
        DATE(time) AS forecast_day,
        AVG(temperature_2m) AS avg_temp
    FROM weather_forecast
    GROUP BY location_name, DATE(time)
)
SELECT 
    forecast_day,
    location_name,
    ROUND(avg_temp::numeric, 1) AS avg_temp,
    RANK() OVER (PARTITION BY forecast_day ORDER BY avg_temp DESC) AS temp_rank
FROM daily_avg
ORDER BY forecast_day, temp_rank;