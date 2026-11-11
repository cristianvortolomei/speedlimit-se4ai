"""SpeedLimit GUI. Run with: streamlit run app/main.py"""

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from air_quality import fetch_air_quality
from speed_limit import set_speed_limit

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

st.set_page_config(page_title="SpeedLimit")
st.title("SpeedLimit")
st.caption("Sets the highway speed limit from the current conditions.")

st.subheader("Road conditions")
col1, col2, col3 = st.columns(3)
light_lux = col1.number_input("Light (lux)", min_value=0.0, value=10000.0, step=0.1)
water = col2.number_input("Water on the road (µm)", min_value=0, value=0, step=100)
temperature = col3.number_input("Temperature (°C)", min_value=-30, max_value=70, value=5)

st.subheader("Air quality")
source = st.radio("Source", ["Live from Open-Meteo", "Enter manually"], horizontal=True)
if source == "Live from Open-Meteo":
    col1, col2 = st.columns(2)
    latitude = col1.number_input("Latitude", value=47.27, format="%.2f")
    longitude = col2.number_input("Longitude", value=11.39, format="%.2f")
else:
    manual_aqi = st.number_input("European AQI", min_value=0, value=30)

if st.button("Set speed limit", type="primary"):
    conditions = {
        "illuminance_millilux": round(light_lux * 1000),
        "water_micrometers": int(water),
        "temperature_celsius": int(temperature),
    }
    try:
        with st.spinner("Deciding..."):
            if source == "Live from Open-Meteo":
                air = fetch_air_quality(latitude, longitude)
            else:
                air = {"european_aqi": manual_aqi}
            decision = set_speed_limit(conditions, air)
    except Exception as error:
        st.error(f"Could not set the speed limit: {error}")
        st.stop()

    st.metric("Speed limit", f"{decision.limit} km/h")
    st.write(f"**Dark:** {'yes' if decision.dark else 'no'}")
    st.write(f"**Black ice risk:** {'yes' if decision.black_ice else 'no'}")
    if decision.network_limit is not None:
        st.write(f"**Network:** {decision.network_limit} km/h")
    st.write(f"**Air quality:** {air}")
    st.write(f"**Air quality reduction:** {decision.air_reduction} km/h. {decision.air_reason}")
