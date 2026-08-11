"""
Odia Panchang API — FastAPI application.
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone, timedelta
from typing import Optional, Literal

import secrets as _secrets

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
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
from src.scheduler import create_scheduler, run_daily_tweet, run_daily_social, run_daily_all_channels
from src.tweet_generator import generate_tweet_bundle
from src.locations import get_city_info, list_all_cities, detect_city_from_ip, resolve_city
from src.engine import compute_panchang, ENGINE_VERSION
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
_meta_page_ready = bool(
    (os.getenv("META_PAGE_ID") or "").strip()
    and (os.getenv("META_PAGE_ACCESS_TOKEN") or "").strip()
)
_meta_ig_ready = _meta_page_ready and bool((os.getenv("META_IG_USER_ID") or "").strip())
print(f"[Panchang] Layer 1 (Groq/Llama):   {'✅ active — llama-3.3-70b-versatile' if _groq_ready else '⚠️  GROQ_API_KEY not set — using rule-based fallback'}")
print(f"[Panchang] Layer 2 (Claude Haiku):  {'✅ active — claude-haiku-4-5' if _claude_ready else '⚠️  ANTHROPIC_API_KEY not set — using rule-based fallback'}")
print(f"[Panchang] Twitter/X posting:       {'✅ active' if _twitter_ready else '⚠️  TWITTER_* keys not set — tweets will be logged to logs/daily_tweets.log'}")
print(f"[Panchang] Facebook Page posting:   {'✅ active' if _meta_page_ready else '⚠️  META_PAGE_ID / META_PAGE_ACCESS_TOKEN not set'}")
print(f"[Panchang] Instagram posting:       {'✅ active' if _meta_ig_ready else '⚠️  META_IG_USER_ID not set (needs Page token + IG Business)'}")

# Additional Twitter diagnostic
if _twitter_ready:
    try:
        import tweepy
        print(f"[Panchang] Tweepy library:          ✅ v{tweepy.__version__} installed")
    except ImportError:
        print("[Panchang] Tweepy library:          ❌ NOT INSTALLED — Twitter posting will fail!")
        _twitter_ready = False


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# Free-tier path: prefer GitHub Actions (or external cron) over in-process APScheduler.
# Set ENABLE_INPROCESS_SCHEDULER=true only if you run always-on and want 05:00 IST inside the app.
_ENABLE_INPROCESS_SCHEDULER = _env_flag("ENABLE_INPROCESS_SCHEDULER", default=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = None
    if _ENABLE_INPROCESS_SCHEDULER:
        scheduler = create_scheduler()
        scheduler.start()
        print("[Panchang] In-process scheduler ON — daily tweet at 05:00 IST")
    else:
        print(
            "[Panchang] In-process scheduler OFF (free-tier default). "
            "Use GitHub Actions workflow 'Daily Odia Panjika Tweet' or external cron → POST /tweet/post. "
            "Set ENABLE_INPROCESS_SCHEDULER=true to re-enable APScheduler."
        )
    yield
    if scheduler is not None:
        scheduler.shutdown()
        print("[Panchang] Scheduler stopped")

app = FastAPI(
    title="Odia Panjika API (ଓଡ଼ିଆ ପଞ୍ଜିକା)",
    description=(
        "Free public bilingual (Odia + English) Panjika API covering tithi, nakshatra, yoga, "
        "karana, soura masa, and festivals for Jagannath (Puri) and Biraja (Jajpur) traditions. "
        "AI-powered enrichment: muhurtas, cultural significance, fasting guidance. "
        "Daily tweet: GitHub Actions → POST /tweet/post (recommended on free tier). "
        "No API key required for basic endpoints."
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


def _filter_festivals(festivals: list, tradition: str | None) -> list:
    """
    Day API filter (spec):
      all      → everything
      common   → common only
      jagannath→ common + jagannath
      biraja   → common + biraja
      lingaraj → common + lingaraj
    """
    t = (tradition or "all").lower()
    if t == "all":
        return festivals
    if t == "common":
        return [f for f in festivals if f.get("tradition") == "common"]
    if t in ("jagannath", "biraja", "lingaraj"):
        return [f for f in festivals if f.get("tradition") in ("common", t)]
    return festivals


def _build_meta(place: dict, tradition: str, *, anchor: str | None = None) -> dict:
    anchor = anchor or "local_sunrise"
    return {
        "engine": "lahiri_swiss_ephemeris",
        "engine_version": ENGINE_VERSION,
        "masa_system": "purnimanta_odia_default",
        # Path A: day elements at local sunrise for the resolved place
        "day_elements_anchor": anchor,
        "day_elements_scope": "local_sunrise",
        "place_affects": [
            "sunrise",
            "sunset",
            "tithi",
            "nakshatra",
            "yoga",
            "karana",
            "chandra_masa",
            "soura_masa",
            "paksha",
            "meta.city",
            "meta.lat",
            "meta.lon",
        ],
        "biraja_civil_status": "rule_only",  # no print-panji civil goldens yet (E-DUAL-004)
        "tradition": tradition or "all",
        "city": place.get("key") or place.get("name", "").lower(),
        "lat": place.get("lat"),
        "lon": place.get("lon"),
        "tz": "Asia/Kolkata" if float(place.get("tz", 5.5)) == 5.5 else place.get("tz"),
        "disclaimer": (
            "Lahiri/Swiss Ephemeris day elements (tithi, masa, nakshatra, yoga, karana) "
            "are computed at local sunrise for the requested place. "
            "Festival overlays follow tradition rules and Tier A civil tables where present. "
            "Not a digital reprint of commercial Khadiratna or Biraja tables. "
            "Biraja peetha civil dates are rule_only until print/panji fixtures exist."
        ),
    }


def _live_for_place(d: date, place: dict) -> dict:
    """Full sunrise-anchored compute for a place."""
    return compute_panchang(
        d,
        lat=place["lat"],
        lon=place["lon"],
        tz_hours=place.get("tz", 5.5),
    )


def _festivals_for_live(live: dict, tradition: str | None) -> list:
    """Tithi + civil festivals for a live engine day; include sankranti if month flips."""
    from datetime import timedelta

    from src.festivals import get_sankranti_festivals, match_festivals

    day_in = {
        "date": live["date"],
        "paksha_en": live["paksha_en"],
        "tithi_num": live["tithi_num"],
        "chandra_masa_en": live["chandra_masa_en"],
        "soura_masa_en": live["soura_masa_en"],
    }
    results = match_festivals(day_in)
    # Sankranti when solar month differs from previous civil day
    try:
        d = date.fromisoformat(live["date"])
        prev = compute_panchang(
            d - timedelta(days=1),
            lat=live.get("lat"),
            lon=live.get("lon"),
        )
        if prev["soura_masa_en"] != live["soura_masa_en"]:
            results.extend(get_sankranti_festivals(live["soura_masa_en"]))
    except Exception:
        pass

    # Normalize to API shape (nested name)
    out = []
    for f in results:
        out.append(
            {
                "name": {"en": f.get("name_en", ""), "or": f.get("name_or", "")},
                "tradition": f.get("tradition"),
                "description": f.get("description"),
                "story": f.get("story"),
                "why_today": f.get("why_today"),
                "story_kind": f.get("story_kind"),
                "story_sources": f.get("story_sources"),
                "story_complete": f.get("story_complete"),
                **(
                    {
                        "civil_override": True,
                        "source_tier": f.get("source_tier"),
                        "source_note": f.get("source_note"),
                    }
                    if f.get("civil_override")
                    else {}
                ),
            }
        )
    return _filter_festivals(out, tradition)


def _day_to_dict(
    day: PanchangDay,
    festivals: list,
    *,
    place: dict | None = None,
    tradition: str = "all",
    sunrise: str | None = None,
    sunset: str | None = None,
    live: dict | None = None,
    recompute_festivals: bool = False,
) -> dict:
    """
    Serialize a DB day. Prefer live sunrise-anchored `live` compute for elements.
    If recompute_festivals and live is set, festivals come from live match.
    """
    if place is None:
        place = resolve_city(tradition="common")

    if live is None:
        try:
            live = _live_for_place(date.fromisoformat(day.date), place)
        except Exception:
            live = None

    if live and recompute_festivals:
        festivals = _festivals_for_live(live, tradition)

    anchor = (live or {}).get("day_elements_anchor") or "local_sunrise"
    src = live  # prefer live fields

    def _b(en_key, or_key, db_en, db_or):
        if src:
            return {"en": src[en_key], "or": src[or_key]}
        return {"en": db_en, "or": db_or}

    tithi = (
        {
            "num": src["tithi_num"],
            "en": src["tithi_en"],
            "or": src["tithi_or"],
        }
        if src
        else {"num": day.tithi_num, "en": day.tithi_en, "or": day.tithi_or}
    )

    return {
        "meta": _build_meta(place, tradition, anchor=anchor),
        "date": day.date,
        "vara": _b("vara_en", "vara_or", day.vara_en, day.vara_or),
        "soura_masa": _b(
            "soura_masa_en", "soura_masa_or", day.soura_masa_en, day.soura_masa_or
        ),
        "chandra_masa": _b(
            "chandra_masa_en",
            "chandra_masa_or",
            day.chandra_masa_en,
            day.chandra_masa_or,
        ),
        "paksha": _b("paksha_en", "paksha_or", day.paksha_en, day.paksha_or),
        "tithi": tithi,
        "nakshatra": _b(
            "nakshatra_en", "nakshatra_or", day.nakshatra_en, day.nakshatra_or
        ),
        "yoga": _b("yoga_en", "yoga_or", day.yoga_en, day.yoga_or),
        "karana": _b("karana_en", "karana_or", day.karana_en, day.karana_or),
        "sunrise": (src or {}).get("sunrise")
        if src
        else (sunrise if sunrise is not None else day.sunrise),
        "sunset": (src or {}).get("sunset")
        if src
        else (sunset if sunset is not None else day.sunset),
        "festivals": festivals,
    }


def _resolve_place_or_400(city: str | None, tradition: str | None) -> dict:
    try:
        return resolve_city(city=city, tradition=tradition)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _place_sun(d: date, place: dict) -> tuple[str | None, str | None]:
    """Sunrise/sunset for place without mutating global env."""
    live = _live_for_place(d, place)
    return live.get("sunrise"), live.get("sunset")


def _festival_to_dict(f: Festival) -> dict:
    """Serialize festival; attach curated story / why_today at read time."""
    from src.festival_civil import lookup_civil_meta
    from src.festival_stories import attach_story

    payload = {
        "name":        {"en": f.name_en, "or": f.name_or},
        "tradition":   f.tradition,
        "description": f.description,
        "name_en":     f.name_en,  # for story lookup; stripped below
    }
    civil = lookup_civil_meta(getattr(f, "date", None), f.name_en)
    if civil:
        payload.update(civil)
    attach_story(payload)
    payload.pop("name_en", None)
    out = {
        "name":           payload["name"],
        "tradition":      payload["tradition"],
        "description":    payload["description"],
        "story":          payload.get("story"),
        "why_today":      payload.get("why_today"),
        "story_kind":     payload.get("story_kind"),
        "story_sources":  payload.get("story_sources"),
        "story_complete": payload.get("story_complete"),
    }
    if payload.get("civil_override"):
        out["civil_override"] = True
        out["source_tier"] = payload.get("source_tier")
        out["source_note"] = payload.get("source_note")
    return out


def _get_day(db: OrmSession, date_str: str) -> PanchangDay:
    day = db.get(PanchangDay, date_str)
    if not day:
        raise HTTPException(
            status_code=404,
            detail=f"Panchang data for {date_str} not found. Run seed.py to populate the database."
        )
    return day


def _build_enrichment(base: dict) -> dict:
    """
    Run both AI enrichment layers. Never mutates `base` panji fields.
    Output is sanitized (denylist, Odia fill, non_authoritative flag).
    """
    from src.enrichment_safety import sanitize_enrichment

    d = date.fromisoformat(base["date"])
    weekday = d.weekday()  # Mon=0, Sun=6

    # Snapshot base identity fields — must remain identical after enrichment
    base_identity = {
        "date": base.get("date"),
        "tithi": base.get("tithi"),
        "chandra_masa": base.get("chandra_masa"),
        "nakshatra": base.get("nakshatra"),
        "paksha": base.get("paksha"),
    }

    muhurtas = compute_muhurtas(
        base["date"],
        base.get("sunrise", ""),
        base.get("sunset", ""),
        weekday,
    )
    yogas = detect_special_yogas(weekday, base["nakshatra"]["en"], base["yoga"]["en"])
    layer1 = validate_with_ai(base, muhurtas, yogas)
    layer2 = enrich_with_claude(base, layer1)

    # Integrity: base must be unchanged by enrichment helpers
    for k, v in base_identity.items():
        if base.get(k) != v:
            logger = logging.getLogger(__name__)
            logger.error("Enrichment mutated base panji field %s — restoring", k)
            base[k] = v

    return sanitize_enrichment({"astronomical": layer1, "cultural": layer2})


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Serve the main web interface."""
    api_base_url = os.getenv("PUBLIC_API_URL", "")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_base_url": api_base_url}
    )


