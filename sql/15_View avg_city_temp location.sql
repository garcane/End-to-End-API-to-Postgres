CREATE VIEW avg_city_temp AS
SELECT
    location_name,
    AVG(temperature_2m) AS avg_temp
FROM weather_forecast
GROUP BY location_name;