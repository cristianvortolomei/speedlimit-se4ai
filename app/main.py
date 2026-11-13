"""SpeedLimit GUI. Run with: streamlit run app/main.py"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from air_quality import fetch_air_quality
from decision_log import log_decision
from speed_limit import (
    CANDIDATE_LIMITS, MAX_NEAR_ACCIDENTS_PER_HOUR, MISSING_READINGS_LIMIT, NORMAL_LIMIT,
    set_speed_limit,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

RECALCULATE_SECONDS = 3600  # SPEC6: every hour
AQI_BANDS = [(20, "good"), (40, "fair"), (60, "moderate"), (80, "poor"), (100, "very poor")]
RED, NAVY = "#c8102e", "#152230"
CHIP_COLORS = {
    "good": ("#e3f4e8", "#1e6b34"),
    "warn": ("#fdecc8", "#8a4b00"),
    "bad": ("#fbe0e0", "#9b1c1c"),
    "unknown": ("#ececec", "#555555"),
}

STYLE = f"""
<style>
.block-container {{ padding-top: 2rem; padding-bottom: 1rem; }}
@keyframes fade-in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
.sign {{
  width: 132px; height: 132px; border-radius: 50%; background: #ffffff; border: 13px solid {RED};
  display: flex; align-items: center; justify-content: center; margin: 4px auto;
  animation: fade-in .3s ease-out;
}}
.sign span {{ font: 800 56px/1 Arial, sans-serif; color: {NAVY}; }}
.sign.waiting {{ border-color: #9aa3ad; }}
.sign.waiting span {{ color: #9aa3ad; }}
.chips {{ margin-bottom: 6px; }}
.chips span {{
  display: inline-block; padding: 3px 11px; margin: 0 6px 6px 0; border-radius: 999px;
  font-size: .85rem; font-weight: 600;
}}
</style>
"""


def aqi_band(aqi: float) -> str:
    for upper, name in AQI_BANDS:
        if aqi <= upper:
            return name
    return "extremely poor"


def speed_sign(text: str, waiting: bool = False) -> str:
    return f'<div class="sign{" waiting" if waiting else ""}"><span>{text}</span></div>'


def chip(text: str, kind: str) -> str:
    bg, fg = CHIP_COLORS[kind]
    return f'<span style="background:{bg};color:{fg}">{text}</span>'


def yes_no_chip(label: str, value: bool | None) -> str:
    if value is None:
        return chip(f"{label}: unknown", "unknown")
    return chip(f"{label}: {'yes' if value else 'no'}", "warn" if value else "good")


def air_chip(air: dict | None) -> str:
    if air is None:
        return chip("Air quality: not available", "unknown")
    band = aqi_band(air["european_aqi"])
    kind = "good" if band in ("good", "fair") else "warn" if band == "moderate" else "bad"
    return chip(f"AQI {air['european_aqi']}: {band}", kind)


def predictions_chart(predictions: dict[int, float]) -> alt.LayerChart:
    data = pd.DataFrame({
        "Speed limit": [f"{limit} km/h" for limit in predictions],
        "Near-accidents per hour": list(predictions.values()),
    })
    bars = alt.Chart(data).mark_bar(cornerRadiusEnd=3, size=38).encode(
        x=alt.X("Speed limit:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Near-accidents per hour:Q", title="Near-accidents per hour"),
        color=alt.condition(
            alt.datum["Near-accidents per hour"] <= MAX_NEAR_ACCIDENTS_PER_HOUR,
            alt.value("#2e9e5b"), alt.value("#d99a1e"),
        ),
        tooltip=["Speed limit", alt.Tooltip("Near-accidents per hour:Q", format=".2f")],
    )
    target = alt.Chart(pd.DataFrame({"target": [MAX_NEAR_ACCIDENTS_PER_HOUR]})).mark_rule(
        color=RED, strokeDash=[6, 4], size=2
    ).encode(y=alt.Y("target:Q", title="Near-accidents per hour"))
    return (bars + target).properties(height=170)


st.set_page_config(page_title="SpeedLimit", page_icon="🚦", layout="wide")
st.markdown(STYLE, unsafe_allow_html=True)
st.markdown("## SpeedLimit")
st.caption("Sets the highway speed limit from light, road conditions and air quality.")

inputs, result = st.columns([1, 1.25], gap="large")

with inputs:
    with st.container(border=True):
        st.markdown("**Road conditions**")
        col1, col2, col3 = st.columns(3)
        light_lux = col1.number_input(
            "Light (lux)", min_value=0.0, value=None, step=0.1, placeholder="e.g. 10000",
            help="Dark below 0.5 lux (500 millilux). Leave empty if the reading is missing.",
        )
        water = col2.number_input(
            "Water (µm)", min_value=0.0, value=None, step=100.0, format="%.1f",
            placeholder="e.g. 0",
            help="Black ice above 1000 µm and below 0 °C. Leave empty if the reading is missing.",
        )
        temperature = col3.number_input(
            "Temperature (°C)", min_value=-30.0, max_value=70.0, value=None, step=0.1,
            format="%.1f", placeholder="e.g. 5", help="Leave empty if the reading is missing.",
        )

    with st.container(border=True):
        st.markdown("**Air quality**")
        source = st.radio(
            "Source", ["Live from Open-Meteo", "Enter manually"], horizontal=True,
            label_visibility="collapsed",
        )
        if source == "Live from Open-Meteo":
            col1, col2 = st.columns(2)
            latitude = col1.number_input("Latitude", value=47.27, format="%.2f")
            longitude = col2.number_input("Longitude", value=11.39, format="%.2f")
        else:
            manual_aqi = st.number_input(
                "European AQI", min_value=0, value=30, help="Above 40 the LLM decides the reduction"
            )

    with st.container(border=True):
        st.markdown("**Control room**")
        col1, col2 = st.columns([1.3, 1], vertical_alignment="bottom")
        override = col1.selectbox(
            "Override", [None, *CANDIDATE_LIMITS],
            format_func=lambda limit: "No override" if limit is None else f"{limit} km/h",
        )
        automatic = col2.toggle("Recalculate every hour")


@st.fragment(run_every=RECALCULATE_SECONDS if automatic else None)
def decide_and_show():
    clicked = st.button("Set speed limit", type="primary", use_container_width=True)
    if not automatic and not clicked:
        sign, text = st.columns([1, 2.2], vertical_alignment="center")
        sign.markdown(speed_sign("–", waiting=True), unsafe_allow_html=True)
        text.caption("Enter the conditions on the left and press **Set speed limit**.")
        return

    conditions = {
        "illuminance_millilux": None if light_lux is None else round(light_lux * 1000),
        "water_micrometers": water,
        "temperature_celsius": temperature,
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

    if decision.network_limit is not None:
        road, road_note = decision.network_limit, "Dark or icy: set by the network"
    elif decision.dark is None:
        road, road_note = MISSING_READINGS_LIMIT, "A reading is missing"
    else:
        road, road_note = NORMAL_LIMIT, "Not dark or icy"
    air_limit = NORMAL_LIMIT - decision.air_reduction
    if air is None:
        air_note = "Not available: no reduction"
    elif decision.air_reduction == 0:
        air_note = "No reduction"
    else:
        air_note = f"LLM: −{decision.air_reduction} km/h"
    final_note = (f"Override (calculated {decision.calculated_limit} km/h)"
                  if decision.override is not None else "The lower one wins")

    sign, details = st.columns([1, 2.2], vertical_alignment="center")
    sign.markdown(speed_sign(str(decision.limit)), unsafe_allow_html=True)
    with details:
        st.markdown(
            '<div class="chips">' + yes_no_chip("Dark", decision.dark)
            + yes_no_chip("Black ice", decision.black_ice) + air_chip(air) + "</div>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns(3)
        col1.metric("Road", f"{road} km/h")
        col1.caption(road_note)
        col2.metric("Air quality", f"{air_limit} km/h")
        col2.caption(air_note)
        col3.metric("Final", f"{decision.limit} km/h")
        col3.caption(final_note)

    for warning in decision.warnings:
        st.warning(warning)

    if decision.predictions is not None:
        st.altair_chart(predictions_chart(decision.predictions), use_container_width=True)
        st.caption("Network's prediction per speed limit. Red line: the target of at most 1 per hour.")
    elif air is not None and decision.air_reduction:
        st.caption(f"LLM's reason: {decision.air_reason}")


with result:
    decide_and_show()