@app.get("/api")
def health_check():
    """
    Health: ok only if today's panji row exists in the DB.
    Degraded (503) when DB is empty/missing today so keep-warm/load balancers notice.
    """
    today = datetime.now(tz=IST).date().isoformat()
    db = SessionLocal()
    try:
        row = db.get(PanchangDay, today)
        if row is None:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "degraded",
                    "service": "Odia Panchang API",
                    "engine_version": ENGINE_VERSION,
                    "detail": f"No panchang row for today ({today}). Run seed.py / start.sh reseed.",
                },
            )
        return {
            "status": "ok",
            "service": "Odia Panchang API",
            "engine_version": ENGINE_VERSION,
            "today": today,
        }
    finally:
        db.close()


def _require_tweet_secret(
    authorization: str | None = Header(default=None),
    x_tweet_cron_secret: str | None = Header(default=None, alias="X-Tweet-Cron-Secret"),
) -> None:
    """
    Protect POST /tweet/post. Callers must send:
      Authorization: Bearer <TWEET_CRON_SECRET>
    or X-Tweet-Cron-Secret: <TWEET_CRON_SECRET>
    """
    expected = (os.getenv("TWEET_CRON_SECRET") or "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail=(
                "TWEET_CRON_SECRET is not configured on the server. "
                "Set it on Render and in GitHub Actions secrets."
            ),
        )
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_tweet_cron_secret:
        token = x_tweet_cron_secret.strip()
    if not token or not _secrets.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/api/status")
