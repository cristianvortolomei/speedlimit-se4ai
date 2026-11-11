# 6. Data problems (case study, slide 16, and ML Architecture deck)

What errors are in the data (inconsistencies, redundancies, missing or wrong values)? How will you deal with each one? What cleaning is needed, and where do you use imputation and how?

## Round 1

- The Year N+1 sensor readings file has no header row. The column names can be inferred from the Year N sensor readings file.
- The sensor type code `T` is used for two sensor types (temperature and traffic). We could tell them apart by checking the unit each sensor provides, or change the value of one of the type codes.
- Some sensor IDs in the readings are not listed in the possible IDs in the sensors file.
- There is only one month of data.
- Some sensors may have invalid negative values.
- Damage is stored as integers, and we don't know what the numbers mean.
- Sensor readings have a minute value, but accidents do not.
- There are null or empty values.

## Round 2

Checked against the V100 files in [`data/`](../data/). Kind says what the fix is: **cleaning** (repair or reformat), **imputation** (fill in a value), **decision** (an assumption we document), or **none** (not an error).

### Sensor types (`SensorTypes`)

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| Code `T` is used for two types | Temperature and traffic are both `T`. Sensors 7, 15, 16 and 18 are all coded `T`. | Give traffic its own code (`TR`) in the cleaned copy. Sensors 15 and 18 read −15 to 12, so they are temperature. Sensor 16 reads 1.85 to 30 and rises and falls with noise sensor 3 (correlation 0.995), so it is traffic. Sensor 7 has no readings, so its type can't be told. | Cleaning |
| Trailing spaces | Code `W ` and unit `degrees   `. `W` in the sensors file does not match `W `. | Trim every text field when loading. | Cleaning |
| Wrong units | Wind strength is in `hm/h`, probably km/h. Air pressure is in `mmHG` with a range of 900 to 1000, which fits hPa (normal air pressure is about 760 mmHg). | Correct wind to km/h. Air pressure has no readings at all (see sensor 17), so only document it. | Decision |
| Light unit differs from the spec | Light is in lux, but SPEC1 says dark is below 500 millilux. | Compare against 0.5 lux. Don't convert the readings. | Decision |

### Sensors (`Sensors`)

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| Sensor 19 is not listed | 744 readings, but no row in the sensors file. Values −15.7 to 13.0, correlation 0.996 to 0.998 with temperature sensors 15 and 18. | Add it as a temperature sensor in the cleaned copy, and document the assumption. | Decision |
| Sensors 7, 10 and 17 never report | Listed, but no readings in either year. 17 is the only air pressure sensor, so there is no air pressure data at all. | Leave them out of the features. Nothing to impute from. | Cleaning |
| Sensor -1 is not a sensor | It is the speed limit (case study, slide 6), stored as a reading. | Split it out into its own column during cleaning. | Cleaning |
| Column names differ | `SensorID` in the sensors file, `Sensor` in the readings. | Rename when loading. | Cleaning |

### Sensor readings (`SensorReadings`)

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| Year N+1 has no header | The first line is already data. | Use the column names from Year N. Every row has the same 7 fields. | Cleaning |
| Decimal commas | `0,00`, `110000,11` | Parse with a comma as the decimal separator. | Cleaning |
| Readings are not on the hour | One reading per sensor per hour, at a random minute and second. Only 3 of 12,648 are at :00:00. | Group by day and hour, so all sensors and the speed limit line up in one row per hour. | Cleaning |
| Several sensors measure the same thing | 3 water (1, 8, 11), 3 light (2, 9, 12), 3 temperature (15, 18, 19), 2 wind strength (6, 14), 2 wind direction (5, 13). They agree closely (correlation 0.955 to 0.998). | Average them into one value per type per hour. If one is missing, the others still give a value. | Cleaning, imputation |
| Wind sensors disagree on calm | Sensor 6 reads 0 in 388 hours, sensor 14 in 224. Wind direction means nothing when there is no wind. | Treat direction as missing when strength is 0, or leave wind direction out. | Decision |
| Only January | Both years are January only (31 days, 744 hours). | Can't be cleaned. The network never sees mild or summer conditions, so document it as a limit and only trust it in winter. | Decision |
| Negative values | Only in temperature sensors 15, 18 and 19 (502 of 744 hours each). Below 0 °C is normal in January. Every value is inside its type's Min and Max. | None. Add a range check with Min and Max to the cleaning code so future data is checked. | None |
| Byte order mark | Five of the six files start with a UTF-8 BOM, which sticks to the first column name. | Read with `utf-8-sig`. | Cleaning |

