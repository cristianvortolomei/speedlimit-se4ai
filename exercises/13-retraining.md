# 13. Retraining (case study, slide 19)

Analyze the sensor readings of the year after the training year and decide whether the neural network needs retraining.

## Round 1
Based on a script (/analysis/compare_years.py) written to compare the readings between the year N and year N+1 file, I could tell that there was 0 difference between the files' values. The model would turn out slightly different due to the different near-accident labels in year N+1, so it is worth a look. 

## Round 2

**Readings.** The Year N+1 sensor readings have the same 12,648 rows as Year N. Every sensor has the same count, average, minimum and maximum in both years, so the conditions did not change and there is no data drift. Retraining on the readings alone would not change anything.

**Labels.** The Year N+1 accidents file is different: 844 rows instead of 997, with 822 near-accidents instead of 964 and 21 accidents instead of 32. Near-accidents dropped from 1.30 to 1.11 per hour, with the same conditions.

**Decision.** The readings give no reason to retrain. Because the labels changed, the network's predictions are probably too high now, so it should be checked against the Year N+1 accidents and retrained if it got worse. From now on, the data should be compared every month so changes are noticed early.

## Round 3

Retraining is needed when the world has changed since the network was trained. There are two kinds of change:

- **Data drift:** the inputs change, for example a milder winter or a new sensor.
- **Concept drift:** the inputs stay the same, but they lead to a different outcome, for example drivers behave differently at the same limit.

The case study (slide 19) asks about the readings, which shows data drift. The accident files show concept drift. All numbers below were checked with code.

### Inputs: no data drift

- `analysis/compare_years.py` shows that all 17 sensors, including the speed limit, have the same count, average, minimum and maximum in both years.
- Row by row, all 12,648 readings are identical and in the same order. Only the header is missing in Year N+1.
- Real weather never repeats exactly, so the Year N+1 file is almost certainly a copy (see [06](06-data-problems.md)). It should be confirmed with whoever delivered the data.

### Labels: concept drift

| | Year N | Year N+1 |
|---|---|---|
| Rows in the accidents file | 997 | 844 |
| Near-accidents | 964 | 822 |
| Accidents | 32 | 21 |
| Near-accidents per hour, all hours | 1.30 | 1.11 |
| Near-accidents per hour, dark or icy hours | 1.27 | 1.06 |

With identical conditions, 142 fewer near-accidents is about 3.4 standard deviations, so chance is very unlikely to explain it.

Near-accidents per hour in dark or icy hours, per speed limit:

| Limit | Year N | Year N+1 |
|---|---|---|
| 40 km/h | 1.86 | 1.14 |
| 50 km/h | 1.44 | 1.18 |
| 60 km/h | 1.26 | 1.05 |
| 70 km/h | 1.13 | 1.00 |

### How the current network does on Year N+1

Tested on the dark or icy hours of days 25 to 31 of Year N+1 (lower error is better):

| | Predicted near-accidents per hour | Average error |
|---|---|---|
| Actual | 0.83 | – |
| Current network (trained on Year N) | 1.24 | 0.946 |
| Network retrained on days 1 to 24 of Year N+1 | 1.12 | 0.869 |
| Always guessing 1 | 1.00 | 0.805 |

The current network overestimates the risk by about half. Retraining helps, but even the retrained network loses to always guessing 1.

### What retraining would change in the app

| Network | Limit chosen in the 389 dark or icy hours of Year N+1 |
|---|---|
| Current network | 40 km/h in all 389 |
| Retrained on Year N+1 | 40 km/h in 382, 50 in 5, 70 in 2 |
| Retrained on Year N and N+1 together | 40 km/h in all 389 |

### Decision

1. **Based on the readings, as slide 19 asks: no retraining.** The inputs did not change at all.
2. **Based on the labels, the network is out of date.** It overestimates near-accidents by about half.
3. **We still don't release a retrained network now.** It hardly changes any decision, and it doesn't beat always guessing 1, so it would fail our release rule (NFR12 in [03](03-non-functional-requirements.md)).
4. **First, clear up the data.** Ask whoever delivered it why the Year N+1 readings are a copy of Year N, and get the real ones.

### Monitoring from now on

| What | How often | Trigger for retraining |
|---|---|---|
| Inputs: average, min and max per sensor, like `compare_years.py` | Monthly | A sensor's average moves clearly outside last year's range, or a sensor is added or replaced |
| Labels: predicted vs actual near-accidents per hour, from the decision log and the accident records | Monthly (the log review in [10](10-human-in-the-loop.md)) | The prediction is off by more than 20% for two months in a row |
| Every new network | Before release | Must beat always guessing a constant on held-out days (NFR12), and a person approves it (10) |

## Comparison

In Round 1, I wrote a script to compare the readings of both years and found that they were exactly the same. I also realised that the near-accident labels are different, so a retrained network would come out slightly different, which is worth a look.

Round 2 came to the same conclusion about the readings and added the numbers for the labels: fewer near-accidents in Year N+1 with the same conditions. Its decision was still quite general though: check the network and retrain if it got worse.

Round 3 explained the difference between data drift and concept drift, which made it clear why identical readings and different labels are not a contradiction. It actually tested the current network on Year N+1, showed that it now overestimates the risk by about half, and that retraining would hardly change the app's decisions. That led to a clearer decision: no retraining for now, clear up the copied data first, and monitor every month with concrete triggers.

The LLM was good at running the numbers and connecting this exercise to our earlier ones (06, 03 and 10). Noticing that the files were identical was easy to do myself with a simple script.