def ai_status():
    """Show AI layers, Twitter, and free-tier scheduler configuration."""
    tweet_secret_set = bool((os.getenv("TWEET_CRON_SECRET") or "").strip())
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
        "twitter": {
            "configured": _twitter_ready,
            "note": "Keys must be set on the web service for POST /tweet/post to publish",
            "cron_auth_required": True,
            "cron_secret_configured": tweet_secret_set,
        },
        "facebook": {
            "configured": _meta_page_ready,
            "note": "META_PAGE_ID + META_PAGE_ACCESS_TOKEN for POST /social/post",
        },
        "instagram": {
            "configured": _meta_ig_ready,
            "note": "META_IG_USER_ID + Page token; needs public HTTPS card URL via PUBLIC_API_URL",
        },
        "engine_version": ENGINE_VERSION,
        "scheduler": {
            "inprocess": _ENABLE_INPROCESS_SCHEDULER,
            "recommended": "github_actions",
            "workflow": ".github/workflows/daily-tweet.yml",
            "enable_inprocess_env": "ENABLE_INPROCESS_SCHEDULER=true",
        },
        "enrichment_endpoints": [
            "/today?enriched=true",
            "/panchang/{date}?enriched=true",
            "/panchang/{date}/insights",
        ],
    }


@app.get("/today")
def get_today(
    enriched: bool = Query(default=False, description="Include AI enrichment layers"),
    city: Optional[str] = Query(default=None, description="City key from /api/cities"),
    tradition: Optional[Literal["jagannath", "biraja", "common", "all", "lingaraj"]] = Query(
        default="all",
        description="Festival overlay + default city when city omitted",
    ),
):
    """Return full Panchang for today (IST)."""
    place = _resolve_place_or_400(city, tradition)
    today = datetime.now(tz=timezone(timedelta(hours=5, minutes=30))).date()
    db = SessionLocal()
    try:
        day = _get_day(db, today.isoformat())
        result = _day_to_dict(
            day,
            [],
            place=place,
            tradition=tradition or "all",
            recompute_festivals=True,
        )
        if enriched:
            result["enrichment"] = _build_enrichment(result)
        return result
    finally:
        db.close()


