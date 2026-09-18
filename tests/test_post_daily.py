"""GitHub Actions local poster — no Render, no live Meta."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.local_day import DayNotFound, load_panchang_day, rule_enrichment
from src.tweet_generator import generate_social_caption


def test_load_known_seeded_day():
    p = load_panchang_day("2026-07-16")
    assert p["date"] == "2026-07-16"
    assert p["tithi"]["or"]
    assert p["chandra_masa"]["or"]
    assert p["meta"]["city"] == "bhubaneswar"
    assert p["sunrise"]
    assert p["sunset"]


def test_load_missing_day_raises():
    with pytest.raises(DayNotFound):
        load_panchang_day("1900-01-01")


def test_rule_enrichment_has_rahu():
    p = load_panchang_day("2026-08-10")
    enr = rule_enrichment(p)
    muh = (enr.get("astronomical") or {}).get("muhurtas") or {}
    assert "rahu_kalam" in muh
    cap = generate_social_caption(p, enr)
    assert "ଜୟ ଜଗନ୍ନାଥ" in cap
    assert "ଓଡ଼ିଆ ପଞ୍ଜିକା" in cap
    assert len(cap) <= 2200


def test_post_daily_test_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("PANJIKA_DATE", "2026-08-10")
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    from scripts.post_daily import main

    assert main([]) == 0


def test_post_daily_missing_date(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("PANJIKA_DATE", "1900-01-01")
    from scripts.post_daily import main

    assert main([]) == 1


def test_daily_workflow_does_not_call_render():
    text = Path(".github/workflows/daily-tweet.yml").read_text(encoding="utf-8")
    assert "onrender.com" not in text
    assert "scripts/post_daily.py" in text
    assert "META_PAGE_ACCESS_TOKEN" in text
    keep = Path(".github/workflows/keep-warm.yml").read_text(encoding="utf-8")
    assert "*/12" not in keep
