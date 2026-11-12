# 10. Human-in-the-loop (SpeedLimit32b)

Would you put one or more people in the loop? Where exactly, and what skills would they need?

## Round 1

Yes. I would let the routine hourly changes happen automatically and have the administrator or staff member step in when there are warnings or a limit looks wrong. We couldn't afford to have a human in the loop for every single calculation or someone that has to approve every single change when the road gets icy suddenly.

- Control room operator. If a sensor stops working/reporting and the road looks icy, they can set a lower limit - they can always check the final limit before it goes to the sign and can always use the override as well. They need to be trained and to understand the road, the warnings, the system.
- People responsible for this model. Our team would check new data and test results before we publish a new version or the retrained model goes live. We need to be able to spot bad sensor data and judge whether the network's predictions are reliable enough.

## Round 2

Yes. I would put humans in the loop at several points, but not as a manual check on every decision. The system sets a speed limit in real time, so a human cannot approve each change. Humans belong where judgement, accountability and error-correction matter most.

**Where the humans go**

1. **Before deployment: design and validation.** A team reviews which data the models are allowed to use, how the accident and near-accident labels are defined, and whether the model's outputs are plausible. The key safeguard is hard limits that the model cannot override. Examples are a minimum and maximum speed limit, a maximum size for each reduction step, and a rule that the limit stays at 80 km/h when it is light and both weather and air quality are good. These limits are set by humans and enforced by simple rule-based code, not by the neural network or the LLM.

2. **Explorative machine learning.** Data scientists work with road-safety experts to interpret the relationships the model finds. They need to separate correlation from causation. For example, accidents may be more frequent in bad weather simply because traffic patterns differ. The domain experts decide which findings are credible enough to be used.

3. **During operation: monitoring with the option to override.** A traffic control centre operator watches the dashboard. The operator sees the current limit, the inputs behind it, and alerts when sensors disagree or fail. The operator can override the limit or switch to a fixed fallback, for example a conservative limit if the sensors fail. This is human-on-the-loop supervision, not approval of every decision. For unusual situations, such as an accident in progress, the operator decides directly.

4. **The LLM branch (air quality).** The LLM has the weakest evidence base, since there is not enough data to train a model. It can also hallucinate or misread the API response. I would therefore have the LLM only propose a reduction, within a small predefined set of options. Rule-based code should validate the API value and the proposal. A human should review a sample of its decisions regularly, and should review immediately any proposal that is unusual or contradicts the air-quality value. Longer term, an environmental expert should agree to fixed thresholds that replace or constrain the LLM.

5. **After operation: review and feedback.** Safety analysts review accidents and near-accidents, and check whether the model's limit at the time was reasonable. They also monitor for drift, for example from new sensors, seasons or road works, and decide when to retrain. This closes the feedback loop.

6. **Governance and data protection.** A data protection officer, or a legal expert, handles the licence plate data, which is personal data, and the question of who is liable if the system makes a wrong decision. Licence plates are not needed for the speed model and should be removed or pseudonymised.

**Skills needed**

- Traffic and road-safety expertise, including knowledge of how speed limits relate to accident risk and of local regulations.
- Machine learning skills: evaluating models, spotting bias, drift and overfitting, and understanding the limits of correlation.
- Understanding of LLM weaknesses, such as hallucination and sensitivity to input wording, so the reviewer knows what to look for.
- Sensor and systems knowledge, to tell a failed sensor from a real change in conditions.
- Environmental or air-quality knowledge, to judge LLM proposals on air quality.
- The ability to stay alert and decide quickly under time pressure, with clear procedures for when and how to override. A further risk is automation bias, where operators trust the system too much. Training and regular exercises help to counter this.
- Legal and ethical knowledge, especially data protection and accountability.

**Why several humans**

The roles need different skills, and one person cannot cover all of them. Separating them also gives independent checks: the people who build the model should not be the only ones who judge it. For operations, a control centre needs more than one person so that someone is always available.

## Round 3

**Yes, but not for every decision.** The limit changes every hour and darkness or ice can come suddenly, so waiting for a person on every change would make the limit late. Instead, people approve what changes the system's behaviour, confirm the decisions of its least reliable part, and handle exceptions.

Following the course's way of deciding this, feature by feature:

| Feature | Person or automatic? | Who | Why |
|---|---|---|---|
| Dark or icy: the network sets the limit | **Automatic**, the control room watches and can override (REQ8) | Control room operator | Speed matters here, and the fallback (40 km/h) is already the safe side |
| Air quality: the LLM proposes a reduction | **A person confirms** before it applies | Control room operator | The LLM is the least consistent part (20 and 30 km/h for the same AQI). Air quality changes slowly, so a short wait is safe |
| A warning appears (missing reading, failed LLM, no limit reaches the target) | **A person acknowledges** and decides whether to step in | Control room operator | The system already chose a safe limit, but someone has to know and fix the cause |
| A new or retrained network goes live | **A person approves** the release | Data scientist and road safety engineer | The network must beat a constant baseline and never predict "faster is safer" |
| The rules and thresholds (500 millilux, 1000 µm, 0 °C, AQI 40) | **A person approves** them once, and again on every change | Road authority | Only the authority may set legal speed limits |
| Monthly review of logs against real near-accidents | **A person decides** whether to retrain | Data scientist | This is how drift is caught (13 Retraining) |

### Skills they need

| Who | Skills |
|---|---|
| Control room operator | Traffic management. Knowing what each rule does and where the system is weak: it was trained on one January, and near-accidents in the data barely depend on the limit. Reading the warnings, and the authority to override. Not trusting the system blindly. |
| Data scientist | Evaluating models against baselines on held-out days, reading the decision log, recognising drift, and the retraining process. |
| Road safety engineer | Judging whether a limit is safe on this road, and the safety rules the network must follow. |
| Road authority | Traffic law, and the duty to approve the rules before they are used. |

### Changes to our app

- The control room has to confirm LLM reductions. Today they apply automatically.
- Overrides and confirmations have to be logged with the person's name.

## Comparison

For Round 1, we decided that the hourly changes should be made automatically, as ice can form suddenly, and people should only intervene when there are warnings or when a limit appears to be incorrect. We included the control room operator and our own team in the process.

The rounds dedicated to AI were more descriptive. Round 2 added more people, such as safety analysts, an environmental expert and a data protection officer, and highlighted the risk of operators placing too much trust in the system.

Round 3 analysed the system feature by feature, just like the avalanche example from the course: the network remains automated, a person confirms the air quality reductions proposed by the LLM, and someone approves each new network before it is put into operation. It also listed the changes we should make to our application.

What we learnt: whether a person needs to be involved depends on how quickly each decision needs to be made and how much trust we can place in the part of the system making it.