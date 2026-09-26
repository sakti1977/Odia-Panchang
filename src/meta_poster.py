"""
Facebook Page + Instagram professional-account publishing via Meta Graph API.

Same pattern as the Bengali panjika bot:
  - Multipart JPEG upload to the Facebook Page (feed photo + caption)
  - Instagram Story (9:16) by default; feed if INSTAGRAM_AS_STORY=false
  - Instagram ingest uses the Facebook photo CDN URL, then a short-lived
    public host if Meta's crawler cannot fetch that CDN URL
  - Duplicate-post fingerprint on recent captions so a retry after Facebook
    succeeded and Instagram failed does not double-post to Facebook
  - Token goes in Authorization, never in a logged URL

Env (set on the Render web service):
  META_PAGE_ID
  META_PAGE_ACCESS_TOKEN
  META_IG_USER_ID           optional — discovered from the Page if omitted
  META_GRAPH_VERSION        default v22.0
  INSTAGRAM_AS_STORY        default true
  SOCIAL_HERITAGE_CARD      default true — second 'ଜାଣନ୍ତୁ ଓଡ଼ିଶା' image
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.retry_utils import retry
from src.tweet_generator import caption_fingerprint, generate_social_caption

logger = logging.getLogger(__name__)

SOCIAL_LOG = Path("logs/daily_social.log")
GRAPH_API_VERSION = os.getenv("META_GRAPH_VERSION") or os.getenv(
    "META_GRAPH_API_VERSION", "v22.0"
)
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
USER_AGENT = "odia-panchang/2.0"
HTTP_TIMEOUT_SECONDS = 30
UPLOAD_TIMEOUT_SECONDS = 120
IG_CONTAINER_POLL_SECONDS = 5
IG_CONTAINER_POLL_ATTEMPTS = 24
BRAND_NAME_OR = "ଓଡ଼ିଆ ପଞ୍ଜିକା"
BRAND_NAME_EN = "Odia Panjika"


class GraphAPIError(Exception):
    """A Graph API call returned an error payload (or a non-JSON HTTP failure)."""

    def __init__(self, message: str, code: int | None = None, status: int | None = None):
        super().__init__(message)
        self.code = code
        self.status = status


@dataclass(frozen=True)
class MetaCredentials:
    page_id: str
    access_token: str
    ig_user_id: str | None


def meta_config() -> dict[str, str | None]:
    return {
        "page_id": (os.getenv("META_PAGE_ID") or "").strip() or None,
        "token": (os.getenv("META_PAGE_ACCESS_TOKEN") or "").strip() or None,
        "ig_user_id": (os.getenv("META_IG_USER_ID") or "").strip() or None,
        "version": (os.getenv("META_GRAPH_VERSION") or "v22.0").strip(),
    }


def meta_configured(*, need_ig: bool = False) -> bool:
    cfg = meta_config()
    ok = bool(cfg["page_id"] and cfg["token"])
    if need_ig:
        ok = ok and bool(cfg["ig_user_id"])
    return ok


def _load_credentials() -> MetaCredentials:
    page_id = os.getenv("META_PAGE_ID")
    access_token = os.getenv("META_PAGE_ACCESS_TOKEN")
    ig_user_id = os.getenv("META_IG_USER_ID") or None
    missing = [
        k
        for k, v in {
            "META_PAGE_ID": page_id,
            "META_PAGE_ACCESS_TOKEN": access_token,
        }.items()
        if not v
    ]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
    assert page_id is not None and access_token is not None
    return MetaCredentials(page_id=page_id, access_token=access_token, ig_user_id=ig_user_id)


def _log_social(platform: str, payload: dict) -> None:
    SOCIAL_LOG.parent.mkdir(exist_ok=True)
    from datetime import datetime, timedelta, timezone

    ist = timezone(timedelta(hours=5, minutes=30))
    ts = datetime.now(ist).strftime("%Y-%m-%d %H:%M IST")
    with open(SOCIAL_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 60}\n{ts} [{platform}]\n")
        f.write(json.dumps(payload, ensure_ascii=False, indent=2)[:4000])
        f.write("\n")


def generate_facebook_message(panchang: dict, enrichment: dict | None = None) -> str:
    return generate_social_caption(panchang, enrichment)


def generate_instagram_caption(panchang: dict, enrichment: dict | None = None) -> str:
    return generate_social_caption(panchang, enrichment)


def _encode_params(params: dict | None) -> str:
    if not params:
        return ""
    return urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})


def _parse_graph_body(raw: str, status: int | None = None) -> dict:
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GraphAPIError(f"Non-JSON Graph API response: {raw[:300]}", status=status) from exc
    if isinstance(payload, dict) and "error" in payload:
        err = payload["error"] if isinstance(payload["error"], dict) else {}
        message = err.get("message") or str(payload["error"])
        code = err.get("code")
        raise GraphAPIError(message, code=code if isinstance(code, int) else None, status=status)
    if not isinstance(payload, dict):
        raise GraphAPIError(f"Unexpected Graph API payload: {raw[:300]}", status=status)
    return payload


def _http_json(
    method: str,
    url: str,
    *,
    token: str,
    params: dict | None = None,
    files: dict | None = None,
    timeout: int = HTTP_TIMEOUT_SECONDS,
) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
    }
    query = _encode_params(params) if files is None else ""
    full_url = f"{url}?{query}" if query else url
    body: bytes | None = None

    if files is not None:
        body, content_type = _encode_multipart(params or {}, files)
        headers["Content-Type"] = content_type
    elif method == "POST":
        body = _encode_params(params).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    req = urllib.request.Request(full_url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return _parse_graph_body(
                resp.read().decode("utf-8", errors="replace"),
                status=getattr(resp, "status", None),
            )
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return _parse_graph_body(raw, status=exc.code)
        except GraphAPIError:
            raise
        except Exception as parse_exc:
            raise GraphAPIError(f"HTTP {exc.code}: {raw[:300]}", status=exc.code) from parse_exc
    except urllib.error.URLError as exc:
        raise GraphAPIError(f"Network error talking to Graph API: {exc}") from exc


def _encode_multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    chunks: list[bytes] = []
    for name, value in fields.items():
        if value is None:
            continue
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")
    for name, (filename, data, content_type) in files.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
        )
        chunks.append(f"Content-Type: {content_type}\r\n\r\n".encode())
        chunks.append(data)
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _graph_url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return GRAPH_BASE + path


def _graph_get(path: str, token: str, params: dict | None = None) -> dict:
    return _http_json("GET", _graph_url(path), token=token, params=params)


def _graph_post(path: str, token: str, params: dict | None = None) -> dict:
    return _http_json("POST", _graph_url(path), token=token, params=params)


def _graph_post_multipart(path: str, token: str, fields: dict, files: dict) -> dict:
    return _http_json(
        "POST",
        _graph_url(path),
        token=token,
        params=fields,
        files=files,
        timeout=UPLOAD_TIMEOUT_SECONDS,
    )


@retry(
    attempts=3,
    base_delay_seconds=2.0,
    exceptions=(GraphAPIError, urllib.error.URLError, TimeoutError, OSError),
)
def _graph_get_retry(path: str, token: str, params: dict | None = None) -> dict:
    return _graph_get(path, token, params)


def _already_posted(recent_captions: list[str], text: str) -> bool:
    header = caption_fingerprint(text)
    if not header:
        return False
    return any(header in (caption or "") for caption in recent_captions)


@retry(
    attempts=3,
    base_delay_seconds=2.0,
    exceptions=(GraphAPIError, urllib.error.URLError, TimeoutError, OSError),
)
def _discover_instagram_user_id(page_id: str, token: str) -> str | None:
    info = _graph_get(f"/{page_id}", token, {"fields": "name,instagram_business_account"})
    page_name = info.get("name") or page_id
    logger.info("Facebook Page: %s", page_name)
    branded = BRAND_NAME_OR in str(page_name) or BRAND_NAME_EN.lower() in str(page_name).lower()
    if not branded:
        logger.warning(
            "Page name %r is not %s / %s — content is still branded; "
            "the linked Instagram may be a personal handle",
            page_name,
            BRAND_NAME_OR,
            BRAND_NAME_EN,
        )
    ig = info.get("instagram_business_account") or {}
    ig_id = ig.get("id") if isinstance(ig, dict) else None
    return str(ig_id) if ig_id else None


def _recent_facebook_captions(page_id: str, token: str) -> list[str]:
    try:
        payload = _graph_get_retry(
            f"/{page_id}/posts", token, {"fields": "message,created_time", "limit": 5}
        )
    except GraphAPIError as exc:
        logger.warning("Could not read recent Facebook posts (duplicate check skipped): %s", exc)
        return []
    return [item.get("message") or "" for item in payload.get("data") or [] if isinstance(item, dict)]


def _recent_instagram_captions(ig_user_id: str, token: str) -> list[str]:
    try:
        payload = _graph_get_retry(
            f"/{ig_user_id}/media", token, {"fields": "caption,timestamp", "limit": 5}
        )
    except GraphAPIError as exc:
        logger.warning("Could not read recent Instagram media (duplicate check skipped): %s", exc)
        return []
    return [item.get("caption") or "" for item in payload.get("data") or [] if isinstance(item, dict)]


def _facebook_photo_cdn_url(photo_id: str, token: str) -> str | None:
    try:
        payload = _graph_get_retry(f"/{photo_id}", token, {"fields": "images"})
    except GraphAPIError as exc:
        logger.warning("Could not fetch Facebook photo URL: %s", exc)
        return None
    images = payload.get("images") or []
    for image in images:
        if isinstance(image, dict) and image.get("source"):
            return image["source"]
    return None


def _read_file_bytes(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


@retry(
    attempts=3,
    base_delay_seconds=2.0,
    exceptions=(urllib.error.URLError, TimeoutError, OSError, GraphAPIError),
)
def _host_image_temporarily(image_path: str) -> str:
    """Fallback public HTTPS URL so Instagram can ingest the JPEG.

    Facebook Page photo CDN URLs are tried first. This is the fallback when
    Instagram's crawler cannot fetch those. Uses litterbox (1-hour expiry) —
    no account, no API key. The URL only needs to live long enough for
    Instagram to ingest the image (seconds).
    """
    data = _read_file_bytes(image_path)
    filename = os.path.basename(image_path) or "daily_image.jpg"
    fields = {"reqtype": "fileupload", "time": "1h"}
    files = {"fileToUpload": (filename, data, "image/jpeg")}
    body, content_type = _encode_multipart(fields, files)
    req = urllib.request.Request(
        "https://litterbox.catbox.moe/resources/internals/api.php",
        data=body,
        method="POST",
        headers={"Content-Type": content_type, "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=UPLOAD_TIMEOUT_SECONDS) as resp:
        url = resp.read().decode("utf-8", errors="replace").strip()
    if not url.startswith("https://"):
        raise GraphAPIError(f"Temporary image host returned an unexpected response: {url[:200]}")
    logger.info("Hosted image temporarily for Instagram ingest")
    return url


def _upload_unpublished_photo(page_id: str, token: str, image_path: str) -> str:
    """Page photo that is not a feed post — Instagram can fetch the CDN URL."""
    data = _read_file_bytes(image_path)
    filename = os.path.basename(image_path) or "story_image.jpg"
    response = _graph_post_multipart(
        f"/{page_id}/photos",
        token,
        fields={"published": "false"},
        files={"source": (filename, data, "image/jpeg")},
    )
    photo_id = response.get("id")
    if not photo_id:
        raise GraphAPIError(f"Unpublished photo upload returned no id: {response}")
    cdn = _facebook_photo_cdn_url(str(photo_id), token)
    if not cdn:
        raise GraphAPIError("Unpublished photo has no CDN URL")
    logger.info("Uploaded unpublished 9:16 photo %s for Instagram Stories", photo_id)
    return cdn


def _resolve_instagram_image_url(image_path: str, token: str, facebook_photo_id: str | None) -> str:
    if facebook_photo_id:
        cdn = _facebook_photo_cdn_url(facebook_photo_id, token)
        if cdn:
            return cdn
        logger.warning("Facebook photo CDN URL unavailable; falling back to a temporary public host")
    return _host_image_temporarily(image_path)


def _upload_photo_for_attach(page_id: str, token: str, image_path: str) -> str:
    """Unpublished Page photo, to be attached to a multi-photo feed post."""
    data = _read_file_bytes(image_path)
    filename = os.path.basename(image_path) or "daily_image.jpg"
    response = _graph_post_multipart(
        f"/{page_id}/photos",
        token,
        fields={"published": "false"},
        files={"source": (filename, data, "image/jpeg")},
    )
    photo_id = response.get("id")
    if not photo_id:
        raise GraphAPIError(f"Unpublished photo upload returned no id: {response}")
    return str(photo_id)


def post_to_facebook(
    text: str,
    image_path: str | None,
    page_id: str,
    token: str,
    extra_image_paths: list[str] | None = None,
) -> dict:
    """Publish to the Facebook Page. Not retried: a lost response may already be live.

    With `extra_image_paths` (the heritage card) this is a multi-photo post:
    every photo is uploaded unpublished, then one /feed post attaches them.
    If an extra photo cannot be uploaded, nothing is live yet, so it falls
    back to the plain single-photo post. The result carries `photo_ids` in
    image order either way.
    """
    extras = [p for p in (extra_image_paths or []) if p and os.path.exists(p)]
    if image_path and os.path.exists(image_path) and extras:
        photo_ids: list[str] | None = None
        try:
            photo_ids = [_upload_photo_for_attach(page_id, token, image_path)]
            for path in extras:
                photo_ids.append(_upload_photo_for_attach(page_id, token, path))
        except (GraphAPIError, OSError) as exc:
            logger.warning("Extra photo upload failed (%s); posting the panji card alone", exc)
            photo_ids = None
        if photo_ids:
            logger.info(
                "Posting %d-photo post to Facebook Page %s (%d chars)",
                len(photo_ids), page_id, len(text),
            )
            params: dict[str, Any] = {"message": text}
            for i, pid in enumerate(photo_ids):
                params[f"attached_media[{i}]"] = json.dumps({"media_fbid": pid})
            response = _graph_post(f"/{page_id}/feed", token, params)
            logger.info("Facebook post succeeded (id=%s)", response.get("id"))
            return {**response, "photo_ids": photo_ids}

    if image_path and os.path.exists(image_path):
        logger.info("Posting photo to Facebook Page %s (%d chars)", page_id, len(text))
        data = _read_file_bytes(image_path)
        filename = os.path.basename(image_path) or "daily_image.jpg"
        response = _graph_post_multipart(
            f"/{page_id}/photos",
            token,
            fields={"message": text, "published": "true"},
            files={"source": (filename, data, "image/jpeg")},
        )
    else:
        if image_path:
            logger.warning("Image path provided but file doesn't exist: %s", image_path)
        logger.info("Posting text-only update to Facebook Page %s (%d chars)", page_id, len(text))
        response = _graph_post(f"/{page_id}/feed", token, {"message": text})

    post_id = response.get("post_id") or response.get("id")
    logger.info("Facebook post succeeded (id=%s)", post_id)
    if image_path and os.path.exists(image_path) and response.get("id"):
        return {**response, "photo_ids": [str(response["id"])]}
    return response


def _wait_for_ig_container(container_id: str, token: str) -> None:
    for attempt in range(1, IG_CONTAINER_POLL_ATTEMPTS + 1):
        status = _graph_get_retry(f"/{container_id}", token, {"fields": "status_code"}).get(
            "status_code"
        )
        logger.info("Instagram container %s status=%s (poll %d)", container_id, status, attempt)
        if status in (None, "FINISHED"):
            return
        if status == "ERROR":
            raise GraphAPIError(f"Instagram media container {container_id} failed to process")
        if status == "EXPIRED":
            raise GraphAPIError(f"Instagram media container {container_id} expired before publish")
        time.sleep(IG_CONTAINER_POLL_SECONDS)
    raise GraphAPIError(f"Instagram media container {container_id} not ready after polling")


def post_to_instagram(
    text: str,
    image_url: str,
    ig_user_id: str,
    token: str,
    alt_text: str | None = None,
    as_story: bool = True,
) -> dict:
    """Two-step Instagram publish: create container, then media_publish.

    Default is a Story (media_type=STORIES), 9:16. Facebook keeps the
    feed photo. media_publish is not retried — a lost response may already
    have posted.
    """
    kind = "story" if as_story else "feed"
    logger.info("Creating Instagram %s container for %s (%d chars)", kind, ig_user_id, len(text))
    params: dict[str, Any] = {"image_url": image_url}
    if as_story:
        params["media_type"] = "STORIES"
    else:
        params["caption"] = text
        if alt_text:
            params["alt_text"] = alt_text[:1000]
    container = _graph_post(f"/{ig_user_id}/media", token, params)
    container_id = container.get("id")
    if not container_id:
        raise GraphAPIError(f"Instagram /media did not return a container id: {container}")

    _wait_for_ig_container(str(container_id), token)

    logger.info("Publishing Instagram container %s", container_id)
    published = _graph_post(f"/{ig_user_id}/media_publish", token, {"creation_id": container_id})
    media_id = published.get("id")
    logger.info("Instagram %s succeeded (id=%s)", kind, media_id)
    return published


def post_instagram_carousel(
    text: str,
    image_urls: list[str],
    ig_user_id: str,
    token: str,
) -> dict:
    """Feed carousel: one child container per image, a CAROUSEL parent with
    the caption, then media_publish (not retried)."""
    logger.info("Creating Instagram carousel (%d images) for %s", len(image_urls), ig_user_id)
    children = []
    for url in image_urls:
        child = _graph_post(
            f"/{ig_user_id}/media", token, {"image_url": url, "is_carousel_item": "true"}
        )
        child_id = child.get("id")
        if not child_id:
            raise GraphAPIError(f"Instagram carousel item returned no id: {child}")
        _wait_for_ig_container(str(child_id), token)
        children.append(str(child_id))
    parent = _graph_post(
        f"/{ig_user_id}/media",
        token,
        {"media_type": "CAROUSEL", "children": ",".join(children), "caption": text},
    )
    parent_id = parent.get("id")
    if not parent_id:
        raise GraphAPIError(f"Instagram carousel container returned no id: {parent}")
    _wait_for_ig_container(str(parent_id), token)
    logger.info("Publishing Instagram carousel %s", parent_id)
    published = _graph_post(f"/{ig_user_id}/media_publish", token, {"creation_id": parent_id})
    logger.info("Instagram carousel succeeded (id=%s)", published.get("id"))
    return published


def _story_image_url(page_id: str, token: str, path: str) -> str:
    try:
        return _upload_unpublished_photo(page_id, token, path)
    except (GraphAPIError, OSError) as exc:
        logger.warning("Unpublished story photo failed (%s); using a temporary host", exc)
        return _host_image_temporarily(path)


def post_to_meta(
    text: str,
    image_path: str | None = None,
    alt_text: str | None = None,
    story_path: str | None = None,
    *,
    platforms: list[str] | None = None,
    heritage_path: str | None = None,
    heritage_story_path: str | None = None,
) -> dict:
    """Post the daily panjika to Facebook and, when linked, Instagram.

    The 'ଜାଣନ୍ତୁ ଓଡ଼ିଶା' heritage card is a second image: Facebook gets a
    two-photo post; Instagram gets a carousel (feed mode) or a second Story
    (story mode). The heritage card is strictly optional — if it cannot be
    attached the panji still posts, and a failed second Story is only a
    warning (it never turns the run red, so a catch-up run cannot re-post
    the panji Story).

    Duplicate-post prevention is layered:
      1. GitHub Actions cache keyed by IST date
      2. Recent-post caption fingerprint on each platform

    A failure on one platform does not skip the other. If any *attempted*
    platform fails, this raises after both have been tried, so the workflow
    stays red and the next run can finish the missing side.
    """
    creds = _load_credentials()
    as_story = os.getenv("INSTAGRAM_AS_STORY", "true").lower() != "false"
    want = {p.lower().strip() for p in (platforms or ["facebook", "instagram"])}
    logger.info("Meta credentials present, targeting Page %s", creds.page_id)

    ig_user_id = creds.ig_user_id
    try:
        discovered = _discover_instagram_user_id(creds.page_id, creds.access_token)
        if discovered and not ig_user_id:
            ig_user_id = discovered
        elif discovered and ig_user_id and discovered != ig_user_id:
            logger.warning(
                "META_IG_USER_ID=%s does not match the Page's linked account %s; using META_IG_USER_ID",
                ig_user_id,
                discovered,
            )
    except GraphAPIError as exc:
        logger.warning("Could not look up the Page's Instagram account: %s", exc)

    results: dict = {"facebook": None, "instagram": None}
    errors: list[str] = []
    facebook_photo_id: str | None = None
    heritage_photo_id: str | None = None

    if "facebook" in want:
        if _already_posted(_recent_facebook_captions(creds.page_id, creds.access_token), text):
            logger.info("Skipping Facebook: already posted today's panjika")
            results["facebook"] = {"skipped": True, "reason": "already_posted"}
        else:
            try:
                fb = post_to_facebook(
                    text,
                    image_path,
                    creds.page_id,
                    creds.access_token,
                    extra_image_paths=[heritage_path] if heritage_path else None,
                )
                results["facebook"] = fb
                photo_ids = fb.get("photo_ids") or []
                facebook_photo_id = photo_ids[0] if photo_ids else None
                heritage_photo_id = photo_ids[1] if len(photo_ids) > 1 else None
            except GraphAPIError as exc:
                errors.append(f"Facebook: {exc}")
                logger.error("Facebook post failed: %s", exc)
                results["facebook"] = {"error": str(exc)}

    if "instagram" not in want:
        results["instagram"] = {"skipped": True, "reason": "not_requested"}
    elif not ig_user_id:
        logger.warning(
            "No Instagram professional account linked to this Page "
            "(set META_IG_USER_ID or connect IG in Meta Business Suite) — skipping Instagram"
        )
        results["instagram"] = {"skipped": True, "reason": "not_linked"}
    elif not image_path or not os.path.exists(image_path):
        logger.warning("Skipping Instagram: an image is required (Instagram has no text-only feed post)")
        results["instagram"] = {"skipped": True, "reason": "no_image"}
    elif not as_story and _already_posted(_recent_instagram_captions(ig_user_id, creds.access_token), text):
        logger.info("Skipping Instagram: already posted today's panjika")
        results["instagram"] = {"skipped": True, "reason": "already_posted"}
    else:
        try:
            ig_file = story_path if (as_story and story_path and os.path.exists(story_path)) else image_path
            if as_story:
                image_url = _story_image_url(creds.page_id, creds.access_token, ig_file)
                results["instagram"] = post_to_instagram(
                    text, image_url, ig_user_id, creds.access_token, as_story=True
                )
            else:
                image_url = _resolve_instagram_image_url(ig_file, creds.access_token, facebook_photo_id)
                heritage_url = None
                if heritage_path and os.path.exists(heritage_path):
                    try:
                        heritage_url = _resolve_instagram_image_url(
                            heritage_path, creds.access_token, heritage_photo_id
                        )
                    except (GraphAPIError, OSError) as exc:
                        logger.warning("Heritage image unavailable for carousel (%s); single image", exc)
                if heritage_url:
                    results["instagram"] = post_instagram_carousel(
                        text, [image_url, heritage_url], ig_user_id, creds.access_token
                    )
                else:
                    results["instagram"] = post_to_instagram(
                        text,
                        image_url,
                        ig_user_id,
                        creds.access_token,
                        alt_text=alt_text,
                        as_story=False,
                    )
        except (GraphAPIError, OSError) as exc:
            errors.append(f"Instagram: {exc}")
            logger.error("Instagram post failed: %s", exc)
            results["instagram"] = {"error": str(exc)}

        # Second Story (heritage) only after the panji Story is live; best-effort.
        heritage_story = heritage_story_path if heritage_story_path and os.path.exists(heritage_story_path) else None
        if as_story and heritage_story and isinstance(results["instagram"], dict) and results["instagram"].get("id"):
            try:
                url = _story_image_url(creds.page_id, creds.access_token, heritage_story)
                hs = post_to_instagram(text, url, ig_user_id, creds.access_token, as_story=True)
                results["instagram"]["heritage_story"] = {"id": hs.get("id")}
            except (GraphAPIError, OSError) as exc:
                logger.warning("Heritage Story failed (panji Story is live; not retried): %s", exc)
                results["instagram"]["heritage_story"] = {"error": str(exc)}

    if errors:
        err = RuntimeError("Posting failed: " + "; ".join(errors))
        err.results = results  # type: ignore[attr-defined]
        raise err
    return results


def _platform_view(raw: Any, platform: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {"status": "error", "platform": platform, "message": "not attempted"}
    if raw.get("skipped"):
        return {
            "status": "skipped",
            "platform": platform,
            "message": raw.get("reason") or "skipped",
        }
    if raw.get("error"):
        return {"status": "error", "platform": platform, "message": str(raw["error"])[:300]}
    post_id = raw.get("post_id") or raw.get("id") or raw.get("media_id")
    if post_id:
        return {"status": "posted", "platform": platform, "post_id": post_id}
    return {"status": "error", "platform": platform, "message": str(raw)[:300]}


def post_facebook_page(message: str, *, image_url: str | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper used by older tests. Prefer post_to_meta."""
    cfg = meta_config()
    if not cfg["page_id"] or not cfg["token"]:
        _log_social("facebook", {"status": "logged", "message": message[:500]})
        return {
            "status": "logged",
            "platform": "facebook",
            "message": "META_PAGE_ID / META_PAGE_ACCESS_TOKEN not set — saved to logs/daily_social.log",
        }
    try:
        fb = post_to_facebook(message, None, cfg["page_id"], cfg["token"])
        return {
            "status": "posted",
            "platform": "facebook",
            "post_id": fb.get("post_id") or fb.get("id"),
        }
    except GraphAPIError as exc:
        _log_social("facebook", {"status": "error", "message": str(exc)})
        return {"status": "error", "platform": "facebook", "message": str(exc)}


