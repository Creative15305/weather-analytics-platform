import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="India Live Weather Dashboard",
    layout="wide"
)

# =====================================================
# DATABASE CONNECTION
# =====================================================

conn = get_connection()

# =====================================================
# PAGE TITLE
# =====================================================

st.title("India Live Weather Dashboard")
st.caption("Real-Time Weather Monitoring System")

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Dashboard Controls")

city_df = pd.read_sql(
    """
    SELECT
        city_id,
        city_name
    FROM latest_weather
    ORDER BY city_name;
    """,
    conn
)

# Duplicate city names count
city_df["count"] = city_df.groupby("city_name")["city_name"].transform("count")

# Display name
city_df["display_name"] = city_df.apply(
    lambda row:
        f"{row['city_name']} (ID: {row['city_id']})"
        if row["count"] > 1
        else row["city_name"],
    axis=1
)

selected_option = st.sidebar.selectbox(
    "Location",
    ["India"] + city_df["display_name"].tolist()
)

if selected_option == "India":
    selected_city = "India"
    selected_city_id = None
else:
    row = city_df.loc[
        city_df["display_name"] == selected_option
    ].iloc[0]

    selected_city = row["city_name"]
    selected_city_id = int(row["city_id"])


# ==========================================
# SIDEBAR STATUS
# ==========================================

if selected_city == "India":

    weather_df = pd.read_sql(
        """
        SELECT DISTINCT weather_condition
        FROM weather_data
        ORDER BY weather_condition;
        """,
        conn
    )

    selected_weather = st.sidebar.selectbox(
        "Weather Condition",
        ["All"] + weather_df["weather_condition"].tolist()
    )

    st.sidebar.info("Showing Weather Across India")

else:

    selected_weather = "All"

    st.sidebar.success(
        f"Selected City : {selected_city}"
    )

# =====================================================
# KPI QUERIES
# =====================================================

total_cities = pd.read_sql(
    """
    SELECT COUNT(*) AS total
    FROM latest_weather;
    """,
    conn
).iloc[0]["total"]

total_records = pd.read_sql(
    """
    SELECT COUNT(*) AS total
    FROM weather_data;
    """,
    conn
).iloc[0]["total"]

last_updated = pd.read_sql(
    """
    SELECT MAX(recorded_time) AS last_updated
    FROM weather_data;
    """,
    conn
).iloc[0]["last_updated"]

# =====================================================
# KPI CARDS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Cities",
        f"{total_cities:,}"
    )

with col2:
    st.metric(
        "Total Records",
        f"{total_records:,}"
    )

with col3:

    last_updated = pd.to_datetime(
        last_updated
    ).strftime("%d-%m-%Y %I:%M %p")

    st.metric(
        "Last Updated",
        last_updated
    )

st.divider()

# =====================================================
# CURRENT WEATHER
# =====================================================

if selected_city != "India":

    current_weather = pd.read_sql(
        """
        SELECT
            c.city_name,
            w.temperature,
            w.humidity,
            w.pressure,
            w.wind_speed,
            w.weather_condition,
            w.recorded_time

        FROM weather_data w

        JOIN cities c
        ON w.city_id = c.city_id

        WHERE c.city_id = %s

        ORDER BY w.recorded_time DESC

        LIMIT 1;
        """,
        conn,
        params=(selected_city_id,)
    )

    if not current_weather.empty:

        row = current_weather.iloc[0]

        st.subheader(f"Current Weather - {selected_city}")

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.metric("Temperature", f"{row['temperature']:.1f} °C")

        with c2:
            st.metric("Humidity", f"{row['humidity']} %")

        with c3:
            st.metric("Pressure", f"{row['pressure']} hPa")

        with c4:
            st.metric("Wind Speed", f"{row['wind_speed']:.1f} m/s")

        with c5:
            st.metric("Weather", row["weather_condition"])

    st.divider()
# =====================================================
# TEMPERATURE TREND
# =====================================================

