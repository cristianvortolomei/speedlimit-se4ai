# 4. Complete the requirements (case study, slide 14)

Complete the system requirements and the requirements specification. Add assumptions and a glossary. Avoid the typical errors of natural-language requirements.

## Round 1

System Requirements:
- If it is dark, or there could be black ice, the system should lower the speed limit. The goal is an average of no more than one near-accident per hour under those conditions.
- If the air-quality forecast is rated poor or worse, the system should lower the speed limit.
- If conditions tell us that we should use different limits at the same time, the system should use the lowest one.
- If none of these conditions apply, the system should set the speed limit to 80 km/h.
- If a reading or forecast is missing/invalid/unavailable, the system should alert the highway operator and ask them for the correct speed limit.

Requirements specification:
- Darkness. The system should treat light below 500 millilux as darkness.
- Black ice risk. The system should flag a risk when the water layer on the road is thicker than 1 mm and the temperature is below 0°C.
- Limit for darkness or ice. The system should use a neural network trained on other past road conditions, near-accident records and speed limits. That way, it should choose the highest approved limit below 80 km/h that the model predicts as safe. If none of them qualifies, the system should ask the highway operator for the correct speed limit.
- Limit for poor air quality. The system should get the local forecast from the API provided. If the prognosis is rated poor or wose, the LLM should choose a limit below 80 km/h using the rules.

Assumptions:
- The sensors and air-quality prognosis cover the same section of the highway if it is large enough.
- The highway operator defines the allowed speed limits, so the system can only choose among those. The operator is also available when the system asks.

Glossary:
- Variable speed limit. The speed limit in effect changes with conditions.
- Near-accident. A situation in which the vehicle skids past the defined threshold or comes closer to another vehicle without hitting it.
- Air-quality API. The external service that our system uses to get the local air-quality prognosis.

## Round 2

**Notes on the given text (defects fixed below)**
- REQ1 says "dark or black ice", but the intro says "dark or bad weather". I treat black ice as the only "bad weather" condition (Assumption A1).
- REQ2 says "predicted" poor air quality, but the intro says the LLM uses the current air quality from an API. I use the current measured value (A2).
- "Appropriate", "poor", "on average", "too close", "reduced" and "at most one near-accident per hour" are undefined, and the actor and scope are missing.
- It is not defined what happens if REQ1 and REQ2 apply at the same time, or if the sensors or API fail.
- SPEC3 is a design/solution statement, not a requirement. I keep it but split it into a learning requirement and a production requirement.

**Glossary**
- System: the speed-limit control system of the highway operator.
- Speed limit: the maximum permitted speed shown on the variable-message signs, in km/h, as an integer multiple of 10.
- Base limit: 80 km/h.
- Highway section: a stretch of highway with its own sensors and its own sign. All requirements apply per section.
- Illuminance: the light level at road level, measured by the section's light sensor, in millilux (mlx).
- Water film: the thickness of water on the road surface, measured by the road sensor, in micrometers (µm).
- Temperature: the road-surface temperature in °C.
- Near-accident: see SPEC4.
- Near-accident rate: the number of near-accidents in a section divided by the observed time, in events per hour.
- Neural network (NN): the model that gives the speed-limit reduction for the dark or black-ice case.
- LLM: the language model that gives the reduction for the air-quality case.
- AQI: the air quality index, a value from 0 to 500 (higher means worse) delivered by the air-quality API.
- Reduction: the number of km/h subtracted from the base limit.
- Control cycle: one evaluation by the system, run every 5 minutes.
- Reduction condition: dark, or black ice, or poor air quality.

