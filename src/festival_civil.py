"""
Tier A civil festival dates — metadata and the reviewed correction register.

History
-------
Until the lunar-month fix (src/lunar_calendar.py) this module *injected*
Puri-cycle festivals for 2022/2023/2025 because the old masa heuristic put
them a month late, and it derived Hera Panchami as Rath+3 without a source
(wrong in every checked year: it is the fifth day of the yatra, Rath+4).
The engine now reproduces every sourced Puri date on its own, so nothing is
injected any more.

What lives here now
-------------------
1. Tier A rows (tests/fixtures/golden_festivals.json): cited civil dates.
   Exposed on the wire (`source_tier`, `source_note`) and asserted by tests.
2. DATE_CORRECTIONS: reviewed cases where the observance rule in
   festival_calendar.py and the reference disagree at a knife edge. Each
   records where the engine puts the festival (so a stale entry fails the
   tests the moment the engine changes) and the date we publish, with the
   source. Add one only after reading the source; never to make CI green.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "golden_festivals.json"

# Festivals whose published date follows a reviewed correction.
DATE_CORRECTIONS: list[dict[str, Any]] = [
    {
        "names": ["Akshaya Tritiya", "Chandan Yatra Begins", "Biraja Akshaya Tritiya"],
        "engine_date": "2023-04-23",
        "date": "2023-04-22",
        "source": "Drik Panchang Odia + Hindu calendars 2023, Bhubaneswar (Tier B, both pages)",
        "reason": (
            "Tritiya lasts 145 min after the 23 Apr sunrise against the 144-min trimuhurta "
            "threshold — inside ephemeris error; published date follows the reference."
        ),
    },
    {
        "names": ["Gamha Purnima"],
        "engine_date": "2022-08-12",
        "date": "2022-08-11",
        "source": "Drik Panchang Odia calendar 2022, Bhubaneswar (Tier B)",
        "reason": (
            "Purnima 11 Aug 10:38 → 12 Aug 07:05 covers neither forenoon; the reference follows "
            "the Rakhi Purnima convention (afternoon, Bhadra-aware). Confirm against the Odisha "
            "government holiday list."
        ),
    },
    {
        "names": ["Gamha Purnima"],
        "engine_date": "2023-08-31",
        "date": "2023-08-30",
        "source": "Drik Panchang Odia calendar 2023, Bhubaneswar (Tier B)",
        "reason": "Same pattern as 2022 (Purnima 30 Aug 10:58 → 31 Aug 07:05).",
    },
]


@lru_cache(maxsize=1)
def tier_a_rows() -> tuple[dict[str, str], ...]:
    return tuple(json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))["rows"])


def tier_a_dates(name_en: str) -> dict[str, dict[str, str]]:
    """ISO date → Tier A row for one festival."""
    return {r["date"]: r for r in tier_a_rows() if r["name_en"] == name_en}


def corrections_for_year(year: int) -> list[dict[str, Any]]:
    return [c for c in DATE_CORRECTIONS if c["date"].startswith(f"{year}-")]


# ── Backward-compatible helpers (API meta, stories) ─────────────────────────

def override_year(year: int | None) -> None:
    """No year is overridden any more (kept for API compatibility)."""
    return None


def suppressed_rule_names(year: int | None) -> frozenset[str]:
    return frozenset()


def civil_festivals_for_date(date_iso: str | None) -> list[dict[str, Any]]:
    """Nothing is injected any more; dates come from festival_calendar."""
    return []


def lookup_civil_meta(date_iso: str | None, name_en: str | None) -> dict[str, Any] | None:
    """Tier A confirmation for a stored festival row (by date + name)."""
    if not date_iso or not name_en:
        return None
    row = tier_a_dates(name_en).get(date_iso)
    if row:
        return {
            "civil_override": False,
            "tier_a_confirmed": True,
            "source_tier": row["tier"],
            "source_note": row["source"],
        }
    for c in DATE_CORRECTIONS:
        if c["date"] == date_iso and name_en in c["names"]:
            return {
                "civil_override": True,
                "tier_a_confirmed": False,
                "source_tier": "B",
                "source_note": f"{c['source']} — {c['reason']}",
            }
    return None


def civil_why_today(source_note: str) -> dict[str, str]:
    """
    Honest why_today for a corrected festival date.
    Odia field must stay pure Odia script (no Latin source strings).
    """
    note = (source_note or "public civil calendar").strip()
    return {
        "en": (
            f"Festival date per {note}. "
            "The observance rule and the public calendar differ at a tithi edge this year; "
            "the published date follows the public calendar."
        ),
        "or": (
            "ଏହି ପର୍ବ ଜନସାଧାରଣ ପାଞ୍ଜି ତାରିଖ ଅନୁସାରେ ପାଳିତ। ଏହି ବର୍ଷ ତିଥି ସୀମାରେ "
            "ପାଳନ ନିୟମ ଓ ପାଞ୍ଜି ଭିନ୍ନ ହେଉଥିବାରୁ ପାଞ୍ଜି ତାରିଖକୁ ଅନୁସରଣ କରାଯାଇଛି।"
        ),
    }


def authority_notes() -> list[dict[str, str]]:
    return [
        {
            "year": "2022, 2023, 2025",
            "topic": "Puri Rath Yatra cycle",
            "authority_civil": "See tests/fixtures/golden_festivals.json (A1/A2/A3 with sources)",
            "engine_without_override": (
                "Matches every sourced date since the Amanta/Adhika month fix "
                "(the old closing-Purnima heuristic was a month late)"
            ),
            "product_resolution": "No override; Tier A rows asserted in tests",
        },
        *[
            {
                "year": c["date"][:4],
                "topic": ", ".join(c["names"]),
                "authority_civil": f"{c['date']} — {c['source']}",
                "engine_without_override": c["engine_date"],
                "product_resolution": f"DATE_CORRECTIONS: {c['reason']}",
            }
            for c in DATE_CORRECTIONS
        ],
    ]