### Accidents (`Accidents`)

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| No Minute column | Month, Day, Hour, Second, but no Minute. | Use the hour only and join to readings by day and hour. | Decision |
| Hours run 1 to 24 | Readings use 0 to 23. Accidents have no hour 0, and 44 rows have hour 24 (31 in Year N+1). | Assume accident hours are counted from 1 and subtract 1. Document it and ask the teacher. | Decision |
| Two kinds of event in one table | 32 accidents (Damage filled) and 964 near-accidents (exactly one of CloseCarCm, CloseGuardrailCm, SkidAngle filled). | Add an event type column. The empty fields don't apply to that kind of event, so don't impute them. | Cleaning |
| Injured is often blank | 22 of 32 accidents have Damage but no Injured. | Fill with 0, assuming blank means nobody was injured. | Imputation |
| An event with no measurements | `1;24;15;45;KD 305RTV;;;;;` (Year N), and one row in Year N+1. | Drop it. It can't be classed as an accident or a near-accident. | Cleaning |
| Damage has no unit | The case study (slide 7) says euros. Values 3,000 to 49,000. | Rename to `DamageEur`. | Cleaning |
| Licence plates are personal data | Every plate is unique, so they add nothing to training. | Drop the column before training. | Cleaning |
| Hours without events are missing | Near-accidents are counted per hour, but 201 of 744 hours have no row at all. | Fill those hours with 0 events, not with a missing value. | Imputation |
| No location | Neither accidents nor sensors have a position on the highway. | Assume the whole highway is one stretch. | Decision |
| Unknown source of Year N+1 accidents | `AccidentsYearNPlus1_V100.csv` is named differently and is not in the course folder. | Confirm where it came from before using it. | Decision |

### Where we impute

- **Injured:** blank becomes 0 for accidents.
- **Near-accidents per hour:** hours with no rows get a count of 0.
- **Missing sensor values:** use the average of the other sensors of the same type in that hour. The V100 files have no gaps, but the cleaning code should still handle them.

We don't impute fields that don't apply to that kind of event (Damage on a near-accident), sensors with no readings at all, or air pressure.

## Round 3

Every number below was checked with code against the V100 files in [`data/`](../data/). Line numbers count the header as line 1. Guesses are marked *(guess)*.

All files are semicolon-separated with Windows line endings. Five of the six start with a UTF-8 byte order mark (all except `SensorTypes`), which ends up glued to the first column name unless the file is read as `utf-8-sig`.

### `Case_Study_Speed_Limit_SensorTypes_V100.csv`

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| Code `T` is not unique | Line 3 `T;temperature` and line 6 `T;traffic`. Sensors 7, 15, 16 and 18 are coded `T`. | Give traffic the code `TR`. Assign sensors by their values: 15 and 18 read −15 to 12 (temperature), 16 reads 1.85 to 30 and follows noise sensor 3 (correlation 0.995) (traffic). Sensor 7 has no readings and stays unknown. | Cleaning |
| Trailing spaces | Line 9 code `W ` and line 8 unit `degrees   `. `W` in `Sensors` does not equal `W `. | Trim all text fields. | Cleaning |
| Wind strength unit | Line 7 `hm/h`. | Treat it as km/h. *(guess: typo)* | Documented assumption |
| Air pressure unit | Line 2 `mmHG` with range 900 to 1000. Normal air pressure is about 760 mmHg, so the range fits hPa. *(guess)* | Correct to hPa. No air pressure readings exist, so it has no effect on training. | Documented assumption |
| Light unit differs from the spec | Line 10 `lux`. The darkness rule is 500 millilux. | Use 0.5 lux as the threshold. | Cleaning |

### `Case_Study_Speed_Limit_Sensors_V100.csv`

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| Sensor 19 is missing | Not in the file, but 744 readings in each readings file (first at Year N line 16). Correlation 0.996 to 0.998 with temperature sensors 15 and 18. | Add 19 as a temperature sensor. | Documented assumption |
| Listed sensors that never report | Line 8 sensor 7 (`T`), line 11 sensor 10 (`N`), line 18 sensor 17 (`AP`). No readings in either year. Sensor 17 is the only air pressure sensor. | Leave them out. There is no air pressure data at all. | Cleaning |
| Column name differs from the readings | `SensorID` here, `Sensor` in the readings. | Rename to one name. | Cleaning |

### `Case_Study_Speed_Limit_SensorReadingsYearN_V100.csv`

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| Speed limit mixed with measurements | Sensor -1 is not in `Sensors`. 744 rows (first at line 3, `-1;70,00`), values 40, 50, 60, 70 and 80. | Move it into its own speed limit column, one value per hour. | Cleaning |
| Decimal commas | Every `Value`, e.g. `70,00`. | Parse with a comma as decimal separator. | Cleaning |
| Readings at random times within the hour | One reading per sensor per hour, but at a random minute and second. Only 3 of 12,648 are at :00:00. | Group by Day and Hour into one row per hour. | Cleaning |
| Several sensors per type | 3 water (1, 8, 11), 3 light (2, 9, 12), 3 temperature (15, 18, 19), 2 wind strength (6, 14), 2 wind direction (5, 13). Correlation 0.955 to 0.998. The light sensors agree on dark in all 744 hours. The water sensors disagree on over 1000 micrometers in 5 hours. | Use the mean per type per hour as the feature. | Cleaning |
| Wind sensors disagree on calm | In 218 hours one wind strength sensor reads 0 and the other does not. Wind direction has no meaning without wind. | Use the mean for strength. Leave wind direction out. | Documented assumption |
| Limit reduced with no cause in the data | 417 hours have a limit below 80. In 28 of them it is neither dark (mean light under 0.5 lux) nor icy (mean water over 1000 and mean temperature under 0). Probably air quality, which is not in the data. *(guess)* | Train only on hours that are dark or icy, since that is the only time the network is used. | Documented assumption |
| Only one month | Month is 1 in all 12,648 rows: 31 days, 744 hours. | Can't be fixed. State that the network is only valid for winter conditions. | Documented assumption |

