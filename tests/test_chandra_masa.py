"""
Phase 1 evals: Purnimanta chandra masa + festival civil anchors.

Non-negotiable: Snana / Rath / Bahuda land on Odisha Tourism–aligned dates
for non-adhika years under Lahiri + this engine.
"""

from datetime import date, timedelta

import pytest

from src.engine import compute_panchang, _chandra_masa_index, _date_to_jd, _sun_longitude, _moon_longitude
from src.festivals import match_festivals
from src.translations import CHANDRA_MASA


def _p(d: date) -> dict:
    return compute_panchang(d)


def _fest_names(d: date) -> list[str]:
    p = _p(d)
    # match_festivals expects paksha_en lower or as stored; date enables civil overrides
    day = {
        "date": p["date"],
        "paksha_en": p["paksha_en"],
        "tithi_num": p["tithi_num"],
        "chandra_masa_en": p["chandra_masa_en"],
        "soura_masa_en": p["soura_masa_en"],
    }
    return [f["name_en"] for f in match_festivals(day)]


# ── Atomic masa battery (Suite 4) ──────────────────────────────────────────

class TestMasaBattery:
    """All rows must pass together — no overfitting a single date."""

    def test_e_masa_2026_06_29_snana_jyeshtha_purnima(self):
        p = _p(date(2026, 6, 29))
        assert p["paksha_en"] == "Shukla"
        assert p["tithi_en"] == "Purnima"
        assert p["tithi_num"] == 15
        assert p["chandra_masa_en"] == "Jyeshtha"

    def test_e_masa_2026_07_16_rath_ashadha_dwitiya(self):
        p = _p(date(2026, 7, 16))
        assert p["paksha_en"] == "Shukla"
        assert p["tithi_num"] == 2
        assert p["tithi_en"] == "Dwitiya"
        assert p["chandra_masa_en"] == "Ashadha"

    def test_e_masa_2024_07_07_rath_ashadha_dwitiya(self):
        p = _p(date(2024, 7, 7))
        assert p["paksha_en"] == "Shukla"
        assert p["tithi_num"] == 2
        assert p["chandra_masa_en"] == "Ashadha"

    def test_e_masa_2024_06_22_snana_jyeshtha_purnima(self):
        p = _p(date(2024, 6, 22))
        assert p["paksha_en"] == "Shukla"
        assert p["tithi_num"] == 15
        assert p["chandra_masa_en"] == "Jyeshtha"

    def test_e_masa_2027_07_05_rath_ashadha_dwitiya(self):
        p = _p(date(2027, 7, 5))
        assert p["paksha_en"] == "Shukla"
        assert p["tithi_num"] == 2
        assert p["chandra_masa_en"] == "Ashadha"

    def test_no_magic_plus_two_on_snana(self):
        """Regression: (solar+2)%12 made 2026-06-29 Shravana."""
        p = _p(date(2026, 6, 29))
        assert p["chandra_masa_en"] != "Shravana"
        assert p["chandra_masa_en"] == "Jyeshtha"


# ── Festival civil anchors (Tourism / multi-year) ──────────────────────────

class TestFestivalCivilAnchors:
    def test_2026_snana_festival_rule(self):
        names = _fest_names(date(2026, 6, 29))
        assert any("Snana" in n for n in names), names

    def test_2026_rath_festival_rule(self):
        names = _fest_names(date(2026, 7, 16))
        assert any("Rath Yatra" in n for n in names), names

    def test_2026_bahuda_festival_rule(self):
        names = _fest_names(date(2026, 7, 24))
        assert any("Bahuda" in n for n in names), names

    def test_2024_snana_and_rath(self):
        assert any("Snana" in n for n in _fest_names(date(2024, 6, 22)))
        assert any("Rath Yatra" in n for n in _fest_names(date(2024, 7, 7)))

    def test_false_may_2026_not_snana_or_rath(self):
        """E-FEST-NO-FALSE-MAY-2026-RATH"""
        assert not any("Snana" in n for n in _fest_names(date(2026, 5, 1)))
        assert not any("Rath Yatra" in n for n in _fest_names(date(2026, 5, 18)))


# ── Structural purnimanta behaviour ────────────────────────────────────────

class TestPurnimantaStructure:
    def test_krishna_uses_closing_not_previous_only(self):
        """
        After a Purnima, Krishna days belong to the *next* named month
        (closing Purnima ahead), not the month that just ended.
        """
        # 2026-06-29 is Jyeshtha Purnima; day after should not stay Jyeshtha only
        # if we're already in Krishna of Ashadha toward Ashadha Purnima.
        d = date(2026, 7, 2)
        p = _p(d)
        assert p["paksha_en"] == "Krishna"
        # Closing Purnima is Ashadha (2026-07-29) → Ashadha
        assert p["chandra_masa_en"] == "Ashadha", p

    def test_masa_index_in_range(self):
        for i in range(0, 365, 7):
            d = date(2026, 1, 1) + timedelta(days=i)
            p = _p(d)
            assert p["chandra_masa_en"] in {m["en"] for m in CHANDRA_MASA}
            assert 1 <= p["tithi_num"] <= 15

    def test_amavasya_is_krishna_15(self):
        found = 0
        for i in range(365):
            d = date(2026, 1, 1) + timedelta(days=i)
            p = _p(d)
            if p["tithi_en"] == "Amavasya":
                found += 1
                assert p["paksha_en"] == "Krishna"
                assert p["tithi_num"] == 15
        assert found >= 12

    def test_pure_function_stable(self):
        jd = _date_to_jd(date(2026, 7, 16), 0.5)
        sun, moon = _sun_longitude(jd), _moon_longitude(jd)
        a = _chandra_masa_index(sun, moon)
        b = _chandra_masa_index(sun, moon)
        assert a == b
        assert CHANDRA_MASA[a]["en"] == "Ashadha"


# ── 2025 authority (Tier A civil) vs engine masa labels ───────────────────

class TestYear2025Authority:
    """
    Odisha Tourism (A1) + Wikipedia (A2): Rath 2025-06-27, Snana 2025-06-11.

    Engine masa labels without adhika still name 2025-06-27 as Jyeshtha and
    place engine Ashadha Shukla 2 on 2025-07-26. Festival *attachment* uses
    civil overrides (festival_civil.py) so product days match Tier A.
    """

    def test_2025_06_27_is_shukla_dwitiya(self):
        p = _p(date(2025, 6, 27))
        assert p["paksha_en"] == "Shukla"
        assert p["tithi_num"] == 2

    def test_2025_engine_ashadha_dwitiya_is_july_26_without_rath(self):
        """Rule-based Rath suppressed in 2025; civil override is 27 Jun only."""
        p = _p(date(2025, 7, 26))
        assert p["chandra_masa_en"] == "Ashadha"
        assert p["paksha_en"] == "Shukla"
        assert p["tithi_num"] == 2
        assert not any("Rath Yatra" in n for n in _fest_names(date(2025, 7, 26)))

    def test_2025_06_27_not_ashadha_under_this_engine(self):
        p = _p(date(2025, 6, 27))
        assert p["chandra_masa_en"] != "Ashadha"

    def test_2025_civil_rath_on_june_27(self):
        assert any("Rath Yatra" in n for n in _fest_names(date(2025, 6, 27)))

    def test_2025_civil_snana_on_june_11(self):
        names = _fest_names(date(2025, 6, 11))
        assert any("Snana" in n for n in names), names

    def test_2025_civil_bahuda_on_july_5(self):
        assert any("Bahuda" in n for n in _fest_names(date(2025, 7, 5)))