@app.get("/panchang/{date_str}/insights")
@limiter.limit("10/minute")
def get_panchang_insights(
    date_str: str,
    request: Request,
    city: Optional[str] = Query(default=None, description="City key from /api/cities"),
    tradition: Optional[Literal["jagannath", "biraja", "common", "all", "lingaraj"]] = Query(
        default="all",
        description="Festival overlay + default city when city omitted",
    ),
):
    """
    Return full AI-enriched Panchang insights for a specific date.
    Always runs both enrichment layers (advisory only — non_authoritative).
    Same city/tradition semantics as GET /panchang/{date}.
    """
    try:
        date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    place = _resolve_place_or_400(city, tradition)
    db = SessionLocal()
    try:
        day = _get_day(db, date_str)
        result = _day_to_dict(
            day,
            [],
            place=place,
            tradition=tradition or "all",
            recompute_festivals=True,
        )
        result["enrichment"] = _build_enrichment(result)
        return result
    finally:
        db.close()


@app.get("/panchang/{date_str}")
def get_panchang_by_date(
    date_str: str,
    enriched: bool = Query(default=False, description="Include AI enrichment layers"),
    city: Optional[str] = Query(default=None, description="City key from /api/cities"),
    tradition: Optional[Literal["jagannath", "biraja", "common", "all", "lingaraj"]] = Query(
        default="all",
        description="Festival overlay + default city when city omitted",
    ),
):
    """
    Return full Panchang for a specific date.
    Date format: YYYY-MM-DD
    Add ?enriched=true for AI-powered astronomical validation + Odia cultural insights.
    Optional ?city= & ?tradition= per dual-tradition spec.
    """
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    place = _resolve_place_or_400(city, tradition)
    db = SessionLocal()
    try:
        day = _get_day(db, date_str)
        result = _day_to_dict(
            day,
            [],
            place=place,
            tradition=tradition or "all",
            recompute_festivals=True,
        )
        if enriched:
            result["enrichment"] = _build_enrichment(result)
        return result
    finally:
        db.close()


