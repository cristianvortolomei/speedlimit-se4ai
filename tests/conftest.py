"""Shared test setup: makes app/ importable and loads the API key from .env."""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
load_dotenv(ROOT / ".env")


def pytest_collection_modifyitems(config, items):
    # Tests marked "llm" call the real Gemini API. Skip them when there is no key.
    if os.environ.get("GEMINI_API_KEY"):
        return
    skip = pytest.mark.skip(reason="GEMINI_API_KEY is not set")
    for item in items:
        if "llm" in item.keywords:
            item.add_marker(skip)
