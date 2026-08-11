"""
Automated binding evals from eval.md (Tier A + structural + dual-tradition).

Never generate expected values by snapshotting compute_panchang blindly.
Civil festival dates for authority years come from festival_civil.py (Tier A).
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from src.engine import compute_panchang
from src.festival_civil import CIVIL_OVERRIDE_YEARS, authority_notes, civil_festivals_for_date
from src.festival_stories import (
    FESTIVAL_STORIES,
    coverage_report,
    get_festival_story,
    validate_all_stories,
)
from src.festivals import TITHI_RULES, SANKRANTI_RULES, match_festivals
from src.locations import resolve_city, TRADITION_DEFAULT_CITY

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]
DENYLIST = ROOT / "tests" / "fixtures" / "denylist_phrases.txt"

# High-visibility festivals — curated Odia body should not be stub-thin
_MAJOR_STORY_MIN_OR = 100
_MAJOR_NAMES = [
    "Rath Yatra",
    "Snana Purnima",
    "Bahuda Yatra",
    "Kartik Purnima / Boita Bandana",
    "Mithuna Sankranti (Raja Parba)",
    "Nuakhai",
    "Dola Purnima",
    "Pana Sankranti (Odia New Year)",
    "Prathamastami",
    "Kumar Purnima",
    "Janmashtami",
    "Maha Shivaratri",
    "Diwali / Lakshmi Puja",
    "Simhadhwaja Rath Yatra",
    "Hera Panchami",
    "Niladri Bije",
    "Akshaya Tritiya",
]


def _fest_names(d: date) -> list[str]:
    p = compute_panchang(d)
    day = {
        "date": p["date"],
        "paksha_en": p["paksha_en"],
        "tithi_num": p["tithi_num"],
        "chandra_masa_en": p["chandra_masa_en"],
        "soura_masa_en": p["soura_masa_en"],
    }
    return [f["name_en"] for f in match_festivals(day)]


# ── Suite 1 — Structural invariants ───────────────────────────────────────

class TestEInv:
    def test_e_inv_001_amavasya_numbering(self):
        found = 0
        for i in range(0, 400, 1):
            d = date(2026, 1, 1) + timedelta(days=i)
            p = compute_panchang(d)
            if p["tithi_en"] == "Amavasya":
                found += 1
                assert p["paksha_en"] == "Krishna"
                assert p["tithi_num"] == 15
        assert found >= 12

    def test_e_inv_002_tithi_num_range(self):
        for i in range(0, 365, 3):
            p = compute_panchang(date(2026, 1, 1) + timedelta(days=i))
            assert 1 <= p["tithi_num"] <= 15

    def test_e_inv_005_default_location_odisha(self):
        place = resolve_city()
        assert 17.5 <= place["lat"] <= 22.5
        assert 81.5 <= place["lon"] <= 87.5

    def test_e_inv_007_one_engine_meta(self):
        r = client.get("/panchang/2026-07-16", params={"tradition": "jagannath"})
        assert r.status_code == 200
        meta = r.json()["meta"]
        assert meta["engine"] == "lahiri_swiss_ephemeris"
        r2 = client.get("/panchang/2026-07-16", params={"tradition": "biraja"})
        assert r2.json()["meta"]["engine"] == "lahiri_swiss_ephemeris"

    def test_e_inv_008_festival_tradition_tags(self):
        allowed = {"common", "jagannath", "biraja", "lingaraj"}
        for rule in TITHI_RULES:
            assert rule[3] in allowed
            if rule[4] == "Rath Yatra":
                assert rule[3] == "jagannath"
            if rule[4] == "Bahuda Yatra":
                assert rule[3] == "jagannath"
        for rule in SANKRANTI_RULES:
            assert rule[1] in allowed
        # Biraja chariot distinct
        names = {r[4] for r in TITHI_RULES}
        assert "Simhadhwaja Rath Yatra" in names

    def test_e_inv_009_story_coverage(self):
        report = coverage_report()
        assert report["missing"] == []

    def test_e_inv_010_odia_script_purity(self):
        assert validate_all_stories() == []


# ── Suite 3 / 4 — Festival civil + masa battery ───────────────────────────

class TestEFestCivil:
    """Tier A civil anchors — non-adhika years + 2025 authority override."""

    def test_e_fest_2026_puri_schedule(self):
        assert any("Snana" in n for n in _fest_names(date(2026, 6, 29)))
        assert any("Rath Yatra" in n for n in _fest_names(date(2026, 7, 16)))
        assert any("Bahuda" in n for n in _fest_names(date(2026, 7, 24)))

    def test_e_fest_2024_rath(self):
        assert any("Rath Yatra" in n for n in _fest_names(date(2024, 7, 7)))

    def test_e_fest_2025_rath_authority_june_27(self):
        """E-FEST-MULTIYEAR-RATH 2025 — Tourism A1 / Wikipedia A2."""
        assert any("Rath Yatra" in n for n in _fest_names(date(2025, 6, 27)))
        # Must NOT still claim Rath only on engine Ashadha Shukla 2
        assert not any("Rath Yatra" in n for n in _fest_names(date(2025, 7, 26)))

    def test_e_fest_2025_snana_authority_june_11(self):
        assert any("Snana" in n for n in _fest_names(date(2025, 6, 11)))

    def test_e_fest_2025_bahuda_july_5(self):
        assert any("Bahuda" in n for n in _fest_names(date(2025, 7, 5)))

    def test_e_fest_2022_rath_authority_july_1(self):
        """Wikipedia A2 — was wrong live (engine 2022-07-30) before multi-year civil."""
        assert any("Rath Yatra" in n for n in _fest_names(date(2022, 7, 1)))
        assert not any("Rath Yatra" in n for n in _fest_names(date(2022, 7, 30)))

    def test_e_fest_2023_rath_authority_june_20(self):
        assert any("Rath Yatra" in n for n in _fest_names(date(2023, 6, 20)))
        assert not any("Rath Yatra" in n for n in _fest_names(date(2023, 7, 19)))

    def test_e_fest_2027_rath(self):
        assert any("Rath Yatra" in n for n in _fest_names(date(2027, 7, 5)))

    def test_e_fest_no_false_may_2026(self):
        assert not any("Rath Yatra" in n for n in _fest_names(date(2026, 5, 18)))
        assert not any("Snana" in n for n in _fest_names(date(2026, 5, 1)))

    def test_e_fest_no_collapse_rath(self):
        for rule in TITHI_RULES:
            if rule[3] == "biraja" and "Rath" in rule[4]:
                assert "Simhadhwaja" in rule[4] or rule[4] != "Rath Yatra"

    def test_e_fest_biraja_rules_exist(self):
        names = {r[4] for r in TITHI_RULES}
        for required in (
            "Biraja Akshaya Tritiya",
            "Nuakhai Juhar",
            "Simhadhwaja Rath Yatra",
            "Shodasha Dinatatmika Puja Begins",
        ):
            assert required in names

    def test_civil_override_source_notes(self):
        notes = authority_notes()
        years = {n["year"] for n in notes}
        assert "2025" in years and "2022" in years and "2023" in years
        rows = civil_festivals_for_date("2025-06-27")
        assert any(r["name_en"] == "Rath Yatra" for r in rows)
        assert "Tourism" in (rows[0].get("source_note") or "")


class TestEMasaBattery:
    """
    Suite 4 — atomic festival-aligned masa rows (must pass together).

    E-MASA-01 (2026-05-10 / Drik Jyeshtha): under the closing-Purnima formula
    that keeps Snana/Rath Tourism dates correct, engine reports Vaishakha Krishna
    Ashtami. Documented open B1 tension in eval.md — do not reintroduce solar+2.
    """

    @pytest.mark.parametrize(
        "d,masa,tithi_num,paksha",
        [
            (date(2026, 6, 29), "Jyeshtha", 15, "Shukla"),  # E-MASA-02 Snana
            (date(2026, 7, 16), "Ashadha", 2, "Shukla"),  # E-MASA-03 Rath
            (date(2024, 7, 7), "Ashadha", 2, "Shukla"),
            (date(2027, 7, 5), "Ashadha", 2, "Shukla"),
        ],
    )
    def test_masa_rows_festival_aligned(self, d, masa, tithi_num, paksha):
        p = compute_panchang(d)
        assert p["chandra_masa_en"] == masa
        assert p["tithi_num"] == tithi_num
        assert p["paksha_en"] == paksha

    def test_e_masa_01_2026_05_10_documented_engine_value(self):
        """Honest lock: current engine masa (not Drik Jyeshtha) until reconciled."""
        p = compute_panchang(date(2026, 5, 10))
        assert p["paksha_en"] == "Krishna"
        assert p["tithi_num"] == 8
        assert p["chandra_masa_en"] == "Vaishakha"
        assert p["chandra_masa_en"] != "Chaitra"  # old bug

    def test_e_masa_05_2025_06_27_not_forced_ashadha(self):
        """
        E-MASA-05 note: civil Rath is 27 Jun, but engine masa is still Jyeshtha
        until adhika naming is implemented. Do not fake Ashadha on the label.
        """
        p = compute_panchang(date(2025, 6, 27))
        assert p["chandra_masa_en"] != "Ashadha"
        # Festival still present via civil override
        assert any("Rath Yatra" in n for n in _fest_names(date(2025, 6, 27)))


# ── Suite 5 / 6 / 9 — Location, API, dual tradition ───────────────────────

class TestELocApiDual:
    def test_e_loc_005_tradition_defaults(self):
        assert TRADITION_DEFAULT_CITY["jagannath"] == "puri"
        assert TRADITION_DEFAULT_CITY["biraja"] == "jajpur"
        assert resolve_city(tradition="jagannath")["key"] == "puri"
        assert resolve_city(tradition="biraja")["key"] == "jajpur"

    def test_e_loc_004_puri_jajpur_coords_differ(self):
        puri = resolve_city(city="puri")
        jajpur = resolve_city(city="jajpur")
        assert (puri["lat"], puri["lon"]) != (jajpur["lat"], jajpur["lon"])

    def test_e_api_001_health(self):
        r = client.get("/api")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"

    def test_e_api_003_bilingual_sample(self):
        r = client.get("/panchang/2026-07-16")
        assert r.status_code == 200
        d = r.json()
        for key in ("vara", "tithi", "nakshatra", "yoga", "karana", "paksha", "chandra_masa"):
            assert d[key]["en"].strip()
            assert d[key]["or"].strip()

    def test_e_api_009_invalid_tradition(self):
        r = client.get("/panchang/2026-07-16", params={"tradition": "martian"})
        assert r.status_code == 422

    def test_e_api_010_rath_story_on_wire(self):
        r = client.get(
            "/panchang/2026-07-16",
            params={"tradition": "jagannath", "city": "puri"},
        )
        assert r.status_code == 200
        fests = r.json()["festivals"]
        rath = next(f for f in fests if f["name"]["en"] == "Rath Yatra")
        blob = (rath["story"]["en"] + " " + rath["why_today"]["en"]).lower()
        assert rath["story_complete"] is True
        assert "gundicha" in blob or "chariot" in blob

    def test_e_api_007_dual_query_meta(self):
        j = client.get(
            "/panchang/2026-07-16",
            params={"tradition": "jagannath", "city": "puri"},
        ).json()
        b = client.get(
            "/panchang/2026-07-16",
            params={"tradition": "biraja", "city": "jajpur"},
        ).json()
        assert j["meta"]["city"] == "puri"
        assert b["meta"]["city"] == "jajpur"
        assert j["tithi"]["num"] == b["tithi"]["num"]
        assert "disclaimer" in j["meta"]

    def test_e_dual_002_overlay_isolation(self):
        j_names = {
            f["name"]["en"]
            for f in client.get(
                "/panchang/2026-07-16", params={"tradition": "jagannath"}
            ).json()["festivals"]
        }
        b_names = {
            f["name"]["en"]
            for f in client.get(
                "/panchang/2026-07-16", params={"tradition": "biraja"}
            ).json()["festivals"]
        }
        # Puri Rath is jagannath-tagged — visible in jagannath mode
        assert "Rath Yatra" in j_names
        # Biraja mode must NOT surface Puri Gundicha Rath
        assert "Rath Yatra" not in b_names
        assert not any("Gundicha" in n for n in b_names)
        # Jagannath mode does not invent Simhadhwaja
        assert "Simhadhwaja Rath Yatra" not in j_names

    def test_e_dual_003_meta_honesty(self):
        meta = client.get("/panchang/2026-07-16").json()["meta"]
        assert meta["masa_system"] == "purnimanta_odia_default"
        assert meta["masa_system"] != "official_biraja"
        assert meta["masa_system"] != "official_khadiratna"
        # Path A: day elements at local sunrise for the requested place
        assert meta.get("day_elements_scope") == "local_sunrise"
        assert meta.get("day_elements_anchor") in (
            "local_sunrise",
            "approx_06:00_IST_fallback",
        )
        assert "tithi" in (meta.get("place_affects") or [])
        assert "sunrise" in (meta.get("place_affects") or [])
        assert meta.get("biraja_civil_status") == "rule_only"
        disc = meta.get("disclaimer", "")
        assert "sunrise" in disc.lower()

    def test_e_dual_004_biraja_fixture_opt_in(self):
        """
        Empty list = no human civil goldens yet (product is rule_only).
        When rows appear they must carry source_edition + retrieved (not engine-generated).
        """
        path = ROOT / "tests" / "fixtures" / "golden_festivals_biraja.json"
        assert path.exists(), "fixture file required (may be empty list)"
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        for row in data:
            assert row.get("source_edition"), row
            assert row.get("retrieved"), row
            assert row.get("date") and row.get("name_contains")


# ── Suite story quality + safety ──────────────────────────────────────────

class TestStoryQualityAndSafe:
    def test_major_stories_min_odia_length(self):
        for name in _MAJOR_NAMES:
            s = get_festival_story(name)
            assert s["complete"] is True, name
            assert len(s["story"]["or"]) >= _MAJOR_STORY_MIN_OR, (
                f"{name}: Odia story too short ({len(s['story']['or'])})"
            )

    def test_e_safe_002_denylist(self):
        phrases = [
            ln.strip()
            for ln in DENYLIST.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        assert phrases
        for name, data in FESTIVAL_STORIES.items():
            blob = " ".join(
                [
                    data["story"]["en"],
                    data["story"]["or"],
                    data["why_today"]["en"],
                    data["why_today"]["or"],
                ]
            ).lower()
            for phrase in phrases:
                assert phrase.lower() not in blob, f"{name} contains denylist: {phrase}"

    def test_civil_override_years_only_when_sourced(self):
        # Only years with human-sourced Tier A/A2 tables
        assert {2022, 2023, 2025} <= set(CIVIL_OVERRIDE_YEARS)
        # Do not invent years without sources
        assert set(CIVIL_OVERRIDE_YEARS.keys()) <= {2020, 2021, 2022, 2023, 2025, 2028, 2029, 2030}
