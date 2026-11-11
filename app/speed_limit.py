"""Combines the router, the network and the air quality decision into one speed limit."""

from dataclasses import dataclass

import air_quality
import network
import router

NORMAL_LIMIT = 80


@dataclass
class Decision:
    limit: int
    dark: bool
    black_ice: bool
    network_limit: int | None
    air_reduction: int
    air_reason: str


def set_speed_limit(conditions: dict, air: dict) -> Decision:
    dark = router.is_dark(conditions["illuminance_millilux"])
    black_ice = router.has_black_ice_risk(
        conditions["water_micrometers"], conditions["temperature_celsius"]
    )

    network_limit = network.predict_limit(conditions) if dark or black_ice else None
    air_reduction, air_reason = air_quality.decide_reduction(air)

    # When both apply, the lower limit wins.
    limit = NORMAL_LIMIT
    if network_limit is not None:
        limit = min(limit, network_limit)
    limit = min(limit, NORMAL_LIMIT - air_reduction)

    return Decision(limit, dark, black_ice, network_limit, air_reduction, air_reason)
