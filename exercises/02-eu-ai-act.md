# 2. EU AI Act (SpeedLimit04)

Assume the system will be deployed worldwide. Does it comply with the relevant norms? Answer no, yes, or yes with specific technical and organizational measures, and give the reasons.

## Round 1

Yes, but only with these technical and organizational measures:

- Road safety. SpeedLimit, according to a bit of research, falls into the EU AI Act's high-risk category because it sets speed limits as part of a road safety system. We need to assess the risks, we need to test the system with reliable data, document the performannce and how it works, and log every decision we make. The staff/operators should also be able to override the system if necessary.
- License plates. A plate can be personal data if it is linked to a person. We would remove the license plate numbers from training data.
- Worldwide use. The EU AI Act is a European regulation, so it does not apply outside of the EU. We would need to check the traffic, privacy, and AI regulations that apply in each country before implementing the system there.

## Round 2

Yes, but only with the following technical and organizational measures:

Why not a plain "Yes": For a worldwide deployment the relevant norms are mainly the GDPR (EU, with equivalents such as UK GDPR, CCPA/CPRA and Brazil's LGPD elsewhere), the EU AI Act (which has extraterritorial reach), and the safety and liability rules for critical road infrastructure. The system is not a plain "No" either. Reducing a speed limit based on weather, light and air quality has a clear legitimate purpose, which is road safety and public interest.

Classification under the AI Act: The system is probably high-risk. It is an AI safety component in the management and operation of critical infrastructure (road traffic), which falls under Annex III. The neural network and the LLM both count as AI systems. The LLM is probably a general-purpose AI model supplied by a third party.

Technical measures:
1. Data minimisation and purpose limitation. Do not feed licence plates, injury data or other personal data from the accident records into the ML exploration or the speed-decision models. Remove them, or anonymise or pseudonymise them. Use aggregated, non-personal data wherever possible (accident location, time, damage, weather). Delete or restrict personal data after it is no longer needed. Sensors such as noise or traffic cameras must not capture identifiable persons or vehicles.
2. Security. Encrypt data, control access, log access, and protect the sensor and API channels against manipulation. The air-quality API data must be authenticated and validated, because it is an external input that can be wrong or poisoned. Protect against prompt injection and adversarial inputs to the LLM, and treat the LLM's output as untrusted.
3. Robust, deterministic safeguards around both models. Hard-code bounds on the output. Enforce a minimum and maximum speed limit and a maximum reduction step. Validate that the output is a number from an allowed set, not free text. Add a rule-based fallback, for example a safe default limit when a sensor, the API or a model fails. Limit rate and frequency of changes so the limit does not flicker.
4. ML quality (AI Act Articles 10, 15). Test and document data quality, representativeness, bias, accuracy and robustness. Cover different climates, regions, road types and extreme weather, since it is deployed everywhere in the world. Retrain and re-validate for each region and for drift. For the LLM, test for hallucinations and consistency, ideally with temperature set to 0. Consider replacing the LLM with a deterministic rule or lookup table based on air-quality index thresholds. The task is simple, there is little data, and a rule is explainable, reproducible and verifiable.
5. Logging and traceability. Automatically record inputs, outputs, model version and decisions (AI Act Article 12) so that decisions can be reconstructed after an incident.
6. Transparency. Show the current limit through signs or variable-message signs. Provide clear documentation and information about the AI use and its logic where needed.
7. Compliance of the data collection itself. Sensors need to follow local laws on data collection and use.

Organizational measures:
1. Human oversight (AI Act Article 14). Operators in a control centre can monitor, override and shut down the system. Define responsibilities and escalation, and the ability to revert to the static limit of 80 km/h or a safe limit.
2. Risk management and quality management system over the whole lifecycle (AI Act Article 9). Include hazard analysis (for example under ISO 26262 / ISO 21448 or the functional-safety standard IEC 61508), post-market monitoring, and incident reporting.
3. Conformity assessment, technical documentation and registration of the high-risk system in the EU database before placing it on the market.
4. Legal basis and data protection governance. Carry out a data protection impact assessment (DPIA), keep a record of processing activities, and name the controller. Appoint a data protection officer if required. Set retention periods, and handle data subject rights (access, deletion). Where personal data is used at all, document the legal basis (public interest or legitimate interest). Sign data processing agreements with the API and LLM providers, and clarify international data transfers (standard contractual clauses) because the LLM and API providers may be abroad.
5. Local regulatory approval for each country. Speed limits are set by law and road authorities, so a dynamic limit has to be legally authorised by the competent authority in each jurisdiction. The company must also settle liability for accidents caused by wrong decisions, and keep suitable insurance.
6. Supplier management for the LLM and the air-quality API (availability, SLAs, terms of use, GPAI provider obligations).
7. Staff training (AI literacy, AI Act Article 4) and regular audits.

## Round 3

**Answer: Yes, but only with the following technical and organizational measures.** As it stands, the system is not compliant.

### Which rules apply

| Rule | Why it applies |
|---|---|
| EU AI Act, high-risk | AI used as a safety component in managing road traffic is listed as high-risk (Annex III, point 2). Setting the speed limit to prevent near-accidents is exactly that. |
| GDPR | The accident records contain licence plates, which are personal data. |
| Road traffic law | A speed limit is a legal order. In most countries only the road authority may set it. |
| The LLM provider's terms | The air quality decision depends on an outside LLM, whose terms decide what it may be used for. |

### Technical measures

| Measure | Rule | In our system |
|---|---|---|
| Risk management: list what can go wrong and how the system reacts | AI Act Art. 9 | Missing readings give 60 km/h (REQ6), a failed LLM gives no air reduction (REQ7) |
| Training data that is relevant and representative | AI Act Art. 10 | Not met yet: one January month, and the data shows no link between the limit and near-accidents. The network must not be used for real decisions until better data exists. |
| Log every decision | AI Act Art. 12 | Done: every decision goes to `logs/decisions.csv` (SPEC7) |
| Human oversight: see why, and be able to override | AI Act Art. 14 | Done: the GUI shows the reasons, and the control room can override (REQ8) |
| Accuracy, robustness and security | AI Act Art. 15 | State the network's accuracy honestly, keep the LLM inside 10 to 40 km/h (SPEC5), and keep the API key secret |
| Data minimisation | GDPR | Done: licence plates are dropped before training and never shown (REQ10) |

### Organizational measures

- Write the technical documentation and pass a conformity assessment before going live.
- Get the road authority's approval for limits that the system sets.
- Monitor the system in use: compare the predicted and the real near-accidents every month, and retrain when they drift apart (see 13 Retraining).
- Run a data protection impact assessment, and set how long licence plates are kept.
- Train the control room staff to understand the system's limits and to override it.
- Check that the LLM provider's terms allow a safety-related use.

### "Everywhere in the world"

There is no single worldwide rule. Each country has its own road traffic law, privacy law and, more and more often, AI law. So the system can only be deployed country by country, after a legal review in each one. The EU rules above are the strictest common starting point.

## Comparison

For round 1, we selected the answer 'yes, but only with measures' and found that the system is classified as high-risk under the EU AI Act. We also addressed issues relating to data logging, overriding, licence plates and checking the legislation of each country. However, we did not mention the GDPR, we did not specify that the road traffic authority must approve the limits, and we omitted what needs to happen before the system is put into operation, such as a conformity assessment.

Round 2 arrived at the same answer and added many more elements: the GDPR and similar laws in other countries, the fact that the AI Act also applies to companies outside the EU, protection against manipulated input data, as well as contracts with API providers and large language model (LLM) providers. However, the response remained at a general level and even suggested replacing the large language model (LLM) with a simple table, which contradicts the case study.

Round 3 linked each measure to a rule and a component of our system and showed which of these are already implemented by our application, such as data logging and control room intervention. It also highlighted that our training data does not yet comply with the requirements of the AI Act, as it covers only one month and does not demonstrate any link between the speed limit and near-accidents.

What we learnt: a legal response only becomes useful when it is linked to what our system actually does.