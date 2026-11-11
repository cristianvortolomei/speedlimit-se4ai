"""Logs every decision to a CSV file (SPEC7)."""

import csv
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "decisions.csv"

COLUMNS = [
    "time", "illuminance_millilux", "water_micrometers", "temperature_celsius",
    "european_aqi", "predicted_near_accidents", "network_limit",
    "air_reduction", "air_reason", "calculated_limit", "override", "limit", "warnings",
]


def log_decision(conditions: dict, air: dict | None, decision) -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    is_new = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new:
            writer.writerow(COLUMNS)
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            conditions["illuminance_millilux"],
            conditions["water_micrometers"],
            conditions["temperature_celsius"],
            air["european_aqi"] if air else None,
            decision.predictions and {
                limit: round(value, 2) for limit, value in decision.predictions.items()
            },
            decision.network_limit,
            decision.air_reduction,
            decision.air_reason,
            decision.calculated_limit,
            decision.override,
            decision.limit,
            " | ".join(decision.warnings),
        ])
