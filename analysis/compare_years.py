"""Retraining (13), steps 1 and 2: compares the sensor readings of Year N and Year N+1.

1. Writes a copy of the Year N+1 readings with a header row to analysis/output/,
   so it opens cleanly in Excel. The original data file stays unchanged.
2. Prints count, average, min and max per sensor for both years side by side.

Run from the repo folder:
    .venv\\Scripts\\python analysis\\compare_years.py
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "training"))

import clean  # noqa: E402  (sensor list and types, already cleaned)

OUTPUT = ROOT / "analysis" / "output"
YEAR_N_FILE, _ = clean.YEARS["N"]
YEAR_N1_FILE, _ = clean.YEARS["N+1"]
HEADER = ";".join(clean.READING_COLUMNS)


def write_year_n1_with_header() -> Path:
    text = (clean.DATA / YEAR_N1_FILE).read_text(encoding="utf-8-sig")
    target = OUTPUT / "SensorReadingsYearNPlus1_with_header.csv"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    # Keep the original text exactly, only add the header line in front.
    target.write_text(HEADER + "\n" + text, encoding="utf-8-sig")
    return target


def sensor_names() -> dict:
    types = clean.load_sensor_types()
    names = {
        row.Sensor: types.loc[row.SensorTypeCode, "Type"]
        for row in clean.load_sensors().itertuples()
    }
    names[clean.SPEED_LIMIT_SENSOR] = "speed limit"
    return names


def summary(readings: pd.DataFrame) -> pd.DataFrame:
    return readings.groupby("Sensor")["Value"].agg(["count", "mean", "min", "max"])


def main() -> None:
    copy = write_year_n1_with_header()
    print(f"Year N+1 with header written to {copy.relative_to(ROOT)}\n")

    year_n = clean.load_readings(YEAR_N_FILE)
    year_n1 = pd.read_csv(copy, sep=";", decimal=",", encoding="utf-8-sig")
    print(f"Rows: Year N {len(year_n)}, Year N+1 {len(year_n1)}\n")

    table = summary(year_n).add_suffix(" N").join(summary(year_n1).add_suffix(" N+1"), how="outer")
    table["mean diff"] = table["mean N+1"] - table["mean N"]
    table.insert(0, "type", table.index.map(sensor_names()))

    pd.set_option("display.width", 200)
    pd.set_option("display.float_format", "{:.2f}".format)
    print(table.to_string())


if __name__ == "__main__":
    main()
