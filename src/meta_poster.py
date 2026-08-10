"""
Facebook Page + Instagram Business posting via Meta Graph API.

Env (set on Render web service):
  META_PAGE_ID              Facebook Page ID
  META_PAGE_ACCESS_TOKEN    Long-lived Page access token
  META_IG_USER_ID           Instagram Business/Creator user ID (optional)
  META_GRAPH_VERSION        default v21.0
  PUBLIC_API_URL            Public base URL so IG can fetch the share card image

Instagram requires a publicly reachable image URL (feed posts are not text-only).
Facebook can post text-only; we attach the card when available.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

SOCIAL_LOG = Path("logs/daily_social.log")


def meta_config() -> dict[str, str | None]:
    return {
        "page_id": (os.getenv("META_PAGE_ID") or "").strip() or None,
        "token": (os.getenv("META_PAGE_ACCESS_TOKEN") or "").strip() or None,
        "ig_user_id": (os.getenv("META_IG_USER_ID") or "").strip() or None,
        "version": (os.getenv("META_GRAPH_VERSION") or "v21.0").strip(),
    }


def meta_configured(*, need_ig: bool = False) -> bool:
    cfg = meta_config()
    ok = bool(cfg["page_id"] and cfg["token"])
    if need_ig:
        ok = ok and bool(cfg["ig_user_id"])
    return ok


def _graph_url(path: str) -> str:
    ver = meta_config()["version"]
    return f"https://graph.facebook.com/{ver}/{path.lstrip('/')}"


def _log_social(platform: str, payload: dict) -> None:
    SOCIAL_LOG.parent.mkdir(exist_ok=True)
    import json
    from datetime import datetime, timezone, timedelta

    ist = timezone(timedelta(hours=5, minutes=30))
    ts = datetime.now(ist).strftime("%Y-%m-%d %H:%M IST")
    with open(SOCIAL_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n{ts} [{platform}]\n")
        f.write(json.dumps(payload, ensure_ascii=False, indent=2)[:4000])
        f.write("\n")


def generate_facebook_message(panchang: dict, enrichment: dict | None = None) -> str:
    """Longer caption for Facebook (up to ~2000 chars used)."""
    from src.tweet_generator import generate_main_tweet, generate_thread_tweet

    main = generate_main_tweet(panchang, enrichment)
    thread = generate_thread_tweet(panchang, enrichment or {})
    # Prefer full Odia main + story thread for FB
    parts = [main]
    if thread:
        parts.append(thread)
    public = (os.getenv("PUBLIC_API_URL") or "").rstrip("/")
    if public:
        parts.append(f"\n🔗 {public}")
    msg = "\n\n".join(parts).strip()
    if len(msg) > 2000:
        msg = msg[:1997] + "…"
    return msg


def generate_instagram_caption(panchang: dict, enrichment: dict | None = None) -> str:
    """Instagram caption (max 2200)."""
    msg = generate_facebook_message(panchang, enrichment)
    if len(msg) > 2200:
        msg = msg[:2197] + "…"
    return msg


def post_facebook_page(
    message: str,
    *,
    image_url: str | None = None,
) -> dict[str, Any]:
    """
    Post to Facebook Page feed (text) or photos edge if image_url given.
    """
    cfg = meta_config()
    if not cfg["page_id"] or not cfg["token"]:
        _log_social("facebook", {"status": "logged", "message": message[:500]})
        return {
            "status": "logged",
            "platform": "facebook",
            "message": "META_PAGE_ID / META_PAGE_ACCESS_TOKEN not set — saved to logs/daily_social.log",
        }

    try:
        with httpx.Client(timeout=60.0) as client:
            if image_url:
                url = _graph_url(f"{cfg['page_id']}/photos")
                data = {
                    "url": image_url,
                    "caption": message,
                    "access_token": cfg["token"],
                }
            else:
                url = _graph_url(f"{cfg['page_id']}/feed")
                data = {
                    "message": message,
                    "access_token": cfg["token"],
                }
            resp = client.post(url, data=data)
            body = resp.json() if resp.content else {}
            if resp.status_code >= 400:
                logger.error("[Facebook] post failed %s %s", resp.status_code, body)
                _log_social("facebook", {"status": "error", "http": resp.status_code, "body": body, "message": message[:300]})
                return {
                    "status": "error",
                    "platform": "facebook",
                    "message": body.get("error", {}).get("message") or str(body)[:300],
                    "http_status": resp.status_code,
                }
            post_id = body.get("id") or body.get("post_id")
            logger.info("[Facebook] posted id=%s", post_id)
            return {
                "status": "posted",
                "platform": "facebook",
                "post_id": post_id,
            }
    except Exception as e:
        logger.error("[Facebook] exception: %s", e, exc_info=True)
        _log_social("facebook", {"status": "error", "message": str(e)})
        return {"status": "error", "platform": "facebook", "message": str(e)}


def post_instagram_feed(
    caption: str,
    image_url: str,
) -> dict[str, Any]:
    """
    Instagram Content Publishing:
      1) create media container
      2) publish container
    image_url must be publicly HTTPS-accessible.
    """
    cfg = meta_config()
    if not cfg["ig_user_id"] or not cfg["token"]:
        _log_social("instagram", {"status": "logged", "caption": caption[:500], "image_url": image_url})
        return {
            "status": "logged",
            "platform": "instagram",
            "message": "META_IG_USER_ID / token not set — saved to logs/daily_social.log",
        }

    if not image_url.startswith("https://"):
        return {
            "status": "error",
            "platform": "instagram",
            "message": "Instagram requires a public HTTPS image_url (set PUBLIC_API_URL)",
        }

    try:
        with httpx.Client(timeout=90.0) as client:
            create_url = _graph_url(f"{cfg['ig_user_id']}/media")
            create_resp = client.post(
                create_url,
                data={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": cfg["token"],
                },
            )
            create_body = create_resp.json() if create_resp.content else {}
            if create_resp.status_code >= 400 or not create_body.get("id"):
                logger.error("[Instagram] container failed %s %s", create_resp.status_code, create_body)
                _log_social(
                    "instagram",
                    {"status": "error", "step": "create", "body": create_body, "image_url": image_url},
                )
                return {
                    "status": "error",
                    "platform": "instagram",
                    "message": create_body.get("error", {}).get("message")
                    or f"container create failed: {create_body}",
                    "http_status": create_resp.status_code,
                }
            creation_id = create_body["id"]

            pub_url = _graph_url(f"{cfg['ig_user_id']}/media_publish")
            pub_resp = client.post(
                pub_url,
                data={
                    "creation_id": creation_id,
                    "access_token": cfg["token"],
                },
            )
            pub_body = pub_resp.json() if pub_resp.content else {}
            if pub_resp.status_code >= 400:
                logger.error("[Instagram] publish failed %s %s", pub_resp.status_code, pub_body)
                return {
                    "status": "error",
                    "platform": "instagram",
                    "message": pub_body.get("error", {}).get("message") or str(pub_body)[:300],
                    "creation_id": creation_id,
                    "http_status": pub_resp.status_code,
                }
            media_id = pub_body.get("id")
            logger.info("[Instagram] published id=%s", media_id)
            return {
                "status": "posted",
                "platform": "instagram",
                "media_id": media_id,
                "creation_id": creation_id,
            }
    except Exception as e:
        logger.error("[Instagram] exception: %s", e, exc_info=True)
        _log_social("instagram", {"status": "error", "message": str(e)})
        return {"status": "error", "platform": "instagram", "message": str(e)}


def post_meta_bundle(
    panchang: dict,
    enrichment: dict | None = None,
    *,
    platforms: list[str] | None = None,
    public_base: str | None = None,
) -> dict[str, Any]:
    """
    Generate card + captions and post to requested platforms.
    platforms: subset of facebook, instagram (default both if configured).
    """
    from src.social_card import generate_daily_card, public_card_url

    platforms = platforms or ["facebook", "instagram"]
    platforms = [p.lower().strip() for p in platforms]

    card_path = generate_daily_card(panchang, enrichment)
    image_url = public_card_url(card_path, public_base=public_base)
    fb_msg = generate_facebook_message(panchang, enrichment)
    ig_cap = generate_instagram_caption(panchang, enrichment)

    results: dict[str, Any] = {
        "date": panchang.get("date"),
        "image_url": image_url,
        "card_path": str(card_path),
        "facebook_message": fb_msg,
        "instagram_caption": ig_cap,
        "platforms": {},
    }

    if "facebook" in platforms:
        results["platforms"]["facebook"] = post_facebook_page(
            fb_msg, image_url=image_url if image_url.startswith("https://") else None
        )
    if "instagram" in platforms:
        results["platforms"]["instagram"] = post_instagram_feed(ig_cap, image_url)

    # Overall status
    statuses = [v.get("status") for v in results["platforms"].values()]
    if statuses and all(s == "posted" for s in statuses):
        results["status"] = "posted"
    elif statuses and any(s == "posted" for s in statuses):
        results["status"] = "partial"
    elif statuses and all(s == "logged" for s in statuses):
        results["status"] = "logged"
    else:
        results["status"] = "error"

    return results
