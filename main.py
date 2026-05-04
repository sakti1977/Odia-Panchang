"""
Odia Panchang API — FastAPI application.
"""

import os
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone, timedelta
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
from src.locations import get_city_info, list_all_cities
from src.engine import compute_panchang
from src.pdf_generator import generate_monthly_text, generate_calendar_view
from src.festivals import match_festivals, get_sankranti_festivals
from src.temple_data import (
    JAGANNATH_NITIS, JAGANNATH_BESHAS,
    BIRAJA_NITIS, BIRAJA_SPECIAL,
    LINGARAJ_NITIS, LINGARAJ_SPECIAL,
    SANKRANTI_INFO,
    ODIA_PERSONALITIES, ODIA_HISTORY,
)

engine = get_engine(DATABASE_URL)
init_db(engine)
SessionLocal = get_session_factory(engine)

# Templates and static files
templates = Jinja2Templates(directory="templates")

IST = timezone(timedelta(hours=5, minutes=30))

# Startup: report AI layer availability
_groq_ready    = bool(os.getenv("GROQ_API_KEY"))
_claude_ready  = bool(os.getenv("ANTHROPIC_API_KEY"))
_twitter_ready = all(os.getenv(k) for k in ("TWITTER_API_KEY","TWITTER_API_SECRET","TWITTER_ACCESS_TOKEN","TWITTER_ACCESS_SECRET"))
print(f"[Panchang] Layer 1 (Groq/Llama):   {'✅ active — llama-3.3-70b-versatile' if _groq_ready else '⚠️  GROQ_API_KEY not set — using rule-based fallback'}")
print(f"[Panchang] Layer 2 (Claude Haiku):  {'✅ active — claude-haiku-4-5' if _claude_ready else '⚠️  ANTHROPIC_API_KEY not set — using rule-based fallback'}")
print(f"[Panchang] Twitter/X posting:       {'✅ active' if _twitter_ready else '⚠️  TWITTER_* keys not set — tweets will be logged to logs/daily_tweets.log'}")

# Additional Twitter diagnostic
if _twitter_ready:
    try:
        import tweepy
        print(f"[Panchang] Tweepy library:          ✅ v{tweepy.__version__} installed")
    except ImportError:
        print("[Panchang] Tweepy library:          ❌ NOT INSTALLED — Twitter posting will fail!")
        _twitter_ready = False


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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


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

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


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


# ── City-based & Location Endpoints ────────────────────────────────────────

@app.get("/api/cities")
def get_cities():
    """
    Return list of all supported Odisha cities with their coordinates.
    """
    return list_all_cities()


@app.get("/api/panchang/today/{city}")
def get_panchang_for_city_today(city: str):
    """
    Get today's Panchang for a specific city in Odisha.
    City can be: puri, bhubaneswar, cuttack, jajpur, berhampur, sambalpur, etc.
    """
    city_info = get_city_info(city)
    if not city_info:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found. Use /api/cities to see available cities."
        )

    # Get today's date in IST
    today = datetime.now(tz=IST).date()

    # Compute panchang with city-specific coordinates
    import os
    # Temporarily set environment variables for this computation
    old_lat = os.getenv("LOCATION_LAT")
    old_lon = os.getenv("LOCATION_LON")
    old_name = os.getenv("LOCATION_NAME")

    os.environ["LOCATION_LAT"] = str(city_info["lat"])
    os.environ["LOCATION_LON"] = str(city_info["lon"])
    os.environ["LOCATION_NAME"] = city_info["name"]

    try:
        # Compute panchang for this city
        p = compute_panchang(today)

        # Get festivals for this date from database
        db = SessionLocal()
        try:
            day = db.get(PanchangDay, today.isoformat())
            if day:
                festivals = [_festival_to_dict(f) for f in day.festivals]
            else:
                # If not in DB, match festivals from computed panchang
                festivals_data = match_festivals(p)
                festivals = [
                    {
                        "name": {"en": f["name_en"], "or": f["name_or"]},
                        "tradition": f["tradition"],
                        "description": f["description"]
                    }
                    for f in festivals_data
                ]
        finally:
            db.close()

        # Build response
        result = {
            "city": city_info["name"],
            "city_or": city_info["name_or"],
            "date": p["date"],
            "vara": {"en": p["vara_en"], "or": p["vara_or"]},
            "soura_masa": {"en": p["soura_masa_en"], "or": p["soura_masa_or"]},
            "chandra_masa": {"en": p["chandra_masa_en"], "or": p["chandra_masa_or"]},
            "paksha": {"en": p["paksha_en"], "or": p["paksha_or"]},
            "tithi": {
                "num": p["tithi_num"],
                "en": p["tithi_en"],
                "or": p["tithi_or"],
            },
            "nakshatra": {"en": p["nakshatra_en"], "or": p["nakshatra_or"]},
            "yoga": {"en": p["yoga_en"], "or": p["yoga_or"]},
            "karana": {"en": p["karana_en"], "or": p["karana_or"]},
            "sunrise": p["sunrise"],
            "sunset": p["sunset"],
            "festivals": festivals,
        }

        return result

    finally:
        # Restore original environment variables
        if old_lat:
            os.environ["LOCATION_LAT"] = old_lat
        if old_lon:
            os.environ["LOCATION_LON"] = old_lon
        if old_name:
            os.environ["LOCATION_NAME"] = old_name


