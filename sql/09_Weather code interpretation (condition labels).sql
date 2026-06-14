SELECT 
    location_name,
    time,
    weather_code,
    CASE weather_code
        WHEN 0 THEN 'Clear sky'
        WHEN 1 THEN 'Mainly clear'
        WHEN 2 THEN 'Partly cloudy'
        WHEN 3 THEN 'Overcast'
        WHEN 45 THEN 'Fog'
        WHEN 48 THEN 'Depositing rime fog'
        WHEN 51 THEN 'Light drizzle'
        WHEN 53 THEN 'Moderate drizzle'
        WHEN 55 THEN 'Dense drizzle'
        WHEN 61 THEN 'Slight rain'
        WHEN 63 THEN 'Moderate rain'
        WHEN 65 THEN 'Heavy rain'
        WHEN 71 THEN 'Slight snow fall'
        WHEN 73 THEN 'Moderate snow fall'
        WHEN 75 THEN 'Heavy snow fall'
        ELSE 'Other'
    END AS weather_condition,
    temperature_2m,
    precipitation
FROM weather_forecast
WHERE weather_code IS NOT NULL
ORDER BY time DESC
LIMIT 20;