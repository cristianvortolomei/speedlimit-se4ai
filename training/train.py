"""Trains the network (07 Round 3) and saves it to models/network.joblib.

    python training/train.py

The network predicts the number of near-accidents in an hour from light, water,
temperature and the speed limit. It is trained on the dark or icy hours of Year N,
because those are the only hours in which the app uses it.
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.neural_network import MLPRegressor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

import clean  # noqa: E402
from features import FEATURES, feature_row  # noqa: E402

MODEL_FILE = ROOT / "models" / "network.joblib"
METRICS_FILE = ROOT / "models" / "metrics.json"

# Split by whole days, because neighbouring hours are almost identical.
TEST_DAYS = range(25, 32)
SEED = 42


def network_hours(year: str = "N"):
    table = clean.hourly_table(year)
    return table[table["dark"] | table["black_ice"]].reset_index(drop=True)


def inputs(table) -> np.ndarray:
    return np.array([
        feature_row(row.light_lux, row.water_micrometers, row.temperature_celsius, row.speed_limit)
        for row in table.itertuples()
    ])


def build_network() -> MLPRegressor:
    return MLPRegressor(
        hidden_layer_sizes=(16, 8),
        activation="relu",
        alpha=0.01,  # weight decay against overfitting on only a few hundred rows
        max_iter=3000,
        random_state=SEED,
    )


def main() -> None:
    hours = network_hours("N")
    is_test = hours["Day"].isin(TEST_DAYS)
    train, test = hours[~is_test], hours[is_test]

    network = build_network()
    network.fit(inputs(train), train["near_accidents"])

    predicted = network.predict(inputs(test)).clip(min=0)
    baseline = np.full(len(test), train["near_accidents"].mean())
    metrics = {
        "training_hours": len(train),
        "test_hours": len(test),
        "test_mae": round(mean_absolute_error(test["near_accidents"], predicted), 3),
        "baseline_mae": round(mean_absolute_error(test["near_accidents"], baseline), 3),
        "mean_prediction_per_limit": {},
    }

    # What the network predicts on average for each limit, over all dark or icy hours.
    for limit in [40, 50, 60, 70, 80]:
        at_limit = hours.assign(speed_limit=limit)
        metrics["mean_prediction_per_limit"][limit] = round(
            float(network.predict(inputs(at_limit)).clip(min=0).mean()), 3
        )

    MODEL_FILE.parent.mkdir(exist_ok=True)
    joblib.dump({"network": network, "features": FEATURES}, MODEL_FILE)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2) + "\n")

    print(f"Trained on {len(train)} hours (days 1-24), tested on {len(test)} hours (days 25-31).")
    print(f"Test mean absolute error: {metrics['test_mae']} near-accidents per hour")
    print(f"Always predicting the training average: {metrics['baseline_mae']}")
    print("Mean prediction per limit:", metrics["mean_prediction_per_limit"])
    print(f"Saved to {MODEL_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