@app.get("/api/panchang/monthly/{year}/{month}/download")
def download_monthly_panchang(
    year: int,
    month: int,
    city: str = Query(default="puri", description="City name"),
    format: str = Query(default="text", description="Format: text or calendar")
):
    """
    Download monthly Panchang as text file for printing or offline use.
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12.")

    # Get month data from database
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

        # Convert to dictionaries
        panchang_data = [
            _day_to_dict(d, [_festival_to_dict(f) for f in d.festivals])
            for d in days
        ]

    finally:
        db.close()

    # Generate text based on format
    if format == "calendar":
        content = generate_calendar_view(year, month, panchang_data)
    else:
        content = generate_monthly_text(year, month, panchang_data)

    # Return as downloadable text file
    from fastapi.responses import Response

    filename = f"Odia_Panchang_{year}_{month:02d}_{city}.txt"
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


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


# ── Temple & Heritage endpoints ─────────────────────────────────────────────

@app.get("/api/temple-nitis")
def get_temple_nitis():
    """
    Return daily niti (ritual) schedules for Jagannath (Puri), Biraja (Jajpur),
    and Lingaraj (Bhubaneswar) temples.
    """
    return {
        "jagannath": {
            "temple": "Jagannath Temple",
            "temple_or": "ଜଗନ୍ନାଥ ମନ୍ଦିର",
            "location": "Puri, Odisha",
            "location_or": "ପୁରୀ, ଓଡ଼ିଶା",
            "description": "One of the four sacred Dhamas of Hinduism. Built by King Anantavarman "
                           "Chodaganga Deva (~1135 CE). The 65-metre tall Vimana tower is visible "
                           "from the sea. Serves 100,000 pilgrims daily from its Ananda Bazar kitchen.",
            "nitis": JAGANNATH_NITIS,
        },
        "biraja": {
            "temple": "Biraja Temple",
            "temple_or": "ବିରଜା ମନ୍ଦିର",
            "location": "Jajpur, Odisha",
            "location_or": "ଯାଜପୁର, ଓଡ଼ିଶା",
            "description": "One of the 51 Shakti Peethas of India. Maa Biraja is worshipped as a "
                           "64-Yogini Devi. The Dashaswamedha Ghat on the Baitarani river is considered "
                           "as sacred as the Ganges at Varanasi.",
            "nitis": BIRAJA_NITIS,
        },
        "lingaraj": {
            "temple": "Lingaraj Temple",
            "temple_or": "ଲିଙ୍ଗରାଜ ମନ୍ଦିର",
            "location": "Bhubaneswar, Odisha",
            "location_or": "ଭୁବନେଶ୍ୱର, ଓଡ଼ିଶା",
            "description": "The largest temple of Bhubaneswar and the oldest continuously worshipped "
                           "Shiva temple in Odisha (~11th century CE). The deity Harihara is a "
                           "unique fusion of Shiva and Vishnu. The 55-metre tower dominates the city's skyline.",
            "nitis": LINGARAJ_NITIS,
        },
    }


@app.get("/api/temple-specials")
def get_temple_specials():
    """
    Return special annual festivals and occasions for all three major temples.
    """
    return {
        "jagannath_beshas": JAGANNATH_BESHAS,
        "biraja_specials":  BIRAJA_SPECIAL,
        "lingaraj_specials": LINGARAJ_SPECIAL,
    }


@app.get("/api/beshas")
def get_jagannath_beshas():
    """
    Return the complete annual Besha (divine attire) calendar for Lord Jagannath.
    Each Besha is a special ceremonial dress worn by the deities on particular occasions.
    """
    return {
        "total": len(JAGANNATH_BESHAS),
        "description": "Lord Jagannath wears different ceremonial attires (Besha) on special occasions "
                       "throughout the year. Each Besha has its own significance and timing.",
        "beshas": JAGANNATH_BESHAS,
    }


@app.get("/api/sankrantis")
def get_sankranti_info():
    """
    Return information about all 12 Sankrantis (solar month transitions) with their
    significance for Odisha, customs, and approximate dates.
    """
    return {
        "total": len(SANKRANTI_INFO),
        "description": "Sankranti marks the Sun's transition into a new zodiac sign (Rashi). "
                       "All 12 Sankrantis are observed in Odisha, with Pana Sankranti (Mesha) and "
                       "Makar Sankranti being the most important.",
        "most_important": ["Pana Sankranti (Mesha — April)", "Makar Sankranti (January)"],
        "sankrantis": SANKRANTI_INFO,
    }


@app.get("/api/heritage")
def get_heritage(
    category: Optional[str] = Query(
        default=None,
        description="Filter personalities by category: Ruler, Poet / Saint, Freedom Fighter, Writer, Statesman / Lawyer, Statesman / Pilot"
    )
):
    """
    Return Odia heritage data: important historical personalities and key events in Odia history.
    """
    personalities = ODIA_PERSONALITIES
    if category:
        personalities = [p for p in personalities if p.get("category", "").lower() == category.lower()]

    return {
        "personalities": personalities,
        "history": ODIA_HISTORY,
    }

