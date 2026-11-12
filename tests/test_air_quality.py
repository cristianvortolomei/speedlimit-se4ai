"""Air quality tests from exercise 12, Round 3 (T1 to T12).

T1 and T3 to T9 test the rules around the LLM with a fake LLM and a fake API, so they are
exact and free. T2 and T10 to T12 call the real LLM and are marked "llm".
"""

import json
import time
from collections import Counter
from types import SimpleNamespace

import pytest
import requests

import air_quality
import speed_limit

# Daylight, dry and warm, so only the air quality part can change the limit.
DAYLIGHT = {"illuminance_millilux": 20_000_000, "water_micrometers": 0, "temperature_celsius": 10}

# The golden answer: the reduction per European AQI band (12, Round 3).
GOLDEN = {50: 10, 70: 20, 90: 30, 150: 40}
RUNS = 10


class FakeLLM:
    """Stands in for genai.Client. Returns a fixed reply or raises a fixed error."""

    def __init__(self, reply=None, error=None):
        self.reply, self.error = reply, error
        self.calls = 0
        self.client_options = []

    def client(self, **options):
        self.client_options.append(options)
        return SimpleNamespace(models=SimpleNamespace(generate_content=self.generate_content))

    def generate_content(self, **request):
        self.calls += 1
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.reply)


@pytest.fixture
def fake_llm(monkeypatch):
    def install(reply=None, error=None):
        fake = FakeLLM(reply, error)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        monkeypatch.setattr(air_quality.genai, "Client", fake.client)
        return fake
    return install


def answer(reduction, reason="Test reason."):
    return json.dumps({"reduction_kmh": reduction, "reason": reason})


# --- Rules around the LLM (exact expected results) -------------------------------------

@pytest.mark.parametrize("aqi", [40, 0], ids=["T1 AQI 40", "T3 AQI 0"])
def test_no_llm_call_and_no_reduction_up_to_aqi_40(fake_llm, aqi):
    fake = fake_llm(reply=answer(40))
    decision = speed_limit.set_speed_limit(DAYLIGHT, {"european_aqi": aqi})
    assert fake.calls == 0
    assert decision.air_reduction == 0
    assert decision.limit == 80
    assert decision.warnings == []


def test_t4_air_quality_api_fails(monkeypatch):
    def unreachable(*args, **kwargs):
        raise requests.ConnectionError("no connection")
    monkeypatch.setattr(air_quality.requests, "get", unreachable)
    with pytest.raises(requests.ConnectionError):
        air_quality.fetch_air_quality(47.27, 11.39)

    # The GUI passes air=None when the API fails.
    decision = speed_limit.set_speed_limit(DAYLIGHT, None)
    assert decision.air_reduction == 0
    assert decision.limit == 80
    assert any("Air quality could not be read" in w for w in decision.warnings)


def test_t5_api_reply_without_aqi(monkeypatch):
    reply = SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {"current": {"pm2_5": 10, "pm10": 20, "nitrogen_dioxide": 5, "ozone": 60}},
    )
    monkeypatch.setattr(air_quality.requests, "get", lambda *args, **kwargs: reply)
    with pytest.raises(KeyError):
        air_quality.fetch_air_quality(47.27, 11.39)


def test_t6_llm_returns_an_error(fake_llm):
    fake_llm(error=RuntimeError("invalid API key"))
    decision = speed_limit.set_speed_limit(DAYLIGHT, {"european_aqi": 95})
    assert decision.air_reduction == 0
    assert decision.limit == 80
    assert any("No usable answer from the LLM" in w for w in decision.warnings)


def test_t7_llm_call_has_a_time_limit_of_15_seconds(fake_llm):
    fake = fake_llm(reply=answer(30))
    air_quality.decide_reduction({"european_aqi": 95})
    options = fake.client_options[0].get("http_options")
    timeout_ms = getattr(options, "timeout", None)
    assert timeout_ms is not None and timeout_ms <= 15_000