@app.get("/panchang/{year}/{month}")
def get_panchang_by_month(
    year: int,
    month: int,
    city: Optional[str] = Query(default=None),
    tradition: Optional[Literal["jagannath", "biraja", "common", "all", "lingaraj"]] = Query(
        default="all",
    ),
):
    """
    Return Panchang for all days in a given month.
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12.")
    place = _resolve_place_or_400(city, tradition)

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
        out = []
        for day in days:
            out.append(
                _day_to_dict(
                    day,
                    [],
                    place=place,
                    tradition=tradition or "all",
                    recompute_festivals=True,
                )
            )
        return out
    finally:
        db.close()


@app.get("/festivals/{year}")
def get_festivals_by_year(
    year: int,
    tradition: Optional[Literal["jagannath", "biraja", "common", "all", "lingaraj"]] = Query(
        default="all",
        description="Filter by temple tradition: jagannath, biraja, common, lingaraj, or all"
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

        out = []
        for f in festivals:
            item = _festival_to_dict(f)
            item["date"] = f.date
            out.append(item)
        return out
    finally:
        db.close()


# ── City-based & Location Endpoints ────────────────────────────────────────

@app.get("/api/cities")
def get_cities():
    """
    Return list of all supported cities with their coordinates.
    """
    return list_all_cities()


@app.get("/api/detect-city")
def detect_city(request: Request):
    """
    Detect the user's nearest *Odisha* city based on IP geolocation.
    Does not echo the raw client IP (privacy). Falls back to Bhubaneswar.
    """
    client_ip = request.client.host if request.client else None
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()

    detected_city = detect_city_from_ip(client_ip or "")
    city_info = get_city_info(detected_city)

    return {
        "detected_city": detected_city,
        "city_info": city_info,
        "fallback": "bhubaneswar",
        "note": "Nearest city among supported Odisha keys only; IP is not returned.",
    }


@app.get("/api/panchang/today/{city}")
def get_panchang_for_city_today(
    city: str,
    tradition: Optional[Literal["jagannath", "biraja", "common", "all", "lingaraj"]] = Query(
        default="all",
    ),
):
    """
    Get today's Panchang for a specific city (sunrise/sunset for that place).
    """
    place = _resolve_place_or_400(city, tradition)
    today = datetime.now(tz=IST).date()
    db = SessionLocal()
    try:
        day = db.get(PanchangDay, today.isoformat())
        if day:
            result = _day_to_dict(
                day,
                [],
                place=place,
                tradition=tradition or "all",
                recompute_festivals=True,
            )
        else:
            p = compute_panchang(
                today, lat=place["lat"], lon=place["lon"], tz_hours=place.get("tz", 5.5)
            )
            festivals_data = _filter_festivals(match_festivals(p), tradition)
            festivals = [
                {
                    "name": {"en": f["name_en"], "or": f["name_or"]},
                    "tradition": f["tradition"],
                    "description": f["description"],
                    "story": f.get("story"),
                    "why_today": f.get("why_today"),
                    "story_kind": f.get("story_kind"),
                    "story_sources": f.get("story_sources"),
                    "story_complete": f.get("story_complete"),
                }
                for f in festivals_data
            ]
            result = {
                "meta": _build_meta(place, tradition or "all"),
                "date": p["date"],
                "vara": {"en": p["vara_en"], "or": p["vara_or"]},
                "soura_masa": {"en": p["soura_masa_en"], "or": p["soura_masa_or"]},
                "chandra_masa": {"en": p["chandra_masa_en"], "or": p["chandra_masa_or"]},
                "paksha": {"en": p["paksha_en"], "or": p["paksha_or"]},
                "tithi": {"num": p["tithi_num"], "en": p["tithi_en"], "or": p["tithi_or"]},
                "nakshatra": {"en": p["nakshatra_en"], "or": p["nakshatra_or"]},
                "yoga": {"en": p["yoga_en"], "or": p["yoga_or"]},
                "karana": {"en": p["karana_en"], "or": p["karana_or"]},
                "sunrise": p["sunrise"],
                "sunset": p["sunset"],
                "festivals": festivals,
            }
        result["city"] = place["name"]
        result["city_or"] = place.get("name_or", "")
        return result
    finally:
        db.close()


@app.get("/api/panchang/monthly/{year}/{month}/download")
def download_monthly_panchang(
    year: int,
    month: int,
    city: str = Query(default="puri", description="City key from /api/cities"),
    format: str = Query(default="text", description="Format: text or calendar"),
    tradition: Optional[Literal["jagannath", "biraja", "common", "all", "lingaraj"]] = Query(
        default="all",
    ),
):
    """
    Download monthly Panchang as text file for printing or offline use.
    City recomputes sunrise/sunset for each day (day elements remain shared IST sample).
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12.")

    place = _resolve_place_or_400(city, tradition)
    city_key = place.get("key") or city

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

        panchang_data = []
        for drow in days:
            panchang_data.append(
                _day_to_dict(
                    drow,
                    [],
                    place=place,
                    tradition=tradition or "all",
                    recompute_festivals=True,
                )
            )
    finally:
        db.close()

    if format == "calendar":
        content = generate_calendar_view(year, month, panchang_data)
    else:
        content = generate_monthly_text(year, month, panchang_data)

    from fastapi.responses import Response

    filename = f"Odia_Panchang_{year}_{month:02d}_{city_key}.txt"
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
        "note": (
            "POST /tweet/post to publish now. Free-tier: use GitHub Actions daily-tweet workflow "
            "(or ENABLE_INPROCESS_SCHEDULER=true on always-on)."
            if twitter_active
            else "Add TWITTER_* keys on the host to enable posting. Until then tweets go to logs/daily_tweets.log"
        ),
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


