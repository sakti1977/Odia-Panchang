"""
Odia Panchang API — FastAPI application.
"""

import os
from datetime import date, datetime, timezone, timedelta
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from sqlalchemy.orm import Session as OrmSession

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/panchang.db")

from src.models import PanchangDay, Festival, get_engine, get_session_factory, init_db
from src.ai_layer1 import compute_muhurtas, detect_special_yogas, validate_with_ai
from src.ai_layer2 import enrich_with_claude

engine = get_engine(DATABASE_URL)
init_db(engine)
SessionLocal = get_session_factory(engine)

app = FastAPI(
    title="Odia Panchang API",
    description=(
        "Bilingual (Odia + English) Panchang API covering tithi, nakshatra, yoga, "
        "karana, soura masa, and festivals for Jagannath (Puri) and Biraja (Jajpur) traditions. "
        "Supports AI-powered two-layer enrichment: astronomical validation (Groq/Llama) + "
        "Odia cultural insights (Claude)."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


def _day_to_dict(day: PanchangDay, festivals: list) -> dict:
    return {
        "date":            day.date,
        "vara":            {"en": day.vara_en,         "or": day.vara_or},
        "soura_masa":      {"en": day.soura_masa_en,   "or": day.soura_masa_or},
        "chandra_masa":    {"en": day.chandra_masa_en, "or": day.chandra_masa_or},
        "paksha":          {"en": day.paksha_en,       "or": day.paksha_or},
        "tithi": {
            "num": day.tithi_num,
            "en":  day.tithi_en,
            "or":  day.tithi_or,
        },
        "nakshatra":       {"en": day.nakshatra_en,    "or": day.nakshatra_or},
        "yoga":            {"en": day.yoga_en,         "or": day.yoga_or},
        "karana":          {"en": day.karana_en,       "or": day.karana_or},
        "sunrise":         day.sunrise,
        "sunset":          day.sunset,
        "festivals":       festivals,
    }


def _festival_to_dict(f: Festival) -> dict:
    return {
        "name":        {"en": f.name_en, "or": f.name_or},
        "tradition":   f.tradition,
        "description": f.description,
    }


def _get_day(db: OrmSession, date_str: str) -> PanchangDay:
    day = db.get(PanchangDay, date_str)
    if not day:
        raise HTTPException(
            status_code=404,
            detail=f"Panchang data for {date_str} not found. Run seed.py to populate the database."
        )
    return day


def _build_enrichment(base: dict) -> dict:
    """Run both AI enrichment layers and attach results to the panchang dict."""
    # Determine weekday (Mon=0, Sun=6)
    d = date.fromisoformat(base["date"])
    weekday = d.weekday()  # Mon=0, Sun=6

    # Layer 1: muhurtas + special yogas + Groq validation
    muhurtas = compute_muhurtas(
        base["date"],
        base.get("sunrise", ""),
        base.get("sunset", ""),
        weekday,
    )
    yogas = detect_special_yogas(weekday, base["nakshatra"]["en"], base["yoga"]["en"])
    layer1 = validate_with_ai(base, muhurtas, yogas)

    # Layer 2: Claude cultural enrichment
    layer2 = enrich_with_claude(base, layer1)

    return {"astronomical": layer1, "cultural": layer2}


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/api")
def health_check():
    return {"status": "ok", "service": "Odia Panchang API"}


@app.get("/today")
def get_today(enriched: bool = Query(default=False, description="Include AI enrichment layers")):
    """Return full Panchang for today (IST)."""
    today = datetime.now(tz=timezone(timedelta(hours=5, minutes=30))).date()
    db = SessionLocal()
    try:
        day = _get_day(db, today.isoformat())
        festivals = [_festival_to_dict(f) for f in day.festivals]
        result = _day_to_dict(day, festivals)
        if enriched:
            result["enrichment"] = _build_enrichment(result)
        return result
    finally:
        db.close()


@app.get("/panchang/{date_str}/insights")
def get_panchang_insights(date_str: str):
    """
    Return full AI-enriched Panchang insights for a specific date.
    Always runs both enrichment layers (Groq validation + Claude cultural context).
    Date format: YYYY-MM-DD
    """
    try:
        date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    db = SessionLocal()
    try:
        day = _get_day(db, date_str)
        festivals = [_festival_to_dict(f) for f in day.festivals]
        result = _day_to_dict(day, festivals)
        result["enrichment"] = _build_enrichment(result)
        return result
    finally:
        db.close()


@app.get("/panchang/{date_str}")
def get_panchang_by_date(
    date_str: str,
    enriched: bool = Query(default=False, description="Include AI enrichment layers"),
):
    """
    Return full Panchang for a specific date.
    Date format: YYYY-MM-DD
    Add ?enriched=true for AI-powered astronomical validation + Odia cultural insights.
    """
    try:
        date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    db = SessionLocal()
    try:
        day = _get_day(db, date_str)
        festivals = [_festival_to_dict(f) for f in day.festivals]
        result = _day_to_dict(day, festivals)
        if enriched:
            result["enrichment"] = _build_enrichment(result)
        return result
    finally:
        db.close()


@app.get("/panchang/{year}/{month}")
def get_panchang_by_month(year: int, month: int):
    """
    Return Panchang for all days in a given month.
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12.")

    # Build date prefix for filtering
    prefix = f"{year:04d}-{month:02d}-"

    db = SessionLocal()
    try:
        days = (
            db.query(PanchangDay)
            .filter(PanchangDay.date.like(f"{prefix}%"))
            .order_by(PanchangDay.date)
            .all()
        )
        if not days:
            raise HTTPException(
                status_code=404,
                detail=f"No data for {year}-{month:02d}. Run seed.py to populate."
            )
        return [
            _day_to_dict(d, [_festival_to_dict(f) for f in d.festivals])
            for d in days
        ]
    finally:
        db.close()


@app.get("/festivals/{year}")
def get_festivals_by_year(
    year: int,
    tradition: Optional[Literal["jagannath", "biraja", "common", "all"]] = Query(
        default="all",
        description="Filter by temple tradition: jagannath, biraja, common, or all"
    ),
):
    """
    Return all festivals for a given year, optionally filtered by tradition.
    """
    db = SessionLocal()
    try:
        query = (
            db.query(Festival)
            .join(PanchangDay)
            .filter(PanchangDay.date.like(f"{year:04d}-%"))
            .order_by(PanchangDay.date)
        )
        if tradition and tradition != "all":
            query = query.filter(Festival.tradition == tradition)

        festivals = query.all()
        if not festivals:
            raise HTTPException(
                status_code=404,
                detail=f"No festival data for {year}. Run seed.py to populate."
            )

        return [
            {
                "date":        f.date,
                "name":        {"en": f.name_en, "or": f.name_or},
                "tradition":   f.tradition,
                "description": f.description,
            }
            for f in festivals
        ]
    finally:
        db.close()