@pytest.mark.parametrize(
    "reply", [answer(25), "Slow down a bit."], ids=["T8 reduction 25", "T9 plain text"]
)
def test_unusable_llm_reply_is_rejected(fake_llm, reply):
    fake_llm(reply=reply)
    decision = speed_limit.set_speed_limit(DAYLIGHT, {"european_aqi": 95})
    assert decision.air_reduction == 0
    assert decision.limit == 80
    assert any("No usable answer from the LLM" in w for w in decision.warnings)


# --- The LLM itself (golden answers, real API) ------------------------------------------

@pytest.mark.llm
def test_t2_aqi_41_gets_one_llm_call_and_a_valid_reduction(monkeypatch):
    calls = []
    real_client = air_quality.genai.Client

    def counting_client(**options):
        client = real_client(**options)
        generate = client.models.generate_content

        def counted(**request):
            calls.append(request)
            return generate(**request)

        client.models.generate_content = counted
        return client

    monkeypatch.setattr(air_quality.genai, "Client", counting_client)
    reduction, _ = paced(air_quality.decide_reduction, {"european_aqi": 41})
    assert len(calls) == 1 or all(call == calls[0] for call in calls)  # retries repeat the one request
    assert reduction in air_quality.ALLOWED_REDUCTIONS


# Gemini's free tier allows 15 requests per minute, so the real-LLM tests wait between calls.
SECONDS_BETWEEN_CALLS = 4.5


RETRY_STATUS = {429, 503}  # rate limit and "model overloaded" are outages, not wrong answers
RETRIES = 4


def paced(call, *args, **kwargs):
    for attempt in range(RETRIES + 1):
        time.sleep(SECONDS_BETWEEN_CALLS)
        try:
            return call(*args, **kwargs)
        except air_quality.genai.errors.APIError as error:
            if error.code not in RETRY_STATUS or attempt == RETRIES:
                raise
            time.sleep(20)


@pytest.fixture(scope="module")
def llm_runs():
    """T10's runs, shared with T11 and T12: RUNS answers per AQI."""
    return {
        aqi: [paced(air_quality.decide_reduction, {"european_aqi": aqi}) for _ in range(RUNS)]
        for aqi in GOLDEN
    }


@pytest.mark.llm
@pytest.mark.parametrize("aqi", list(GOLDEN))
def test_t10_llm_matches_the_golden_answer_9_of_10_times(llm_runs, aqi):
    reductions = [reduction for reduction, _ in llm_runs[aqi]]
    matches = reductions.count(GOLDEN[aqi])
    assert matches >= 9, f"AQI {aqi}: expected {GOLDEN[aqi]} km/h, got {Counter(reductions)}"


@pytest.mark.llm
def test_t11_worse_air_never_gets_a_smaller_reduction(llm_runs):
    most_common = [
        Counter(reduction for reduction, _ in llm_runs[aqi]).most_common(1)[0][0]
        for aqi in sorted(GOLDEN)
    ]
    assert most_common == sorted(most_common), most_common


JUDGE_PROMPT = """You check the reasons another AI gave for lowering a highway speed limit because of air quality.
European AQI bands: 40-60 moderate, 60-80 poor, 80-100 very poor, above 100 extremely poor.

The European AQI was {aqi}. The reduction was {reduction} km/h. The reason given was:
"{reason}"

Does the reason correctly describe the air quality and fit the reduction?"""

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"fits": {"type": "boolean"}, "why": {"type": "string"}},
    "required": ["fits", "why"],
}


@pytest.mark.llm
@pytest.mark.parametrize("aqi", list(GOLDEN))
def test_t12_a_second_llm_judges_the_reason_fits(llm_runs, aqi):
    import os

    reduction, reason = llm_runs[aqi][0]
    client = air_quality.genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = paced(
        client.models.generate_content,
        model=air_quality.MODEL,
        contents=JUDGE_PROMPT.format(aqi=aqi, reduction=reduction, reason=reason),
        config=air_quality.types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_json_schema=JUDGE_SCHEMA,
        ),
    )
    verdict = json.loads(response.text)
    assert verdict["fits"], f"AQI {aqi}, {reduction} km/h, reason {reason!r}: {verdict['why']}"
