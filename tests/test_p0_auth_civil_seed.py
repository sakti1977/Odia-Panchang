"""
P0 tickets #17–#20: tweet auth, civil honesty, multi-year civil, engine stamp.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app, _festival_to_dict
from src.engine import ENGINE_VERSION, compute_panchang
from src.festival_civil import (
    DATE_CORRECTIONS,
    civil_festivals_for_date,
    civil_why_today,
    lookup_civil_meta,
)
from src.festival_stories import validate_odia_text
from src.festivals import match_festivals
from src.models import Festival


client = TestClient(app)


def _names(d: date) -> list[str]:
    p = compute_panchang(d)
    return [f["name_en"] for f in match_festivals(p)]


# ── #18 tweet auth ─────────────────────────────────────────────────────────

class TestTweetAuth:
    def test_post_without_secret_unauthorized_or_unconfigured(self, monkeypatch):
        monkeypatch.delenv("TWEET_CRON_SECRET", raising=False)
        r = client.post("/tweet/post")
        assert r.status_code in (401, 503)

    def test_post_wrong_secret_401(self, monkeypatch):
        monkeypatch.setenv("TWEET_CRON_SECRET", "correct-secret-value")
        r = client.post(
            "/tweet/post",
            headers={"Authorization": "Bearer wrong"},
        )
        assert r.status_code == 401

    def test_post_bearer_accepted_reaches_job(self, monkeypatch):
        monkeypatch.setenv("TWEET_CRON_SECRET", "correct-secret-value")

        async def fake_job():
            return {
                "date": "2026-08-10",
                "bundle": {
                    "date": "2026-08-10",
                    "main_tweet": "x",
                    "main_tweet_length": 1,
                    "thread_reply": "",
                    "thread_reply_length": 0,
                    "festivals": [],
                },
                "result": {"status": "logged", "message": ""},
            }

        monkeypatch.setattr("main.run_daily_tweet", fake_job)
        r = client.post(
            "/tweet/post",
            headers={"Authorization": "Bearer correct-secret-value"},
        )
        assert r.status_code == 200
        assert r.json()["result"]["status"] == "logged"

    def test_status_reports_cron_auth(self):
        r = client.get("/api/status")
        assert r.status_code == 200
        tw = r.json()["twitter"]
        assert tw["cron_auth_required"] is True


# ── #17 multi-year civil ───────────────────────────────────────────────────

class TestMultiYearCivil:
    def test_no_year_needs_injected_festivals(self):
        """The engine reaches 2022/2023/2025 Tier A dates without overrides."""
        assert civil_festivals_for_date("2022-07-01") == []
        assert civil_festivals_for_date("2025-06-27") == []

    def test_2022_rath_on_july_1_not_july_30(self):
        assert "Rath Yatra" in _names(date(2022, 7, 1))
        assert "Rath Yatra" not in _names(date(2022, 7, 30))

    def test_2023_rath_on_june_20_not_july_19(self):
        assert "Rath Yatra" in _names(date(2023, 6, 20))
        assert "Rath Yatra" not in _names(date(2023, 7, 19))

    def test_2022_snana_and_bahuda(self):
        assert any("Snana" in n for n in _names(date(2022, 6, 14)))
        assert any("Bahuda" in n for n in _names(date(2022, 7, 9)))


# ── #19 civil honesty on wire ──────────────────────────────────────────────

class TestCivilHonesty:
    def test_civil_why_today_odia_pure(self):
        w = civil_why_today("Odisha Tourism 2025")
        validate_odia_text(w["or"])
        assert "Ashadha" not in w["en"]  # no fake masa claim

    def test_tier_a_festival_carries_source(self):
        p = compute_panchang(date(2025, 6, 27))
        rath = next(f for f in match_festivals(p) if f["name_en"] == "Rath Yatra")
        assert rath.get("tier_a_confirmed") is True
        assert rath.get("civil_override") is False
        assert "Tourism" in rath.get("source_note", "")

    def test_correction_uses_honest_why_today(self):
        c = DATE_CORRECTIONS[0]
        p = compute_panchang(date.fromisoformat(c["date"]))
        fest = next(f for f in match_festivals(p) if f["name_en"] == c["names"][0])
        assert fest.get("civil_override") is True
        assert "public calendar" in fest["why_today"]["en"]
        validate_odia_text(fest["why_today"]["or"])

    def test_api_payload_exposes_source_fields(self):
        r = client.get("/panchang/2025-06-27?tradition=jagannath")
        assert r.status_code == 200
        rath = next(
            f for f in r.json()["festivals"] if f["name"]["en"] == "Rath Yatra"
        )
        assert rath.get("tier_a_confirmed") is True
        assert rath.get("source_note")
        assert "Ashadha" not in rath["why_today"]["en"] or rath["story_complete"]

    def test_lookup_and_festival_to_dict(self):
        meta = lookup_civil_meta("2025-06-27", "Rath Yatra")
        assert meta and meta["tier_a_confirmed"] is True
        fake = Festival(
            date="2025-06-27",
            name_en="Rath Yatra",
            name_or="ରଥ ଯାତ୍ରା",
            tradition="jagannath",
            description="x",
        )
        d = _festival_to_dict(fake)
        assert d.get("tier_a_confirmed") is True and d.get("source_tier") == "A1"


# ── #20 engine version ─────────────────────────────────────────────────────

class TestEngineVersion:
    def test_engine_version_constant(self):
        assert ENGINE_VERSION
        assert "lahiri" in ENGINE_VERSION

    def test_api_exposes_engine_version(self):
        r = client.get("/api")
        assert r.json().get("engine_version") == ENGINE_VERSION
        meta = client.get("/panchang/2026-07-16").json()["meta"]
        assert meta.get("engine_version") == ENGINE_VERSION
        assert meta.get("day_elements_anchor")

    def test_seed_version_helpers(self, tmp_path, monkeypatch):
        import seed as seedmod

        monkeypatch.setattr(seedmod, "DATABASE_URL", f"sqlite:///{tmp_path}/t.db")
        # redirect version file next to tmp db
        p = seedmod.engine_version_path()
        seedmod.write_stored_engine_version("v-test")
        assert seedmod.read_stored_engine_version() == "v-test"
        assert seedmod.engine_version_path().name == ".engine_version"