if selected_city != "India":

    trend_df = pd.read_sql(
        """
        SELECT
            recorded_time,
            temperature
        FROM weather_data
        WHERE city_id = %s
        ORDER BY recorded_time;
        """,
        conn,
       params=(selected_city_id,)
    )

    st.subheader(f"Temperature Trend - {selected_city}")

    fig = px.line(
        trend_df,
        x="recorded_time",
        y="temperature",
        markers=True
    )

    fig.update_layout(
        height=450,
        xaxis_title="Recorded Time",
        yaxis_title="Temperature (°C)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()
# =====================================================
# LATEST WEATHER RECORDS
# =====================================================

st.subheader(f"Latest Weather Records - {selected_city}")

latest_records = pd.read_sql(
    """
    SELECT
        w.temperature,
        w.humidity,
        w.pressure,
        w.wind_speed,
        w.weather_condition,
        w.recorded_time
    FROM weather_data w
    JOIN cities c
        ON w.city_id = c.city_id
    WHERE c.city_id = %s
    ORDER BY w.recorded_time DESC
    LIMIT 20;
    """,
    conn,
    params=(selected_city_id,)
)

# ---------------------------------------
# Formatting
# ---------------------------------------

latest_records["temperature"] = pd.to_numeric(
    latest_records["temperature"],
    errors="coerce"
)

latest_records["wind_speed"] = pd.to_numeric(
    latest_records["wind_speed"],
    errors="coerce"
)

latest_records = latest_records.dropna(
    subset=["temperature"]
)

latest_records["temperature"] = latest_records["temperature"].round(1)
latest_records["wind_speed"] = latest_records["wind_speed"].round(1)

latest_records["recorded_time"] = pd.to_datetime(
    latest_records["recorded_time"]
).dt.strftime("%d-%m-%Y %I:%M %p")

latest_records = latest_records.rename(
    columns={
        "temperature": "Temperature (°C)",
        "humidity": "Humidity (%)",
        "pressure": "Pressure (hPa)",
        "wind_speed": "Wind Speed (m/s)",
        "weather_condition": "Weather",
        "recorded_time": "Recorded Time"
    }
)

st.dataframe(
    latest_records,
    use_container_width=True,
    hide_index=True
)

st.divider()
# =====================================================
# TOP 10 HOTTEST & COLDEST CITIES
# =====================================================

latest_temp = pd.read_sql(
    """
    WITH latest_weather AS
    (
        SELECT
            c.city_name,
            w.temperature,
            ROW_NUMBER() OVER (
                PARTITION BY w.city_id
                ORDER BY w.recorded_time DESC
            ) AS rn

        FROM weather_data w
        JOIN cities c
            ON w.city_id = c.city_id
    )

    SELECT
        city_name,
        temperature
    FROM latest_weather
    WHERE rn = 1;
    """,
    conn
)

# ------------------------------------------
# Top 10 Hottest
# ------------------------------------------

top_hot = latest_temp.nlargest(10, "temperature")

# ------------------------------------------
# Top 10 Coldest
# ------------------------------------------

top_cold = latest_temp.nsmallest(10, "temperature")

col_hot, col_cold = st.columns(2)

# =====================================================
# HOTTEST CITIES
# =====================================================

with col_hot:

    st.subheader("Top 10 Hottest Cities")

    fig_hot = px.bar(
        top_hot,
        x="temperature",
        y="city_name",
        orientation="h",
        color="temperature",
        text="temperature",
        color_continuous_scale="Oranges"
    )

    fig_hot.update_traces(
    texttemplate="%{text:.1f} °C",
    textposition="outside",
    cliponaxis=False
)

    fig_hot.update_layout(
    height=450,
    xaxis_title="Temperature (°C)",
    yaxis_title="",
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
    margin=dict(r=70)
)

    st.plotly_chart(
        fig_hot,
        use_container_width=True
    )

# =====================================================
# COLDEST CITIES
# =====================================================

with col_cold:

    st.subheader("Top 10 Coldest Cities")

    fig_cold = px.bar(
        top_cold,
        x="temperature",
        y="city_name",
        orientation="h",
        color="temperature",
        text="temperature",
        color_continuous_scale="Blues"
    )

    fig_cold.update_traces(
    texttemplate="%{text:.1f} °C",
    textposition="outside",
    cliponaxis=False
)

    fig_cold.update_layout(
    height=450,
    xaxis_title="Temperature (°C)",
    yaxis_title="",
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
    margin=dict(r=70)
)

    st.plotly_chart(
        fig_cold,
        use_container_width=True
    )

st.divider()
import plotly.graph_objects as go

# =====================================================
# WEATHER CONDITION DISTRIBUTION
# =====================================================

st.subheader("Weather Condition Distribution")

weather_condition_df = pd.read_sql(
    """
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
    """,
    conn
)
 
fig = px.pie(
    weather_condition_df,
    names="weather_condition",
    values="total_cities",
    hole=0.55,
    title="Current Weather Conditions Across India"
)

fig.update_traces(
    textinfo="label+percent",
    textposition="outside",
    hovertemplate="<b>%{label}</b><br>Percentage: %{percent}<extra></extra>"
)

fig.update_layout(
    legend_title="Weather"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# =====================================================
# INDIA LIVE WEATHER MAP
# =====================================================

map_df = pd.read_sql(
    """
    WITH latest_weather AS (
        SELECT
            city_id,
            temperature,
            humidity,
            weather_condition,
            recorded_time,
            ROW_NUMBER() OVER (
                PARTITION BY city_id
                ORDER BY recorded_time DESC
            ) AS rn
        FROM weather_data
    )

    SELECT
    c.city_id,
    c.city_name,
    c.latitude,
    c.longitude,
    lw.temperature,
    lw.humidity,
    lw.weather_condition
    FROM cities c
    JOIN latest_weather lw
        ON c.city_id = lw.city_id
    WHERE lw.rn = 1;
    """,
    conn
)

# ==========================================
# Apply Weather Filter (Only for India View)
# ==========================================

if selected_city == "India":

    if selected_weather != "All":

        map_df = map_df[
            map_df["weather_condition"] == selected_weather
        ]

st.subheader("India Live Weather Map")

# ----------------------------------------
# Selected city details
# ----------------------------------------

if selected_city == "India":

    selected = pd.DataFrame()

    center_lat = 23.5
    center_lon = 78.9629
    zoom = 3.8

else:

    selected = map_df[
        map_df["city_id"] == selected_city_id
    ]

    center_lat = float(selected.iloc[0]["latitude"])
    center_lon = float(selected.iloc[0]["longitude"])
    zoom = 11
# ----------------------------------------
# Base Map
# ----------------------------------------

fig_map = px.scatter_map(
    map_df,
    lat="latitude",
    lon="longitude",
    color="temperature",
    size="temperature",
    hover_name="city_name",
    hover_data={
    "humidity": True,
    "weather_condition": True,
    "latitude": True,
    "longitude": True
},
    color_continuous_scale="Turbo",
    zoom=zoom,
    center={
        "lat": center_lat,
        "lon": center_lon
    },
    height=700
)

# ----------------------------------------
# Highlight Selected City
# ----------------------------------------

if not selected.empty:

    fig_map.add_trace(

        go.Scattermap(

            lat=[center_lat],
            lon=[center_lon],

            mode="markers+text",

            text=[selected_city],

            textposition="top center",

            marker=dict(
                size=24,
                color="red"
            ),

            name="Selected City"

        )

    )

fig_map.update_layout(

    map=dict(

        center=dict(
            lat=center_lat,
            lon=center_lon
        ),

        zoom=zoom

    ),

    margin=dict(
        l=0,
        r=0,
        t=0,
        b=0
    )

)

st.plotly_chart(
    fig_map,
    use_container_width=True
)

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
"""
<div style="text-align:center;color:gray">

###Real-Time Weather Data Engineering Project

Developed by **Srijan Baranwal**

Python • PostgreSQL • SQL • ETL • REST API • Streamlit • Plotly • Power BI

</div>
""",
unsafe_allow_html=True
)

# =====================================================
# CLOSE DATABASE
# =====================================================

conn.close()