"""Reads the current air quality and asks the LLM how much to lower the limit (REQ2, SPEC5)."""

import json
import os

import requests
from google import genai
from google.genai import types

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
MODEL = "gemini-3.5-flash-lite"
AQI_THRESHOLD = 40
LLM_TIMEOUT_MS = 15_000  # NFR2: stop waiting for the LLM after 15 seconds
ALLOWED_REDUCTIONS = [10, 20, 30, 40]

POLLUTANTS = {
    "european_aqi": "European AQI",
    "pm2_5": "PM2.5 (µg/m³)",
    "pm10": "PM10 (µg/m³)",
    "nitrogen_dioxide": "NO2 (µg/m³)",
    "ozone": "Ozone (µg/m³)",
}

INSTRUCTIONS = """You decide how much the speed limit on a highway should be lowered because of air quality.
Lower speeds reduce traffic emissions. The normal limit is 80 km/h.

Current air quality at the highway:
{measurements}

European AQI bands: 40-60 moderate, 60-80 poor, 80-100 very poor, above 100 extremely poor.

The air quality is moderate or worse, so the limit must be lowered.
Choose a reduction of 10, 20, 30 or 40 km/h. Worse air quality must never get a smaller reduction.
Give the reason in one short sentence."""

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "reduction_kmh": {"type": "integer", "enum": ALLOWED_REDUCTIONS},
        "reason": {"type": "string"},
    },
    "required": ["reduction_kmh", "reason"],
}


def fetch_air_quality(latitude: float, longitude: float) -> dict:
    response = requests.get(
        AIR_QUALITY_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(POLLUTANTS),
        },
        timeout=15,
    )
    response.raise_for_status()
    current = response.json()["current"]
    return {name: current[name] for name in POLLUTANTS}


def decide_reduction(air_quality: dict) -> tuple[int, str]:
    """Returns the reduction in km/h and the reason. Raises if the LLM's answer is unusable."""
    if air_quality["european_aqi"] <= AQI_THRESHOLD:
        return 0, f"AQI {AQI_THRESHOLD} or below, so no reduction."

    measurements = "\n".join(
        f"- {POLLUTANTS[name]}: {value}" for name, value in air_quality.items()
    )
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"],
        http_options=types.HttpOptions(timeout=LLM_TIMEOUT_MS),  # NFR2
    )
    response = client.models.generate_content(
        model=MODEL,
        contents=INSTRUCTIONS.format(measurements=measurements),
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_json_schema=ANSWER_SCHEMA,
        ),
    )
    answer = json.loads(response.text)
    reduction = answer["reduction_kmh"]
    if reduction not in ALLOWED_REDUCTIONS:
        raise ValueError(f"unexpected reduction from the LLM: {reduction}")
    return reduction, answer["reason"]
