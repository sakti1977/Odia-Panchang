"""
Odia Panchang API — FastAPI application.
"""

import os
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone, timedelta
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from sqlalchemy.orm import Session as OrmSession

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/panchang.db")

from src.models import PanchangDay, Festival, get_engine, get_session_factory, init_db
from src.ai_layer1 import compute_muhurtas, detect_special_yogas, validate_with_ai
from src.ai_layer2 import enrich_with_claude
from src.scheduler import create_scheduler, run_daily_tweet
from src.tweet_generator import generate_tweet_bundle

engine = get_engine(DATABASE_URL)
init_db(engine)
SessionLocal = get_session_factory(engine)

IST = timezone(timedelta(hours=5, minutes=30))

# Startup: report AI layer availability
_groq_ready    = bool(os.getenv("GROQ_API_KEY"))
_claude_ready  = bool(os.getenv("ANTHROPIC_API_KEY"))
_twitter_ready = all(os.getenv(k) for k in ("TWITTER_API_KEY","TWITTER_API_SECRET","TWITTER_ACCESS_TOKEN","TWITTER_ACCESS_SECRET"))
print(f"[Panchang] Layer 1 (Groq/Llama):   {'✅ active — llama-3.3-70b-versatile' if _groq_ready else '⚠️  GROQ_API_KEY not set — using rule-based fallback'}")
print(f"[Panchang] Layer 2 (Claude Haiku):  {'✅ active — claude-haiku-4-5' if _claude_ready else '⚠️  ANTHROPIC_API_KEY not set — using rule-based fallback'}")
print(f"[Panchang] Twitter/X posting:       {'✅ active' if _twitter_ready else '⚠️  TWITTER_* keys not set — tweets will be logged to logs/daily_tweets.log'}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    print("[Panchang] Scheduler started — daily tweet at 05:00 IST | self-ping every 10 min")
    yield
    scheduler.shutdown()
    print("[Panchang] Scheduler stopped")

app = FastAPI(
    title="Odia Panjika API (ଓଡ଼ିଆ ପଞ୍ଜିକା)",
    description=(
        "Free public bilingual (Odia + English) Panjika API covering tithi, nakshatra, yoga, "
        "karana, soura masa, and festivals for Jagannath (Puri) and Biraja (Jajpur) traditions. "
        "AI-powered enrichment: muhurtas, cultural significance, fasting guidance. "
        "Daily tweet at 5 AM IST. No API key required for basic endpoints."
    ),
    version="2.0.0",
    lifespan=lifespan,
    contact={"name": "Odia Panjika", "url": "https://github.com/sakti1977/Odia-Panchang"},
    license_info={"name": "MIT"},
)

# Rate limiting — 60 req/min for basic, 10/min for AI-enriched endpoints
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"],
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


@app.get("/api/status")
def ai_status():
    """Show which AI enrichment layers are configured and active."""
    return {
        "layer1_groq": {
            "active": _groq_ready,
            "model": "llama-3.3-70b-versatile",
            "description": "Astronomical validation: muhurtas, special yogas",
            "cost": "free",
            "setup": "Set GROQ_API_KEY in .env — https://console.groq.com/keys",
        },
        "layer2_claude": {
            "active": _claude_ready,
            "model": "claude-haiku-4-5",
            "description": "Odia cultural enrichment: Jagannath/Biraja significance, fasting, proverbs",
            "cost": "~$0.001/request",
            "setup": "Set ANTHROPIC_API_KEY in .env — https://console.anthropic.com/",
        },
        "enrichment_endpoints": [
            "/today?enriched=true",
            "/panchang/{date}?enriched=true",
            "/panchang/{date}/insights",
        ],
    }


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
@limiter.limit("10/minute")
def get_panchang_insights(date_str: str, request: Request):
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


# ── Tweet endpoints ─────────────────────────────────────────────────────────

@app.get("/tweet/today")
@limiter.limit("10/minute")
def preview_tweet(request: Request):
    """
    Preview today's scheduled tweet (without posting).
    Returns main tweet + thread reply ready for Twitter/X.
    """
    today = datetime.now(tz=IST).date()
    db = SessionLocal()
    try:
        day = _get_day(db, today.isoformat())
        festivals = [_festival_to_dict(f) for f in day.festivals]
        panchang = _day_to_dict(day, festivals)
    finally:
        db.close()

    enrichment = _build_enrichment(panchang)
    bundle = generate_tweet_bundle(panchang, enrichment)
    twitter_active = _twitter_ready

    return {
        **bundle,
        "twitter_configured": twitter_active,
        "note": "POST /tweet/post to publish now, or it auto-posts at 05:00 IST" if twitter_active
                else "Add TWITTER_* keys to .env to enable auto-posting. Tweets saved to logs/daily_tweets.log",
    }


@app.get("/tweet/{date_str}")
def preview_tweet_for_date(date_str: str):
    """Preview tweet for a specific date (YYYY-MM-DD). Does not post."""
    try:
        date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    db = SessionLocal()
    try:
        day = _get_day(db, date_str)
        festivals = [_festival_to_dict(f) for f in day.festivals]
        panchang = _day_to_dict(day, festivals)
    finally:
        db.close()

    enrichment = _build_enrichment(panchang)
    bundle = generate_tweet_bundle(panchang, enrichment)
    return bundle


@app.post("/tweet/post")
async def post_tweet_now(background_tasks: BackgroundTasks):
    """
    Manually trigger today's tweet right now (same as the 5 AM job).
    Runs in the background — returns immediately.
    """
    background_tasks.add_task(run_daily_tweet)
    return {
        "status": "triggered",
        "message": "Tweet job running in background. Check logs/daily_tweets.log or Twitter.",
    }