_log = logging.getLogger(__name__)


@app.post("/tweet/post")
@limiter.limit("5/hour")
async def post_tweet_now(
    request: Request,
    _: None = Depends(_require_tweet_secret),
):
    """
    Manually trigger today's tweet right now (same as the 5 AM job).
    Requires TWEET_CRON_SECRET (Bearer or X-Tweet-Cron-Secret).
    Waits for completion and returns the full result so callers can see
    whether the tweet was posted to Twitter or saved to the log file.
    """
    try:
        data = await run_daily_tweet()
        # Sanitize: replace raw exception messages with a generic string so
        # internal details are not exposed in the HTTP response.
        # Re-build the response from explicit safe fields to break any taint chain.
        if "error" in data:
            _log.error("[tweet/post] Tweet job error (details in app logs)")
            result_out = {"status": "error", "message": "Tweet job failed. Check application logs."}
        else:
            result = data.get("result", {})
            result_status = result.get("status", "unknown")
            if result_status == "error":
                _log.error("[tweet/post] Tweet post error: %s",
                           result.get("message") or "No error message provided")
                result_out = {"status": "error", "message": "Tweet post failed. Check application logs."}
            else:
                result_out = {"status": result_status, "message": result.get("message", "")}

        bundle = data.get("bundle") or {}
        return {
            "date": data.get("date"),
            "bundle": {
                "date": bundle.get("date"),
                "main_tweet": bundle.get("main_tweet"),
                "main_tweet_length": bundle.get("main_tweet_length"),
                "thread_reply": bundle.get("thread_reply"),
                "thread_reply_length": bundle.get("thread_reply_length"),
                "festivals": bundle.get("festivals"),
            },
            "result": result_out,
        }
    except Exception as exc:
        _log.error("[tweet/post] Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Tweet job encountered an unexpected error. Check application logs.")


