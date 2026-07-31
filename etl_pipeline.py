from datetime import datetime
from database import get_connection
from api_fetch import get_weather

# Number of cities to fetch
CITY_LIMIT = 500

print("=" * 60)
print(f"ETL Started : {datetime.now()}")
print("=" * 60)

with open("etl_log.txt", "a", encoding="utf-8") as log:
    log.write(f"\nETL Started : {datetime.now()}\n")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Fetch top cities by population
    cur.execute("""
        SELECT city_id, city_name, latitude, longitude
        FROM cities
        ORDER BY population DESC
        LIMIT %s
    """, (CITY_LIMIT,))

    cities = cur.fetchall()

    total_processed = 0
    total_inserted = 0
    failed_count = 0

    for city in cities:

        city_id = city[0]
        city_name = city[1]
        lat = city[2]
        lon = city[3]

        total_processed += 1

        print(f"[{total_processed}/{CITY_LIMIT}] Fetching weather for {city_name}...")

        data = get_weather(lat, lon)

        if data:

            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind_speed = data["wind"]["speed"]
            condition = data["weather"][0]["main"]

            cur.execute(
                """
                INSERT INTO weather_data (
                    city_id,
                    temperature,
                    humidity,
                    pressure,
                    wind_speed,
                    weather_condition
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    city_id,
                    temperature,
                    humidity,
                    pressure,
                    wind_speed,
                    condition
                )
            )

            total_inserted += 1
            print(f"✓ {city_name} inserted")

        else:
            failed_count += 1
            print(f"✗ Failed to fetch weather for {city_name}")

    # Commit once after all inserts
    conn.commit()

    cur.close()
    conn.close()

    print("\n" + "=" * 60)
    print("ETL Completed Successfully")
    print("=" * 60)
    print(f"Cities Processed : {total_processed}")
    print(f"Records Inserted : {total_inserted}")
    print(f"Failed Requests  : {failed_count}")
    print("=" * 60)

    with open("etl_log.txt", "a", encoding="utf-8") as log:
        log.write(f"ETL Completed : {datetime.now()}\n")
        log.write(f"Cities Processed : {total_processed}\n")
        log.write(f"Records Inserted : {total_inserted}\n")
        log.write(f"Failed Requests : {failed_count}\n")

except Exception as e:

    print("ERROR:", e)

    with open("etl_log.txt", "a", encoding="utf-8") as log:
        log.write(f"ERROR : {e}\n")