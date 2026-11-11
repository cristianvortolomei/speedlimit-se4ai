"""Turns the conditions and a speed limit into the network's inputs (07 Round 3).

Used by both training and the app, so the features are always computed the same way.
Each feature is normalized into 0 to 1 using the Min and Max from SensorTypes,
like the ML Architecture deck projects age onto 0 to 200.
"""

import math

FEATURES = ["light", "water", "temperature", "speed_limit"]

# Light is log-scaled, because it ranges from 0 to over 100,000 lux and half the hours
# are below 0.5 lux. The range is log10(0.001) to log10(1,000,000), the SensorTypes Max.
LIGHT_OFFSET_LUX = 0.001
LIGHT_LOG_MIN, LIGHT_LOG_MAX = -3, 6
WATER_MIN, WATER_MAX = 0, 10000  # micrometers
TEMPERATURE_MIN, TEMPERATURE_MAX = -30, 70  # °C
LIMIT_MIN, LIMIT_MAX = 40, 80  # km/h


def scale(value: float, low: float, high: float) -> float:
    return (value - low) / (high - low)


def feature_row(
    light_lux: float, water_micrometers: float, temperature_celsius: float, speed_limit: float
) -> list[float]:
    light_log = math.log10(light_lux + LIGHT_OFFSET_LUX)
    return [
        scale(light_log, LIGHT_LOG_MIN, LIGHT_LOG_MAX),
        scale(water_micrometers, WATER_MIN, WATER_MAX),
        scale(temperature_celsius, TEMPERATURE_MIN, TEMPERATURE_MAX),
        scale(speed_limit, LIMIT_MIN, LIMIT_MAX),
    ]
