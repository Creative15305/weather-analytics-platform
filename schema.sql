-- ============================================================
-- Weather Monitoring & Analytics Platform — Database Schema
-- ============================================================
-- Note: This schema is reverse-engineered from the columns used
-- across the project's queries (etl_pipeline.py, weather_dashboard.py).
-- Adjust data types/constraints as needed to match your exact setup.
-- ============================================================

-- Cities table: sourced from the Kaggle "Indian Cities Database"
-- (https://www.kaggle.com/datasets/parulpandey/indian-cities-database)
CREATE TABLE cities (
    city_id     SERIAL PRIMARY KEY,
    city_name   VARCHAR(100) NOT NULL,
    latitude    NUMERIC(9,6) NOT NULL,
    longitude   NUMERIC(9,6) NOT NULL,
    population  BIGINT
);

-- Weather data table: populated by the ETL pipeline from the
-- OpenWeatherMap API, one row per reading per city
CREATE TABLE weather_data (
    id                 SERIAL PRIMARY KEY,
    city_id            INTEGER NOT NULL REFERENCES cities(city_id),
    temperature        NUMERIC(5,2),
    humidity           INTEGER,
    pressure           INTEGER,
    wind_speed         NUMERIC(5,2),
    weather_condition  VARCHAR(50),
    recorded_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Helpful index for the ROW_NUMBER() / PARTITION BY queries
-- used throughout the dashboard to fetch the latest reading per city
CREATE INDEX idx_weather_city_recorded
    ON weather_data (city_id, recorded_time DESC);
