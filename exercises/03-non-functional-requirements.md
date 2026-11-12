# 3. Non-functional requirements (SpeedLimit07)

Define the non-functional requirements of the system.

## Round 1

- Speed. The system shall display a limit within 15 seconds of each hourly calculation. If an external service (the API) is too slow, the system shall use the fallback rule and show a warning as well.
- Access. The system shall allow only the staff and administrators to access and override the speed limit.
- Privacy. The system shall include zero license plate numbers in the cleaned training data or logs.
- Accessibility. The system shall let a trained operator find the current limit and apply overrides within 30 seconds of the request.
- Retraining. The system shall let us clean a new dataset, retrain the model/network, and generate a test report with just a few commands and no code changes.

## Round 2

Non-functional requirements for the SpeedLimit system

1. Safety and reliability
- NFR1 (safe default): If the system fails (sensor outage, neural network or LLM failure, API timeout, invalid output), it must fall back to a safe speed limit (e.g. the last valid limit or a predefined conservative limit) and alert operators.
- NFR2 (bounded output): The speed limit must always lie within a legal range (e.g. 30-80 km/h), and reductions may be applied only in defined steps (e.g. 10 km/h). Outputs from the neural network or LLM outside this range are rejected or clamped.
- NFR3 (rate of change): The limit must not change more often than every X minutes or by more than Y km/h per change, to avoid confusing drivers.
- NFR4 (consistency): The rule "not dark, good weather and good air quality means 80 km/h" must always hold; the models must never raise the limit above 80 km/h.

2. Availability
- NFR5: Availability of the production decision function of at least 99.9% (24/7 operation). Sensor or API failure must degrade gracefully (e.g. ignore a faulty sensor, use redundant sensors).
- NFR6: Recovery after failure (MTTR) within 15 minutes.

3. Performance
- NFR7: A new decision (limit update) is made within 10 seconds of a change in sensor data. Neural network inference below 1 second.
- NFR8: The LLM and air-quality API call must complete within 5 seconds; on timeout the fallback in NFR1 applies.
- NFR9: The system handles the sensor data rate of all highway sensors (e.g. a reading per sensor per second) without data loss.

4. Accuracy and quality of the ML components
- NFR10: The neural network must reach a defined minimum quality on held-out test data (e.g. recommended limits within 10 km/h of the expert or accident-derived reference in 90% of cases) and must not recommend limits that are less safe than the current rule-based practice.
- NFR11: The LLM's air-quality decisions must be consistent and reproducible (low temperature, fixed prompt and version) and its output must be in a strict, machine-readable format that is validated.
- NFR12: Model quality is monitored in production (drift, accident and near-accident rates) and models can be retrained and rolled back.

5. Explainability and traceability
- NFR13: Every decision (inputs, model used, output, timestamp) is logged and retained (e.g. 5 years) so it can be audited after accidents.
- NFR14: Decisions must be explainable to operators (e.g. main input factors shown).

6. Security
- NFR15: All sensor, API and operator communication is encrypted and authenticated. Role-based access control for operators and data scientists.
- NFR16: Protection against manipulated sensor data and against prompt injection or malicious content from the air-quality API affecting the LLM; the LLM has no ability to act beyond proposing a limit.

7. Privacy and legal compliance
- NFR17: Accident records contain licence plates and injury data (personal data). They must comply with GDPR: access restricted, purpose limited, data minimised, and licence plates pseudonymised or removed in the data used for machine learning.
- NFR18: Compliance with road traffic law and the EU AI Act (high-risk system: documentation, human oversight, risk management).

8. Human oversight and usability
- NFR19: Operators can see the current limit and reasoning, and can override or disable the automatic decision at any time (manual override takes priority).
- NFR20: Alerts for failures are delivered within 1 minute.

9. Maintainability and scalability
- NFR21: Modular design so that the neural network, LLM and API provider can be replaced independently; configuration (thresholds, limits) changeable without redeployment.
- NFR22: The system can be extended to more highway sections and sensors without redesign.

10. Cost and sustainability
- NFR23: LLM and API usage cost kept within budget (call only when needed, e.g. on air-quality change, with caching of results for a few minutes).

## Round 3

Grouped by the qualities from the course. The numbers are targets to agree with the operator. The last column says whether our app meets them today.

| ID | Quality | Requirement | Our app today |
|---|---|---|---|
| NFR1 | Performance | The system shall set a new limit within 30 seconds after the hourly readings arrive, including the LLM call. | Met in our tests |
| NFR2 | Performance | The system shall stop waiting for the LLM after 15 seconds and continue as in REQ7. | Not yet: the LLM call has no time limit |
| NFR3 | Reliability | The system shall always set a valid limit, even when a sensor, the air quality API or the LLM fails (REQ6, REQ7). | Met |
| NFR4 | Availability | The system shall set a limit in at least 99.9% of hours per month. | Not tested |
| NFR5 | Security | Only control room staff shall be able to override the limit, and every override shall be logged with the person's name. | Not yet: no login, and overrides are logged without a name |
| NFR6 | Security | API keys shall never be stored in the code repository. | Met: the key is in `.env`, which git ignores |
| NFR7 | Privacy | Licence plates shall be removed before training and never shown (REQ10). | Met |
| NFR8 | Usability | The control room shall see the limit, its reasons and any warnings on one screen, and override it in at most three clicks. | Met |
| NFR9 | Transparency | For every limit, the system shall show which rule set it (network, LLM, missing readings or override) and with which inputs. | Met in the GUI and the log |
| NFR10 | Changeability | The thresholds (500 millilux, 1000 µm, 0 °C, AQI 40) shall each be defined once, so changing one needs one edit. | Met |
| NFR11 | Changeability | Retraining the network on new data shall take one command. | Met: `training/train.py` |
| NFR12 | Accuracy | Before every release, the network shall beat always predicting a constant on held-out days. | Not met: the network's error is 0.859, a constant 1 gets 0.793 |
| NFR13 | Consistency | For the same air quality, the LLM shall give the same reduction in at least 9 of 10 calls. | Not met in our tests: AQI 95 gave 20 and 30 km/h |
| NFR14 | Energy | The LLM shall only be called when the AQI is above 40, at most once per decision. | Met (SPEC5) |

The last three come from the course's list of responsible AI requirements: as few wrong answers as possible, and no waste of energy.

## Comparison

In Round 1, I focused on the most important requirements for the day-to-day operation of the system: how quickly a speed limit is displayed, who can override it, the removal of licence plates from the data, how quickly an operator can intervene, and how straightforward retraining is.

The rounds dedicated to AI were more descriptive. Round 2 took a much broader approach, with 23 requirements, ranging from availability to costs, although some of them, such as a reading every second or speed limits down to 30 km/h, do not really fit our system.

Round 3 assigned a specific value to each requirement and assessed each one in relation to our application. This revealed four areas we still need to work on: a time limit for the call to the LLM, a login for overrides, a network that beats a simple guess, and more consistent responses from the LLM.

What we learnt: requirements are most useful when you test them against the system you've actually built.