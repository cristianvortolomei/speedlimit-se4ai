"""Near-accident prediction from the trained network (SPEC3b).

Placeholder until the trained network is ready (Turn 9). The made-up formula below
only exists so the app runs. Keep the same function signature so the rest of the
app does not need to change.

conditions has illuminance_millilux, water_micrometers and temperature_celsius.
Add more inputs to the GUI in main.py if the network needs them.
"""


def predict_near_accidents(conditions: dict, speed_limit: int) -> float:
    """Predicted near-accidents per hour at this speed limit under these conditions."""
    return speed_limit / 60
