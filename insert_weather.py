from database import get_connection
from api_fetch import get_weather

lat = 28.6667
lon = 77.2167

city_id = 355

data = get_weather(lat, lon)

if data:

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind_speed = data["wind"]["speed"]
    condition = data["weather"][0]["main"]

    conn = get_connection()
    cur = conn.cursor()

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
        VALUES (%s,%s,%s,%s,%s,%s)
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

    conn.commit()

    cur.close()
    conn.close()

    print("Weather data inserted successfully!")