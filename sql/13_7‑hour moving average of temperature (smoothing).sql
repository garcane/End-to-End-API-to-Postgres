SELECT 
    location_name,
    time,
    temperature_2m,
    ROUND(AVG(temperature_2m) OVER (
        PARTITION BY location_name 
        ORDER BY time 
        ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    )::numeric, 1) AS temp_moving_avg_7h
FROM weather_forecast
ORDER BY location_name, time;