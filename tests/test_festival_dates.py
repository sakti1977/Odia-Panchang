"""
E-FEST-REFERENCE — festival dates can't silently go wrong.

Blocking in CI. Each test guards a different failure path:

  1. DB vs independent reference (Drik, Tier B)      — a bad seed / bad rule
  2. Engine vs DB                                    — reseed skipped
  3. Tier A goldens (Tourism / temple / dated news)  — Puri cycle, Odia days
  4. Month labels vs the reference's own labels      — masa formula regressions
  5. Corrections not stale                           — engine changed under a correction
  6. Coverage look-ahead                             — reference / Tier A not refreshed
  7. Publication gate                                — unverified festivals never announced

Fixtures: tests/fixtures/festival_reference/drik_bhubaneswar.json (refresh with
scripts/fetch_festival_reference.py) and tests/fixtures/golden_festivals.json
(human-maintained, cited). Never regenerate either from the engine.
"""

from __future__ import annotations

import re
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import pytest

from src.festival_audit import (
    MAJOR_FESTIVALS,
    REFERENCE_MAP,
    audit,
    check_day,
    festivals_from_db,
    is_verified,
    load_reference,
    prepare_for_publish,
    reference_years,
)
from src.festival_calendar import festival_calendar
from src.festival_civil import DATE_CORRECTIONS, tier_a_rows
from src.translations import CHANDRA_MASA

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "panchang.db"
BBSR = (20.2961, 85.8245, 5.5)


def _db_years() -> list[int]:
    with sqlite3.connect(DB) as conn:
        lo, hi = conn.execute("select min(date), max(date) from panchang_days").fetchone()
    return list(range(int(lo[:4]), int(hi[:4]) + 1))


def _db_festivals_by_date() -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    with sqlite3.connect(DB) as conn:
        for d, name in conn.execute("select date, name_en from festivals"):
            out[d].add(name)
    return out


# 1 ────────────────────────────────────────────────────────────────────────

def test_db_festival_dates_match_reference_every_year():
    res = audit(festivals_from_db(DB))
    assert res.checked > 800
    assert res.ok, "\n" + "\n".join(res.lines())


def test_every_major_festival_is_independently_checked():
    from src.festival_civil import tier_a_rows

    tier_a_names = {r["name_en"] for r in tier_a_rows()}
    for name in MAJOR_FESTIVALS:
        assert name in REFERENCE_MAP or name in tier_a_names, name


# 2 ────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("year", [date.today().year, date.today().year + 1])
def test_db_festivals_equal_engine_calendar(year):
    """A stale DB (engine or rules changed, no reseed) fails here."""
    if year not in _db_years():
        pytest.skip(f"{year} not seeded")
    db = _db_festivals_by_date()
    cal = festival_calendar(year, *BBSR)
    engine = {d: {f["name_en"] for f in fs} for d, fs in cal.items()}
    db_year = {d: v for d, v in db.items() if d.startswith(f"{year}-")}
    diff = sorted(
        (d, sorted(db_year.get(d, set()) ^ engine.get(d, set())))
        for d in set(db_year) | set(engine)
        if db_year.get(d, set()) != engine.get(d, set())
    )
    assert not diff, f"DB differs from engine — run `python seed.py --refresh-festivals`: {diff[:10]}"


# 3 ────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("row", tier_a_rows(), ids=lambda r: r["id"])
def test_tier_a_golden_date_exact(row):
    """Present on the cited date and not on the day either side."""
    db = _db_festivals_by_date()
    d = date.fromisoformat(row["date"])
    assert row["name_en"] in db.get(row["date"], set()), row
    for k in (-1, 1):
        assert row["name_en"] not in db.get((d + timedelta(days=k)).isoformat(), set()), row


def test_tier_a_rows_cite_a_source():
    ids = set()
    for r in tier_a_rows():
        assert r["tier"] in {"A1", "A2", "A3"} and len(r["source"]) > 15, r
        assert r["id"] not in ids
        ids.add(r["id"])


# 4 ────────────────────────────────────────────────────────────────────────

_ALIAS = {"Ashwin": "Ashwina", "Margashirsha": "Margashira"}
# Drik keeps these in the Adhika month in Adhika years but prints the nija
# label (e.g. Ganga Dussehra 2026-05-25 "Jyeshtha, Shukla Dashami"), so the
# day's true label is Adhika — not a masa disagreement.
_OBSERVED_IN_ADHIKA = {"Ganga Dussehra"}


