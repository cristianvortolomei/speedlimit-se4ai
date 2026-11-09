# 1. Stakeholders (SpeedLimit01)

Who are the stakeholders of the SpeedLimit project?

## Round 1

- Drivers want clear speed limits that keep them safe in darkness or on icy roads. They do not want delays.
- Police want to know what speed limit was in effect so they can enforce it.
- Emergency services want fewer crashes and enough room to reach people quickly when one happens.
- People living near the highway want cleaner air and worry about more traffic on their streets if drivers take another route.
- Transport companies want safe trips and predictable travel times for deliveries and buses.
- The team that builds and maintains the system wants reliable data and an easy way to spot problems.

## Round 2

- Highway operator company (management): wants safer roads, fewer accidents and lower costs and liability; worries about wrong speed limit decisions, legal responsibility and a reliable return on the ML investment.
- Drivers (road users): want safe, sensible speed limits that fit conditions without needless slowdowns; worry about being fined under a wrongly reduced limit and about privacy of licence plates.
- Accident victims and their insurers: want fewer accidents and accurate accident records (damage, injuries); worry about missed warnings or wrong limits during bad conditions.
- Police and traffic enforcement authorities: want clear, consistent and enforceable limits, and access to accident and licence plate data; worry about limits that change unpredictably or that nobody can explain.
- Government and road regulators: want compliance with road safety law and certification of the AI components; worry about unsafe or unexplained automated decisions (neural network and LLM) and accountability.
- Data scientists and ML engineers: want enough good quality data (including near-accidents) to explore relationships and train the network; worry about too little data for air quality, bias, and model drift.
- Software developers and maintainers: want a clear, testable and maintainable system; worry about the unpredictable LLM output, API failures and integrating many sensors.
- Sensor and hardware maintenance staff: want working, calibrated sensors (water, light, temperature, wind, humidity, noise, traffic); worry about faulty or missing sensor data causing wrong decisions.
- Operations and control room staff: want monitoring, override ability and a safe fallback (for example the 80 km/h default); worry about system failures and being blamed for automated decisions.
- Air quality API provider: wants correct and agreed use of its service; worry about outages, load and misuse of its data.
- LLM provider: wants correct and agreed use of its service; worry about misuse and costs of its service.
- Emergency services (ambulance, fire, rescue): want fast access to accident information and traffic that flows safely; worry about congestion and wrong limits hampering response.
- Data protection authority and the public: want licence plates and personal data stored lawfully and minimally; worry about privacy breaches and surveillance.
- Local residents and environmental groups: want less pollution and noise; worry that limits do not react enough to bad air quality or increase noise.
- Freight and transport companies: want predictable travel times; worry about frequent limit reductions causing delays and costs.

## Round 3

| Stakeholder | Wants | Main worry | Influence |
|---|---|---|---|
| **On the road** | | | |
| Car and motorcycle drivers | A limit that matches real conditions | Unexplained drops to 40-70 km/h, or a fine right after a sudden change | Low |
| Passengers | A safe trip | Having no say while the limit is wrong for the conditions | Low |
| Truck drivers and freight companies | Predictable travel times | Frequent reductions raising delays and costs | Medium |
| Road workers on the highway | Safe speeds past their work zone | The system returning to 80 km/h because it cannot know they are there | Medium |
| Emergency services | Reaching accidents quickly | Reduced limits creating congestion on the way | Medium |
| Accident and near-accident victims | Accurate records of damage and injuries | The limit not being reduced when it should have been | Low |
| Drivers named in accident records | Licence plates kept only as long as needed | Near-accident records being used against them | Low |
| **Inside the operator** | | | |
| Management | At most one near-accident per hour, at acceptable cost | Liability when a crash follows an automated limit | High |
| Control room staff | Seeing why a limit changed, and being able to override it | Being blamed for a decision they did not make | Medium |
| Legal and compliance team | Lawful handling of plates and documented decisions | Deployment before EU AI Act and privacy duties are met | High |
| Data scientists | Enough labelled near-accident data | Training on one month, which misses most conditions | Medium |
| Developers and testers | Components that can be tested | The LLM giving different answers for the same air quality | Medium |
| Sensor technicians | Knowing quickly which sensor failed | A faulty sensor silently feeding wrong values | Medium |
| **Suppliers** | | | |
| Sensor manufacturers | Sensors used within their specified range | Being blamed for readings outside it | Low |
| Air quality API provider | Use within its terms | An outage leaving the system without input | Medium |
| LLM provider | Use within its terms | Its model being used for a safety decision it does not support | Medium |
| **Authorities** | | | |
| Road traffic authority | Limits that are legally valid | An operator changing limits without approval | High |
| Police | Knowing which limit applied at any moment | Fines that cannot be defended | Medium |
| Data protection authority | Minimal storage of plates | Drivers being tracked | High |
| Environment agency | Reductions that respond to measured pollution | Air quality decisions with no traceable basis | Medium |
| **Indirectly affected** | | | |
| Insurers | Reconstructing the limit at the time of a crash | Unclear liability between driver, operator and supplier | Medium |
| Residents near the highway | Less noise and pollution | Traffic moving onto local roads when the limit is low | Low |
| Operators of connecting roads | Coordinated limits at the handover | Jams caused by sudden changes at the boundary | Medium |

## Comparison

For Round 1, I came up with 6 stakeholders, mostly people who use the road or live near it. I thought of traffic moving onto local streets, but I forgot management, the authorities and the suppliers.

Round 2 had 15 and filled most of those gaps. Some groups were lumped together though, like accident victims and insurers, and you couldn't tell who matters most.

Round 3 had 23. The groups were separate, each worry was tied to something the system actually does, and it added people like road workers. It was the most complete, but also long, and a few entries barely matter.

Asking a more specific question made a big difference. We still have to decide who really matters, and I'd say that's management, the legal team and the authorities, because they can stop the project.
