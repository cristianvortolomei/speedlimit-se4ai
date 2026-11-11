# 7. Features (case study, slide 16, and ML Architecture deck)

Define the features for the neural network and how to compute them from the raw data. What is the input, and which attribute does the network predict?

## Round 1
- The network should only be used when it is dark or the weather is bad (black ice). Otherwise the speed limit is set to a fixed 80 km/h. Air quality being bad is also determined by the LLM. The limit is otherwise 80 if none of these conditions are met.
- One training example per hour, including near-accidents.
- The inputs would be the values from SensorReadings.
- The network would predict the number of near-accidents in an hour.
- All the cleaning steps in 06 Round 3 are done before training. SensorReadings are joined with Accidents on Month, Day, Hour, and the network trains only on dark or icy hours, since that is the only time the network is used.
- I am not sure which transformations are needed.

## Round 2

**When the network is used.** Only when it is dark or there is a danger of black ice (REQ1, SPEC1, SPEC2). Air quality is handled by the LLM (REQ2), and when nothing applies the limit is 80 km/h (REQ3).

**Training examples.** One row per hour, with that hour's readings, its speed limit and the number of near-accidents in it (0 if none). Only dark or icy hours are kept, which is 389 of 744 hours in Year N.

**Inputs.**

- Light, water and temperature, from `SensorReadings`. They define the conditions the network is used in.
- Humidity is plausible. Traffic is worth considering, because most near-accidents are cars getting too close to each other.
- The current speed limit (sensor `-1`). In use, the network is asked about 40, 50, 60, 70 and 80 km/h, and the highest limit with at most 1 predicted near-accident is chosen (04 Round 3, SPEC3b).

**Output.** The number of near-accidents in the hour (a regression), not a yes or no. Real accidents are rare (14 of 32 are in dark or icy hours), so decide whether they also count, and how much.

**From raw data to rows.**

1. Run the cleaning steps from 06 Round 3.
2. Turn the readings into one row per hour, with the mean per sensor type.
3. Count near-accidents per hour, after subtracting 1 from the accident hour.
4. Join on Month, Day and Hour. Don't join on Second.

**Transformations.**

- Scale all inputs to a similar range (for example mean 0 and standard deviation 1), fitted on the training data and saved for the app.
- Take the log of light. It is extremely skewed: the median is about 7,000 lux, but half of all hours are below 0.5 lux.
- Use the same unit for light in training and in the app. The data is in lux, the app passes millilux.
- Split training and test data by whole days, not random hours, because neighbouring hours are almost identical.

**Two risks.**

- The limit was never 80 km/h in a dark or icy hour (always 40 to 70), so the network should not be trusted at 80.
- In dark or icy hours, a lower limit goes with more near-accidents: 1.86 per hour at 40 km/h (7 hours), 1.44 at 50 (55 hours), 1.26 at 60 (230 hours), 1.13 at 70 (97 hours). *(Guess: the operator lowered the limit when conditions were worse.)* The weather inputs are needed so the network does not learn "slower is more dangerous".

## Round 3

Follows the ML Architecture deck: for each raw attribute, decide whether to use it as a feature, combine it with others, or ignore it, then normalize the features into small numbers. Every number below was checked with code on the Year N files.

### How the network is used

- **When:** only in hours that are dark (mean light below 0.5 lux) or have a danger of black ice (mean water above 1000 micrometers and mean temperature below 0 °C). The router decides this (SPEC1, SPEC2). Air quality is the LLM's job.
- **Question it answers:** "Under these conditions, with this speed limit, how many near-accidents will happen in the next hour?"
- **How the limit is chosen:** ask the network for each candidate limit (40, 50, 60, 70 km/h). Choose the highest one with a prediction of at most 1. If none qualifies, use 40 km/h (04 Round 3, SPEC3b). This fits inside the app's existing `predict_limit(conditions)`, which can loop over the candidates and return the chosen limit.

### Training examples and label

- **One example = one hour.** Only dark or icy hours: 389 of 744 in Year N (354 dark, 62 icy, some both).
- **Label:** the number of near-accidents in that hour. A near-accident is an accidents row with CloseCarCm, CloseGuardrailCm or SkidAngle filled (SPEC4). Hours without a row get 0. In the 389 hours the label ranges from 0 to 5: 112 hours have 0, 136 have 1, 87 have 2, 38 have 3, 12 have 4 and 4 have 5.
- **Accidents are not in the label.** REQ1 is about near-accidents. The 14 accidents in dark or icy hours are reported next to the evaluation instead.

### Features

Normalization uses the Min and Max from `SensorTypes`, like the deck projects age onto 0 to 200: `(value − Min) / (Max − Min)`. This needs no fitted scaler, and the app can use the same formula.