# ── Facebook / Instagram (Meta Graph) ───────────────────────────────────────

@app.get("/social/preview")
@limiter.limit("10/minute")
def preview_social(request: Request):
    """
    Preview Facebook caption, Instagram caption, and share-card image URL.
    Does not publish.
    """
    from src.meta_poster import (
        generate_facebook_message,
        generate_instagram_caption,
        meta_configured,
    )
    from src.social_card import generate_daily_card, public_card_url

    today = datetime.now(tz=IST).date()
    db = SessionLocal()
    try:
        day = _get_day(db, today.isoformat())
        festivals = [_festival_to_dict(f) for f in day.festivals]
        panchang = _day_to_dict(day, festivals)
    finally:
        db.close()

    enrichment = _build_enrichment(panchang)
    card = generate_daily_card(panchang, enrichment)
    image_url = public_card_url(card, public_base=os.getenv("PUBLIC_API_URL"))
    return {
        "date": panchang["date"],
        "facebook_message": generate_facebook_message(panchang, enrichment),
        "instagram_caption": generate_instagram_caption(panchang, enrichment),
        "card_path": str(card),
        "image_url": image_url,
        "facebook_configured": meta_configured(need_ig=False),
        "instagram_configured": meta_configured(need_ig=True),
        "note": (
            "POST /social/post with Bearer TWEET_CRON_SECRET to publish. "
            "Instagram needs a public HTTPS image_url (PUBLIC_API_URL)."
        ),
    }