def post_instagram_feed(caption: str, image_url: str) -> dict[str, Any]:
    """Backward-compatible wrapper. Prefer post_to_meta."""
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
            "message": "Instagram requires a public HTTPS image_url",
        }
    try:
        published = post_to_instagram(
            caption, image_url, cfg["ig_user_id"], cfg["token"], as_story=False
        )
        return {
            "status": "posted",
            "platform": "instagram",
            "media_id": published.get("id"),
        }
    except GraphAPIError as exc:
        _log_social("instagram", {"status": "error", "message": str(exc)})
        return {"status": "error", "platform": "instagram", "message": str(exc)}


def post_meta_bundle(
    panchang: dict,
    enrichment: dict | None = None,
    *,
    platforms: list[str] | None = None,
    public_base: str | None = None,
) -> dict[str, Any]:
    """
    Generate JPEG cards + caption and post to requested platforms.
    platforms: subset of facebook, instagram (default both).
    """
    from src.social_card import generate_daily_card, generate_story_card, public_card_url

    from src.festival_audit import PublishBlocked, prepare_for_publish

    platforms = [p.lower().strip() for p in (platforms or ["facebook", "instagram"])]
    try:
        panchang, unverified = prepare_for_publish(panchang)
    except PublishBlocked as exc:
        # Festival list contradicts the verified reference: never announce it.
        logger.error("Publish blocked — festival dates failed verification: %s", exc)
        _log_social("bundle", {"status": "blocked", "reason": str(exc)})
        return {
            "date": panchang.get("date"),
            "status": "error",
            "message": f"Festival verification failed: {exc}"[:300],
            "platforms": {
                name: {"status": "error", "platform": name, "message": "festival verification failed"}
                for name in platforms
            },
        }
    if unverified:
        logger.warning("Not announcing unverified festivals: %s", ", ".join(unverified))
    card_path = generate_daily_card(panchang, enrichment)
    story_path = None
    as_story = os.getenv("INSTAGRAM_AS_STORY", "true").lower() != "false"
    if "instagram" in platforms and as_story:
        try:
            story_path = generate_story_card(panchang, enrichment, feed_path=card_path)
        except Exception as exc:
            logger.warning("Story card failed (Instagram may skip or use feed card): %s", exc)

    heritage_path = heritage_story_path = None
    if os.getenv("SOCIAL_HERITAGE_CARD", "true").lower() != "false":
        from src.social_card import generate_heritage_card, generate_heritage_story_card

        try:
            heritage_path = generate_heritage_card(panchang)
            if "instagram" in platforms and as_story:
                heritage_story_path = generate_heritage_story_card(
                    panchang, heritage_path=heritage_path
                )
        except Exception as exc:  # noqa: BLE001 — optional second image
            logger.warning("Heritage card failed (posting the panji card alone): %s", exc)
            heritage_path = heritage_story_path = None

    caption = generate_social_caption(panchang, enrichment)
    image_url = public_card_url(card_path, public_base=public_base)
    results: dict[str, Any] = {
        "date": panchang.get("date"),
        "image_url": image_url,
        "card_path": str(card_path),
        "story_path": str(story_path) if story_path else None,
        "heritage_path": str(heritage_path) if heritage_path else None,
        "facebook_message": caption,
        "instagram_caption": caption,
        "platforms": {},
    }

    if not meta_configured():
        _log_social(
            "bundle",
            {"status": "logged", "caption": caption[:500], "card": str(card_path)},
        )
        for name in platforms:
            results["platforms"][name] = {
                "status": "logged",
                "platform": name,
                "message": "META_PAGE_ID / META_PAGE_ACCESS_TOKEN not set — saved to logs/daily_social.log",
            }
        results["status"] = "logged"
        return results

    raw: dict = {}
    err_msg = ""
    try:
        raw = post_to_meta(
            caption,
            image_path=str(card_path),
            story_path=str(story_path) if story_path else None,
            platforms=platforms,
            heritage_path=str(heritage_path) if heritage_path else None,
            heritage_story_path=str(heritage_story_path) if heritage_story_path else None,
        )
    except RuntimeError as exc:
        logger.error("Meta bundle posting failed: %s", exc)
        raw = getattr(exc, "results", None) or {}
        err_msg = str(exc)[:300]

    for name in platforms:
        view = _platform_view(raw.get(name), name)
        if view["status"] == "error" and err_msg and not view.get("message"):
            view["message"] = err_msg
        results["platforms"][name] = view

    statuses = [v.get("status") for v in results["platforms"].values()]
    if statuses and all(s in ("posted", "skipped") for s in statuses):
        results["status"] = "posted"
    elif statuses and any(s == "posted" for s in statuses):
        results["status"] = "partial"
    else:
        results["status"] = "error"
    if err_msg:
        results["message"] = err_msg
    return results
