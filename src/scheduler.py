"""
Daily 5 AM IST scheduler for Odia Panchang tweets.
Uses APScheduler. Posts via Tweepy if TWITTER_* keys are set in .env,
otherwise writes generated tweets to logs/daily_tweets.log.

When PUBLIC_API_URL is set, the scheduler fetches panchang data from the
public Render API instead of computing locally — this reduces server load
on the web service.
"""

import os
import logging
import httpx
from datetime import datetime, timezone, timedelta
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))
TWEET_LOG = Path("logs/daily_tweets.log")


def _get_twitter_client():
    """Return Tweepy client if credentials are configured, else None."""
    try:
        import tweepy
        keys = {
            "consumer_key":        os.getenv("TWITTER_API_KEY"),
            "consumer_secret":     os.getenv("TWITTER_API_SECRET"),
            "access_token":        os.getenv("TWITTER_ACCESS_TOKEN"),
            "access_token_secret": os.getenv("TWITTER_ACCESS_SECRET"),
        }

        # Check which keys are missing
        missing_keys = [k for k, v in keys.items() if not v]
        if missing_keys:
            logger.warning(f"[Twitter] Missing credentials: {', '.join(missing_keys)}")
            return None

        logger.info("[Twitter] All credentials found, creating client...")

        # Add bearer token if available (recommended for v2 API)
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if bearer_token:
            logger.info("[Twitter] Using OAuth 2.0 Bearer Token + OAuth 1.0a credentials")
            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=keys["consumer_key"],
                consumer_secret=keys["consumer_secret"],
                access_token=keys["access_token"],
                access_token_secret=keys["access_token_secret"],
            )
        else:
            logger.info("[Twitter] Using OAuth 1.0a User Context authentication")
            client = tweepy.Client(
                consumer_key=keys["consumer_key"],
                consumer_secret=keys["consumer_secret"],
                access_token=keys["access_token"],
                access_token_secret=keys["access_token_secret"],
            )
        logger.info(f"[Twitter] Client created successfully (tweepy v{tweepy.__version__})")
        return client
    except ImportError as e:
        logger.error(f"[Twitter] Failed to import tweepy: {e}")
        return None
    except Exception as e:
        logger.error(f"[Twitter] Failed to create client: {e}", exc_info=True)
        return None


def _log_tweet(bundle: dict):
    """Write tweet to log file when Twitter is not configured."""
    TWEET_LOG.parent.mkdir(exist_ok=True)
    timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
    with open(TWEET_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"📅 Generated: {timestamp}\n")
        f.write(f"Date: {bundle['date']}\n")
        f.write(f"Festivals: {', '.join(bundle['festivals']) or 'none'}\n\n")
        f.write("── MAIN TWEET ──\n")
        f.write(bundle["main_tweet"] + "\n")
        f.write(f"[{bundle['main_tweet_length']} chars]\n\n")
        if bundle.get("thread_reply"):
            f.write("── THREAD REPLY ──\n")
            f.write(bundle["thread_reply"] + "\n")
            f.write(f"[{bundle['thread_reply_length']} chars]\n")
    logger.info(f"Tweet logged to {TWEET_LOG}")