**Assumptions**
- A1: "Bad weather" means black ice only (SPEC2). Rain, fog and snow are out of scope.
- A2: The API returns a current AQI for each section at least once per control cycle.
- A3: Poor air quality means AQI > 100 (the API's "unhealthy for sensitive groups" level). This threshold is to be confirmed with the operator.
- A4: Sensors deliver values at least once per control cycle. The sensors are calibrated.
- A5: There is enough historic data (speed limit, weather, light, accidents, near-accidents) for the NN. There is not enough data for the air-quality case.
- A6: Drivers comply with the displayed limit. The NN only learns the relationship between limit and near-accident rate.
- A7: The lowest speed limit permitted by law is 30 km/h.
- A8: Near-accidents are detected automatically by cameras and radar and logged with a timestamp and section.

**System requirements (revised)**
- REQ1: In every control cycle, if a section is dark or has black ice, the system shall set that section's speed limit to the highest value for which the NN predicts a near-accident rate of at most 1 per hour for that section. The limit shall not be below 30 km/h or above 80 km/h. The rate is the expected value over the next 60 minutes.
- REQ1a: If the NN predicts more than 1 near-accident per hour even at 30 km/h, the system shall set 30 km/h and notify the operator.
- REQ2: In every control cycle, if the current AQI for a section is above 100, the system shall query the LLM for a reduction. It shall set the limit to 80 km/h minus that reduction, where the reduction is an integer multiple of 10 km/h between 10 and 50 km/h.
- REQ2a: The reduction shall follow the table agreed with the operator. For AQI 101 to 150 it is 10 km/h, for 151 to 200 it is 20 km/h, and for above 200 it is 30 km/h. The LLM is allowed to deviate from the table by at most 10 km/h.
- REQ3: In every control cycle, if a section is not dark, has no black ice and has AQI of at most 100, the system shall set the speed limit to 80 km/h.
- REQ4 (conflict): If both REQ1 and REQ2 apply, the system shall set the lower of the two limits.
- REQ5 (failure): If a required sensor value or the API response is missing or older than 10 minutes, the system shall keep the last valid limit for at most 15 minutes and then set 60 km/h. It shall notify the operator.
- REQ6: The system shall update the sign within 60 seconds after the limit is computed.
- REQ7: The system shall log each evaluation with section, time, inputs, source (NN, LLM or base) and resulting limit.

**Requirements specification (revised)**
- SPEC1: A section is dark if the illuminance is below 500 mlx (0.5 lux). The condition is evaluated per control cycle with the latest reading.
- SPEC2: A section has black ice if the water film is more than 1000 µm (1 mm) and the temperature is below 0 °C. Both conditions must hold in the same reading.
- SPEC3a (learning): The NN shall be trained offline on logged sensor data. The inputs are illuminance, water film, temperature and speed limit. The target is the number of near-accidents per hour. The NN shall be retrained at least once per year and before use shall be validated on held-out data.
- SPEC3b (production): In the dark or black-ice case the NN shall receive the current values of the inputs from SPEC3a and shall return the predicted near-accident rate for each candidate limit (30, 40, ..., 80 km/h). REQ1 selects the limit from this.
- SPEC4: A near-accident is an event in which (a) a car skids, detected as a lateral slip angle above 15 degrees, or (b) the time gap to the car in front falls below 0.5 s, or (c) a car comes closer than 0.5 m to the guardrail while the speed is above 30 km/h. This detection is automatic (A8).
- SPEC5: The LLM shall receive only the AQI and the table of REQ2a. It shall return one integer reduction. If it returns anything else, the system shall use the table value of REQ2a.
- SPEC6: Verification: REQ1 is checked by a simulation or field trial of at least 100 hours in dark or black-ice conditions with an observed rate of at most 1 near-accident per hour. REQ2 and REQ3 are checked with test inputs for each AQI band. REQ4 and REQ5 are checked with test inputs covering both conditions and sensor failure.

**How typical errors are avoided**
- Ambiguity and vague words ("appropriate", "poor", "too close") are replaced by numbers and units.
- The actor is named ("the system") and statements are active.
- Each requirement has one testable condition and one response.
- The missing cases (conflicts between conditions, sensor and API failure, minimum limit, unreachable rate) are specified.
- Terms are used consistently and defined in the glossary.
- Solution details (NN, LLM) are separated from the requirements.

## Round 3

### System requirements

What must be true on the highway. "Shall" marks a requirement.

- **REQ1:** When it is dark or there is a danger of black ice, the speed limit shall be reduced so that, averaged over all such hours in a month, there is at most one near-accident per hour.
- **REQ2:** When the current air quality is moderate or worse (European AQI above 40), the speed limit shall be reduced by 10 to 40 km/h. Worse air quality shall never lead to a smaller reduction.
- **REQ3:** When neither REQ1 nor REQ2 applies, the speed limit shall be 80 km/h.
- **REQ4:** When REQ1 and REQ2 both apply, the lower of the two limits shall apply.
- **REQ5:** The speed limit shall always be 40, 50, 60, 70 or 80 km/h.
- **REQ6:** If light, water or temperature readings are missing, the speed limit shall be 60 km/h until they return.
- **REQ7:** If the air quality or the LLM's answer is missing, the air quality part shall not reduce the limit, and the control room shall be informed.
- **REQ8:** The control room shall be able to override the speed limit at any time.

Negative requirements (what must not happen):

- **REQ9:** The speed limit shall never be set above 80 km/h.
- **REQ10:** Licence plates shall not be used for training and shall not be shown in the GUI.

### Assumptions

Facts about the world the requirements depend on. If one is wrong, the system can fail even when the software is correct.

- **A1:** Most drivers keep to the displayed limit, so the limit affects the number of near-accidents.
- **A2:** Every near-accident is recorded.
- **A3:** The highway is one section. The data has no locations, so one reading per sensor type stands for the whole highway.
- **A4:** January data is only valid for winter conditions.
- **A5:** In the accident files, hour 1 means the hour starting at 0:00 (the files use 1 to 24, the readings 0 to 23).
- **A6:** Sensor 19 measures temperature and sensor 16 measures traffic (inferred from their values).
- **A7:** A lower speed limit reduces traffic emissions near the highway.
- **A8:** The air quality at the API's nearest grid point is the air quality at the highway.

### Requirements specification

What the software does, in terms of its inputs and outputs.

- **SPEC1:** It is dark when the mean of the three light sensors in that hour is below 500 millilux (0.5 lux).
- **SPEC2:** There is a danger of black ice when the mean of the three water sensors is above 1000 micrometers and the mean of the three temperature sensors is below 0 °C in the same hour.
- **SPEC3a (training):** The neural network shall be trained on the hours where SPEC1 or SPEC2 holds. Its inputs are the speed limit and the weather readings of that hour. Its output is the number of near-accidents in that hour.
- **SPEC3b (operation):** For the current conditions, the network shall predict the near-accidents for 40, 50, 60, 70 and 80 km/h. The limit is the highest one with a prediction of at most 1. If none qualifies, the limit is 40 km/h.
- **SPEC4:** A near-accident is a record with a car-to-car distance or a car-to-guardrail distance of 20 cm or less, or a skid angle of 30 degrees or more. (These bounds are inferred from the data, where every near-accident is within them.)
- **SPEC5:** The air quality is the European AQI from Open-Meteo for the highway's coordinates. Above 40, the LLM returns a reduction of 10, 20, 30 or 40 km/h. Any other answer counts as missing (REQ7).
- **SPEC6:** The speed limit is recalculated every hour, matching the hourly sensor readings.
- **SPEC7:** Every decision is logged with its time, inputs, network prediction, AQI, LLM answer and final limit.

### Glossary

| Term | Meaning |
|---|---|
| Highway | The one section covered by the sensors (A3) |
| Speed limit | The maximum allowed speed in km/h: 40, 50, 60, 70 or 80 |
| Normal limit | 80 km/h |
| Dark | See SPEC1 |
| Danger of black ice | See SPEC2 |
| Near-accident | See SPEC4. Counted per hour |
| Accident | A crash with damage in euros and possibly injured people |
| European AQI | Air quality index from 0 (best) upwards. Above 40 is moderate or worse |
| Reduction | The number of km/h taken off the normal limit |
| Control room | The operator's staff who watch and can override the limit |

### Open questions

- REQ2 says "predicted" air quality, but the case study says the current air quality is read from an API. We use the current value.
- The case study doesn't say how long "on average" in REQ1 is. We use one month.
- The AQI threshold of 40 is our choice and should be confirmed with the operator.

## Comparison

For Round 1, we correctly established the main structure: requirements, specifications, assumptions and a glossary, plus what happens when two limits apply simultaneously or when a measured value is missing. But we wrote 'should' instead of 'shall', left words such as 'poor' and 'the rules' undefined, used the terms 'forecast' and 'prediction' interchangeably even though the case study refers to current air quality, and forgot the guardrail in the definition of 'near-accident'.

Round 2 removed the vague words by inserting figures throughout, but many of them were made up: an AQI limit of 100, a minimum speed of 30 km/h, a 5-minute cycle and a 0.5-second gap to the car in front. None of these values appear in the case study or in the data, and in the data the speed limit never falls below 40 km/h.

Round 3 took the numerical values from the case study and the data, broke down the requirements, assumptions and specifications as we do in the course, and listed what we still needed to decide as open-ended questions. This is the version I would build on further.

What I learnt: numerical values make requirements verifiable, but only if they come from somewhere.