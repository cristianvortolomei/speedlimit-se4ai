"""Decides whether darkness or the weather calls for a lower speed limit (SPEC1, SPEC2)."""

DARK_BELOW_MILLILUX = 500
ICE_WATER_ABOVE_MICROMETERS = 1000
ICE_TEMPERATURE_BELOW_CELSIUS = 0


def is_dark(illuminance_millilux: int) -> bool:
    return illuminance_millilux < DARK_BELOW_MILLILUX


def has_black_ice_risk(water_micrometers: int, temperature_celsius: int) -> bool:
    return (
        water_micrometers > ICE_WATER_ABOVE_MICROMETERS
        and temperature_celsius < ICE_TEMPERATURE_BELOW_CELSIUS
    )


def weather_reduction_needed(
    illuminance_millilux: int, water_micrometers: int, temperature_celsius: int
) -> bool:
    return is_dark(illuminance_millilux) or has_black_ice_risk(
        water_micrometers, temperature_celsius
    )
