"""
Tier A civil-date festival overrides (Jagannath / Puri cycle).

Why this exists
---------------
Tithi rules (Ashadha Shukla 2 → Rath, Jyeshtha Shukla 15 → Snana) are correct
in non-adhika years under our Lahiri + Purnimanta map. In some years (notably
2025) public authorities place the Puri cycle about one lunar month earlier
than pure engine masa names, because commercial Odia panji / temple calendars
apply adhika-masa naming that this engine does not yet fully model.

Product rule (spec / eval.md):
  - On conflict between engine masa labels and Tier A public civil dates for
    **Puri festival days**, prefer Tier A civil dates for *festival attachment*.
  - Do not invent a second ephemeris or silently rename months.
  - Document sources; never “fix” evals to match the bug.

Sources
-------
2025 table: Odisha Tourism — Rath Yatra 2025
  https://odishatourism.gov.in/content/tourism/en/experience/event/ratha-jatra-2025.html
  (retrieved 2026-08-10): Deba Snana 11 Jun · Rath 27 Jun · Bahuda 5 Jul ·
  Suna Besha 6 Jul · Adharapana 7 Jul · Niladri Bije 8 Jul.
Cross-check: Wikipedia Ratha Yatra (Puri) 2025 = 27 June; Snana Yatra 2025 = 11 June.
"""

from __future__ import annotations

from typing import Any

# Festival name_en values whose *tithi rules* are suppressed in years that
# have a full civil override set (so we do not double-fire on wrong months).
_SUPPRESS_IN_OVERRIDE_YEARS: frozenset[str] = frozenset(
    {
        "Snana Purnima",
        "Snana Yatra",
        "Nava Jaubana Darshan",
        "Gundicha Marjana",
        "Rath Yatra",
        "Hera Panchami",
        "Bahuda Yatra",
        "Suna Besha",
        "Adhara Pana",
        "Niladri Bije",
    }
)

# year → date_iso → list of festival dicts (pre-story; match_festivals attaches)
# Each dict: name_en, name_or, tradition, description, source_tier, source_note
CIVIL_OVERRIDE_YEARS: dict[int, dict[str, list[dict[str, str]]]] = {
    2025: {
        "2025-06-11": [
            {
                "name_en": "Snana Purnima",
                "name_or": "ସ୍ନାନ ପୂର୍ଣ୍ଣିମା",
                "tradition": "common",
                "description": (
                    "108-pot ritual bathing of Lord Jagannath; Anavasara begins "
                    "(civil date per Odisha Tourism 2025)"
                ),
                "source_tier": "A1",
                "source_note": "Odisha Tourism Rath Yatra 2025 — Deba Snana Purnima",
            },
            {
                "name_en": "Snana Yatra",
                "name_or": "ସ୍ନାନ ଯାତ୍ରା",
                "tradition": "jagannath",
                "description": (
                    "Public Snana Yatra darshan at Puri before Anavasara "
                    "(civil date per Odisha Tourism 2025)"
                ),
                "source_tier": "A1",
                "source_note": "Odisha Tourism Rath Yatra 2025 — Deba Snana Purnima",
            },
        ],
        "2025-06-26": [
            {
                "name_en": "Nava Jaubana Darshan",
                "name_or": "ନବ ଯୌବନ ଦର୍ଶନ",
                "tradition": "jagannath",
                "description": (
                    "Rejuvenated darshan after Anavasara, day before Rath Yatra "
                    "(derived: day before Tourism Rath 27 Jun 2025)"
                ),
                "source_tier": "A1-derived",
                "source_note": "Day before Odisha Tourism Rath Yatra 2025",
            },
            {
                "name_en": "Gundicha Marjana",
                "name_or": "ଗୁଣ୍ଡିଚା ମାର୍ଜନ",
                "tradition": "jagannath",
                "description": (
                    "Ritual cleaning of Gundicha Temple before the Lord's arrival "
                    "(derived: day before Tourism Rath 27 Jun 2025)"
                ),
                "source_tier": "A1-derived",
                "source_note": "Day before Odisha Tourism Rath Yatra 2025",
            },
        ],
        "2025-06-27": [
            {
                "name_en": "Rath Yatra",
                "name_or": "ରଥ ଯାତ୍ରା",
                "tradition": "common",
                "description": (
                    "Chariot festival of Lord Jagannath, Balabhadra and Subhadra; "
                    "chariots pulled to Gundicha Temple "
                    "(civil date per Odisha Tourism 2025)"
                ),
                "source_tier": "A1",
                "source_note": "Odisha Tourism Rath Yatra 2025 — Rath Yatra 27 June",
            },
        ],
        "2025-06-30": [
            {
                "name_en": "Hera Panchami",
                "name_or": "ହେର ପଞ୍ଚମୀ",
                "tradition": "jagannath",
                "description": (
                    "Lakshmi’s search for Jagannath during Gundicha stay "
                    "(derived: Ashadha Shukla Panchami = Rath + 3 days from Tourism date)"
                ),
                "source_tier": "A1-derived",
                "source_note": "Rath 27 Jun 2025 + 3 days (Shukla 2 → Shukla 5)",
            },
        ],
        "2025-07-05": [
            {
                "name_en": "Bahuda Yatra",
                "name_or": "ବାହୁଡ଼ା ଯାତ୍ରା",
                "tradition": "common",
                "description": (
                    "Return chariot festival from Gundicha "
                    "(civil date per Odisha Tourism 2025)"
                ),
                "source_tier": "A1",
                "source_note": "Odisha Tourism Rath Yatra 2025 — Bahuda Yatra",
            },
        ],
        "2025-07-06": [
            {
                "name_en": "Suna Besha",
                "name_or": "ସୁନା ବେଶ",
                "tradition": "jagannath",
                "description": (
                    "Gold adornment of the deities on the chariots "
                    "(civil date per Odisha Tourism 2025)"
                ),
                "source_tier": "A1",
                "source_note": "Odisha Tourism Rath Yatra 2025 — Suna Besha",
            },
        ],
        "2025-07-07": [
            {
                "name_en": "Adhara Pana",
                "name_or": "ଅଧର ପଣା",
                "tradition": "jagannath",
                "description": (
                    "Special pana offering on the chariots "
                    "(civil date per Odisha Tourism 2025)"
                ),
                "source_tier": "A1",
                "source_note": "Odisha Tourism Rath Yatra 2025 — Adharapana",
            },
        ],
        "2025-07-08": [
            {
                "name_en": "Niladri Bije",
                "name_or": "ନୀଳାଦ୍ରି ବିଜେ",
                "tradition": "jagannath",
                "description": (
                    "Re-entry into the main temple after Rath Yatra "
                    "(civil date per Odisha Tourism 2025)"
                ),
                "source_tier": "A1",
                "source_note": "Odisha Tourism Rath Yatra 2025 — Niladri Bije",
            },
        ],
    },
}