| Raw attribute | Decision | How it is computed | Normalized |
|---|---|---|---|
| Light (sensors 2, 9, 12) | Use, combined | Mean of the three sensors in that hour. Log scale, because values range from 0 to 120,000 lux and half the hours are below 0.5: `log10(lux + 0.001)` | `(log − (−3)) / (6 − (−3))`, using 0.001 to 1,000,000 lux |
| Water (1, 8, 11) | Use, combined | Mean of the three sensors | `/ 10000` |
| Temperature (15, 18, 19) | Use, combined | Mean of the three sensors (19 assumed to be temperature, see 06) | `(t + 30) / 100` |
| Speed limit (sensor −1) | Use | The limit in that hour. A number, not one-hot, because the order matters and the app asks about each limit in turn | `(limit − 40) / 40` |
| Humidity (4) | Ignore for now | Not part of the dark or ice rules, and not in the GUI. Correlation with the label: −0.02 | – |
| Traffic (16) | Ignore | It partly depends on the speed limit, so it is more an effect than a cause. Correlation with the label: −0.01 | – |
| Noise (3) | Ignore | Follows traffic (correlation 0.995). Sensor 10 never reports | – |
| Wind strength and direction (6, 14, 5, 13) | Ignore | Not part of the dark or ice rules. Direction means nothing without wind | – |
| Air pressure (17) | Ignore | No readings at all | – |
| Month, Day, Hour, Minute, Second | Ignore as features | Only used to group and join. Month is always 1. Hour of day has correlation 0.02 with the label | – |
| CloseCarCm, CloseGuardrailCm, SkidAngle | Combine into the label | Any filled column counts as one near-accident | – |
| Damage, Injured | Ignore | Accidents are reported, not learned | – |
| LicencePlate | Ignore | Personal data, every plate unique | – |

In the app, the GUI already asks for light, water and temperature. The light it passes is in millilux, so divide by 1000 before computing the light feature.

### From raw data to training rows

1. Run the cleaning steps from 06 Round 3.
2. Readings: group by Day and Hour, and take the mean per sensor type. Take the speed limit (sensor −1) as its own column. Result: 744 rows.
3. Accidents: subtract 1 from Hour, keep near-accidents, count them per Day and Hour.
4. Join the two on Day and Hour. Fill hours without a count with 0.
5. Keep only dark or icy hours (389 rows).
6. Compute and normalize the four features.
7. Split by day: days 1 to 24 for training, days 25 to 31 for testing.

### Weaknesses of this feature engineering

- **The signal is very weak.** In the 389 hours, no input correlates with the label by more than ±0.1 (light +0.06, water +0.05, temperature −0.01, limit −0.10). Expect the network to predict values close to the average.
- **The data does not reach the target at any limit.** The average is 1.26 near-accidents per hour. Per limit it is 1.86 at 40 km/h (7 hours), 1.44 at 50 (55 hours), 1.26 at 60 (230 hours) and 1.13 at 70 (97 hours). If the network learns these averages, no limit reaches at most 1, and SPEC3b's fallback of 40 km/h would apply almost every time. Discuss this with Cristian before Turn 9.
- **A lower limit goes with more near-accidents, and the data does not explain why.** Round 2 guessed that the operator lowered the limit when conditions were worse, but the limit hardly correlates with the conditions (light +0.02, water −0.03, temperature −0.13). The 40 km/h figure rests on only 7 hours, so it may simply be chance. The network could still learn "slower is more dangerous", so check that its predictions do not fall as the limit rises.
- **The limit was never 80 km/h in a dark or icy hour.** The network has never seen it, so 80 is left out of the candidates.
- **One month, one section.** Only January, and no locations. The features are only valid for winter on this highway.

## Comparison

Round 1 was the hardest one so far to do without AI, because it needs an understanding of both the requirements and the data. I got the overall idea right: the network is only used when it is dark or there is black ice, and the cleaning from 06 has to happen before training.

Round 2 added things I hadn't thought of, like taking the log of the light values, splitting the training and test data by whole days, and that the limit was never 80 km/h in a dark or icy hour. It also guessed why a lower limit goes with more near-accidents.

Round 3 followed the method from the ML Architecture deck and went through every attribute, deciding whether to use it, combine it or ignore it, and how to normalize it. It also checked the data again and found that its own guess from Round 2 didn't hold up, and that no input really predicts the number of near-accidents. This means the network would set 40 km/h almost every time, which we need to discuss before writing the code.

The LLM was very useful for checking ideas against the data and finding things I couldn't see by just looking at the CSV files. But Round 2 shows that it also makes confident guesses, so its answers need checking just like my own. Deciding what the network should actually do with this data is still up to us.
