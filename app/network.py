"""Near-accident prediction from the trained network (SPEC3b, 07 Round 3).

The network is trained by training/train.py and saved to models/network.joblib.
conditions has illuminance_millilux, water_micrometers and temperature_celsius.

Two safety rules sit on top of the network:
- A higher limit is never predicted to be safer than a lower one. In the training data,
  lower limits went with more near-accidents, which the conditions don't explain
  (07 Round 3), so the network must not learn "faster is safer" from it.
- The limit was never above 70 km/h in a dark or icy hour, so higher limits get at least
  the prediction for 70 km/h instead of an extrapolation.
"""

from functools import cache
from pathlib import Path

import joblib

from features import feature_row

MODEL_FILE = Path(__file__).resolve().parent.parent / "models" / "network.joblib"
TRAINED_LIMITS = [40, 50, 60, 70]  # the limits seen in dark or icy hours


@cache
def _network():
    return joblib.load(MODEL_FILE)["network"]


def _raw_prediction(conditions: dict, speed_limit: int) -> float:
    row = feature_row(
        conditions["illuminance_millilux"] / 1000,  # the network was trained on lux
        conditions["water_micrometers"],
        conditions["temperature_celsius"],
        speed_limit,
    )
    return max(0.0, float(_network().predict([row])[0]))


def predict_near_accidents(conditions: dict, speed_limit: int) -> float:
    """Predicted near-accidents per hour at this speed limit under these conditions."""
    limits = [limit for limit in TRAINED_LIMITS if limit <= speed_limit] or TRAINED_LIMITS[:1]
    return max(_raw_prediction(conditions, limit) for limit in limits)
