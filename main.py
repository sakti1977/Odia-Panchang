"""
Odia Panchang API — FastAPI application.
"""

import os
from datetime import date, datetime
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from sqlalchemy.orm import Session as OrmSession

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/panchang.db")

from src.models import PanchangDay, Festival, get_engine, get_session_factory, init_db

engine = get_engine(DATABASE_URL)
init_db(engine)
SessionLocal = get_session_factory(engine)

app = FastAPI(
    title="Odia Panchang API",
    description=(
        "Bilingual (Odia + English) Panchang API covering tithi, nakshatra, yoga, "
        "karana, soura masa, and festivals for Jagannath (Puri) and Biraja (Jajpur) traditions."
    ),
    version="1.0.0",
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


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/api")
def health_check():
    return {"status": "ok", "service": "Odia Panchang API"}


@app.get("/today")
def get_today():
    """Return full Panchang for today (IST)."""
    today = datetime.now().date()
    db = SessionLocal()
    try:
        day = _get_day(db, today.isoformat())
        festivals = [_festival_to_dict(f) for f in day.festivals]
        return _day_to_dict(day, festivals)
    finally:
        db.close()


@app.get("/panchang/{date_str}")
def get_panchang_by_date(date_str: str):
    """
    Return full Panchang for a specific date.
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
        return _day_to_dict(day, festivals)
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
