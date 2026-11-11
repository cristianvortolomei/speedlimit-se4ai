"""Data cleaning (06 Round 3): turns the raw CSV files into one row per hour.

Each row has the mean light, water and temperature of that hour, the speed limit,
the number of near-accidents and accidents, and whether it was dark or icy.

Run on its own to print a summary:
    python training/clean.py
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

import router  # noqa: E402  (the same dark and black ice rules as the app)

DATA = ROOT / "data"
SENSORS_FILE = "Case_Study_Speed_Limit_Sensors_V100.csv"
SENSOR_TYPES_FILE = "Case_Study_Speed_Limit_SensorTypes_V100.csv"
YEARS = {
    "N": (
        "Case_Study_Speed_Limit_SensorReadingsYearN_V100.csv",
        "Case_Study_Speed_Limit_AccidentsYearN_V100.csv",
    ),
    "N+1": (
        "Case_Study_Speed_Limit_SensorReadingsYearNPlus1_V100.csv",
        "AccidentsYearNPlus1_V100.csv",
    ),
}

READING_COLUMNS = ["Month", "Day", "Hour", "Minute", "Second", "Sensor", "Value"]
HOUR_KEY = ["Month", "Day", "Hour"]
SPEED_LIMIT_SENSOR = -1
NEAR_ACCIDENT_COLUMNS = ["CloseCarCm", "CloseGuardrailCm", "SkidAngle"]

# Column names for the sensor types we keep, after cleaning the type codes.
TYPE_COLUMNS = {
    "L": "light_lux",
    "W": "water_micrometers",
    "T": "temperature_celsius",
    "H": "humidity_percent",
    "TR": "traffic_cars_per_second",
}


def read_csv(name: str, **options) -> pd.DataFrame:
    # utf-8-sig drops the byte order mark that five of the six files start with.
    return pd.read_csv(DATA / name, sep=";", decimal=",", encoding="utf-8-sig", **options)


def load_sensor_types() -> pd.DataFrame:
    types = read_csv(SENSOR_TYPES_FILE)
    for column in ["SensorTypeCode", "Type", "Unit"]:
        types[column] = types[column].str.strip()  # "W " and "degrees   "
    # T was used for both temperature and traffic. Traffic gets its own code.
    types.loc[types["Type"] == "traffic", "SensorTypeCode"] = "TR"
    # Assumption: "hm/h" is a typo for km/h.
    types.loc[types["Unit"] == "hm/h", "Unit"] = "km/h"
    return types.set_index("SensorTypeCode")


def load_sensors() -> pd.DataFrame:
    sensors = read_csv(SENSORS_FILE).rename(columns={"SensorID": "Sensor"})
    sensors["SensorTypeCode"] = sensors["SensorTypeCode"].str.strip()
    # Sensor 16 is coded T, but its values (1.85 to 30, following the noise sensor) are traffic.
    sensors.loc[sensors["Sensor"] == 16, "SensorTypeCode"] = "TR"
    # Sensor 19 has readings but is not listed. Its values follow sensors 15 and 18 (temperature).
    missing = pd.DataFrame({"Sensor": [19], "SensorTypeCode": ["T"]})
    return pd.concat([sensors, missing], ignore_index=True)


def load_readings(name: str) -> pd.DataFrame:
    with (DATA / name).open(encoding="utf-8-sig") as file:
        has_header = file.readline().startswith("Month")
    if has_header:
        return read_csv(name)
    # The Year N+1 file has no header row. It has the same columns as Year N.
    return read_csv(name, header=None, names=READING_COLUMNS)


def hourly_readings(readings: pd.DataFrame) -> pd.DataFrame:
    """One row per hour: the mean per sensor type, plus the speed limit."""
    types = load_sensor_types()
    readings = readings.merge(load_sensors(), on="Sensor", how="left")

    # Sensor -1 is the speed limit, not a measurement.
    limits = (
        readings[readings["Sensor"] == SPEED_LIMIT_SENSOR]
        .groupby(HOUR_KEY)["Value"].first().rename("speed_limit")
    )

    measured = readings[readings["Sensor"] != SPEED_LIMIT_SENSOR].copy()
    unknown = measured["SensorTypeCode"].isna()
    if unknown.any():
        print(f"Ignoring {unknown.sum()} readings from unknown sensors.")
        measured = measured[~unknown]

    # Values outside the type's Min and Max count as missing.
    low = measured["SensorTypeCode"].map(types["Min"])
    high = measured["SensorTypeCode"].map(types["Max"])
    measured.loc[~measured["Value"].between(low, high), "Value"] = None

    # The mean ignores missing values, so a missing reading is filled by the
    # other sensors of the same type in that hour (imputation).
    hourly = measured.pivot_table(
        index=HOUR_KEY, columns="SensorTypeCode", values="Value", aggfunc="mean"
    )
    hourly = hourly[list(TYPE_COLUMNS)].rename(columns=TYPE_COLUMNS)
    return hourly.join(limits)


def hourly_events(accidents: pd.DataFrame) -> pd.DataFrame:
    """Near-accidents and accidents per hour."""
    accidents = accidents.drop(columns="LicencePlate")  # personal data, not needed
    # Assumption: the accident files count hours from 1 to 24, the readings from 0 to 23.
    accidents["Hour"] = accidents["Hour"] - 1

    is_near_accident = accidents[NEAR_ACCIDENT_COLUMNS].notna().any(axis=1)
    is_accident = accidents["Damage"].notna()
    # Rows with neither (one per file) are dropped by only counting these two kinds.

    near = accidents[is_near_accident].groupby(HOUR_KEY).size().rename("near_accidents")
    crashes = accidents[is_accident].groupby(HOUR_KEY).size().rename("accidents")
    return pd.concat([near, crashes], axis=1)


def hourly_table(year: str = "N") -> pd.DataFrame:
    readings_file, accidents_file = YEARS[year]
    hourly = hourly_readings(load_readings(readings_file))
    events = hourly_events(read_csv(accidents_file))

    # Hours without a row in the accidents file had no events (imputation with 0).
    hourly = hourly.join(events).fillna({"near_accidents": 0, "accidents": 0})
    hourly[["near_accidents", "accidents"]] = hourly[["near_accidents", "accidents"]].astype(int)

    hourly["dark"] = hourly["light_lux"] * 1000 < router.DARK_BELOW_MILLILUX
    hourly["black_ice"] = (
        (hourly["water_micrometers"] > router.ICE_WATER_ABOVE_MICROMETERS)
        & (hourly["temperature_celsius"] < router.ICE_TEMPERATURE_BELOW_CELSIUS)
    )
    return hourly.reset_index()


if __name__ == "__main__":
    for year in YEARS:
        table = hourly_table(year)
        network_hours = table[table["dark"] | table["black_ice"]]
        print(
            f"Year {year}: {len(table)} hours, {len(network_hours)} dark or icy, "
            f"{table['near_accidents'].sum()} near-accidents, {table['accidents'].sum()} accidents, "
            f"{table.isna().sum().sum()} missing values"
        )