def _post_tweet(bundle: dict) -> dict:
    """Post to Twitter/X. Returns result dict."""
    logger.info(f"[Twitter] Attempting to post tweet for {bundle.get('date')}")

    client = _get_twitter_client()
    if not client:
        logger.warning("[Twitter] Client not available, falling back to log file")
        _log_tweet(bundle)
        return {"status": "logged", "message": "Twitter not configured — tweet saved to logs/daily_tweets.log"}

    try:
        logger.info(f"[Twitter] Posting main tweet ({bundle['main_tweet_length']} chars)")
        # Post main tweet
        resp = client.create_tweet(text=bundle["main_tweet"])
        main_id = resp.data["id"]
        result = {"status": "posted", "main_tweet_id": main_id}
        logger.info(f"[Twitter] ✅ Main tweet posted successfully: {main_id}")

        # Post thread reply if available
        if bundle.get("thread_reply"):
            logger.info(f"[Twitter] Posting thread reply ({bundle['thread_reply_length']} chars)")
            reply = client.create_tweet(
                text=bundle["thread_reply"],
                in_reply_to_tweet_id=main_id,
            )
            result["thread_tweet_id"] = reply.data["id"]
            logger.info(f"[Twitter] ✅ Thread reply posted: {reply.data['id']}")

        logger.info(f"[Twitter] Tweet job complete: {result}")
        return result
    except Exception as e:
        logger.error(f"[Twitter] ❌ Post failed: {type(e).__name__}: {e}", exc_info=True)
        _log_tweet(bundle)  # fallback to log
        return {"status": "error", "message": f"{type(e).__name__}: {str(e)}"}


async def run_daily_tweet():
    """
    Main scheduled job: fetch today's panchang + enrichment, generate tweet, post or log.
    Called at 5:00 AM IST every day.

    If PUBLIC_API_URL is set, fetches enriched data from the public API (keeps
    the Render free-tier server warm). Falls back to local computation otherwise.
    """
    today = datetime.now(IST).date()
    logger.info(f"[Scheduler] Running daily tweet job for {today}")

    public_url = os.getenv("PUBLIC_API_URL", "").rstrip("/")

    try:
        panchang = None
        enrichment = {}

        # ── Try public API first (warms up Render free tier) ──────────────
        if public_url:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get(
                        f"{public_url}/panchang/{today.isoformat()}",
                        params={"enriched": "true"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                panchang = data
                enrichment = {
                    "astronomical": data.get("enrichment", {}).get("astronomical", {}),
                    "cultural":     data.get("enrichment", {}).get("cultural", {}),
                }
                logger.info(f"[Scheduler] Fetched from public API: {public_url}")
            except Exception as api_err:
                logger.warning(f"[Scheduler] Public API call failed ({api_err}), falling back to local compute")
                panchang = None

        # ── Local fallback ─────────────────────────────────────────────────
        if panchang is None:
            from src.ai_layer1 import compute_muhurtas, detect_special_yogas, validate_with_ai
            from src.ai_layer2 import enrich_with_claude
            from main import SessionLocal, _get_day, _day_to_dict, _festival_to_dict

            db = SessionLocal()
            try:
                day = _get_day(db, today.isoformat())
                festivals = [_festival_to_dict(f) for f in day.festivals]
                panchang = _day_to_dict(day, festivals)
            finally:
                db.close()

            weekday  = today.weekday()
            muhurtas = compute_muhurtas(today.isoformat(), panchang["sunrise"], panchang["sunset"], weekday)
            yogas    = detect_special_yogas(weekday, panchang["nakshatra"]["en"], panchang["yoga"]["en"])
            layer1   = validate_with_ai(panchang, muhurtas, yogas)
            layer2   = enrich_with_claude(panchang, layer1)
            enrichment = {"astronomical": layer1, "cultural": layer2}

        # ── Generate + post ────────────────────────────────────────────────
        from src.tweet_generator import generate_tweet_bundle
        bundle = generate_tweet_bundle(panchang, enrichment)
        result = _post_tweet(bundle)
        logger.info(f"[Scheduler] Tweet job done: {result}")
        return {"date": today.isoformat(), "bundle": bundle, "result": result}

    except Exception as e:
        logger.error(f"[Scheduler] Daily tweet job failed: {e}", exc_info=True)
        return {"error": str(e)}


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
    scheduler = AsyncIOScheduler(timezone=IST)
    scheduler.add_job(
        run_daily_tweet,
        trigger=CronTrigger(hour=5, minute=0, timezone=IST),
        id="daily_tweet",
        name="Daily 5 AM Odia Panchang Tweet",
        replace_existing=True,
        misfire_grace_time=300,  # allow 5 min late start
    )
    return scheduler
