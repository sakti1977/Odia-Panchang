"""
Load one panji day from the local SQLite DB — no FastAPI, no Render.

Used by GitHub Actions daily posting (scripts/post_daily.py).
"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone

from src.models import Festival, PanchangDay, get_engine, get_session_factory

IST = timezone(timedelta(hours=5, minutes=30))
DEFAULT_DB = "sqlite:///./data/panchang.db"


class DayNotFound(LookupError):
    """No panchang_days row for this civil date."""


def today_ist() -> date:
    return datetime.now(IST).date()


def load_panchang_day(day: str | date | None = None) -> dict:
    """Return an API-shaped panchang dict from SQLite (Bhubaneswar seed row)."""
    if day is None:
        day = today_ist()
    if isinstance(day, date):
        date_str = day.isoformat()
    else:
        date_str = str(day)

    url = os.getenv("DATABASE_URL") or DEFAULT_DB
    engine = get_engine(url)
    Session = get_session_factory(engine)
    db = Session()
    try:
        row = db.get(PanchangDay, date_str)
        if not row:
            raise DayNotFound(
                f"Panchang data for {date_str} not found. Run seed.py to populate the database."
            )
        festivals = [_festival_row(f) for f in row.festivals]
        return {
            "meta": {
                "city": "bhubaneswar",
                "tradition": "common",
                "engine": "lahiri",
                "masa_system": "purnimanta",
            },
            "date": row.date,
            "vara": {"en": row.vara_en, "or": row.vara_or},
            "soura_masa": {"en": row.soura_masa_en, "or": row.soura_masa_or},
            "chandra_masa": {"en": row.chandra_masa_en, "or": row.chandra_masa_or},
            "paksha": {"en": row.paksha_en, "or": row.paksha_or},
            "tithi": {
                "num": row.tithi_num,
                "en": row.tithi_en,
                "or": row.tithi_or,
                "end_ts": row.tithi_end_ts,
            },
            "nakshatra": {
                "en": row.nakshatra_en,
                "or": row.nakshatra_or,
                "end_ts": row.nakshatra_end_ts,
            },
            "yoga": {"en": row.yoga_en, "or": row.yoga_or},
            "karana": {"en": row.karana_en, "or": row.karana_or},
            "sunrise": row.sunrise,
            "sunset": row.sunset,
            "festivals": festivals,
        }
    finally:
        db.close()


def _festival_row(f: Festival) -> dict:
    from src.festival_stories import attach_story

    payload = {
        "name": {"en": f.name_en, "or": f.name_or},
        "tradition": f.tradition,
        "description": f.description,
        "name_en": f.name_en,
        "name_or": f.name_or,
    }
    attach_story(payload)
    return payload


def rule_enrichment(panchang: dict) -> dict:
    """Layer 1 math only (no Groq/Claude). Safe for GitHub Actions."""
    from src.ai_layer1 import compute_muhurtas, detect_special_yogas, validate_with_ai

    d = date.fromisoformat(panchang["date"])
    muhurtas = compute_muhurtas(
        panchang["date"],
        panchang.get("sunrise") or "",
        panchang.get("sunset") or "",
        d.weekday(),
    )
    yogas = detect_special_yogas(
        d.weekday(),
        panchang["nakshatra"]["en"],
        panchang["yoga"]["en"],
    )
    # GROQ_API_KEY unset → validate_with_ai stays rule-based
    layer1 = validate_with_ai(panchang, muhurtas, yogas)
    return {"astronomical": layer1, "cultural": {}}