### `Case_Study_Speed_Limit_SensorReadingsYearNPlus1_V100.csv`

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| No header row | Line 1 is data: `1;1;0;3;35;6;0,00`. | Use the Year N header. Every row has the same 7 fields. | Cleaning |
| Same problems as Year N | Same sensors, row counts and formats as Year N. | Same fixes as Year N. | Cleaning |

### `Case_Study_Speed_Limit_AccidentsYearN_V100.csv`

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| No Minute column | Header is `Month;Day;Hour;Second;…`. | Match to readings by Day and Hour only. | Documented assumption |
| Hours run 1 to 24 | Readings use 0 to 23. No row has hour 0. 44 rows have hour 24 (first at line 74), one of them on day 31. | Subtract 1 from Hour, assuming hours are counted from 1. *(guess)* | Documented assumption |
| Not sorted by time | Line 2 is day 27, line 3 is day 26. | Sort by Day, Hour, Second. | Cleaning |
| Two kinds of event in one file | 32 rows with Damage (accidents), 964 with exactly one of CloseCarCm (886), CloseGuardrailCm (63) or SkidAngle (15). Never both. | Add an event type column. The other kind's fields don't apply to it, so leave them blank and don't impute them. | Cleaning |
| Injured blank for accidents | 22 of 32 accidents, e.g. line 99 `…;41000;;;;`. | Fill with 0. *(guess: blank means nobody injured)* | Imputation |
| An event with no measurements | Line 461 `1;24;15;45;KD 305RTV;;;;;`. | Drop the row. | Cleaning |
| Damage has no unit | The column is just `Damage`, values 3,000 to 49,000. The case study says euros. | Rename to `DamageEur`. | Cleaning |
| Licence plates are personal data | 997 rows, 997 different plates, so a plate never repeats. | Drop before training. | Cleaning |
| Hours with no events have no row | 543 of 744 hours have at least one event. 201 have none. | Count near-accidents per hour and fill the 201 hours with 0. | Imputation |
| No location | No highway position in this file or in `Sensors`. | Treat the highway as one section. | Documented assumption |

### `AccidentsYearNPlus1_V100.csv`

| Problem | Evidence | Fix | Kind |
|---|---|---|---|
| File name differs | No `Case_Study_Speed_Limit_` prefix, unlike every other file. | Rename to match. | Cleaning |
| Same structure problems as Year N | 31 rows with hour 24 (first at line 45, three on day 31). Injured blank for 15 of 21 accidents (first at line 65). Empty event at line 87 `1;6;1;38;CJ 104GNA;;;;;`. Not sorted (line 2 day 23, line 3 day 24, line 4 day 3). 233 of 744 hours have no event. | Same fixes as Year N. | Cleaning, imputation |

### Checked and not a problem

- No empty or non-numeric values in either readings file.
- No duplicate rows, and no sensor has two readings in the same hour.
- Every sensor that reports has exactly 744 readings per file.
- Every value is inside its type's Min and Max. Negative values occur only in temperature sensors 15, 18 and 19 (502 of 744 hours each), which is normal in January.

### Imputation

**Where we impute:**

- **Injured:** blank becomes 0 for accidents (22 in Year N, 15 in Year N+1).
- **Near-accidents per hour:** hours with no row get a count of 0 (201 in Year N). This count is what the network learns from, so leaving those hours out would overstate the risk.
- **A missing sensor value:** use the mean of the other sensors of the same type in that hour. The V100 files have no gaps, but new data might.

**Where we deliberately don't:**

- Fields that don't apply to that kind of event (Damage on a near-accident, CloseCarCm on an accident). Blank is the correct value.
- Sensors 7, 10 and 17, and air pressure in general. There is nothing to base a value on.
- Minute for accidents. It can't be recovered from anything in the data.
- The empty event rows. They are dropped instead.

## Comparison
Getting an understanding of and proper look at the data yourself without an LLM is important in my opinion. In round 1 I identified glaring issues with the data that had pretty straightforward solutions, just by skimming each csv file we were provided. 

The LLM took a look for Round 2, it identified the same issues as me, plus some issues that I could not spot by eye, for example the trailing whitespaces after some values. It also has more domain knowledge than me and recognized some incorrect units of measurement for certain values, which would have been difficult for me to recognize without deeper research. 

Round 3 identified all the problems as well as the appropriate solutions, it had the benefit of also seeing the context of Rounds 1 and 2 and improving on that. It laid out a clear plan regarding imputation and where we deliberately do not plan to do that.