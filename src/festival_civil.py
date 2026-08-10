"""
Tier A civil-date festival overrides (Jagannath / Puri cycle).

Why this exists
---------------
Tithi rules (Ashadha Shukla 2 → Rath, Jyeshtha Shukla 15 → Snana) are correct
in non-adhika years under our Lahiri + Purnimanta map. In some years public
authorities place the Puri cycle about one lunar month earlier than pure
engine masa names (adhika / nija-Ashadha naming this engine does not model).

Product rule (spec / eval.md):
  - Prefer Tier A civil dates for *festival attachment*.
  - Do not invent a second ephemeris or silently rename months.
  - Expose civil_override + source on the wire; never “fix” evals to match the bug.

Sources
-------
- A1 Odisha Tourism Rath Yatra pages (year-specific)
- A2 Wikipedia Ratha Yatra (Puri) multi-year table
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


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


def _row(
    name_en: str,
    name_or: str,
    tradition: str,
    description: str,
    *,
    source_tier: str,
    source_note: str,
) -> dict[str, str]:
    return {
        "name_en": name_en,
        "name_or": name_or,
        "tradition": tradition,
        "description": description,
        "source_tier": source_tier,
        "source_note": source_note,
    }


def _build_puri_cycle(
    *,
    snana: date,
    rath: date,
    bahuda: date,
    source_label: str,
    primary_tier: str = "A2",
    late_cycle: bool = True,
) -> dict[str, list[dict[str, str]]]:
    """
    Build a year map of civil festivals from core civil dates.

    late_cycle: when True, attach Suna/Adhara/Niladri as Bahuda+1/+2/+3
    (Tourism 2025 pattern). When False, only core + Hera (+3 from Rath).
    """
    out: dict[str, list[dict[str, str]]] = {}

    def add(d: date, *rows: dict[str, str]) -> None:
        key = d.isoformat()
        out.setdefault(key, []).extend(rows)

    note = source_label
    tier = primary_tier
    tier_d = f"{primary_tier}-derived"

    add(
        snana,
        _row(
            "Snana Purnima",
            "ସ୍ନାନ ପୂର୍ଣ୍ଣିମା",
            "common",
            f"Deba Snana Purnima — civil date per {note}",
            source_tier=tier,
            source_note=f"{note} — Snana Purnima",
        ),
        _row(
            "Snana Yatra",
            "ସ୍ନାନ ଯାତ୍ରା",
            "jagannath",
            f"Puri Snana Yatra — civil date per {note}",
            source_tier=tier,
            source_note=f"{note} — Snana Yatra",
        ),
    )

    pre = rath - timedelta(days=1)
    add(
        pre,
        _row(
            "Nava Jaubana Darshan",
            "ନବ ଯୌବନ ଦର୍ଶନ",
            "jagannath",
            f"Day before Rath (derived from civil Rath; {note})",
            source_tier=tier_d,
            source_note=f"Day before civil Rath ({rath.isoformat()})",
        ),
        _row(
            "Gundicha Marjana",
            "ଗୁଣ୍ଡିଚା ମାର୍ଜନ",
            "jagannath",
            f"Gundicha cleaning day before Rath (derived; {note})",
            source_tier=tier_d,
            source_note=f"Day before civil Rath ({rath.isoformat()})",
        ),
    )

    add(
        rath,
        _row(
            "Rath Yatra",
            "ରଥ ଯାତ୍ରା",
            "jagannath",  # not common — dual-tradition isolation
            f"Puri Rath Yatra — civil date per {note}",
            source_tier=tier,
            source_note=f"{note} — Rath Yatra {rath.isoformat()}",
        ),
    )

    hera = rath + timedelta(days=3)
    add(
        hera,
        _row(
            "Hera Panchami",
            "ହେର ପଞ୍ଚମୀ",
            "jagannath",
            f"Hera Panchami (Rath+3; derived from civil Rath; {note})",
            source_tier=tier_d,
            source_note=f"Civil Rath {rath.isoformat()} + 3 days",
        ),
    )

    add(
        bahuda,
        _row(
            "Bahuda Yatra",
            "ବାହୁଡ଼ା ଯାତ୍ରା",
            "jagannath",  # not common — dual-tradition isolation
            f"Bahuda (return) Yatra — civil date per {note}",
            source_tier=tier,
            source_note=f"{note} — Bahuda Yatra {bahuda.isoformat()}",
        ),
    )

    if late_cycle:
        add(
            bahuda + timedelta(days=1),
            _row(
                "Suna Besha",
                "ସୁନା ବେଶ",
                "jagannath",
                f"Suna Besha (Bahuda+1; derived; {note})",
                source_tier=tier_d,
                source_note=f"Civil Bahuda {bahuda.isoformat()} + 1 day",
            ),
        )
        add(
            bahuda + timedelta(days=2),
            _row(
                "Adhara Pana",
                "ଅଧର ପଣା",
                "jagannath",
                f"Adhara Pana (Bahuda+2; derived; {note})",
                source_tier=tier_d,
                source_note=f"Civil Bahuda {bahuda.isoformat()} + 2 days",
            ),
        )
        add(
            bahuda + timedelta(days=3),
            _row(
                "Niladri Bije",
                "ନୀଳାଦ୍ରି ବିଜେ",
                "jagannath",
                f"Niladri Bije (Bahuda+3; derived; {note})",
                source_tier=tier_d,
                source_note=f"Civil Bahuda {bahuda.isoformat()} + 3 days",
            ),
        )

    return out


# year → date_iso → festival rows
CIVIL_OVERRIDE_YEARS: dict[int, dict[str, list[dict[str, str]]]] = {
    # A2 Wikipedia Ratha Yatra (Puri): Rath 1 Jul / Bahuda 9 Jul 2022
    # Snana = Purnima ~16d before Rath under engine sample (2022-06-14)
    2022: _build_puri_cycle(
        snana=date(2022, 6, 14),
        rath=date(2022, 7, 1),
        bahuda=date(2022, 7, 9),
        source_label="Wikipedia Ratha Yatra (Puri) 2022 table (A2)",
        primary_tier="A2",
        late_cycle=True,
    ),
    # A2: Rath 20 Jun / Bahuda 28 Jun 2023; Snana engine Purnima 2023-06-04
    2023: _build_puri_cycle(
        snana=date(2023, 6, 4),
        rath=date(2023, 6, 20),
        bahuda=date(2023, 6, 28),
        source_label="Wikipedia Ratha Yatra (Puri) 2023 table (A2)",
        primary_tier="A2",
        late_cycle=True,
    ),
    # A1 Odisha Tourism 2025 full table (authoritative for that year)
    2025: _build_puri_cycle(
        snana=date(2025, 6, 11),
        rath=date(2025, 6, 27),
        bahuda=date(2025, 7, 5),
        source_label="Odisha Tourism Rath Yatra 2025 (A1)",
        primary_tier="A1",
        late_cycle=True,
    ),
}


def override_year(year: int | None) -> dict[str, list[dict[str, str]]] | None:
    if year is None:
        return None
    return CIVIL_OVERRIDE_YEARS.get(year)


def suppressed_rule_names(year: int | None) -> frozenset[str]:
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


def lookup_civil_meta(date_iso: str | None, name_en: str | None) -> dict[str, Any] | None:
    """Look up civil override metadata for a stored festival row (by date + name)."""
    if not date_iso or not name_en:
        return None
    for row in civil_festivals_for_date(date_iso):
        if row["name_en"] == name_en:
            return {
                "civil_override": True,
                "source_tier": row.get("source_tier", "A"),
                "source_note": row.get("source_note", ""),
            }
    return None


def civil_why_today(source_note: str) -> dict[str, str]:
    """
    Honest why_today for civil-override festivals.
    Must not claim engine masa name (e.g. Ashadha) when labels may differ.
    Odia field must stay pure Odia script (no Latin source strings).
    """
    note = (source_note or "public civil calendar (Tier A)").strip()
    return {
        "en": (
            f"Civil festival date per {note}. "
            "The engine lunar month label may differ until full adhika-masa naming "
            "is implemented; festival attachment follows public authority dates."
        ),
        "or": (
            "ଏହି ପର୍ବ ସରକାରୀ କିମ୍ବା ପାଞ୍ଜିର ନାଗରିକ ତାରିଖ ଅନୁସାରେ ପାଳିତ। "
            "ଅଧିକ ମାସ ନାମକରଣ ସମ୍ପୂର୍ଣ୍ଣ ହେବା ପର୍ଯ୍ୟନ୍ତ ଇଞ୍ଜିନର ଚାନ୍ଦ୍ର ମାସ ନାମ "
            "ଭିନ୍ନ ହୋଇପାରେ; ପର୍ବ ସଂଯୋଜନା ଜନସାଧାରଣ ଅଧିକାରୀ ତାରିଖକୁ ଅନୁସରଣ କରେ।"
        ),
    }


def authority_notes() -> list[dict[str, str]]:
    return [
        {
            "year": "2022",
            "topic": "Puri Rath Yatra cycle",
            "authority_civil": "Rath 2022-07-01; Bahuda 2022-07-09 (Wikipedia A2); Snana 2022-06-14 (Purnima before Rath)",
            "engine_without_override": "Rath ~2022-07-30 (engine Ashadha Shukla 2)",
            "product_resolution": "CIVIL_OVERRIDE_YEARS[2022]",
        },
        {
            "year": "2023",
            "topic": "Puri Rath Yatra cycle",
            "authority_civil": "Rath 2023-06-20; Bahuda 2023-06-28 (Wikipedia A2); Snana 2023-06-04",
            "engine_without_override": "Rath ~2023-07-19 (engine Ashadha Shukla 2)",
            "product_resolution": "CIVIL_OVERRIDE_YEARS[2023]",
        },
        {
            "year": "2025",
            "topic": "Puri Rath Yatra cycle",
            "authority_civil": (
                "Snana 2025-06-11; Rath 2025-06-27; Bahuda 2025-07-05 "
                "(Odisha Tourism A1; Wikipedia A2 agrees on Rath)"
            ),
            "engine_without_override": (
                "Snana ~2025-07-10; Rath ~2025-07-26 under engine masa labels"
            ),
            "product_resolution": "CIVIL_OVERRIDE_YEARS[2025]; do not fake Ashadha on engine labels",
        },
    ]
