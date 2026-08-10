"""P2: AI enrichment safety + API contracts (#25–#26)."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from main import app, _build_enrichment
from src.ai_layer1 import detect_special_yogas
from src.enrichment_safety import (
    fill_rule_based_odia,
    load_denylist,
    sanitize_enrichment,
    text_hits_denylist,
)
from src.locations import detect_city_from_ip


client = TestClient(app)


def _base_day() -> dict:
    return {
        "date": "2026-07-16",
        "vara": {"en": "Thursday", "or": "ଗୁରୁବାର"},
        "tithi": {"num": 2, "en": "Dwitiya", "or": "ଦ୍ୱିତୀୟା"},
        "chandra_masa": {"en": "Ashadha", "or": "ଆଷାଢ଼"},
        "paksha": {"en": "Shukla", "or": "ଶୁକ୍ଳ"},
        "nakshatra": {"en": "Ashlesha", "or": "ଆଶ୍ଲେଷା"},
        "yoga": {"en": "Siddhi", "or": "ସିଦ୍ଧି"},
        "soura_masa": {"en": "Mithuna", "or": "ମିଥୁନ"},
        "sunrise": "05:16",
        "sunset": "18:29",
        "festivals": [],
    }


# ── #25 enrichment ─────────────────────────────────────────────────────────

class TestEnrichmentSafety:
    def test_denylist_loaded(self):
        assert load_denylist()

    def test_denylist_hits(self):
        assert text_hits_denylist("has Mahakashiya Shakti claim")

    def test_sanitize_flags_non_authoritative_and_scrubs(self):
        raw = {
            "astronomical": {"day_energy": "guaranteed cosmic energy today"},
            "cultural": {
                "jagannath_significance": {
                    "en": "Visit temple",
                    "or": "",
                }
            },
        }
        out = sanitize_enrichment(raw)
        assert out["non_authoritative"] is True
        # denylist blanked the bad energy string
        assert "cosmic" not in str(out.get("astronomical", {})).lower()
        # Odia filled for jagannath pair
        jag = out["cultural"]["jagannath_significance"]
        assert jag.get("en")
        assert jag.get("or")

    def test_build_enrichment_does_not_mutate_base(self):
        base = _base_day()
        tithi_before = dict(base["tithi"])
        enr = _build_enrichment(base)
        assert base["tithi"] == tithi_before
        assert enr.get("non_authoritative") is True
        assert "muhurtas" in enr.get("astronomical", {})

    def test_vishkambha_ashubha_alias(self):
        # translations use Vishkambha; must flag as inauspicious
        found = detect_special_yogas(0, "Rohini", "Vishkambha")
        assert any("Ashubha" in f["name"] or f["quality"] == "inauspicious" for f in found)


# ── #26 API ────────────────────────────────────────────────────────────────

class TestApiContracts:
    def test_health_ok_when_today_seeded(self):
        r = client.get("/api")
        # 200 if today in DB; 503 if not (still structured)
        assert r.status_code in (200, 503)
        body = r.json()
        assert body.get("service") == "Odia Panchang API"
        assert "engine_version" in body
        if r.status_code == 200:
            assert body["status"] == "ok"
            assert body.get("today")

    def test_insights_accepts_city_tradition(self):
        r = client.get(
            "/panchang/2026-07-16/insights",
            params={"tradition": "jagannath", "city": "puri"},
        )
        assert r.status_code == 200
        d = r.json()
        assert d["meta"]["city"] == "puri"
        assert d["meta"]["tradition"] == "jagannath"
        assert any(f["name"]["en"] == "Rath Yatra" for f in d["festivals"])
        assert d["enrichment"].get("non_authoritative") is True

        r2 = client.get(
            "/panchang/2026-07-16/insights",
            params={"tradition": "biraja", "city": "jajpur"},
        )
        assert r2.status_code == 200
        assert r2.json()["meta"]["city"] == "jajpur"
        assert "Rath Yatra" not in {
            f["name"]["en"] for f in r2.json()["festivals"]
        }

    def test_monthly_download_uses_city_key(self):
        r = client.get(
            "/api/panchang/monthly/2026/7/download",
            params={"city": "puri", "format": "text"},
        )
        assert r.status_code == 200
        cd = r.headers.get("content-disposition", "")
        assert "puri" in cd.lower()
        # Body should mention dates
        assert "2026-07" in r.text or "July" in r.text or "ଜୁଲାଇ" in r.text or len(r.text) > 100

    def test_detect_city_no_ip_echo(self):
        r = client.get("/api/detect-city")
        assert r.status_code == 200
        body = r.json()
        assert "client_ip" not in body
        assert body.get("detected_city")
        assert body.get("fallback") == "bhubaneswar"


class TestGeo:
    def test_private_ip_bhubaneswar(self):
        assert detect_city_from_ip("127.0.0.1") == "bhubaneswar"
        assert detect_city_from_ip("192.168.1.1") == "bhubaneswar"