def test_month_labels_match_reference_labels():
    """Every reference Purnima/Amavasya/Ekadashi/festival carries Drik's own
    Purnimanta label. Where our sunrise tithi equals Drik's tithi, the month
    (and Adhika flag) must match exactly — no tolerance."""
    with sqlite3.connect(DB) as conn:
        rows = {
            d: (m, p, t)
            for d, m, p, t in conn.execute(
                "select date, chandra_masa_en, paksha_en, tithi_en from panchang_days"
            )
        }
    checked, bad = 0, []
    for e in load_reference()["events"]:
        m = re.match(r"(Adhika )?(\w+), (Shukla|Krishna) (\w+)$", e["lunar"])
        if e["page"] != "hindu" or not m or e["date"] not in rows:
            continue
        if e["name"] in _OBSERVED_IN_ADHIKA:
            continue
        ours_masa, ours_paksha, ours_tithi = rows[e["date"]]
        ref_tithi = {"Amavasya": "Amavasya", "Purnima": "Purnima"}.get(m.group(4), m.group(4))
        if (ours_paksha, ours_tithi) != (m.group(3), ref_tithi):
            continue  # tithi changes near sunrise: observance-day label, not a masa check
        expected = (m.group(1) or "") + _ALIAS.get(m.group(2), m.group(2))
        checked += 1
        if ours_masa != expected:
            bad.append((e["date"], e["name"], e["lunar"], ours_masa))
    assert checked > 900
    assert not bad, bad[:10]


# 5 ────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("corr", DATE_CORRECTIONS, ids=lambda c: f"{c['names'][0]}-{c['date']}")
def test_corrections_are_current_and_verified(corr):
    """festival_calendar raises StaleCorrection if the engine no longer puts
    the festival on engine_date; the corrected date must be confirmed."""
    year = int(corr["date"][:4])
    cal = festival_calendar(year, *BBSR)
    for name in corr["names"]:
        assert name in {f["name_en"] for f in cal.get(corr["date"], ())}
        if name in REFERENCE_MAP:
            assert is_verified(name, corr["date"])


# 6 ────────────────────────────────────────────────────────────────────────

def test_reference_covers_every_seeded_year():
    missing = [y for y in _db_years() if y not in reference_years()]
    assert not missing, f"Fetch reference: scripts/fetch_festival_reference.py --start {missing[0]} --end {missing[-1]}"


def test_reference_look_ahead():
    """From 1 October the reference must cover next year, so the January
    posts are never unchecked."""
    today = date.today()
    need = today.year + 1 if today.month >= 10 else today.year
    assert need in reference_years(), (
        f"Festival reference ends before {need}: "
        f"python scripts/fetch_festival_reference.py --start {today.year} --end {need + 4}"
    )


def test_tier_a_rath_look_ahead():
    """The Puri cycle must be confirmed from Tier A before it is announced:
    within 120 days of Rath Yatra the year's Tier A Rath row must exist."""
    today = date.today()
    for year in (today.year, today.year + 1):
        ref = [e["date"] for e in load_reference()["events"]
               if e["name"] == "Rath Yatra" and e["date"].startswith(f"{year}-")]
        if not ref:
            continue
        days_to_rath = (date.fromisoformat(ref[0]) - today).days
        if 0 <= days_to_rath <= 120:
            assert any(r["name_en"] == "Rath Yatra" and r["date"].startswith(f"{year}-")
                       for r in tier_a_rows()), f"Add the {year} Tier A Puri schedule to golden_festivals.json"


# 7 ────────────────────────────────────────────────────────────────────────

def test_publication_gate_blocks_contradiction():
    from src.festival_audit import PublishBlocked

    wrong = {"date": "2026-07-17", "festivals": [{"name_en": "Rath Yatra"}]}
    with pytest.raises(PublishBlocked):
        prepare_for_publish(wrong)
    missing = {"date": "2026-07-16", "festivals": []}
    with pytest.raises(PublishBlocked):
        prepare_for_publish(missing)


def test_publication_gate_drops_unverified():
    day = {"date": "2026-07-27", "festivals": [{"name_en": "Niladri Bije"}, {"name_en": "Pradosha Vrat"}]}
    kept, omitted = prepare_for_publish(day)
    assert kept["festivals"] == [] and set(omitted) == {"Niladri Bije", "Pradosha Vrat"}


def test_every_seeded_day_this_year_passes_the_gate():
    """What the daily job will do, for every remaining day of the year."""
    from src.local_day import load_panchang_day

    today = date.today()
    d = today
    failures = []
    while d.year == today.year:
        try:
            prepare_for_publish(load_panchang_day(d))
        except Exception as exc:  # noqa: BLE001 — collect every day's problem
            failures.append(f"{d}: {exc}")
        d += timedelta(days=1)
    assert not failures, failures[:10]


def test_check_day_requires_reference_year():
    assert check_day("2099-01-01", []) != []
