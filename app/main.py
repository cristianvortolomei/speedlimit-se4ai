"""SpeedLimit GUI. Run with: streamlit run app/main.py"""

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from air_quality import fetch_air_quality
from decision_log import log_decision
from speed_limit import CANDIDATE_LIMITS, set_speed_limit

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

RECALCULATE_SECONDS = 3600  # SPEC6: every hour

st.set_page_config(page_title="SpeedLimit")
st.title("SpeedLimit")
st.caption("Sets the highway speed limit from the current conditions.")

st.subheader("Road conditions")
st.caption("Leave a field empty if that reading is missing.")
col1, col2, col3 = st.columns(3)
light_lux = col1.number_input(
    "Light (lux)", min_value=0.0, value=None, step=0.1, placeholder="e.g. 10000",
    help="Dark below 0.5 lux (500 millilux)",
)
water = col2.number_input(
    "Water on the road (µm)", min_value=0, value=None, step=100, placeholder="e.g. 0",
    help="Black ice above 1000 µm and below 0 °C",
)
temperature = col3.number_input(
    "Temperature (°C)", min_value=-30, max_value=70, value=None, placeholder="e.g. 5"
)

st.subheader("Air quality")
source = st.radio("Source", ["Live from Open-Meteo", "Enter manually"], horizontal=True)
if source == "Live from Open-Meteo":
    col1, col2 = st.columns(2)
    latitude = col1.number_input("Latitude", value=47.27, format="%.2f")
    longitude = col2.number_input("Longitude", value=11.39, format="%.2f")
else:
    manual_aqi = st.number_input(
        "European AQI", min_value=0, value=30, help="Above 40 the LLM decides the reduction"
    )

st.subheader("Control room")
override = st.selectbox(
    "Override", [None, *CANDIDATE_LIMITS],
    format_func=lambda limit: "No override" if limit is None else f"{limit} km/h",
)
automatic = st.toggle("Recalculate every hour")


@st.fragment(run_every=RECALCULATE_SECONDS if automatic else None)
def decide_and_show():
    if not automatic and not st.button("Set speed limit", type="primary"):
        return

    conditions = {
        "illuminance_millilux": None if light_lux is None else round(light_lux * 1000),
        "water_micrometers": None if water is None else int(water),
        "temperature_celsius": None if temperature is None else int(temperature),
    }
    with st.spinner("Deciding..."):
        if source == "Live from Open-Meteo":
            try:
                air = fetch_air_quality(latitude, longitude)
            except Exception:
                air = None
        else:
            air = {"european_aqi": manual_aqi}
        decision = set_speed_limit(conditions, air, override)
        log_decision(conditions, air, decision)

    st.metric("Speed limit", f"{decision.limit} km/h")
    if decision.override is not None:
        st.info(f"Set by the control room. Calculated limit: {decision.calculated_limit} km/h.")
    for warning in decision.warnings:
        st.warning(f"Control room: {warning}")

    def yes_no(value):
        return "unknown" if value is None else ("yes" if value else "no")

    st.write(f"**Dark:** {yes_no(decision.dark)}")
    st.write(f"**Black ice risk:** {yes_no(decision.black_ice)}")
    if decision.predictions is not None:
        predictions = ", ".join(
            f"{limit} km/h: {value:.2f}" for limit, value in decision.predictions.items()
        )
        st.write(f"**Network:** {decision.network_limit} km/h")
        st.caption(f"Predicted near-accidents per hour: {predictions}")
    if air is not None:
        st.write(f"**Air quality:** {air}")
        st.write(f"**Air quality reduction:** {decision.air_reduction} km/h. {decision.air_reason}")


decide_and_show()
