# 11. Router tests (SpeedLimit10b)

The router takes illuminance (millilux), water level (micrometers) and temperature (degrees Celsius), all integers, and decides yes or no whether the limit should drop because of the weather. Based on the requirements, write the four test cases most likely to find defects, as a table: test case ID, the three inputs, expected output. Negative testing is not needed.

## Round 1

ID | Light (mlx) | Water (µm) | Temp (°C) | Expected | What
| --- | --- | --- | --- | ---| --- |
1 |	499 |	0 |	10	| yes |	Dark
2 | 500 | 1001 | −1	| yes | Light, but too much water and too cold
3 | 500 |	1000 | −1 | no | Light, but there is not enough water for black ice despite the cold
4 | 500 | 1001 | 0 | no | Light, there is too much water, but it's not cold enough

## Round 2

The router says yes when it is dark (SPEC1: illuminance below 500 millilux) or there is a danger of black ice (SPEC2: water above 1000 micrometers and temperature below 0 °C). Defects are most likely at the thresholds, so every test case sits right next to one.

| ID | Illuminance (mlx) | Water (µm) | Temperature (°C) | Expected |
|---|---|---|---|---|
| TC1 | 499 | 0 | 10 | yes |
| TC2 | 500 | 1001 | −1 | yes |
| TC3 | 500 | 1000 | −1 | no |
| TC4 | 500 | 1001 | 0 | no |

- TC1: just dark, no ice.
- TC2: just not dark, but just enough water and just below freezing.
- TC3: cold, but exactly 1000 µm is not more than 1000, so no black ice.
- TC4: wet, but exactly 0 °C is not below 0, so no black ice.

## Round 3

Follows the Testing deck: split each input into equivalence classes, then test the boundary values, because programmers often use `<` instead of `<=` (off-by-one errors).

**Equivalence classes and boundary values.** Each condition in the requirements draws one line:

| Input | Condition | Classes | Boundary values |
|---|---|---|---|
| Illuminance | below 500 mlx (SPEC1) | dark: 0 to 499, not dark: 500 and up | 499, 500 |
| Water | above 1000 µm (SPEC2) | not wet: up to 1000, wet: 1001 and up | 1000, 1001 |
| Temperature | below 0 °C (SPEC2) | freezing: −1 and down, not freezing: 0 and up | −1, 0 |

That gives six boundary values. Four test cases can still cover all of them, if no value is hidden by another condition:

- **Darkness hides the ice check.** When it is dark the answer is yes whatever the water and temperature are, so a dark test case can't find a defect in the black ice check. Only one test case is dark (499). The other three use 500, which also tests the other side of the darkness boundary.
- **Each black ice test changes one input at a time.** Starting from the case that is just icy (1001 µm, −1 °C), each "no" case moves exactly one input across its boundary. If the answer is wrong, the cause is clear.

| ID | Illuminance (mlx) | Water (µm) | Temperature (°C) | Expected | Boundary values covered | Defects it finds |
|---|---|---|---|---|---|---|
| TC1 | 499 | 0 | 10 | yes | 499 | Darkness checked with `<= 498` or a wrong threshold. Input mistaken for lux: comparing 499 against 0.5 wrongly says not dark. Black ice wrongly required as well (`and` instead of `or` between darkness and black ice). |
| TC2 | 500 | 1001 | −1 | yes | 500, 1001, −1 | Black ice not detected just past both thresholds: water checked with `> 1001` or temperature with `< −1`. |
| TC3 | 500 | 1000 | −1 | no | 500, 1000, −1 | Water checked with `>=` instead of `>`. Black ice checked with `or` instead of `and` (the cold alone would trigger it). 500 counted as dark (`<=` instead of `<`). |
| TC4 | 500 | 1001 | 0 | no | 500, 1001, 0 | Temperature checked with `<=` instead of `<`. Black ice checked with `or` instead of `and` (the water alone would trigger it). 500 counted as dark. |

**What is deliberately not tested:**

- Dark and icy at the same time, or light, dry and warm. These are further combinations of the same classes, so they would hardly find new defects.
- Invalid inputs such as negative illuminance or text (negative testing), as the exercise says.
- Decimal values. The exercise says the inputs are integers, but the app now accepts decimals (−0.1 °C, 1000.5 µm), which would be worth testing separately.

The four cases run automatically in [`tests/test_router.py`](../tests/test_router.py) with `pytest`, and all pass against `app/router.py`.

## Comparison

This was quite a straightforward task, with the LLM not deciding to create different tests from what I did. The additions of pytests in the repo was great from round 3. Round 3 added some notable good points regarding:
- the equivalence classes and six boundary values, explained the way the Testing deck does
- why the dark case hides the ice check
- which bug each case catches
- what’s deliberately not tested, including decimals