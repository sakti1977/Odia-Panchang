"""
E-INV-004: Database rows must match live engine for the seed default location.
"""

from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from src.engine import compute_panchang
from src.models import PanchangDay, Festival, get_engine, get_session_factory
from src.festivals import match_festivals

DATABASE_URL = "sqlite:///./data/panchang.db"


@pytest.fixture(scope="module")
def session():
    engine = get_engine(DATABASE_URL)
    SessionLocal = get_session_factory(engine)
    s = SessionLocal()
    yield s
    s.close()


def test_db_has_full_range(session: Session):
    count = session.query(PanchangDay).count()
    assert count >= 4000
    assert session.get(PanchangDay, "2020-01-01") is not None
    assert session.get(PanchangDay, "2030-12-31") is not None


def test_db_engine_parity_sample_year_2026(session: Session):
    """Every day of 2026: DB masa/tithi/nakshatra match compute_panchang."""
    mismatches = []
    d0 = date(2026, 1, 1)
    for i in range(365):
        d = d0 + timedelta(days=i)
        row = session.get(PanchangDay, d.isoformat())
        assert row is not None, f"missing {d}"
        live = compute_panchang(d)
        for field in (
            "chandra_masa_en",
            "tithi_num",
            "tithi_en",
            "paksha_en",
            "nakshatra_en",
            "soura_masa_en",
        ):
            db_val = getattr(row, field)
            live_val = live[field]
            if db_val != live_val:
                mismatches.append((d.isoformat(), field, db_val, live_val))
    assert mismatches == [], f"parity failures (first 10): {mismatches[:10]}"


def test_db_2026_festival_anchors(session: Session):
    def names(ds: str) -> list[str]:
        rows = session.query(Festival).filter(Festival.date == ds).all()
        return [r.name_en for r in rows]

    assert any("Snana" in n for n in names("2026-06-29")), names("2026-06-29")
    assert any("Rath Yatra" in n for n in names("2026-07-16")), names("2026-07-16")
    assert any("Bahuda" in n for n in names("2026-07-24")), names("2026-07-24")
    assert not any("Snana" in n for n in names("2026-05-01"))
    assert not any("Rath Yatra" in n for n in names("2026-05-18"))


def test_db_row_matches_match_festivals_rules(session: Session):
    """Spot-check: festivals stored for a day ⊆ rules for that day."""
    for ds in ("2026-06-29", "2026-07-16", "2024-07-07"):
        row = session.get(PanchangDay, ds)
        assert row
        live = compute_panchang(date.fromisoformat(ds))
        expected = {
            f["name_en"]
            for f in match_festivals(
                {
                    "paksha_en": live["paksha_en"],
                    "tithi_num": live["tithi_num"],
                    "chandra_masa_en": live["chandra_masa_en"],
                    "soura_masa_en": live["soura_masa_en"],
                }
            )
        }
        stored = {f.name_en for f in row.festivals}
        # stored may include sankranti extras; at least tithi-rule festivals must be present
        assert expected <= stored or expected.issubset(stored) or expected & stored
        # stronger: every expected tithi festival is stored
        missing = expected - stored
        assert not missing, f"{ds} missing festivals {missing}; have {stored}"
