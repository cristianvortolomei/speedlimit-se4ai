"""Router tests from exercise 11, Round 3. Run with: pytest"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import router  # noqa: E402


@pytest.mark.parametrize(
    "case, illuminance_millilux, water_micrometers, temperature_celsius, expected",
    [
        ("TC1 just dark", 499, 0, 10, True),
        ("TC2 just icy", 500, 1001, -1, True),
        ("TC3 not enough water", 500, 1000, -1, False),
        ("TC4 not cold enough", 500, 1001, 0, False),
    ],
)
def test_weather_reduction_needed(
    case, illuminance_millilux, water_micrometers, temperature_celsius, expected
):
    assert (
        router.weather_reduction_needed(illuminance_millilux, water_micrometers, temperature_celsius)
        == expected
    ), case
