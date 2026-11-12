"""Combines the router, the network and the air quality decision into one speed limit."""

from dataclasses import dataclass

import air_quality
import network
import router

NORMAL_LIMIT = 80
MISSING_READINGS_LIMIT = 60
CANDIDATE_LIMITS = [40, 50, 60, 70, 80]
NETWORK_LIMITS = [40, 50, 60, 70]  # the limit was never 80 in a dark or icy hour
MAX_NEAR_ACCIDENTS_PER_HOUR = 1


@dataclass
class Decision:
    limit: int
    calculated_limit: int
    override: int | None
    dark: bool | None
    black_ice: bool | None
    predictions: dict[int, float] | None
    network_limit: int | None
    air_reduction: int
    air_reason: str
    warnings: list[str]


def choose_network_limit(predictions: dict[int, float]) -> int:
    """SPEC3b: the highest limit with at most one predicted near-accident per hour, else 40."""
    safe = [
        limit for limit, near_accidents in predictions.items()
        if near_accidents <= MAX_NEAR_ACCIDENTS_PER_HOUR
    ]
    return max(safe, default=min(NETWORK_LIMITS))


def set_speed_limit(conditions: dict, air: dict | None, override: int | None = None) -> Decision:
    """A reading in conditions is None when it is missing. air is None when it could not be read.
    override is the control room's limit, or None."""
    warnings = []
    limit = NORMAL_LIMIT
    dark = black_ice = None
    predictions = network_limit = None

    if None in conditions.values():
        # REQ6: missing readings mean 60 km/h until they return.
        warnings.append(
            f"Light, water or temperature reading missing. Limit set to {MISSING_READINGS_LIMIT} km/h."
        )
        limit = MISSING_READINGS_LIMIT
    else:
        dark = router.is_dark(conditions["illuminance_millilux"])
        black_ice = router.has_black_ice_risk(
            conditions["water_micrometers"], conditions["temperature_celsius"]
        )
        if dark or black_ice:
            predictions = {
                candidate: network.predict_near_accidents(conditions, candidate)
                for candidate in NETWORK_LIMITS
            }
            network_limit = choose_network_limit(predictions)
            if min(predictions.values()) > MAX_NEAR_ACCIDENTS_PER_HOUR:
                warnings.append(
                    f"No limit reaches at most {MAX_NEAR_ACCIDENTS_PER_HOUR} predicted near-accident "
                    f"per hour. {network_limit} km/h is used."
                )
            limit = network_limit

    # REQ7: if the air quality or the LLM's answer is missing, skip the air quality reduction.
    air_reduction, air_reason = 0, "Not available."
    if air is None:
        warnings.append("Air quality could not be read. No air quality reduction applied.")
    else:
        try:
            air_reduction, air_reason = air_quality.decide_reduction(air)
        except Exception as error:
            warnings.append(
                f"No usable answer from the LLM ({type(error).__name__}). "
                "No air quality reduction applied."
            )

    # REQ4: when both apply, the lower limit wins.
    calculated_limit = min(limit, NORMAL_LIMIT - air_reduction)

    # REQ8: the control room's override replaces the calculated limit.
    final_limit = override if override is not None else calculated_limit

    return Decision(
        final_limit, calculated_limit, override, dark, black_ice,
        predictions, network_limit, air_reduction, air_reason, warnings,
    )
