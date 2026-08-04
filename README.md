# Weather Monitoring & Analytics Platform

An end-to-end data engineering project that collects real-time weather data for Indian cities, stores it in a normalized PostgreSQL database, and visualizes it through an interactive Streamlit dashboard.

<!-- Optional: add a banner screenshot of your dashboard here -->
<!-- ![Dashboard Preview](assets/dashboard_preview.png) -->

---

## Overview

This project automates the full lifecycle of weather data — from ingestion to analytics:

**OpenWeatherMap API → ETL Pipeline (Python) → PostgreSQL → Streamlit Dashboard**

The ETL script fetches live weather data for the top cities by population, validates and inserts it into PostgreSQL, and logs each run. The Streamlit dashboard then queries the latest readings per city (using window functions) to power live visualizations — hottest/coldest cities, weather condition distribution, and an India-wide live map.

---

## Data Sources

- **City metadata** (names, coordinates, population): [Indian Cities Database](https://www.kaggle.com/datasets/parulpandey/indian-cities-database) — Kaggle dataset by Parul Pandey, providing coordinates of prominent Indian cities.
- **Live weather readings**: [OpenWeatherMap API](https://openweathermap.org/api), fetched per city using the coordinates above.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Source | OpenWeatherMap API |
| Ingestion & ETL | Python, `requests`, `psycopg2` |
| Database | PostgreSQL |
| Querying / Analytics | SQL (CTEs, Window Functions) |
| Dashboard | Streamlit, Plotly |

---

## Key Features

- **Automated ETL pipeline** (`etl_pipeline.py`): Fetches live weather data (temperature, humidity, pressure, wind speed, condition) for the top cities by population from OpenWeatherMap, and bulk-inserts it into PostgreSQL with success/failure tracking and logging (`etl_log.txt`).
- **Latest-reading resolution with window functions**: Since each city has multiple historical readings, a `ROW_NUMBER() OVER (PARTITION BY city_id ORDER BY recorded_time DESC)` pattern is used throughout to always pull the most recent reading per city.
- **Interactive Streamlit dashboard**: India-wide live weather map, Top 10 hottest/coldest cities, and weather condition distribution — all powered by live SQL queries against PostgreSQL.
- **Modular codebase**: Separated concerns across `config.py` (settings), `database.py` (connection handling), `api_fetch.py` (API layer), and `etl_pipeline.py` (orchestration).

---

## Sample SQL Queries

**Getting the latest reading per city (core pattern used across the dashboard):**
```sql
WITH latest_weather AS (
    SELECT
        c.city_name,
        w.temperature,
        ROW_NUMBER() OVER (
            PARTITION BY w.city_id
            ORDER BY w.recorded_time DESC
        ) AS rn
    FROM weather_data w
    JOIN cities c ON w.city_id = c.city_id
)
SELECT city_name, temperature
FROM latest_weather
WHERE rn = 1;
```

**Weather condition distribution across India (latest reading per city, grouped):**
```sql
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
    weather_condition,
    COUNT(*) AS total_cities
FROM latest_weather
WHERE rn = 1
GROUP BY weather_condition
ORDER BY total_cities DESC;
```

**Selecting top cities by population to fetch weather for (ETL pipeline):**
```sql
SELECT city_id, city_name, latitude, longitude
FROM cities
ORDER BY population DESC
LIMIT %s;
```

**Inserting a new weather reading:**
```sql
INSERT INTO weather_data (
    city_id, temperature, humidity, pressure, wind_speed, weather_condition
)
VALUES (%s, %s, %s, %s, %s, %s);
```

A few additional aggregation/join-based queries (average temperature by condition, most-tracked cities, current hot cities) are available in [`analytics_queries.sql`](analytics_queries.sql).

---

## Project Structure

```
weather-analytics-platform/
│
├── README.md
├── schema.sql             # PostgreSQL table definitions (cities, weather_data)
├── analytics_queries.sql  # Additional aggregation/join/filter queries
├── config.py              # DB and API configuration (use .env in production — see Setup)
├── database.py            # PostgreSQL connection handler
├── api_fetch.py           # OpenWeatherMap API wrapper
├── etl_pipeline.py        # Main ETL job — fetches & inserts weather data for top cities
├── insert_weather.py      # Single-city insert script (used for testing/debugging)
├── test_api.py            # API connectivity test
├── test_db.py             # Database connectivity test
├── weather_dashboard.py   # Streamlit dashboard (map, top 10 hot/cold, condition distribution)
├── requirements.txt
└── .env.example           # Template for environment variables (never commit real .env)
```

---

## Dashboard Screenshots

**Power BI Dashboard — India Live Weather Overview**
Live map of 500+ cities, KPI cards (total cities, total records), Top 10 hottest/coldest cities, average temperature trend, and weather condition distribution.

<img width="1338" height="752" alt="Screenshot 2026-08-01 011832" src="https://github.com/user-attachments/assets/82e39047-4f40-4264-b666-d42282acc889" />


**Streamlit Dashboard — Top 10 Hottest / Coldest Cities**
Interactive view with location and weather-condition filters, showing live temperature rankings across India.

<img width="1910" height="813" alt="Screenshot 2026-08-01 012144" src="https://github.com/user-attachments/assets/59e7845d-a6b3-4306-8788-f3f5fc83d56f" />


---

## How to Run

1. Clone the repository
   ```bash
   git clone https://github.com/<your-username>/weather-analytics-platform.git
   cd weather-analytics-platform
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```bash
   cp .env.example .env
   # Add your OpenWeatherMap API key and PostgreSQL credentials to .env
   ```
   > **Important:** `config.py` originally held these values directly. Before publishing this repo, move them into a `.env` file and load them with `python-dotenv`, so no real credentials are ever committed.

4. Set up the database
   ```bash
   psql -U <username> -d <database> -f schema.sql
   ```
   Then populate the `cities` table using the [Indian Cities Database](https://www.kaggle.com/datasets/parulpandey/indian-cities-database) from Kaggle (city name, latitude, longitude, population).

5. Run the ETL pipeline
   ```bash
   python etl_pipeline.py
   ```

6. Launch the dashboard
   ```bash
   streamlit run weather_dashboard.py
   ```

---

## Notes

- API keys and database credentials should never be committed — use a `.env` file (see `.env.example`) and ensure `.env` is listed in `.gitignore`.
- This project was built independently during a data engineering internship; all code and queries shown here reflect original work.
- The `venv/` (virtual environment) folder should not be committed — add it to `.gitignore`.

---

## Author

**Srijan Baranwal**

