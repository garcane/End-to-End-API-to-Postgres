WITH london AS (
    SELECT time, temperature_2m AS london_temp
    FROM weather_forecast
    WHERE location_name = 'London'
),
edinburgh AS (
    SELECT time, temperature_2m AS edinburgh_temp
    FROM weather_forecast
    WHERE location_name = 'Edinburgh'
)
SELECT 
    london.time,
    london.london_temp,
    edinburgh.edinburgh_temp,
    ROUND((london.london_temp - edinburgh.edinburgh_temp)::numeric, 1) AS temp_diff_c
FROM london
JOIN edinburgh ON london.time = edinburgh.time
ORDER BY ABS(london.london_temp - edinburgh.edinburgh_temp) DESC
LIMIT 10;