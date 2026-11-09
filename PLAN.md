# Plan

## What we hand in

1. **A working app** that runs on our own laptops.
   - **Training:** clean the CSV data, then train the neural network.
   - **Operation:** a GUI where we enter values like temperature, and the app sets the speed limit.
2. **13 written exercises**, in [`exercises/`](exercises/).
3. **A presentation for management** with all exercise results and our lessons learned, ready for the last unit (Day 4).

Keep everything afterwards. The course says we need it again in the 3rd semester.

## What the app decides

| Situation | Who decides |
|---|---|
| Dark (below 500 millilux), or black ice risk (over 1000 micrometers of water and below 0 °C) | Neural network, aiming for at most 1 near-accident per hour on average |
| Bad air quality (read from an API) | LLM |
| None of these | No reduction: 80 km/h |

## How a turn works

1. Pull.
2. Review what the other person just pushed.
3. Do your part.
4. Tick it off in [`CHECKLIST.md`](CHECKLIST.md), push and message the other person.

Written exercises follow the three rounds on slide 28 of the Introduction deck, plus the comparison it asks for. Each exercise file has a section for every round.

Turns 2 and 3 can run at the same time. After that, wait for the previous turn.

## Turns

| Turn | Who | What |
|---|---|---|
| 1 | Both | Repo set up. Read the case study before your first exercise |
| 2 | Cristian | [01 Stakeholders](exercises/01-stakeholders.md), [04 Complete requirements](exercises/04-complete-requirements.md) |
| 3 | Morgan | [05 Class diagram](exercises/05-class-diagram.md), [06 Data problems](exercises/06-data-problems.md) |
| 4 | Cristian | [02 EU AI Act](exercises/02-eu-ai-act.md), [03 Non-functional requirements](exercises/03-non-functional-requirements.md) |
| 5 | Morgan | [07 Features](exercises/07-features.md) |
| 6 | Cristian | [10 Human-in-the-loop](exercises/10-human-in-the-loop.md), [12 Air quality tests](exercises/12-air-quality-tests.md) |
| 7 | Morgan | [08 Architecture](exercises/08-architecture.md), [11 Router tests](exercises/11-router-tests.md) |
| 8 | Cristian | [09 Sequence diagram](exercises/09-sequence-diagram.md), based on Morgan's architecture |
| 9 | Morgan | Code: data cleaning, neural network training and prediction |
| 10 | Cristian | Code: router, LLM and air quality, GUI |
| 11 | Morgan | Connect the network to the app, run all tests, [13 Retraining](exercises/13-retraining.md) |
| 12 | Cristian | Slides: requirements, LLM, GUI |
| 13 | Morgan | Slides: data, network, architecture, retraining |
| 14 | Both | Lessons learned, then practice explaining each other's half |

We are graded individually, so each of us must be able to explain the whole project.

## Good to know

- The data is in [`data/`](data/). The original files stay untouched in the course folder.
- API keys go in a `.env` file, which git ignores. Never commit a key.
