"""
Path A (sunrise-anchored day elements) + monthly vrata coverage (Ekadashi / Pradosha / Sankashti).
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from main import app
from src.engine import ENGINE_VERSION, compute_panchang
from src.festival_stories import FESTIVAL_STORIES, coverage_report
from src.festivals import TITHI_RULES, match_festivals

client = TestClient(app)

_CHANDRA = [
    "Chaitra",
    "Vaishakha",
    "Jyeshtha",
    "Ashadha",
    "Shravana",
    "Bhadrapada",
    "Ashwina",
    "Kartika",
    "Margashira",
    "Pausha",
    "Magha",
    "Phalguna",
]


class TestPathASunriseAnchor:
    def test_engine_version_marks_sunrise(self):
        assert "sunrise" in ENGINE_VERSION
        assert "lahiri" in ENGINE_VERSION

    def test_default_compute_uses_local_sunrise(self):
        p = compute_panchang(date(2026, 7, 16))
        assert p["day_elements_anchor"] == "local_sunrise"
        assert p["sunrise"]  # HH:MM present
        assert "lat" in p and "lon" in p

    def test_place_changes_sunrise_time(self):
        d = date(2026, 6, 21)  # long day; latitude effect clear
        bbs = compute_panchang(d, lat=20.2961, lon=85.8245)
        delhi = compute_panchang(d, lat=28.6139, lon=77.2090)
        assert bbs["day_elements_anchor"] == "local_sunrise"
        assert delhi["day_elements_anchor"] == "local_sunrise"
        # Different longitudes → different local sunrise clock times
        assert bbs["sunrise"] != delhi["sunrise"]

    def test_key_festival_tithi_anchors_hold(self):
        """Civil-aligned masa/tithi still hold under sunrise JD (Bhubaneswar default)."""
        cases = [
            (date(2024, 6, 22), "Jyeshtha", "Shukla", 15),  # Snana
            (date(2024, 7, 7), "Ashadha", "Shukla", 2),  # Rath
            (date(2026, 6, 29), "Jyeshtha", "Shukla", 15),
            (date(2026, 7, 16), "Ashadha", "Shukla", 2),
        ]
        for d, masa, paksha, tnum in cases:
            p = compute_panchang(d)
            assert p["chandra_masa_en"] == masa, d
            assert p["paksha_en"] == paksha, d
            assert p["tithi_num"] == tnum, d

    def test_api_meta_path_a(self):
        r = client.get("/panchang/2026-07-16")
        assert r.status_code == 200
        meta = r.json()["meta"]
        assert meta["day_elements_scope"] == "local_sunrise"
        assert meta["day_elements_anchor"] == "local_sunrise"
        affects = meta.get("place_affects") or []
        for key in ("tithi", "nakshatra", "chandra_masa", "sunrise", "sunset"):
            assert key in affects
        assert meta.get("engine_version") == ENGINE_VERSION


class TestMonthlyVrataCoverage:
    def _rules_for(self, masa: str, paksha: str, tithi: int) -> list:
        return [
            r
            for r in TITHI_RULES
            if r[0] == masa and r[1] == paksha and r[2] == tithi and r[3] == "common"
        ]

    def test_twenty_four_named_ekadashi(self):
        """12 months × 2 paksha = 24 named common Ekadashi rules."""
        found = []
        for masa in _CHANDRA:
            for paksha in ("shukla", "krishna"):
                rules = self._rules_for(masa, paksha, 11)
                assert rules, f"missing Ekadashi for {masa} {paksha}"
                assert any("Ekadashi" in r[4] for r in rules), (masa, paksha, rules)
                found.append(rules[0][4])
        assert len(found) == 24
        # All unique names (Phalguna papamochani is disambiguated)
        assert len(set(found)) == 24

    def test_pradosha_every_trayodashi(self):
        """Every masa × both paksha (except none) has Pradosha on tithi 13."""
        for masa in _CHANDRA:
            for paksha in ("shukla", "krishna"):
                rules = self._rules_for(masa, paksha, 13)
                assert any(r[4] == "Pradosha Vrat" for r in rules), (masa, paksha)

    def test_sankashti_every_krishna_chaturthi(self):
        for masa in _CHANDRA:
            rules = self._rules_for(masa, "krishna", 4)
            assert any(r[4] == "Sankashti Chaturthi" for r in rules), masa

    def test_stories_cover_all_vrata_names(self):
        report = coverage_report()
        assert report["missing"] == [], report["missing"]
        for name in (
            "Nirjala Ekadashi",
            "Pradosha Vrat",
            "Sankashti Chaturthi",
            "Devshayani / Padma Ekadashi",
            "Prabodhini / Devutthana Ekadashi",
        ):
            assert name in FESTIVAL_STORIES

    def test_year_has_many_ekadashi_hits(self):
        """Across 2026, named Ekadashi festivals fire on many civil days."""
        hits = 0
        for i in range(366):
            d = date(2026, 1, 1) + timedelta(days=i)
            p = compute_panchang(d)
            day = {
                "date": p["date"],
                "paksha_en": p["paksha_en"],
                "tithi_num": p["tithi_num"],
                "chandra_masa_en": p["chandra_masa_en"],
                "soura_masa_en": p["soura_masa_en"],
            }
            names = [f["name_en"] for f in match_festivals(day)]
            if any("Ekadashi" in n for n in names):
                hits += 1
        # ~24 lunar Ekadashis; allow calendar drift / double counts
        assert hits >= 20
