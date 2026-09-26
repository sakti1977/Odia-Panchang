#!/usr/bin/env python3
"""Post today's Odia panjika to Facebook + Instagram from this checkout.

No Render / no public HTTP API. GitHub Actions runs:

    python scripts/post_daily.py

Env:
  META_PAGE_ID, META_PAGE_ACCESS_TOKEN   required to publish
  META_IG_USER_ID                        optional (discovered from the Page)
  INSTAGRAM_AS_STORY                     default true
  SOCIAL_HERITAGE_CARD                   default true (second image)
  PLATFORMS                              comma list, default facebook,instagram
  TEST_MODE=true                         generate caption + cards, do not publish
  PANJIKA_DATE=YYYY-MM-DD                override IST today
  DATABASE_URL                           default sqlite:///./data/panchang.db
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.chdir(ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("post_daily")


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main(argv: list[str] | None = None) -> int:
    _load_dotenv()
    test_mode = os.getenv("TEST_MODE", "false").lower() in ("1", "true", "yes", "on")
    date_override = (os.getenv("PANJIKA_DATE") or "").strip() or None
    platforms = [
        p.strip().lower()
        for p in (os.getenv("PLATFORMS") or "facebook,instagram").split(",")
        if p.strip()
    ]
    allowed = {"facebook", "instagram"}
    platforms = [p for p in platforms if p in allowed]
    if not platforms:
        logger.error("PLATFORMS must include facebook and/or instagram")
        return 1

    from src.local_day import DayNotFound, load_panchang_day, rule_enrichment
    from src.tweet_generator import generate_social_caption

    try:
        panchang = load_panchang_day(date_override)
    except DayNotFound as exc:
        logger.error("%s", exc)
        return 1

    from src.festival_audit import PublishBlocked, prepare_for_publish

    try:
        panchang, unverified = prepare_for_publish(panchang)
    except PublishBlocked as exc:
        logger.error("Festival verification failed — not posting: %s", exc)
        return 1
    if unverified:
        logger.warning("Not announcing unverified festivals: %s", ", ".join(unverified))

    enrichment = rule_enrichment(panchang)
    caption = generate_social_caption(panchang, enrichment)
    logger.info("Loaded panji for %s", panchang["date"])
    logger.info("Caption (%d chars):\n%s", len(caption), caption)

    from src.social_card import generate_daily_card, generate_story_card

    card = generate_daily_card(panchang, enrichment)
    logger.info("Feed card: %s", card)
    if "instagram" in platforms:
        story = generate_story_card(panchang, enrichment, feed_path=card)
        logger.info("Story card: %s", story)
    if os.getenv("SOCIAL_HERITAGE_CARD", "true").lower() != "false":
        from src.social_card import generate_heritage_card

        logger.info("Heritage card: %s", generate_heritage_card(panchang))

    if test_mode:
        logger.info("TEST_MODE: not publishing (platforms=%s)", ",".join(platforms))
        return 0

    from src.meta_poster import post_meta_bundle

    result = post_meta_bundle(panchang, enrichment, platforms=platforms)
    status = result.get("status")
    logger.info("Social status=%s platforms=%s", status, result.get("platforms"))
    if status != "posted":
        logger.error("Publish did not fully succeed: %s", result.get("message") or status)
        return 1

    marker = ROOT / ".state" / "posted.marker"
    marker.parent.mkdir(exist_ok=True)
    marker.write_text(f"{panchang['date']}\n", encoding="utf-8")
    logger.info("Wrote %s", marker)
    return 0


if __name__ == "__main__":
    sys.exit(main())