def override_year(year: int | None) -> dict[str, list[dict[str, str]]] | None:
    if year is None:
        return None
    return CIVIL_OVERRIDE_YEARS.get(year)


def suppressed_rule_names(year: int | None) -> frozenset[str]:
    """Tithi-rule names to skip when a civil override year is active."""
    if year is not None and year in CIVIL_OVERRIDE_YEARS:
        return _SUPPRESS_IN_OVERRIDE_YEARS
    return frozenset()


def civil_festivals_for_date(date_iso: str | None) -> list[dict[str, Any]]:
    """Return civil override festival payloads for YYYY-MM-DD (without stories)."""
    if not date_iso or len(date_iso) < 10:
        return []
    try:
        year = int(date_iso[:4])
    except ValueError:
        return []
    year_map = CIVIL_OVERRIDE_YEARS.get(year)
    if not year_map:
        return []
    out: list[dict[str, Any]] = []
    for row in year_map.get(date_iso, []):
        out.append(
            {
                "name_en": row["name_en"],
                "name_or": row["name_or"],
                "tradition": row["tradition"],
                "description": row["description"],
                "civil_override": True,
                "source_tier": row.get("source_tier", "A"),
                "source_note": row.get("source_note", ""),
            }
        )
    return out


def authority_notes() -> list[dict[str, str]]:
    """Human-readable authority notes for eval / docs."""
    return [
        {
            "year": "2025",
            "topic": "Puri Rath Yatra cycle",
            "authority_civil": (
                "Snana 2025-06-11; Rath 2025-06-27; Bahuda 2025-07-05 "
                "(Odisha Tourism A1; Wikipedia A2 agrees on Rath)"
            ),
            "engine_without_override": (
                "Snana lands ~2025-07-10 (engine Jyeshtha Purnima); "
                "Rath ~2025-07-26 (engine Ashadha Shukla 2) — "
                "masa naming lacks full adhika handling"
            ),
            "product_resolution": (
                "Attach festivals via CIVIL_OVERRIDE_YEARS[2025]; "
                "suppress rule-based Snana/Rath cycle names for 2025; "
                "do not rewrite engine masa labels to fake Ashadha on 27 Jun"
            ),
        }
    ]
