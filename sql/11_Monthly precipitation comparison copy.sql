SELECT 
    location_name,
    DATE_TRUNC('month', time) AS month,
    ROUND(SUM(precipitation)::numeric, 1) AS total_precip_mm,
    ROUND(AVG(precipitation)::numeric, 2) AS avg_hourly_precip_mm,
    COUNT(*) FILTER (WHERE precipitation > 0) AS wet_hours
FROM weather_forecast
WHERE time >= '2026-06-01' AND time < '2026-07-01'
GROUP BY location_name, DATE_TRUNC('month', time)
ORDER BY location_name, month;