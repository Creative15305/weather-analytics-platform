-- ============================================================
-- Weather Monitoring & Analytics Platform — Additional Analytics Queries
-- ============================================================
-- These queries supplement the core window-function queries used
-- in weather_dashboard.py, demonstrating aggregation, joins, and
-- filtering on top of the same schema.
-- ============================================================

-- 1. Average temperature per weather condition
SELECT
    weather_condition,
    ROUND(AVG(temperature), 2) AS avg_temperature
FROM weather_data
GROUP BY weather_condition
ORDER BY avg_temperature DESC;


-- 2. Cities with the highest number of weather readings recorded
SELECT
    c.city_name,
    COUNT(w.id) AS total_readings
FROM weather_data w
JOIN cities c ON w.city_id = c.city_id
GROUP BY c.city_name
ORDER BY total_readings DESC
LIMIT 10;


-- 3. Currently hot cities (latest reading per city, filtered above a threshold)
WITH latest_weather AS (
    SELECT
        city_id,
        temperature,
        ROW_NUMBER() OVER (
            PARTITION BY city_id
            ORDER BY recorded_time DESC
        ) AS rn
    FROM weather_data
)
SELECT
    c.city_name,
    lw.temperature
FROM latest_weather lw
JOIN cities c ON lw.city_id = c.city_id
WHERE lw.rn = 1 AND lw.temperature > 35
ORDER BY lw.temperature DESC;


-- 4. Cities currently experiencing rain (latest reading per city)
WITH latest_weather AS (
    SELECT
        city_id,
        weather_condition,
        ROW_NUMBER() OVER (
            PARTITION BY city_id
            ORDER BY recorded_time DESC
        ) AS rn
    FROM weather_data
)
SELECT
    c.city_name
FROM latest_weather lw
JOIN cities c ON lw.city_id = c.city_id
WHERE lw.rn = 1 AND lw.weather_condition = 'Rain'
ORDER BY c.city_name;


-- 5. Day-wise average temperature trend across all cities
SELECT
    DATE(recorded_time) AS reading_date,
    ROUND(AVG(temperature), 2) AS avg_temperature
FROM weather_data
GROUP BY DATE(recorded_time)
ORDER BY reading_date;