@app.post("/social/post")
@limiter.limit("5/hour")
async def post_social_now(
    request: Request,
    _: None = Depends(_require_tweet_secret),
    platforms: str = Query(
        default="facebook,instagram",
        description="Comma-separated: facebook,instagram",
    ),
):
    """
    Publish today's panjika to Facebook Page and/or Instagram Business.
    Requires TWEET_CRON_SECRET. Uses META_* env on the server.
    """
    plat_list = [p.strip().lower() for p in platforms.split(",") if p.strip()]
    allowed = {"facebook", "instagram"}
    plat_list = [p for p in plat_list if p in allowed]
    if not plat_list:
        raise HTTPException(
            status_code=400,
            detail="platforms must include facebook and/or instagram",
        )
    try:
        data = await run_daily_social(plat_list)
        if "error" in data and "social" not in data:
            _log.error("[social/post] job error: %s", data.get("error"))
            return {
                "date": data.get("date"),
                "status": "error",
                "message": "Social post job failed. Check application logs.",
            }
        social = data.get("social") or {}
        # Sanitize platform messages (no raw tokens)
        safe_platforms = {}
        for name, res in (social.get("platforms") or {}).items():
            safe_platforms[name] = {
                "status": res.get("status"),
                "message": res.get("message", ""),
                "post_id": res.get("post_id") or res.get("media_id"),
            }
        return {
            "date": data.get("date") or social.get("date"),
            "status": social.get("status", "unknown"),
            "image_url": social.get("image_url"),
            "platforms": safe_platforms,
            "facebook_message": social.get("facebook_message"),
            "instagram_caption": social.get("instagram_caption"),
        }
    except Exception as exc:
        _log.error("[social/post] Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Social post job failed. Check application logs.",
        )


@app.post("/social/post/all")
@limiter.limit("5/hour")
async def post_all_channels(
    request: Request,
    _: None = Depends(_require_tweet_secret),
):
    """
    One wake: post X + Facebook + Instagram (free-tier daily cron).
    Requires TWEET_CRON_SECRET.
    """
    try:
        data = await run_daily_all_channels()
        tw = data.get("twitter") or {}
        social = data.get("social") or {}
        safe_platforms = {}
        for name, res in (social.get("platforms") or {}).items():
            if isinstance(res, dict):
                safe_platforms[name] = {
                    "status": res.get("status"),
                    "message": res.get("message", ""),
                    "post_id": res.get("post_id") or res.get("media_id"),
                }
        return {
            "date": data.get("date"),
            "twitter": {
                "status": tw.get("status") if isinstance(tw, dict) else "unknown",
                "message": (tw.get("message") if isinstance(tw, dict) else "") or "",
            },
            "social": {
                "status": social.get("status"),
                "image_url": social.get("image_url"),
                "platforms": safe_platforms,
            },
        }
    except Exception as exc:
        _log.error("[social/post/all] Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="All-channels post failed.")


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

